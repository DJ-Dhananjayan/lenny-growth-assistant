import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Float
from sqlalchemy.orm import relationship
from app.db.session import Base


def generate_uuid():
    return str(uuid.uuid4())


def utc_now():
    return datetime.now(timezone.utc)


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    title = Column(String(255), nullable=False, default="New Chat")
    provider = Column(String(50), nullable=False, default="ollama")
    model = Column(String(100), nullable=False, default="llama3.2")
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    messages = relationship("MessageModel", back_populates="session", cascade="all, delete-orphan", order_by="MessageModel.created_at")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    citations_json = Column(JSON, nullable=True)
    artifact_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    session = relationship("SessionModel", back_populates="messages")


class TranscriptModel(Base):
    __tablename__ = "transcripts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    episode_title = Column(String(255), nullable=False)
    guest = Column(String(255), nullable=False)
    episode_url = Column(String(512), nullable=True)
    episode_num = Column(Integer, nullable=True)
    publish_date = Column(String(50), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

    chunks = relationship("TranscriptChunkModel", back_populates="transcript", cascade="all, delete-orphan")


class TranscriptChunkModel(Base):
    __tablename__ = "transcript_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    transcript_id = Column(String(36), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    embedding = Column(JSON, nullable=True)  # Store vector as float list JSON array for universal compatibility
    created_at = Column(DateTime, default=utc_now)

    transcript = relationship("TranscriptModel", back_populates="chunks")
