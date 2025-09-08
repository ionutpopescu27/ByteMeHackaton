from typing import Union
import chromadb
import re
import os
from langchain_openai import OpenAIEmbeddings
from pathlib import Path
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger
from chromadb.utils import embedding_functions
from ..config import settings

client = chromadb.PersistentClient("./db/")
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=settings.OPENAI_API_KEY,
    model_name=settings.OPENAI_MODEL_NAME_EMBEDDING,
)
embeddings = OpenAIEmbeddings(
    model=settings.OPENAI_MODEL_NAME_EMBEDDING,  # "text-embedding-3-small"
    api_key=settings.OPENAI_API_KEY,  # type: ignore
)


def populate_db_tmp():
    lst = []
    abs_path = os.path.abspath("./tmp_databases/Insurance.pdf")
    lst.append(abs_path)
    add_pdfs(lst, "insurance_docs")


def add_pdfs(file_paths: list[Path], collection_name: str):
    "We take the pdfs paths, the collection name , and we populate chroma db"
    for file_path in file_paths:
        loader = PyPDFLoader(file_path)
        document = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        chunked_documents = text_splitter.split_documents(document)

        Chroma.from_documents(
            documents=chunked_documents,
            embedding=embeddings,
            collection_name=collection_name,
            client=client,
        )

        logger.debug(
            f"Added {len(chunked_documents)} chunks to chroma db, in the collection_name {collection_name}"
        )


HEADER_PATS = [
    re.compile(r"^\s*PHOTO\s*$", re.I),
    re.compile(r"^\s*UNDERSTANDING INSURANCE\s*$", re.I),
    re.compile(r"^\s*\d+\s*$"),  # linii doar cu număr (ex. "4")
]


def _clean_pdf_text(s: str) -> str:
    # do not touch chat gpt been here, just simple function to clean text
    s = s.replace("\xa0", " ")
    s = s.replace("\u00ad", "")
    s = s.replace("\uf0fc", "• ")
    s = re.sub(r"[\uE000-\uF8FF]", "", s)

    s = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1-\2", s)

    lines = s.splitlines()
    keep = []
    for line in lines:
        if any(p.match(line) for p in HEADER_PATS):
            continue
        keep.append(line)

    s = " ".join(keep)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def query_db(
    query: str, collection_name: str, k: int, join: bool = False
) -> Union[list[str], str]:
    "Take the query, collection_name and return top k number of results from the docs"
    collection = client.get_collection(
        name=collection_name,
        embedding_function=openai_ef,  # type: ignore
    )

    results = collection.query(
        query_texts=[query],
        n_results=k,
        include=["documents"],
    )

    raw_docs = results["documents"][0]  # type: ignore
    cleaned = [_clean_pdf_text(d or "") for d in raw_docs]

    return " ".join(cleaned).strip() if join else cleaned


if __name__ == "__main__":
    pass
