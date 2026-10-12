from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.services.providers.factory import get_provider_config
from app.config import settings

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("")
def health_check(db: Session = Depends(get_db)):
    """Health and readiness check for application, database, and LLM providers."""
    db_status = "ok"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    provider_config = get_provider_config()

    return {
        "status": "healthy" if db_status == "ok" else "degraded",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": db_status,
        "active_provider": provider_config.active_provider,
        "providers": [
            {
                "id": p.id,
                "name": p.name,
                "available": p.available,
                "error": p.error_message
            }
            for p in provider_config.providers
        ]
    }
