from typing import Optional, Literal
from pydantic import BaseModel


class ArtifactResponse(BaseModel):
    id: str
    session_id: str
    title: str
    artifact_type: Literal["markdown", "html"]
    content: str
