from contextlib import asynccontextmanager
from datetime import datetime, timezone
import uuid
from fastapi import FastAPI, HTTPException
from pathlib import Path

from loguru import logger
from .models import (
    PathRequest,
    TextRequest,
    TextResponse,
    PathResponse,
    PdfsRequest,
    QueryRequest,
)

from .populate import populate_db
from .core_functions import (
    final_response,
    generate_audio,
    generate_text_from_audio,
    final_response_gpt,
    search_text_in_pdfs,
)
from .tmp_databases.query import add_pdfs, query_db, populate_db_tmp
from .raport.reporting import (
    ConversationReport,
    Match,
    build_summary_plain,
    save_report_files,
)
from .config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_db()
    populate_db_tmp()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello World"}


# POST : http://127.0.0.1:8000/rsp
# {
#   "text": "How can I file an insurance claim?"
# }
@app.post("/rsp", response_model=TextResponse)
async def response_from_llm(request: TextRequest) -> TextResponse:
    reply = await final_response(request.text)
    logger.debug(f"Generated reply text: {reply}")
    return TextResponse(text=reply)


#  POST : http://127.0.0.1:8000/tts
# {
#   "text": "How can I file an insurance claim?"
# }
@app.post("/tts")
async def tts(request: TextRequest) -> PathResponse:
    """
    Need the text to return the path to the audio
    """
    audio_path: str = await generate_audio(request.text)
    logger.debug(f"Generated audio path : {audio_path}")
    return PathResponse(path=Path(audio_path))


# POST: http://127.0.0.1:8000/speech
# {
#   "path": "/home/alex/projects/hackaton_endava/backend/out/audio/56943cb325764722b95fb34cf0009107.mp3"
# }
@app.post("/speech")
async def speech_to_text(request: PathRequest) -> TextResponse:
    """
    Need the path of the speech that we will returns the text of that
    """
    text: str = await generate_text_from_audio(request.path)
    logger.debug(f"Generated text from path {request.path}, text: {text}")
    return TextResponse(text=text)


# POST http://127.0.0.1:8000/populate_chroma
# {
#   "paths": ["/home/alex/projects/hackaton_endava/backend/tmp_databases/Insurance.pdf"]
# }
@app.post("/populate_chroma")
async def populate_chroma(request: PdfsRequest) -> TextResponse:
    """
    Need a list of paths of pdfs
    """
    # we generate a collection name by guid
    collection_name = f"docs_{uuid.uuid4()}"
    add_pdfs(request.paths, collection_name)
    return TextResponse(text=collection_name)


# POST http://127.0.0.1:8000/q_db
# {
#   "text": "What is third party insurance?",
#   "collection_name": "docs_824bea41-28d0-4a58-a459-bd50e857e6d2",
#   "k": 2
# }
@app.post("/q_db")
async def q_db(request: QueryRequest):
    try:
        docs = query_db(request.text, request.collection_name, request.k)

        return {"matches": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST http://127.0.0.1:8000/rsp_db
# {
#   "text": "Who is Motor Third Party Insurance claim process",
#   "collection_name": "docs_824bea41-28d0-4a58-a459-bd50e857e6d2",
#   "k": 3
# }
@app.post("/rsp_db")
async def rsp_db(request: QueryRequest) -> TextResponse:
    try:
        docs = query_db(request.text, request.collection_name, request.k)
        answer = await final_response_gpt(request.text, docs)  # type: ignore
        summary = build_summary_plain(docs)  # type: ignore
        # TODO: ar trebui sa caut in ce fisier e docs si sa returnez fisierul si pagina + rand
        # docs e o lista de string-uri , pot sa iau
        path_pdf, number_page = await search_text_in_pdfs(
            Path("./tmp_databases/"), docs[0]
        )
        logger.debug(f"Path pdf {path_pdf} , number of page {number_page}")
        report = ConversationReport(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            query=request.text,
            collection_name=request.collection_name,
            k=request.k,
            matches=[Match(rank=i + 1, text=t) for i, t in enumerate(docs)],
            summary=summary,  # poate il sterg, e cam inutil
            answer=answer,
            model=getattr(settings, "OPENAI_MODEL_NAME_TEXT", None),
            path_to_pdf=path_pdf,  # type:ignore
            number_of_page=number_page,
        )
        paths = save_report_files(report)
        logger.debug(paths)
        return TextResponse(text=str(answer))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
