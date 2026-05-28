import os
from abc import ABC, abstractmethod

import anthropic
import ollama
from dotenv import load_dotenv

load_dotenv()


class ModelProvider(ABC):
    @abstractmethod
    def complete(self, system: str, user_message: str) -> str:
        pass

class OllamaProvider(ModelProvider):
    def __init__(self, model: str = "gemma3"):
        self.model = model

    def complete(self, system: str, user_message: str) -> str:
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user_message}
            ],
            format="json"
        )
        return response.message.content
    
def AnthropicProvider(ModelProvider):
    def __init__(self, model: str = "claude-sonnet-4-5"):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def complete(self, system: str, user_message: str) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": user_message}]
        )
        return response.content[0].text
    
def get_provider(model_flag: str) -> ModelProvider:
    if model_flag == "local":
        return OllamaProvider()
    if model_flag == "anthropic":
        return AnthropicProvider()
    raise ValueError(f"Unknown model: '{model_flag}'. Use 'local' or 'anthropic'.")