from fastapi import APIRouter
from app.schemas.provider import ProviderConfigResponse, SelectProviderRequest
from app.services.providers.factory import get_provider_config, get_provider
from app.config import settings

router = APIRouter(prefix="/providers", tags=["Providers"])


@router.get("", response_model=ProviderConfigResponse)
def list_providers():
    """Retrieve list of available LLM providers and their operational status."""
    return get_provider_config()


@router.post("/select")
def select_provider(payload: SelectProviderRequest):
    """Update global active LLM provider selection."""
    provider = get_provider(payload.provider_id)
    available, err = provider.is_available()
    settings.DEFAULT_PROVIDER = payload.provider_id
    return {
        "success": True,
        "active_provider": payload.provider_id,
        "available": available,
        "error": err
    }
