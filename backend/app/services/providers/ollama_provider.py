import logging
import httpx
from typing import List, Dict, Optional
from app.config import settings
from app.services.providers.base import BaseLLMProvider

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = settings.DEFAULT_OLLAMA_MODEL

    @property
    def provider_id(self) -> str:
        return "ollama"

    @property
    def display_name(self) -> str:
        return "Ollama (Local)"

    @property
    def provider_type(self) -> str:
        return "local"

    def get_installed_models(self) -> List[str]:
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name") for m in data.get("models", []) if m.get("name")]
        except Exception:
            pass
        return []

    def is_available(self) -> tuple[bool, Optional[str]]:
        try:
            with httpx.Client(timeout=3.0) as client:
                res = client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    installed = self.get_installed_models()
                    if installed:
                        return True, None
                    return False, f"Ollama is running, but no models are downloaded. Run 'ollama pull {self.default_model}'."
                return False, f"Ollama HTTP {res.status_code}"
        except Exception as e:
            return False, f"Ollama instance unavailable at {self.base_url}. Run 'ollama serve' locally."

    def list_models(self) -> List[str]:
        installed = self.get_installed_models()
        if installed:
            return installed
        return [self.default_model, "qwen2.5:0.5b", "mistral"]

    def _resolve_model(self, requested_model: Optional[str] = None) -> str:
        installed = self.get_installed_models()
        if not installed:
            return requested_model or self.default_model

        if requested_model:
            if requested_model in installed:
                return requested_model
            for m in installed:
                if m.startswith(requested_model) or requested_model.startswith(m.split(":")[0]):
                    return m

        for m in installed:
            if m.startswith(self.default_model) or self.default_model.startswith(m.split(":")[0]):
                return m

        return installed[0]

    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        available, err = self.is_available()
        if not available:
            raise RuntimeError(
                f"Local Ollama provider error ({err}). "
                f"Please ensure Ollama is installed and running (`ollama serve`), or switch to another provider."
            )

        model_name = self._resolve_model(model)

        payload = {
            "model": model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        try:
            with httpx.Client(timeout=180.0) as client:
                response = client.post(f"{self.base_url}/api/chat", json=payload)
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama returned HTTP {response.status_code}: {response.text}")
                data = response.json()
                content = data.get("message", {}).get("content", "")
                if not content:
                    raise RuntimeError("Ollama returned empty response content.")
                return content
        except httpx.TimeoutException:
            raise RuntimeError(f"Ollama inference timed out after 180s for model '{model_name}'.")
        except Exception as e:
            raise RuntimeError(f"Ollama inference failed: {str(e)}")
