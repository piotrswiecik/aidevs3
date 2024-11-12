from dotenv import load_dotenv

load_dotenv()

from aidevs3.services.ai_service import LocalLlamaService, OllamaCompletionRequest


llama_service = LocalLlamaService()

res = llama_service.completion(OllamaCompletionRequest(messages=[{"role": "user", "content": "Hello, how are you?"}], model="gemma2:latest"))
print(res)