from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import MessageModel
from app.schemas.artifact import ArtifactResponse

router = APIRouter(prefix="/artifacts", tags=["Artifacts"])


@router.get("/{message_id}", response_model=ArtifactResponse)
def get_artifact(message_id: str, db: Session = Depends(get_db)):
    """Retrieve artifact payload generated for a specific message."""
    message = db.query(MessageModel).filter(MessageModel.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found.")
    
    if not message.artifact_json:
        raise HTTPException(status_code=404, detail="No artifact associated with this message.")

    art = message.artifact_json
    return ArtifactResponse(
        id=message.id,
        session_id=message.session_id,
        title=art.get("title", "Generated Artifact"),
        artifact_type=art.get("artifact_type", "markdown"),
        content=art.get("content", "")
    )
