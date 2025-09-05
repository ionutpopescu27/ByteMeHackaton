# populate.py
import chromadb
import json
from loguru import logger

# chromadb imports
from chromadb.api.types import EmbeddingFunction
import chromadb.utils.embedding_functions as embedding_functions

# local imports
from .config import settings

client = chromadb.PersistentClient(path="./db/")

openai_embedding: EmbeddingFunction = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name=settings.OPENAI_MODEL_NAME_EMBEDDING,
)

collection = client.get_or_create_collection(
    name="my_db",
    embedding_function=openai_embedding,  # type:ignore
)


def populate_db(path: str = "./db.json"):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
    questions = data["questions"]
    qs = [q["question"] for q in questions]
    answers = [q["answer"] for q in questions]

    collection.add(documents=qs, ids=answers)
    logger.info(f"Number of documents in populated collection: {collection.count()}")


if __name__ == "__main__":
    populate_db()
