import os
from typing import List, Optional
import uuid
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from pydantic import BaseModel
import uvicorn

from aidevs3.services.ai_service import CompletionRequest, OpenAIService
from aidevs3.services.vector_service import AsyncVectorService, VectorPointDto

load_dotenv()


class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    conversation_id: Optional[str] = None


app = FastAPI()

CONVERSATION_COLLECTION = "conversations"

@app.post("/chat")
async def chat(chat_request: ChatRequest):
    user_messages = filter(lambda m: m.role == "user", chat_request.messages)

    ai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))
    vector_service = AsyncVectorService(ai_service)

    # TODO: add trace here

    await vector_service.create_collection(CONVERSATION_COLLECTION)

    last_message = list(user_messages)[-1]
    similar_messages = await vector_service.search(CONVERSATION_COLLECTION, last_message.content)
    print(f"found {len(similar_messages)} similar messages")
    for msg in similar_messages:
        print(msg)

    answer = ai_service.completion(CompletionRequest(
        model="gpt-4o-mini",
        messages=[{"role": last_message.role, "content": last_message.content}],
    ))

    print("answer", answer)

    await vector_service.add_points(
        CONVERSATION_COLLECTION, [VectorPointDto(id=str(uuid.uuid4()), text=last_message.content, role=last_message.role)]
    )

    return {"message": "Hello, World!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
