"""Service for interacting with vector databases."""


import os
from typing import Optional

from qdrant_client import QdrantClient


class VectorService:
    def __init__(self, url: Optional[str] = None, api_key: Optional[str] = None):
        if url is None:
            self.url = os.getenv("QDRANT_REMOTE_URL")
        else:
            self.url = url
        if api_key is None:
            self.api_key = os.getenv("QDRANT_API_KEY")
        else:
            self.api_key = api_key

        self._client = QdrantClient(url=self.url, api_key=self.api_key)
