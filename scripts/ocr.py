import logging
import os
import base64
import cv2 as cv
import numpy as np
from pydantic import BaseModel
import tiktoken

from dotenv import load_dotenv
from langfuse import Langfuse
from langfuse.decorators import observe
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile
from mistralai import Mistral, SystemMessage, UserMessage


logging.basicConfig(level=logging.INFO)
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI()

langfuse = Langfuse(
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY"),
    host=os.environ.get("LANGFUSE_HOST"),
)


class MistralService:
    def __init__(self, *args, **kwargs):
        _api_key = os.environ.get("MISTRAL_API_KEY")
        if not _api_key:
            raise ValueError("MISTRAL_API_KEY environment variable is not set")
        
        self._client = Mistral(api_key=_api_key)
        self._model = "pixtral-12b-2409"

    @observe(as_type="generation")
    def mistral_request(self, prompt, image_payload):
        system_prompt = """
        You are an OCR assistant - your task is to recognize handwritten text in an image and return it without any additional information.
        """
        system_message = SystemMessage(content=system_prompt)
        user_message = UserMessage(content=[
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": f"data:image/jpeg;base64,{image_payload}"}
        ])
        response = self._client.chat.complete(
            model=self._model,
            messages=[system_message, user_message]
        )
        return response
    

async def encode_image(image_bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


@app.post("/ocr")
async def ocr(file: UploadFile, prompt: str):
    f_bytes = file.file.read()
    f_numpy = np.frombuffer(f_bytes, dtype=np.uint8)
    image = cv.imdecode(f_numpy, cv.IMREAD_COLOR)
    image.resize((256, 256))

    success, encoded_image = cv.imencode(".png", image)
    if success:
        image_bytes = encoded_image.tobytes()
    else:
        return {"status": "error encoding image"}
    
    image_payload = await encode_image(image_bytes)
    logging.info(f"Payload length: {len(image_payload)}")

    # TODO: count tokens

    service = MistralService()
    response = service.mistral_request(prompt, image_payload)

    return {"raw_response": response}