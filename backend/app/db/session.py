import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

logger = logging.getLogger(__name__)

database_url = settings.DATABASE_URL
connect_args = {}

# Try creating engine with configured URL
try:
    if database_url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
        engine = create_engine(database_url, connect_args=connect_args)
    else:
        # Test postgresql connection quickly
        temp_engine = create_engine(database_url, connect_args={"connect_timeout": 2})
        with temp_engine.connect() as conn:
            pass
        engine = temp_engine
except Exception as e:
    logger.warning(f"PostgreSQL connection to {database_url} failed ({e}). Falling back to local SQLite database.")
    database_url = "sqlite:///./lenny_growth_db.sqlite"
    connect_args = {"check_same_thread": False}
    engine = create_engine(database_url, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
