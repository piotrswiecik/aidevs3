from typing import Any, Dict, List

import httpx
from pydantic import BaseModel


class PoligonRequest(BaseModel):
    task: str
    apikey: str
    answer: str | List[Any] | Dict


def send(url: str, task: str, apikey: str, answer: str | List[Any]):
    """Send task solution for verification.

    Args:
        url (str): Verification URL
        task (str): Task ID (typically UPPERCASE)
        apikey (str): Poligon API key
        answer (str | List[Any]): Task solution
    """
    payload = PoligonRequest(task=task, apikey=apikey, answer=answer)
    res = httpx.post(url, json=payload.model_dump())
    if res.status_code != 200:
        raise Exception(f"Failed to send data: {res.text}")
    return res.json()
