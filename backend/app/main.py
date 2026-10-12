import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.session import engine, Base, SessionLocal
from app.services.ingestion import run_full_ingestion
from app.api.health import router as health_router
from app.api.sessions import router as sessions_router
from app.api.chat import router as chat_router
from app.api.providers import router as providers_router
from app.api.artifacts import router as artifacts_router
from app.api.ingestion import router as ingestion_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("lenny_growth_assistant")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle handler."""
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)

    # Automatically run initial ingestion if database is empty
    db = SessionLocal()
    try:
        from app.db.models import TranscriptModel
        if db.query(TranscriptModel).count() == 0:
            logger.info("Database empty on boot. Ingesting default Lenny Growth Podcast sample dataset...")
            res = run_full_ingestion(db)
            logger.info(f"Boot ingestion result: {res}")
    except Exception as e:
        logger.warning(f"Could not complete startup transcript ingestion: {e}")
    finally:
        db.close()

    yield
    logger.info("Shutting down Lenny Growth Assistant API.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Grounded AI Assistant for Product Managers & Founders based on Lenny's Podcast transcripts.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled endpoint exception at {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal application error: {str(exc)}"}
    )


# Include Routers
app.include_router(health_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(providers_router, prefix="/api/v1")
app.include_router(artifacts_router, prefix="/api/v1")
app.include_router(ingestion_router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "health_url": "/api/v1/health"
    }
