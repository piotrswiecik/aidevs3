from aidevs3.memory.ai_service import AIService
from aidevs3.memory.prompts.extractqueries import create_extract_queries_prompt
from aidevs3.memory.prompts.knowledge import default_knowledge
from aidevs3.memory.prompts.structure import memory_structure
from openai.types.chat import ChatCompletionMessageParam



from langfuse.client import StatefulTraceClient


import json


class AssistantService:
    def __init__(self, ai_service: AIService, trace: StatefulTraceClient = None):
        self.ai_service = ai_service
        self.trace = trace

    async def extract_queries(
        self, messages: list[ChatCompletionMessageParam], trace: StatefulTraceClient
    ) -> list[str]:

        # create generation step in langfuse logging
        if self.trace is not None:
            generation = self.trace.generation(name="Extract Queries", input=messages)

        # memory_structure -> describes how agent memory is structured (categories, subcategories, etc.)
        # default_knowledge -> describes what the agent knows about the world (name, personality, etc.)

        # thread contains all user messages + system message generated by agent based on memory_structure and default_knowledge

        thread = [
            {
                "role": "system",
                "content": create_extract_queries_prompt(
                    memory_structure, default_knowledge
                ),
            },
            *messages,
        ]

        thinking = self.ai_service.completion(thread, json_mode=True)
        result = self.ai_service.parse_json_response(thinking)

        # store result in langfuse
        try:
            usage = {
                "prompt_tokens": thinking.usage.prompt_tokens,
                "completion_tokens": thinking.usage.completion_tokens,
                "total_tokens": thinking.usage.total_tokens,
            }
        except AttributeError:
            usage = None
        finally:
            if self.trace is not None:
                generation.update(output=json.dumps(result), model=thinking.model, usage=usage)

        return result["q"]