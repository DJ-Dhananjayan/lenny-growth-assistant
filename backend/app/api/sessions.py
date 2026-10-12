from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import SessionModel, MessageModel
from app.schemas.chat import SessionCreate, SessionResponse, MessageResponse
from app.config import settings

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.get("", response_model=List[SessionResponse])
def list_sessions(db: Session = Depends(get_db)):
    """Retrieve all chat sessions ordered by latest update time."""
    sessions = db.query(SessionModel).order_by(SessionModel.updated_at.desc()).all()
    return sessions


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session."""
    session = SessionModel(
        title=payload.title or "New Growth Chat",
        provider=payload.provider or settings.DEFAULT_PROVIDER,
        model=payload.model or "default"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    """Retrieve details and messages for a specific session ID."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all associated messages."""
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    db.delete(session)
    db.commit()
    return None
