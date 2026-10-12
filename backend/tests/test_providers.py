import pytest
from app.services.providers.factory import get_provider, get_provider_config


def test_provider_factory():
    demo = get_provider("demo")
    assert demo.provider_id == "demo"
    assert demo.provider_type == "local"

    anthropic = get_provider("anthropic")
    assert anthropic.provider_id == "anthropic"
    assert anthropic.provider_type == "cloud"

    openai = get_provider("openai")
    assert openai.provider_id == "openai"

    config = get_provider_config()
    assert len(config.providers) == 4
    assert any(p.id == "ollama" for p in config.providers)
    assert any(p.id == "demo" for p in config.providers)


def test_invalid_provider_raises_error():
    with pytest.raises(ValueError):
        get_provider("non_existent_provider")
