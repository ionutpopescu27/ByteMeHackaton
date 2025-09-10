
# cache.py - simple SQLite cache for Q/A
import sqlite3
from datetime import datetime
from typing import Optional

class QAStore:
    def __init__(self, db_path: str = "cache.db") -> None:
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS qa_cache (
                    qkey TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    answer   TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _mk_key(self, question: str, scope: str) -> str:
        return f"{scope}::{question.strip()}"

    def get_answer(self, question: str, scope: str = "general") -> Optional[str]:
        key = self._mk_key(question, scope)
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT answer FROM qa_cache WHERE qkey = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def save_qa(self, question: str, answer: str, scope: str = "general") -> None:
        key = self._mk_key(question, scope)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO qa_cache(qkey, question, answer, created_at) VALUES (?, ?, ?, ?)",
                (key, question.strip(), answer, datetime.utcnow().isoformat(timespec="seconds")),
            )
            conn.commit()
