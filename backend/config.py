import os
from pathlib import Path  # ← ADDED
from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine which env file to use (prod vs dev), but resolve it RELATIVE TO THIS FILE
BASE_DIR = Path(__file__).resolve().parent                # backend/
mode = os.getenv("ENV")
env_filename = ".env" if mode != "production" else ".env.production"
ENV_PATH = BASE_DIR / env_filename                        # ← KEY CHANGE (absolute path)

logger.debug(f"Loading env file: {ENV_PATH}")

# Load env for the whole process (so other libs can see it, too)
load_dotenv(dotenv_path=ENV_PATH)                         # ← KEY CHANGE

class __Settings(BaseSettings):
    # Make Pydantic also read the SAME file explicitly
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")  # ← KEY CHANGE

    OPENAI_MODEL_NAME_TEXT: str = Field("Model name for text")
    OPENAI_MODEL_NAME_TTS: str = Field("Model name for tts")
    OPENAI_MODEL_NAME_EMBEDDING: str = Field("Model name for embeddings")
    OPENAI_MODEL_NAME_STT: str = Field("Model for speech to text")
    OPENAI_MODEL_NAME_IMAGE: str = Field("Model for image generation")
    OPENAI_API_KEY: str = Field("Api key")

# Always use this settings rather than instantiating __Settings directly
settings = __Settings()  # type: ignore

if mode != "production":
    # ⚠️ This will print your API key in logs. Consider masking it or removing in production.
    logger.debug(settings.model_dump_json(indent=3))
