# database.py
from typing import Optional, Union
from sqlalchemy.types import JSON
from sqlalchemy.ext.mutable import MutableList
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone
import uuid

DATABASE_URL = "sqlite+aiosqlite:///./app.db"

engine = create_async_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class MessageRole(PyEnum):
    user = "user"
    bot = "bot"


class ConversationLabel(PyEnum):
    resolved = "resolved"
    escalated_website = "escalated_website"
    escalated_human = "escalated_human"


class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String, primary_key=True)  # uuid4 str
    phone_number: Mapped[Union[str, None]] = mapped_column(String, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[Union[datetime, None]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    messages = relationship(
        "Message", back_populates="conversation", cascade="all, delete-orphan"
    )
    label: Mapped[Optional[ConversationLabel]] = mapped_column(
        SQLAEnum(
            ConversationLabel,
            name="conversation_label",
            native_enum=False,  # pe SQLite creează CHECK constraint
            validate_strings=True,  # validează la runtime valorile din string
        ),
        nullable=True,
        default=None,
    )

    forms = relationship(
        "Form", back_populates="conversation", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole))
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    path_df: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    number_page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    conversation = relationship("Conversation", back_populates="messages")


class Form(Base):
    __tablename__ = "forms"

    id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    conversation_id: Mapped[str] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE")
    )
    questions: Mapped[list[str]] = mapped_column(
        MutableList.as_mutable(JSON), default=list
    )
    locale: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    conversation = relationship("Conversation", back_populates="forms")


async def init_db_conversations():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
