"""LangFuse test"""

import os
from fastapi import FastAPI
from dotenv import load_dotenv
from openai import AsyncOpenAI
from langfuse.decorators import observe
from langfuse.openai import openai
from langfuse import Langfuse


load_dotenv()

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = FastAPI()


langfuse = Langfuse(
  secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
  public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
  host=os.environ.get("LANGFUSE_HOST")
)

@observe()
async def call_llm(question: str):
    response_a = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "how are you?"}
        ]
    )
    response_b =  await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": question}
        ]
    )
    return response_a.choices[0].message.content, response_b.choices[0].message.content

@app.post("/chat")
async def chat(question: str):
    return await call_llm(question)