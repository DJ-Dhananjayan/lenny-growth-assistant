from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict, computed_field


class Citation(BaseModel):
    episode_title: str
    guest: str
    episode_url: Optional[str] = None
    chunk_id: str
    snippet: str
    score: Optional[float] = None


class ArtifactPayload(BaseModel):
    title: str
    artifact_type: Literal["markdown", "html"]
    content: str


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, description="Message prompt from user")
    provider: Optional[str] = Field(None, description="Override LLM provider for this message")
    model: Optional[str] = Field(None, description="Override LLM model for this message")


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: str
    session_id: str
    role: Literal["user", "assistant", "system"]
    content: str
    citations_json: Optional[List[Citation]] = None
    artifact_json: Optional[ArtifactPayload] = None
    created_at: datetime

    @computed_field
    @property
    def citations(self) -> Optional[List[Citation]]:
        return self.citations_json

    @computed_field
    @property
    def artifact(self) -> Optional[ArtifactPayload]:
        return self.artifact_json


class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"
    provider: Optional[str] = "ollama"
    model: Optional[str] = "llama3.2"


class SessionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    messages: Optional[List[MessageResponse]] = None
