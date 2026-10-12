from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM Provider Adapters."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Unique string ID for the provider (e.g. 'ollama', 'anthropic', 'openai')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def provider_type(self) -> str:
        """'local' or 'cloud'."""
        pass

    @abstractmethod
    def is_available(self) -> tuple[bool, Optional[str]]:
        """Check if provider is configured and reachable. Returns (available, error_message)."""
        pass

    @abstractmethod
    def list_models(self) -> List[str]:
        """Return list of available model names for this provider."""
        pass

    @abstractmethod
    def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> str:
        """Generate response text from LLM given message history."""
        pass
