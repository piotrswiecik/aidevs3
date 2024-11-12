"""Tracing service provided by Langfuse SDK."""


import os
from typing import Any, Optional
from langfuse import Langfuse
from pydantic import BaseModel
from langfuse.client import StatefulClient, StatefulSpanClient, StatefulTraceClient, StatefulGenerationClient


class CreateTraceRequest(BaseModel):
    id: str
    name: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class CreateSpanRequest(BaseModel):
    trace_id: str
    name: str
    input: Any = None
    parent_observation_id: Optional[str] = None


class CreateGenerationRequest(BaseModel):
    name: str
    input: Any = None
    prompt: Any = None


class TokenUsage(BaseModel):
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class LangfuseService:
    def __init__(self):
        public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
        secret_key = os.getenv("LANGFUSE_SECRET_KEY")
        host = os.getenv("LANGFUSE_HOST")
        self._langfuse = Langfuse(host=host, public_key=public_key, secret_key=secret_key)

    
    def create_trace(self, request: CreateTraceRequest):
        return self._langfuse.trace(id=request.id, name=request.name, session_id=request.session_id, user_id=request.user_id)

    def create_span(self, trace: StatefulTraceClient, request: CreateSpanRequest):
        return self._langfuse.span(
            trace_id=trace.id, name=request.name, parent_observation_id=request.parent_observation_id, input=request.input
        )
    
    def finalize_span(self, span: StatefulSpanClient, name: str, output: Any):
        span.update(name=name, output=output)
        span.end()

    def finalize_trace(self, trace: StatefulTraceClient, input: Any, output: Any):
        trace.update(input=input, output=output)
        self._langfuse.flush()

    def create_generation(self, trace: StatefulTraceClient, request: CreateGenerationRequest):
        return trace.generation(name=request.name, input=request.input, prompt=request.prompt)
    
    def finalize_generation(self, generation: StatefulGenerationClient, output: Any, model: str, usage: Optional[TokenUsage] = None):
        generation.update(output=output, model=model, usage=usage)
        generation.end()
