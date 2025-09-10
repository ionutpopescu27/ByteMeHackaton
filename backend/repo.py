# repo.py
import re
import unicodedata
from typing import Optional, Union, Dict, Any
import uuid
from datetime import datetime, timezone
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .database import (
    SessionLocal,
    Conversation,
    Message,
    MessageRole,
    ConversationLabel,
    Form,
)

PHONE_RE = re.compile(r"\+?\d[\d\s\-()]{6,}")


def extract_phone(text: str) -> Union[str, None]:
    m = PHONE_RE.search(text or "")
    return m.group(0).strip() if m else None


async def start_new_conversation(conv_id: str) -> str:
    conv_id = conv_id or str(uuid.uuid4())

    async with SessionLocal() as s:
        s.add(
            Conversation(
                id=conv_id,
                started_at=datetime.now(timezone.utc),
                phone_number=None,
                ended_at=None,
            )
        )
        await s.commit()
    return conv_id


async def append_message(
    conversation_id: str,
    role: MessageRole,
    text: str,
    path_df: Optional[str] = None,
    number_page: Optional[int] = None,
):
    async with SessionLocal() as s:
        s.add(
            Message(
                conversation_id=conversation_id,
                role=role,
                text=text,
                path_df=path_df,
                number_page=number_page,
            )
        )
        await s.commit()


SMS_KEYS = ("sent a sms", "sms", "link", "form link", "formular")
HUMAN_KEYS = ("human", "operator", "agent", "escalat", "escalation", "transfer")


def _normalize(s: str) -> str:
    return "".join(
        ch for ch in unicodedata.normalize("NFD", s) if unicodedata.category(ch) != "Mn"
    )


SMS_RE = re.compile(
    r"\b(sent\s+(?:an|a)?\s*sms|sms|form(?:ular)?\s*link|formular|link)\b",
    flags=re.IGNORECASE,
)
HUMAN_RE = re.compile(
    r"\b(human|operator|agent|escalat(?:ion|e|ed|are)?|transfer)\b",
    flags=re.IGNORECASE,
)


async def close_conversation(conversation_id: str, phone_number: Union[str, None]):
    async with SessionLocal() as s:
        conv = await s.get(Conversation, conversation_id)
        if not conv:
            return

        res = await s.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(1)
        )
        last_message = res.scalars().first()

        label = ConversationLabel.resolved  # default
        if last_message and last_message.text:
            logger.debug(f"Last message : {last_message.text}")
            t = _normalize(last_message.text)
            if re.search("sms", t) or SMS_RE.search(t):
                label = ConversationLabel.escalated_website
            elif re.search("agent", t) or HUMAN_RE.search(t):
                label = ConversationLabel.escalated_human

        if phone_number and not conv.phone_number:
            conv.phone_number = phone_number
        conv.ended_at = datetime.now(timezone.utc)
        conv.label = label

        await s.commit()


async def get_conversations_with_messages_by_phone(
    phone_number: str,
) -> list[Conversation]:
    """
    We return a list of conversations based on phone_number sorted by timestamp
    """
    async with SessionLocal() as s:
        stmt = (
            select(Conversation)
            .where(Conversation.phone_number == phone_number)
            .options(selectinload(Conversation.messages))
            .order_by(Conversation.started_at.desc())
        )
        res = await s.execute(stmt)
        conversations = res.scalars().all()

        # sortam mesajele crescator
        for conv in conversations:
            conv.messages.sort(
                key=lambda m: m.created_at or datetime.min.replace(tzinfo=timezone.utc)
            )

        return conversations  # type:ignore


def conversation_to_dict(conv: Conversation) -> Dict[str, Any]:
    return {
        "id": conv.id,
        "phone_number": conv.phone_number,
        "started_at": conv.started_at.isoformat() if conv.started_at else None,
        "ended_at": conv.ended_at.isoformat() if conv.ended_at else None,
        "label": (
            conv.label.value if getattr(conv.label, "value", None) else conv.label  # type:ignore
        ),
        "messages": [
            {
                "id": msg.id,
                "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                "text": msg.text,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "path_df": msg.path_df,
                "number_page": msg.number_page,
            }
            for msg in conv.messages
        ],
    }


async def create_form(
    conversation_id: str, questions: list[str], locale: Union[str, None]
) -> str:
    async with SessionLocal() as s:
        form = Form(conversation_id=conversation_id, questions=questions, locale=locale)
        s.add(form)
        await s.commit()
        return form.id


async def append_question(form_id: str, question: str) -> None:
    async with SessionLocal() as s:
        form = await s.get(Form, form_id)
        if not form:
            return
        form.questions.append(question)
        await s.commit()


async def list_forms(
    conversation_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[Form]:
    async with SessionLocal() as s:
        stmt = (
            select(Form)
            .options(selectinload(Form.conversation))
            .order_by(Form.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        if conversation_id:
            stmt = stmt.where(Form.conversation_id == conversation_id)

        res = await s.execute(stmt)
        return res.scalars().all()  # type:ignore


def form_to_dict(f: Form) -> Dict[str, Any]:
    conv = getattr(f, "conversation", None)
    return {
        "id": f.id,
        "conversation_id": f.conversation_id,
        "questions": f.questions or [],
        "locale": f.locale,
        "created_at": f.created_at.isoformat() if f.created_at else None,
        "conversation": {
            "phone_number": getattr(conv, "phone_number", None),
            "label": (
                getattr(getattr(conv, "label", None), "value", None)
                or (conv.label if conv else None)
            ),
            "started_at": conv.started_at.isoformat()
            if conv and conv.started_at
            else None,
            "ended_at": conv.ended_at.isoformat() if conv and conv.ended_at else None,
        }
        if conv
        else None,
    }
