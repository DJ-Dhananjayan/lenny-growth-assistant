from typing import List, Optional, Literal
from pydantic import BaseModel


class ProviderOption(BaseModel):
    id: str  # 'ollama', 'anthropic', 'openai'
    name: str
    type: Literal["local", "cloud"]
    available: bool
    models: List[str]
    default_model: str
    description: str
    error_message: Optional[str] = None


class ProviderConfigResponse(BaseModel):
    active_provider: str
    providers: List[ProviderOption]


class SelectProviderRequest(BaseModel):
    provider_id: str
    model_id: Optional[str] = None
