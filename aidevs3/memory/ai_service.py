from abc import ABC, abstractmethod
from typing import Optional
from openai import OpenAI
from openai.resources.chat.completions import ChatCompletionChunk, Stream
from openai.types.chat import ChatCompletion
from openai.types.chat import ChatCompletionMessageParam
from langfuse.client import StatefulTraceClient

import json
import logging
import os


class AIService(ABC):
    """Represents AI completion service interface. Can be implemented for different LLM providers."""

    @abstractmethod
    def completion(
        self,
        messages: list[ChatCompletionMessageParam],
        model: Optional[str] = None,
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: Optional[int] = None,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """
        Returns a string or a generator of strings based on the stream flag.
        If json_mode is true, the response is parsed as a JSON object.

        Args:
            messages: List of messages to be sent to the LLM.
            model: Optional model name e.g. "gpt-4o-mini".
            stream: If true, the response is streamed.
            json_mode: If true, the response is parsed as a JSON object.
            max_tokens: Optional maximum number of tokens in the response.
        Returns:
            String or a generator of strings.
        """
        pass

    @abstractmethod
    def parse_json_response(self, response: ChatCompletion):
        """
        Parses the model stringified response into a JSON object.
        """
        pass

    @abstractmethod
    def create_embedding(self, text: str) -> list[float]:
        """
        Creates an embedding for a given text.
        """
        pass


class OpenAIServiceImpl(AIService):
    """Implementation of AI service for OpenAI."""

    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.logger = logging.getLogger("openai_service")

    def completion(
        self,
        messages: list[ChatCompletionMessageParam],
        model: Optional[str] = None,
        stream: bool = False,
        json_mode: bool = False,
        max_tokens: Optional[int] = None,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        response = self.client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=messages,
            stream=stream,
            response_format={"type": "json_object"} if json_mode else None,
            max_tokens=max_tokens,
        )

        return response

    def parse_json_response(self, response: ChatCompletion):
        try:
            content = response.choices[0].message.content # this comes as string from openai json mode format
            return json.loads(content)
        except (AttributeError, KeyError, IndexError) as e:
            self.logger.error(e)
            raise Exception(f"Invalid JSON response structure")
        
    def create_embedding(self, text: str) -> list[float]:
        response = self.client.embeddings.create(input=text, model="text-embedding-3-small")
        return response.data[0].embedding
