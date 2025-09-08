# reporting.py
from __future__ import annotations
from typing import Optional, Dict, Union
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime


class ConversationReport(BaseModel):
    id: str
    timestamp: datetime
    query: str
    collection_name: str
    k: int
    answer: str
    model: Optional[str] = None
    path_to_pdf: Union[Path, None]
    number_of_page: int


def render_report_md(r: ConversationReport) -> str:
    lines = [
        f"# Conversation Report {r.id}",
        f"# Pdf {r.path_to_pdf}",
        f"# Number of page of pdf {r.number_of_page}",
        f"- **Timestamp:** {r.timestamp.isoformat()}",
        f"- **Collection:** {r.collection_name}",
        f"- **Query:** {r.query}",
        f"- **k:** {r.k}",
        "",
        "## Answer",
        r.answer,
    ]
    return "\n".join(lines)


def save_report_files(r: ConversationReport) -> Dict[str, str]:
    reports_dir = Path("./reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    json_path = reports_dir / f"{r.id}.json"
    md_path = reports_dir / f"{r.id}.md"
    json_path.write_text(r.model_dump_json(indent=2), encoding="utf-8")
    md_path.write_text(render_report_md(r), encoding="utf-8")
    return {"json": str(json_path), "md": str(md_path)}
