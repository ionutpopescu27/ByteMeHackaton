# core_functions.py
from openai import OpenAI
import os
import uuid
from pathlib import Path
import requests
from loguru import logger
from fastapi import HTTPException, status
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Any, Dict, List, Tuple, Optional

# local imports
from .populate import collection, openai_embedding
from .config import settings


def get_top_answers(query: str, k: int):
    "Function that will look the local chroma db collection and retrieve top k answers"
    query_embedding = openai_embedding.embed_with_retries(query)
    results = collection.query(query_embeddings=query_embedding, n_results=k)
    return results


# ---- Helpers ----


def _coerce_docs(
    results: Dict[str, Any],
) -> List[Tuple[str, Optional[Dict[str, Any]], Optional[float]]]:
    """
    Flatten Chroma's nested lists into [(doc, metadata, distance), ...].
    Handles both single-query and multi-query shapes.
    """
    docs = results.get("documents") or []
    metas = results.get("metadatas") or []
    dists = results.get("distances") or []

    if docs and isinstance(docs[0], list):
        docs = docs[0]
        metas = metas[0] if metas and isinstance(metas[0], list) else [None] * len(docs)
        dists = dists[0] if dists and isinstance(dists[0], list) else [None] * len(docs)
    else:
        if metas and not isinstance(metas, list):
            metas = [metas] * len(docs)
        if dists and not isinstance(dists, list):
            dists = [dists] * len(docs)

    out: List[Tuple[str, Optional[Dict[str, Any]], Optional[float]]] = []
    for i, doc in enumerate(docs):
        meta = metas[i] if i < len(metas) else None
        dist = dists[i] if i < len(dists) else None
        if isinstance(doc, str):
            out.append((doc.strip(), meta, dist))
        else:
            out.append((str(doc).strip(), meta, dist))
    return out


def _build_summary(
    docs_meta_dists: List[Tuple[str, Optional[Dict[str, Any]], Optional[float]]],
    max_chars: int = 1600,
) -> str:
    """
    Make a tight summary block the model can riff on—concise, newline-separated.
    Truncates to avoid prompt bloat.
    """
    lines: List[str] = []
    for i, (doc, meta, dist) in enumerate(docs_meta_dists, start=1):
        tag_parts = []
        if meta:
            if "source" in meta:
                tag_parts.append(f"source={meta['source']}")
            if "category" in meta:
                tag_parts.append(f"category={meta['category']}")
        if dist is not None:
            tag_parts.append(f"score={round(dist, 4)}")

        tag = f" [{', '.join(tag_parts)}]" if tag_parts else ""
        snippet = doc.replace("\n", " ").strip()
        if len(snippet) > 300:
            snippet = snippet[:300].rstrip() + "…"
        lines.append(f"{i}. {snippet}{tag}")

        candidate = "\n".join(lines)
        if len(candidate) >= max_chars:
            break

    return "\n".join(lines) if lines else ""


async def generate_response(answers: Dict[str, Any], user_query: str) -> str:
    "Generate the response using OpenAI API"
    items = _coerce_docs(answers)
    summary = _build_summary(items)

    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "Summary not generated",
                "message": "Could not make the summary of the response try 1 better",
            },
        )
    system_template = (
        "You are a professional call center assistant for ByteMe Insurance. "
        "Always answer in the shortest possible way: 1 sentence if possible, maximum 2. "
        "Be clear, friendly, and direct. "
        "Do not repeat or rephrase the knowledge base text — just give the exact useful answer."
    )

    user_template = (
        "Customer asked: {question}\n\n"
        "Knowledge base entry:\n{summary}\n\n"
        "Answer the customer with the shortest possible helpful response."
    )

    prompt_tmpl = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            ("human", user_template),
        ]
    )

    model_text = ChatOpenAI(
        model=settings.OPENAI_MODEL_NAME_TEXT,
        temperature=0.2,
        max_tokens=100,
    )  # type: ignore

    chain = prompt_tmpl | model_text | StrOutputParser()
    extra: str = await chain.ainvoke({"summary": summary, "question": user_query})
    extra = (extra or "").strip()

    # hard stop 2 propozitii
    if extra.count(".") > 2:
        extra = " ".join(extra.split(".")[:2]).strip() + "."

    return extra


async def final_response(prompt: str) -> str:
    answers = get_top_answers(
        query=prompt, k=3
    )  # TODO: poate sa fie k dinamic in functie de intrebare
    logger.debug(f"Top 3 answers : {answers}, generated from prompt : {prompt}")
    # TODO: adauga daca raspunsurile nu sunt prea bune sa ceri sa reformulezi , daca nu s-a gasit ceva in db
    # si dai raise la un HTTPException
    gpt_answer = await generate_response(answers, user_query=prompt)  # type: ignore
    return gpt_answer


async def generate_audio(story: str) -> str:
    """
    Generating the audio for the story
    will return a path to the audio
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Missing OPENAI_API_KEY")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": settings.OPENAI_MODEL_NAME_TTS,  # should be 'tts-1'
        "input": story,
        "voice": "alloy",  # options: alloy, echo, fable, onyx, nova, shimmer
        "response_format": "mp3",
    }

    logger.debug("Requesting TTS from OpenAI...")

    response = requests.post(
        "https://api.openai.com/v1/audio/speech", headers=headers, json=data
    )

    if response.status_code != 200:
        logger.error(f"TTS API failed: {response.status_code} - {response.text}")
        raise RuntimeError("Failed to generate TTS audio")

    audio_path = Path("out/audio") / f"{uuid.uuid4().hex}.mp3"
    audio_path.parent.mkdir(parents=True, exist_ok=True)

    with open(audio_path, "wb") as f:
        f.write(response.content)

    logger.success(f"Saved TTS audio to: {audio_path}")
    directory = os.path.dirname(__file__)
    audio_path = os.path.join(directory, audio_path)
    return audio_path


async def generate_text_from_audio(path_audio: Path) -> str:
    "Here we just take the path of the audio and convert it to text"
    client = OpenAI()
    audio_file = open(path_audio, "rb")

    transcription = client.audio.transcriptions.create(
        model=settings.OPENAI_MODEL_NAME_STT, file=audio_file
    )

    logger.debug(
        f"Generating audio from path: {path_audio} - text : {transcription.text}"
    )
    return transcription.text
