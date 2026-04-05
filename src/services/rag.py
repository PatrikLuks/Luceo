"""RAG retrieval service — semantic search over clinical knowledge base."""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.knowledge_base import KnowledgeDocument

logger = logging.getLogger("luceo.rag")


async def retrieve_context(
    query: str,
    db: AsyncSession,
    top_k: int = 3,
) -> list[KnowledgeDocument]:
    """Retrieve the most relevant knowledge documents for a query.

    For MVP without embedding infrastructure, falls back to keyword-based
    search. When embeddings are populated, uses pgvector cosine similarity.
    """
    # MVP fallback: simple keyword search using PostgreSQL ilike
    # TODO: Replace with proper embedding-based search when embedding service is ready
    # Escape LIKE-special chars to prevent pattern injection
    safe_query = query[:100].replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    result = await db.execute(
        select(KnowledgeDocument)
        .where(KnowledgeDocument.content.ilike(f"%{safe_query}%"))
        .limit(top_k)
    )
    docs = list(result.scalars().all())

    if not docs:
        # Fallback: get most recent documents from relevant categories
        result = await db.execute(
            select(KnowledgeDocument).order_by(KnowledgeDocument.created_at.desc()).limit(top_k)
        )
        docs = list(result.scalars().all())

    return docs


def format_context(documents: list[KnowledgeDocument]) -> str:
    """Format retrieved documents into context string for the LLM prompt."""
    if not documents:
        return ""

    parts = ["KONTEXT Z KLINICKÉ DATABÁZE:"]
    for doc in documents:
        parts.append(f"\n[{doc.source} — {doc.category}] {doc.title}:\n{doc.content}")

    return "\n".join(parts)
