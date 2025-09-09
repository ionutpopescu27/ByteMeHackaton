# documents.py
import os
import uuid
import sqlite3
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from loguru import logger

# Re-use your existing Chroma ingestion function directly
from .tmp_databases.query import add_pdfs  # same as in /populate_chroma

router = APIRouter()

BASE_DIR = os.getcwd()
UPLOAD_DIR = os.path.join(BASE_DIR, "backend\\tmp_databases")
os.makedirs(UPLOAD_DIR, exist_ok=True)

DOC_DB_PATH = os.path.join(BASE_DIR, "documents.db")


def _init_doc_db():
    with sqlite3.connect(DOC_DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                collection TEXT NOT NULL,
                uploaded_at TEXT NOT NULL,
                deleted INTEGER DEFAULT 0
            )
        """)
_init_doc_db()


def _insert_document(name: str, path: str, collection: str) -> int:
    with sqlite3.connect(DOC_DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO documents (name, path, collection, uploaded_at, deleted) VALUES (?, ?, ?, ?, 0)",
            (name, path, collection, datetime.utcnow().isoformat() + "Z"),
        )
        conn.commit()
        return cur.lastrowid


def _fetch_documents(include_deleted: bool = False, limit: Optional[int] = None):
    with sqlite3.connect(DOC_DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        q = "SELECT * FROM documents"
        args = []
        if not include_deleted:
            q += " WHERE deleted = 0"
        q += " ORDER BY datetime(uploaded_at) DESC"
        if limit is not None:
            q += " LIMIT ?"
            args.append(limit)
        rows = conn.execute(q, args).fetchall()
        return [dict(r) for r in rows]


@router.post("/upload_and_index")
async def upload_and_index(file: UploadFile = File(...)):
    """
    Accepts a PDF file from the frontend, saves it to tmp_databases/,
    indexes it into a new Chroma collection (docs_<uuid>), and stores metadata.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save to tmp_databases/
    save_path = os.path.join(UPLOAD_DIR, file.filename)
    if os.path.exists(save_path):
        name, ext = os.path.splitext(file.filename)
        save_path = os.path.join(UPLOAD_DIR, f"{name}_{int(datetime.now().timestamp())}{ext}")

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)
    logger.info(f"Saved PDF to {save_path}")

    # Create a fresh collection and add the PDF (same behavior as /populate_chroma)
    collection_name = f"docs_{uuid.uuid4()}"
    try:
        add_pdfs([save_path], collection_name)
    except Exception as e:
        logger.exception("Failed to add PDFs to Chroma")
        raise HTTPException(status_code=500, detail=f"Chroma ingestion failed: {str(e)}")

    # Store metadata we can query later
    doc_id = _insert_document(os.path.basename(save_path), save_path, collection_name)

    return {
        "id": doc_id,
        "name": os.path.basename(save_path),
        "path": save_path,
        "collection": collection_name,
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "deleted": 0,
    }


@router.get("/documents")
def list_documents(include_deleted: bool = Query(False)):
    """
    List all documents (non-deleted by default).
    """
    return _fetch_documents(include_deleted=include_deleted)


@router.get("/documents/recent")
def recent_documents(limit: int = Query(3)):
    """
    List the most recent N documents (defaults to 3).
    """
    return _fetch_documents(include_deleted=False, limit=limit)
