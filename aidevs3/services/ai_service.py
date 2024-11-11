"""Definitions of AI services used to communicate with various models."""


from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Dict, List, Optional

from openai import OpenAI
from pydantic import BaseModel


class CompletionMessage(BaseModel):
    """A message in a completion request - equivalent to ChatCompletionMessageParam in OpenAI API spec."""
    role: str = "user"
    content: str
    name: Optional[str] = None


class CompletionRequest(BaseModel):
    messages: List[CompletionMessage]
    model: str = "gpt-4o-mini"
    stream: bool = False
    temperature: float = 0.0
    json_mode: bool = False
    max_tokens: Optional[int] = None


class AIServiceBase(ABC):
    @abstractmethod
    def completion(self, request: CompletionRequest) -> str:
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
    def __init__(self, api_key: str, logger: Optional[Logger] = None):
        self._client = OpenAI(api_key=api_key)
        self._logger = logger
        
    def completion(self, request: CompletionRequest) -> str:
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
        raise NotImplementedError()
    
    def count_tokens(self, text: str) -> int:
        raise NotImplementedError()

    def parse_json_response(self, response: str) -> Dict[str, Any]:
        raise NotImplementedError()

    def is_stream_response(self) -> bool:
        raise NotImplementedError()


class LocalLlamaService(AIServiceBase):
    pass
