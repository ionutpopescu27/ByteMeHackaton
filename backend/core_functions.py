# core_functions.py
import unicodedata
from openai import OpenAI
import re
from fastapi import HTTPException, status
import PyPDF2
import os
import uuid
from pathlib import Path
import requests
from loguru import logger
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Any, Dict, List, Union, Tuple

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
    answers: Union[Dict[str, Any], List[str], List[Dict[str, Any]]],
) -> List[str]:
    """
    Normalize various answer shapes into a simple list[str] of texts.
    Accepts:
      - dict: {"doc_1": {"text": "..."} , "doc_2": "..." , ...}
      - list[str]
      - list[dict] with keys like "text" or "page_content"
    """
    texts: List[str] = []

    if isinstance(answers, dict):
        for _, v in answers.items():
            if isinstance(v, str):
                t = v.strip()
                if t:
                    texts.append(t)
            elif isinstance(v, dict):
                t = (v.get("text") or v.get("page_content") or "").strip()
                if t:
                    texts.append(t)
            else:
                t = str(v).strip()
                if t:
                    texts.append(t)

    elif isinstance(answers, list):
        for v in answers:
            if isinstance(v, str):
                t = v.strip()
                if t:
                    texts.append(t)
            elif isinstance(v, dict):
                t = (v.get("text") or v.get("page_content") or "").strip()
                if t:
                    texts.append(t)
            else:
                t = str(v).strip()
                if t:
                    texts.append(t)

    return texts


def _build_summary(docs: List[str], max_chars: int = 1600) -> str:
    """
    Build a minimal, literal summary by concatenating the doc texts,
    preserving content (e.g., years like 1989). Truncate only by length.
    """
    parts: List[str] = []
    used = 0
    for t in docs:
        if not t:
            continue
        # squash newlines to avoid prompt bloat, but keep text as-is
        t_flat = " ".join(t.split())
        if not t_flat:
            continue

        remaining = max_chars - used
        if remaining <= 0:
            break

        if len(t_flat) > remaining:
            t_flat = t_flat[:remaining].rstrip()

        parts.append(t_flat)
        used += len(t_flat) + 1  # +1 for join separator

    return "\n".join(parts)


async def generate_response(answers: Dict[str, Any], user_query: str) -> str:
    "Generate the response using OpenAI API"
    logger.debug(f"Answers: {answers}")
    items = _coerce_docs(answers)
    summary = _build_summary(items)
    logger.debug(f"Summary : {summary}")

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
        "Be clear, friendly, and direct and if years appear do not change them."
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
    answers = get_top_answers(query=prompt, k=3)
    logger.debug(f"Top 3 answers : {answers}, generated from prompt : {prompt}")
    gpt_answer = await generate_response(answers, user_query=prompt)  # type: ignore
    return gpt_answer


def list_to_answers_dict(lst: List[str]) -> Dict[str, Any]:
    """
    Convertește o listă de string-uri într-un dict compatibil generate_response.
    Cheia va fi doc_1, doc_2, ..., iar payload-ul minim are câmpul 'text'.
    """
    return {f"doc_{i + 1}": {"text": s} for i, s in enumerate(lst)}


async def final_response_gpt(query: str, lst: List[str]) -> str:
    logger.debug(f"Prompt was : {query}")
    for i in range(len(lst)):
        logger.debug(f"Match {i} was : {lst[i]}")
    #     logger.debug(f"Responses collected {lst}, with prompt {query}")
    answers: Dict[str, Any] = list_to_answers_dict(lst)
    gpt_answer = await generate_response(answers, query)
    logger.debug(f"Generated response from gpt : {gpt_answer}")
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


# WARN: Do not touch chat gpt cooked
def _normalize(s: str) -> str:
    # Normalize Unicode, replace NBSP with space, collapse whitespace, lowercase
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("\u00a0", " ")  # NBSP -> space
    s = s.replace("\u200b", "")  # zero-width space
    s = re.sub(r"\s+", " ", s)  # collapse all whitespace
    return s.strip().lower()


def _flex_pattern(phrase: str) -> re.Pattern:
    # Build regex that ignores arbitrary whitespace between words
    # e.g. "Documents required to support a claim" ->
    # r'\bDocuments\s+required\s+to\s+support\s+a\s+claim\b' (case-insensitive)
    words = [re.escape(w) for w in phrase.split()]
    regex = r"\b" + r"\s+".join(words) + r"\b"
    return re.compile(regex, re.IGNORECASE)


async def search_text_in_pdfs(
    directory_pdfs: Path, text: str
) -> Tuple[Union[Path, None], int]:
    """
    Returns (pdf_path, 1-based page_number) of the first page containing `text`,
    using normalization + flexible whitespace matching. If not found, (None, -1).
    """
    # Use a short anchor (first ~8 words) to avoid over-specific matching
    anchor = " ".join((text or "").split()[:8]).strip()
    if not anchor:
        return None, -1

    pattern = _flex_pattern(anchor)

    for file in directory_pdfs.glob("*.pdf"):
        try:
            reader = PyPDF2.PdfReader(file)
        except Exception:
            continue
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                raw = page.extract_text() or ""
            except Exception:
                raw = ""
            # Normalize *for a fallback contains check*
            norm_page = _normalize(raw)
            norm_anchor = _normalize(anchor)

            # Fast path: normalized substring (handles NBSP/newlines)
            if norm_anchor and norm_anchor in norm_page:
                return file, page_number

            # Slower path: flexible whitespace regex on the raw text
            if pattern.search(raw):
                return file, page_number

    return None, -1
