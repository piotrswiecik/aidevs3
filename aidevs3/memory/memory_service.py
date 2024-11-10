import json
from pydantic import BaseModel
from aidevs3.memory.ai_service import OpenAIServiceImpl
from aidevs3.memory.ai_service import AIService
from typing import TypeAlias, Tuple, List

from pathlib import Path

from langfuse.client import StatefulTraceClient


class Location(BaseModel):
    city: str | None = None
    address: str | None = None

class Content(BaseModel):
    text: str
    additional_fields: dict = {}

class Metadata(BaseModel):
    confidence: float | None = None
    location: Location | None = None
    source: str | None = None
    urls: list[str] | None = None
    tags: list[str] | None = None
    priority: str | None = None
    source_type: str | None = None
    additional_fields: dict = {}

class Memory(BaseModel):
    uuid: str
    category: str
    subcategory: str
    name: str
    content: Content
    metadata: Metadata
    created_at: str
    updated_at: str


Similarity: TypeAlias = int


class MemoryService:
    def __init__(self, ai_service: AIService = OpenAIServiceImpl(), base_dir: str | Path = "./.memories", trace: StatefulTraceClient = None):
        self.ai_service = ai_service
        self.trace = trace
        if isinstance(base_dir, str):
            base_dir = Path(base_dir)

        # create base directory for memories if it doesn't exist
        if not base_dir.exists():
            base_dir.mkdir(parents=True)
        self.base_dir = base_dir

        # create memory subdirectories
        categories = ["profiles", "preferences", "resources", "events", "locations", "environment"]
        subcategories = {
            "profiles": ["basic", "work", "development", "relationships"],
            "preferences": ["hobbies", "interests"],
            "resources": ["books", "movies", "music", "videos", "images", "apps", "devices",
                         "courses", "articles", "communities", "channels", "documents", "notepad"],
            "events": ["personal", "professional"],
            "locations": ["places", "favorites"],
            "environment": ["current"]
        }
        for category in categories:
            category_path = self.base_dir / category
            category_path.mkdir(exist_ok=True)

            for subcategory in subcategories[category]:
                subcategory_path = category_path / subcategory
                subcategory_path.mkdir(exist_ok=True)

    async def search_similar_memories(self, query: str, k: int = 15) -> List[Tuple[Memory, Similarity]]:
        """
        Args:
            query: query string to search for
            k: number of similar memories to return
        Returns:
            list of tuples (memory, similarity) of k most similar memories
        """
        # convert each query to embedding (list of floats)
        if self.trace is not None:
            generation = self.trace.generation(name="Create embeddings", input=query)
        query_embedding = self.ai_service.create_embedding(query)

        # update trace in langfuse
        if self.trace is not None:
            generation.update(output=query_embedding, model="text-embedding-3-small")
        try:
            usage = {
                "prompt_tokens": query_embedding.usage.prompt_tokens,
                "completion_tokens": query_embedding.usage.completion_tokens,
                "total_tokens": query_embedding.usage.total_tokens,
            }
        except AttributeError:
            usage = None
        finally:
            if self.trace is not None:
                generation.update(output=json.dumps(query_embedding), model="text-embedding-3-small", usage=usage)

        print(query_embedding)

    async def recall(self, queries: List[str]) -> str:
        """
        Args:
            queries: list of queries to search for
        Returns:
            ...
        """
        # search for similar memories for each provided query
        recalled_memories = [
            await self.search_similar_memories(query)
            for query in queries
        ]

        for memory in recalled_memories:
            print(memory)
