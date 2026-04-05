from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.embedding import KnowledgeChunk


class RAGRetriever:
    def __init__(self, top_k: int = 3):
        self.top_k = top_k

    async def retrieve(
        self, query_embedding: list[float], db: AsyncSession
    ) -> list[KnowledgeChunk]:
        """Semantic search over knowledge base using pgvector cosine distance."""
        stmt = (
            select(KnowledgeChunk)
            .order_by(KnowledgeChunk.embedding.cosine_distance(query_embedding))
            .limit(self.top_k)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
