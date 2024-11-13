"""Definitions of AI services used to communicate with various models."""


from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Dict, List, Optional
from ollama import Client

from openai import OpenAI
from pydantic import BaseModel

from aidevs3.services.langfuse_service import LangfuseService


class CompletionMessage(BaseModel):
    """A message in a completion request - equivalent to ChatCompletionMessageParam in OpenAI API spec."""
    role: str = "user"
    content: str | Dict[str, Any]
    name: Optional[str] = None


class BaseCompletionRequest(BaseModel):
    messages: List[CompletionMessage]
    model: str


class OpenAICompletionRequest(BaseModel):
    messages: List[CompletionMessage]
    model: str = "gpt-4o-mini"
    stream: bool = False
    temperature: float = 0.0
    json_mode: bool = False
    max_tokens: Optional[int] = None


class OllamaCompletionRequest(BaseCompletionRequest):
    pass


class OllamaCompletionResponse(BaseModel):
    message: Dict[str, Any]
    created_at: str
    done_reason: Optional[str] = None
    done: bool
    total_duration: float
    load_duration: float
    prompt_eval_count: int
    prompt_eval_duration: float
    eval_count: int
    eval_duration: float
    model: str


class AIServiceBase(ABC):
    @abstractmethod
    def completion(self, request: OpenAICompletionRequest) -> str:
        pass

    @abstractmethod
    def embedding(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        pass

    @abstractmethod
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def is_stream_response(self) -> bool:
        pass


class AIServiceError(Exception):
    pass


class OpenAIService(AIServiceBase):
    def __init__(self, api_key: str, logger: Optional[Logger] = None, langfuse_service: Optional[LangfuseService] = None):
        self._client = OpenAI(api_key=api_key)
        self._logger = logger
        self._langfuse_service = langfuse_service
    
    def completion(self, request: OpenAICompletionRequest) -> str:
        """Send completion request to OpenAI service."""
        try:
            return self._client.chat.completions.create(
                model=request.model,
                messages=request.messages,
                temperature=request.temperature,
                stream=request.stream,
                response_format= "json_mode" if request.json_mode else None,
                max_tokens=request.max_tokens,
            ).choices[0].message.content
        except Exception as e:
            if self._logger:
                self._logger.error(f"Error in OpenAI completion: {e}")
            raise AIServiceError(e)
        
    def embedding(self, text: str) -> List[float]:
        res = self._client.embeddings.create(input=text, model="text-embedding-3-large")
        return res.data[0].embedding
    
    def count_tokens(self, text: str) -> int:
        raise NotImplementedError()

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        raise NotImplementedError()

    def is_stream_response(self) -> bool:
        raise NotImplementedError()


class LocalLlamaService(AIServiceBase):
    def __init__(self, model_url: str = "http://localhost:11434"):
        self._client = Client(host=model_url)

    def completion(self, request: OllamaCompletionRequest) -> str:
        """Send completion request to hosted Ollama service."""
        res = OllamaCompletionResponse(**self._client.chat(model=request.model, messages=[item.model_dump() for item in request.messages]))
        return res.message["content"]
    
    def embedding(self, text: str) -> List[float]:
        pass

    def count_tokens(self, text: str) -> int:
        pass

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        pass

    def is_stream_response(self) -> bool:
        pass
