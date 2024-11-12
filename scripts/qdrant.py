import os
from typing import List, Optional
import uuid
from dotenv import load_dotenv
from fastapi import Depends, FastAPI
from pydantic import BaseModel
import uvicorn
from langfuse import Langfuse

from aidevs3.qdrant.system_prompt import get_system_prompt
from aidevs3.services.ai_service import CompletionRequest, OpenAIService
from aidevs3.services.langfuse_service import CreateGenerationRequest, CreateTraceRequest, LangfuseService
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
    user_messages = list(filter(lambda m: m.role == "user", chat_request.messages))
    print(f"user messages: {user_messages}")
    
    # TODO: convert langfuse service to something more generic
    langfuse_service = LangfuseService()
    ai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"), langfuse_service=langfuse_service)
    vector_service = AsyncVectorService(ai_service)

    last_message = user_messages[-1]

    trace = langfuse_service.create_trace(CreateTraceRequest(id=str(uuid.uuid4()), name=f"chat-{last_message.content}"))

    await vector_service.create_collection(CONVERSATION_COLLECTION)
    similar_messages = await vector_service.search(CONVERSATION_COLLECTION, last_message.content)
    print(f"found {len(similar_messages)} similar messages")
    for msg in similar_messages:
        print(f"similar msg id: {msg.id}, score: {msg.score}, payload: {msg.payload}")

    # similar messages are added to the conversation as context
    context_messages = [{"role": msg.payload["role"], "content": msg.payload["text"]} for msg in similar_messages]

    completion_request = CompletionRequest(
        model="gpt-4o-mini",
        messages=[
            {"role": last_message.role, "content": last_message.content}, 
            {"role": "system", "content": get_system_prompt(context=context_messages)}
        ],
    )
    answer = ai_service.completion(completion_request)
    langfuse_service.create_generation(
        trace,
        CreateGenerationRequest(name="chat", input=completion_request, output=answer)
    )

    print("answer", answer)

    await vector_service.add_points(
        CONVERSATION_COLLECTION, [VectorPointDto(id=str(uuid.uuid4()), text=last_message.content, role=last_message.role)]
    )

    langfuse_service.finalize_trace(trace, input=last_message.content, output=answer)

    return {"answer": answer}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
