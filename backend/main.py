from contextlib import asynccontextmanager
from fastapi import FastAPI
from pathlib import Path

from loguru import logger
from .models import PathRequest, TextRequest, TextResponse, PathResponse

from .populate import populate_db
from .core_functions import final_response, generate_audio, generate_text_from_audio


@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_db()
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
