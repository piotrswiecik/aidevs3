from typing import Any, Dict, List
from faiss import IndexFlatIP
import math

from fastapi import Path
from pydantic import BaseModel


class VectorSearchResult(BaseModel):
    id: str
    similarity: float


class VectorStore:
    def __init__(self, storage_path: str | Path, dimension: int = 3072):
        self.index = IndexFlatIP(dimension)
        self.storage_path = storage_path
        self.index_path = storage_path / "index.faiss"
        self.metadata: Dict[str, Any] = {}
        self.metadata_path = storage_path / "metadata.json"

    async def add(self, vector: List[float], id: str):
        normalized_vector = self._normalize_vector(vector)
        index = self.index.ntotal
        self.index.add(normalized_vector)
        self.metadata[index] = id
        await self._save()

    async def search(self, vector: List[float], k: int) -> List[VectorSearchResult]:
        normalized_vector = self._normalize_vector(vector)
        total_vectors = self.index.ntotal
        if total_vectors == 0:
            return []
        actual_k = min(k, total_vectors)
        distances, indices = self.index.search(normalized_vector, actual_k)
        # TODO: proc

    async def _normalize_vector(self, vector: List[float]) -> List[float]:
        magnitude = math.sqrt(sum(val * val for val in vector))
        return [val / magnitude for val in vector]
    
    async def _save(self):
        raise NotImplementedError()
