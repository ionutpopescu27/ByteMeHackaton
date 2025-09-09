# repo.py
import re
import unicodedata
from typing import Optional, Union, Dict, Any
import uuid
from datetime import datetime, timezone
from loguru import logger
from numpy import log
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from .database import (
    SessionLocal,
    Conversation,
    Message,
    MessageRole,
    ConversationLabel,
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


# async def close_conversation(conversation_id: str, phone_number: Union[str, None]):
#     async with SessionLocal() as s:
#         conv = await s.get(Conversation, conversation_id)
#
#         # vreau ultimul mesaj contine sms , daca a fost un raspuns simplu sau daca a fost human escalation
#         if conv:
#             if phone_number and not conv.phone_number:
#                 conv.phone_number = phone_number
#             conv.ended_at = datetime.now(timezone.utc)
#             await s.commit()


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
            conv.label.value if getattr(conv.label, "value", None) else conv.label
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


# async def set_conversation_label(
#     conversation_id: str, label: ConversationLabel
# ) -> None:
#     async with SessionLocal() as s:
#         conv = await s.get(Conversation, conversation_id)
#         messages = conv.messages  # tpye:ignore
#         # vreau doar ultimul mesaj dat de bot , daca e ceva cu sms
#         last_message = messages[-1]
#
#         if not conv:
#             return
#         conv.label = label
#         await s.commit()
