import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import BaseModel

try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    # Allow import without pgvector installed (tests with SQLite)
    Vector = None


class KnowledgeDocument(BaseModel):
    __tablename__ = "knowledge_documents"

    title: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)
    source: Mapped[str] = mapped_column(String(100))  # "who_guidelines", "cbt_protocol", etc.
    category: Mapped[str] = mapped_column(
        String(50), index=True
    )  # "cbt", "screening", "crisis", "motivational_interviewing"

    # pgvector embedding — nullable for records not yet embedded
    # Using 1024 dimensions (can be adjusted based on embedding model)
    # Note: Vector column defined via raw SQL if pgvector not available
    embedding = mapped_column(Vector(1024), nullable=True) if Vector else None

    verified_by: Mapped[str | None] = mapped_column(String(200))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
