"""Service for interacting with vector databases."""


import os
from typing import List, Optional, TypeVar

from pydantic import BaseModel
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import VectorParams
from qdrant_client.http.models.models import Distance

from aidevs3.services.ai_service import AIServiceBase
from aidevs3.services.langfuse_service import LangfuseService


EmbeddingProvider = TypeVar("EmbeddingProvider", bound=AIServiceBase)


class VectorPointDto(BaseModel):
    id: str
    text: str
    role: str


class AsyncVectorService:
    def __init__(self, embedding_provider: EmbeddingProvider, url: Optional[str] = None, api_key: Optional[str] = None):
        if url is None:
            self.url = os.getenv("QDRANT_REMOTE_URL")
        else:
            self.url = url
        if api_key is None:
            self.api_key = os.getenv("QDRANT_API_KEY")
        else:
            self.api_key = api_key

        self._client = AsyncQdrantClient(url=self.url, api_key=self.api_key)
        self._embedding_provider = embedding_provider

    async def create_collection(self, collection_name: str) -> None:
        """Create a collection in the vector database (idempotent)."""
        c = await self._client.collection_exists(collection_name)
        if not c:
            await self._client.create_collection(collection_name, vectors_config=VectorParams(size=3072, distance=Distance.COSINE))

    async def add_points(self, collection_name: str, payload: List[VectorPointDto]) -> None:
        # before sending - encode payload to vector embeddings, convert payload to format required by qdrant client
        vector_db_payload = [
            {"id": point.id, "vector": self._embedding_provider.embedding(point.text), "payload": {"role": point.role, "text": point.text}} for point in payload
        ]
        await self._client.upsert(collection_name, points=vector_db_payload, wait=True)

    async def search(self, collection_name: str, query: str, limit: int = 5):
        embedding = self._embedding_provider.embedding(query)
        return await self._client.search(collection_name, query_vector=embedding, limit=limit, with_payload=True, with_vectors=False)