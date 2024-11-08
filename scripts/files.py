from dataclasses import dataclass, field
from fastapi import FastAPI
from uuid import uuid4
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam


class OpenAiService:
    pass


class ContextService:
    pass


class AssistantService:
    pass


@dataclass(frozen=True)
class ChatRequest:
    messages: list[ChatCompletionMessageParam]
    conversation_id: str = field(default_factory=lambda: str(uuid4()))
    

app = FastAPI()


@app.post("/chat")
def chat(request: ChatRequest):
    thread = []
    return {}
