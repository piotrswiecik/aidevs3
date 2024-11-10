import os
from dataclasses import dataclass, field
from typing import Annotated, Generator, Optional, TypeVar
from uuid import uuid4
from pydantic import BaseModel, Field
from typing import Optional


from aidevs3.memory.ai_service import OpenAIServiceImpl
from aidevs3.memory.assistant_service import AssistantService
from aidevs3.memory.memory_service import MemoryService
from dotenv import load_dotenv
from fastapi import FastAPI
from langfuse import Langfuse
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()


app = FastAPI()

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_API_KEY"),
    secret_key=os.getenv("LANGFUSE_PRIVATE_API_KEY"),
    host=os.getenv("LANGFUSE_HOST"),
)


class ChatMessage(BaseModel):
    role: str = "user"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    conversation_id: Optional[str] = Field(default_factory=lambda: str(uuid4()))


@app.post("/chat")
async def chat(
    request: ChatRequest,
):
    ai_service = OpenAIServiceImpl()
    assistant_service = AssistantService(ai_service, trace=langfuse)
    memory_service = MemoryService(ai_service, trace=langfuse)

    # get only user messages
    messages = list(filter(lambda i: i.role == "user", request.messages))

    # start logging
    trace_name = str(messages[0].content) if len(messages) > 0 else ""
    trace = langfuse.trace(
        session_id=request.conversation_id,
        name=trace_name[:45],
    )

    # use LLM agent to prepare queries that can be useful to recall information from memory
    # example of such queries: "profiles:basic Who is Alice?", "profiles:basic Who is Adam?"
    # generally they contain a category:subcategory and a query string
    queries = await assistant_service.extract_queries(request.messages, trace)

    # search for k most similar memories related to each query
    memories = await memory_service.recall(queries)

    return memories
