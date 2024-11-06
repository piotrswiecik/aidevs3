import logging
import os
import tiktoken
from openai import AsyncOpenAI
from fastapi import FastAPI


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = FastAPI()

model = "gpt-3.5-turbo"
enc = tiktoken.encoding_for_model(model)

@app.post("/chat")
async def chat(question: str):
    encoding = enc.encode(question)
    logging.info(f"Input # of tokens: {len(encoding)}") # net - without special tokens
    messages = [
        {"role": "user", "content": question}
    ]
    response = await client.chat.completions.create(
        model=model,
        messages=messages
    )
    logging.info(response)
    return {
        "response": response.choices[0].message.content,
        "n_input_toks": len(encoding),
        "n_output_toks": len(enc.encode(response.choices[0].message.content))
        }
