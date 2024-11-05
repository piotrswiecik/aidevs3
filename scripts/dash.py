import time
import httpx
import os
import json
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class LlamaResponse(BaseModel):
    model: str
    created_at: str
    response: str
    done: bool


def get_llm_status():
    """Get the status of the LLM."""
    try:
        port = os.getenv('LOCAL_LLM_PORT')
        res = httpx.get(f"http://localhost:{port}")
        if res.status_code == 200:
            return res.text
        else:
            return "Error"
    except Exception as e:
        return "Error"


def send_to_model(prompt):
    """Send the prompt to the model."""
    port = os.getenv('LOCAL_LLM_PORT')
    query = {
        "model": "gemma2:2b",
        "prompt": prompt,
        "max_tokens": 50,
        "temperature": 0.5,
    }
    response_window = st.empty()
    response = ""
    try:
        res = httpx.post(f"http://localhost:{port}/api/generate", json=query)
        for line in res.iter_lines():
            data = json.loads(line)
            partial = LlamaResponse(**data)
            if not partial.done:
                response += partial.response
                response_window.write(response)
                time.sleep(0.03)
    except Exception as e:
        print(e)
        st.write("Error sending to model.")
        return

st.write(f"Local LLM port: {os.getenv('LOCAL_LLM_PORT')}")
st.write(f"Status: {get_llm_status()}")
prompt = st.chat_input("Ask AI")
if prompt:
    send_to_model(prompt)