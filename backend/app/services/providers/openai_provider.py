import logging
from typing import List, Dict, Optional
from app.config import settings
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.default_model = settings.OPENAI_DEFAULT_MODEL

    @property
    def provider_id(self) -> str:
        return "openai"

    @property
    def display_name(self) -> str:
        return "OpenAI (GPT)"

    @property
    def provider_type(self) -> str:
        return "cloud"

    def is_available(self) -> tuple[bool, Optional[str]]:
        if not self.api_key or self.api_key.startswith("your_"):
            return False, "OPENAI_API_KEY environment variable is not configured."
        return True, None

    def list_models(self) -> List[str]:
        return ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"]

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        available, err = self.is_available()
        if not available:
            raise RuntimeError(f"OpenAI provider error: {err}")

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise RuntimeError(f"OpenAI API execution failed: {str(e)}")
