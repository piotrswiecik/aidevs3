from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from slowapi import Limiter
from slowapi.util import get_remote_address


app = FastAPI()
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


async def extract_token(request: Request):
    return request.headers.get("Authorization")


async def verify_token(token: Optional[str]):
    if not token:
        return False
    if not token.startswith("Bearer "):
        return False
    try:
        token = token.split(" ")[1]
        return token == "super_secret_token"
    except IndexError:
        return False


async def basic_token_auth(request: Request):
    token = await extract_token(request)
    res = await verify_token(token)
    if not res:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/chat", dependencies=[Depends(basic_token_auth)])
@limiter.limit("2/minute")
def read_root(request: Request, chat_request: ChatRequest):
    return {"message": "Hello, World!"}
