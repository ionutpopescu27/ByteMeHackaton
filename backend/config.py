import os
from dotenv import load_dotenv
from loguru import logger
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# trebuie sa dai log la toate detaliile de configurare a unui proiect
load_dotenv()

parent = os.getcwd()


env_file = ".env"
mode = os.getenv("ENV")

if mode == "production":
    logger.info("Running in production..." + env_file)
    env_file = ".env.production"

logger.debug(f"Loading env file: {env_file}")

# loading env for prisma schema that don't have access to this settings class
load_dotenv(env_file)


class __Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=env_file, extra="ignore")

    OPENAI_MODEL_NAME_TEXT: str = Field("Model name for text")
    OPENAI_MODEL_NAME_TTS: str = Field("Model name for tts")
    OPENAI_MODEL_NAME_EMBEDDING: str = Field("Model name for embeddings")
    OPENAI_MODEL_NAME_STT: str = Field("Model for speech to text")
    OPENAI_MODEL_NAME_IMAGE: str = Field("Model for image generation")
    OPENAI_API_KEY: str = Field("Api key")


# all ways use this settings rather than using __Settings()
settings = __Settings()  # type: ignore

if not mode == "production":
    logger.debug(settings.model_dump_json(indent=3))
