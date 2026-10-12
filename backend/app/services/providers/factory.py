from typing import Dict, List, Optional
from app.services.providers.base import BaseLLMProvider
from app.services.providers.demo_provider import DemoProvider
from app.services.providers.ollama_provider import OllamaProvider
from app.services.providers.anthropic_provider import AnthropicProvider
from app.services.providers.openai_provider import OpenAIProvider
from app.schemas.provider import ProviderOption, ProviderConfigResponse
from app.config import settings

_PROVIDERS: Dict[str, BaseLLMProvider] = {
    "ollama": OllamaProvider(),
    "demo": DemoProvider(),
    "anthropic": AnthropicProvider(),
    "openai": OpenAIProvider(),
}


def get_provider(provider_id: Optional[str] = None) -> BaseLLMProvider:
    target_id = (provider_id or settings.DEFAULT_PROVIDER).lower()
    
    # If target is ollama but ollama is unavailable, fallback gracefully to demo provider
    if target_id == "ollama":
        ollama_prov = _PROVIDERS["ollama"]
        avail, _ = ollama_prov.is_available()
        if not avail:
            logger_msg = "Ollama offline. Routing request to Demo (Local Synthesis) Provider."
            return _PROVIDERS["demo"]
        return ollama_prov

    if target_id not in _PROVIDERS:
        raise ValueError(f"Unknown LLM provider '{target_id}'. Supported: {list(_PROVIDERS.keys())}")
    return _PROVIDERS[target_id]


def get_provider_config(active_id: Optional[str] = None) -> ProviderConfigResponse:
    current_active = active_id or settings.DEFAULT_PROVIDER
    provider_options = []

    for pid, provider in _PROVIDERS.items():
        avail, err = provider.is_available()
        models = provider.list_models()
        default_model = getattr(provider, "default_model", models[0] if models else "default")

        provider_options.append(
            ProviderOption(
                id=pid,
                name=provider.display_name,
                type=provider.provider_type,
                available=avail,
                models=models,
                default_model=default_model,
                description=f"{provider.display_name} ({provider.provider_type.upper()})",
                error_message=err
            )
        )

    return ProviderConfigResponse(
        active_provider=current_active,
        providers=provider_options
    )
