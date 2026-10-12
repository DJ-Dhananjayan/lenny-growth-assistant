from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import SessionModel, MessageModel
from app.schemas.chat import MessageCreate, MessageResponse
from app.services.providers.factory import get_provider
from app.agent.engine import execute_agent_rag
from app.config import settings

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/{session_id}", response_model=MessageResponse)
def send_message(session_id: str, payload: MessageCreate, db: Session = Depends(get_db)):
    """
    Send a message to the agent within a session context.
    Executes RAG retrieval over podcast transcripts and returns grounded answer.
    """
    # Find session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        # Create session automatically if new
        session = SessionModel(
            id=session_id if session_id != "new" else None,
            title=payload.content[:35] + "...",
            provider=payload.provider or settings.DEFAULT_PROVIDER,
            model=payload.model or "default"
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    # Save user message
    user_msg = MessageModel(
        session_id=session.id,
        role="user",
        content=payload.content
    )
    db.add(user_msg)
    db.commit()

    # Load session history for agent context
    past_messages = (
        db.query(MessageModel)
        .filter(MessageModel.session_id == session.id)
        .order_by(MessageModel.created_at.asc())
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in past_messages[:-1]]

    # Select provider
    provider_id = payload.provider or session.provider or settings.DEFAULT_PROVIDER
    try:
        provider = get_provider(provider_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider initialization error: {str(e)}"
        )

    # Execute agent RAG workflow
    try:
        answer_text, citations, artifact = execute_agent_rag(
            db=db,
            provider=provider,
            prompt=payload.content,
            history_messages=history,
            model=payload.model or session.model
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent execution failure: {str(e)}"
        )

    # Save assistant response
    assistant_msg = MessageModel(
        session_id=session.id,
        role="assistant",
        content=answer_text,
        citations_json=citations if citations else None,
        artifact_json=artifact if artifact else None
    )
    db.add(assistant_msg)

    # Auto-update session title if generic
    if session.title in ["New Chat", "New Growth Chat"]:
        session.title = payload.content[:40] + ("..." if len(payload.content) > 40 else "")
    
    db.commit()
    db.refresh(assistant_msg)

    return assistant_msg
