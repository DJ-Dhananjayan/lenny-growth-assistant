from typing import Optional
from pydantic import BaseModel


class IngestionStatusResponse(BaseModel):
    transcripts_count: int
    chunks_count: int
    last_ingested_at: Optional[str] = None


class IngestionRunResponse(BaseModel):
    success: bool
    message: str
    episodes_ingested: int
    chunks_created: int
