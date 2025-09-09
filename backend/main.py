# main.py
from contextlib import asynccontextmanager
import re
import uuid
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # <<< ADDED

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
    check_if_user_wants_form,
    generate_form_json,
)
from .tmp_databases.query import add_pdfs, query_db, populate_db_tmp
from .repo import (
    start_new_conversation,
    append_message,
    close_conversation,
    extract_phone,
    get_conversations_with_messages_by_phone,
    conversation_to_dict,
)
from .database import init_db_conversations, MessageRole

# >>> ADDED: import our new router
from .documents import router as documents_router  # <<< ADDED


BASE_URL = ""


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db_conversations()

    # Seed Q/A collection (skip on error so startup continues)
    try:
        populate_db(path=str(Path(__file__).with_name("db.json")))
    except Exception as e:
        logger.warning(f"populate_db skipped due to error: {e}")  # <<< ADDED

    # Seed tmp pdfs into chroma (skip on error so startup continues)
    try:
        populate_db_tmp()  # may call embeddings; guard it
    except Exception as e:
        logger.warning(f"populate_db_tmp skipped due to error: {e}")  # <<< ADDED

    app.state.conversation_id = await start_new_conversation(str(uuid.uuid4()))
    yield


app = FastAPI(lifespan=lifespan)

# CORS so the React dev server can call the API  # <<< ADDED
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# >>> ADDED: register the router (prefix left empty on purpose)
app.include_router(documents_router)  # <<< ADDED


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
    # we add to the db
    await append_message(app.state.conversation_id, MessageRole.user, request.text)
    await append_message(app.state.conversation_id, MessageRole.bot, reply)
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
async def rsp_db(request: QueryRequest):  # -> TextResponse:
    try:
        answer = await check_if_user_wants_form(request.text)
        if re.search("YES", answer) is not None:
            # await append_message(
            #     app.state.conversation_id, MessageRole.user, request.text
            # )
            logger.debug("User wants a form, sending on other server...")
            js = await generate_form_json(request.text)
            logger.debug(js)

            return "Sent a sms", js
            return TextResponse(text="Sent a sms")

        logger.debug(f"Check if user wants a form : {answer}")
        docs = query_db(request.text, request.collection_name, request.k)
        answer_gpt = await final_response_gpt(request.text, docs)  # type: ignore
        path_pdf, number_page = await search_text_in_pdfs(
            Path("./tmp_databases/"), docs[0]
        )
        logger.debug(f"Path pdf {path_pdf} , number of page {number_page}")

        # await append_message(app.state.conversation_id, MessageRole.user, request.text)
        # await append_message(
        #     app.state.conversation_id,
        #     MessageRole.bot,
        #     answer_gpt,
        #     path_df=str(path_pdf),
        #     number_page=number_page,
        # )
        return TextResponse(text=str(answer_gpt))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/stop_call")
async def stop_call(request: TextRequest) -> TextResponse:
    phone = extract_phone(request.text)
    await close_conversation(app.state.conversation_id, phone)
    app.state.conversation_id = await start_new_conversation(conv_id=str(uuid.uuid4()))
    logger.debug(f"Phone number {phone}")
    return TextResponse(text=f"Call ended. Phone={phone}. New conversation started.")


# POST http://127.0.0.1:8000/conv
# {
#   "text": "+40774596204"
# }
@app.post("/conv")
async def conversations_by_phone(request: TextRequest):
    conversations = await get_conversations_with_messages_by_phone(request.text)
    return [conversation_to_dict(c) for c in conversations]
