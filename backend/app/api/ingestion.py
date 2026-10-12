from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import TranscriptModel, TranscriptChunkModel
from app.schemas.ingestion import IngestionStatusResponse, IngestionRunResponse
from app.services.ingestion import run_full_ingestion

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.get("/status", response_model=IngestionStatusResponse)
def get_ingestion_status(db: Session = Depends(get_db)):
    """Check current count of ingested podcast transcripts and total vector chunks."""
    t_count = db.query(TranscriptModel).count()
    c_count = db.query(TranscriptChunkModel).count()
    latest_chunk = db.query(TranscriptChunkModel).order_by(TranscriptChunkModel.created_at.desc()).first()
    
    return IngestionStatusResponse(
        transcripts_count=t_count,
        chunks_count=c_count,
        last_ingested_at=latest_chunk.created_at.isoformat() if latest_chunk else None
    )


@router.post("/trigger", response_model=IngestionRunResponse)
def trigger_ingestion(db: Session = Depends(get_db)):
    """Trigger the transcript ingestion pipeline."""
    res = run_full_ingestion(db)
    return IngestionRunResponse(
        success=res.get("success", False),
        message=res.get("message", "Ingestion finished."),
        episodes_ingested=res.get("episodes_ingested", 0),
        chunks_created=res.get("chunks_created", 0)
    )
