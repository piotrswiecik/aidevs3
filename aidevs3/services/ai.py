"""Definitions of AI services used to communicate with various models."""


from abc import ABC, abstractmethod
from logging import Logger
from typing import Any, Dict, List, Optional

from openai import OpenAI


class AIServiceBase(ABC):
    @abstractmethod
    def completion(self, prompt: str) -> str:
        pass

    @abstractmethod
    def embedding(self, text: str) -> List[float]:
        pass


class AIServiceError(Exception):
    pass


class OpenAIService(AIServiceBase):
    def __init__(self, api_key: str, logger: Optional[Logger] = None):
        self._client = OpenAI(api_key=api_key)
        self._logger = logger
        
    def completion(self, user_prompt: str, sys_prompt: Optional[str] = None, model: str = "gpt-4o-mini") -> str:
        """Simple API - user prompt and system prompt provided as strings."""
        messages = [{"role": "user", "content": user_prompt}]
        if sys_prompt:
            messages.append({"role": "system", "content": sys_prompt})
        try:
            return self._client.chat.completions.create(
                model=model,
                messages=messages,
            ).choices[0].message.content
        except Exception as e:
            if self._logger:
                self._logger.error(f"Error in OpenAI completion: {e}")
            raise AIServiceError(e)
        
    def custom_completion(self, messages: List[Dict[str, Any]], model: str = "gpt-4o-mini", temperature: float = 0.0) -> str:
        """Advanced API - prompt is a ModelSpec formatted JSON dict."""
        try:
            return self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            ).choices[0].message.content
        except Exception as e:
            if self._logger:
                self._logger.error(f"Error in OpenAI completion: {e}")
            raise AIServiceError(e)
        
    def embedding(self, text: str) -> List[float]:
        raise NotImplementedError()


class LocalLlamaService(AIServiceBase):
    pass
