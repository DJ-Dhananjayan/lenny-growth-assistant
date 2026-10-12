import os
import json
import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.db.session import SessionLocal, engine, Base
from app.db.models import TranscriptModel, TranscriptChunkModel
from app.services.embedding import get_embedding

logger = logging.getLogger(__name__)

SAMPLE_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "sample_transcripts")


def chunk_text(text: str, chunk_size: int = 350, overlap: int = 50) -> List[str]:
    """Splits text into chunks of approximately chunk_size words with overlap."""
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += (chunk_size - overlap)
    return chunks


def ingest_transcript_file(db: Session, file_path: str) -> Dict[str, Any]:
    """Ingests a single transcript JSON file into PostgreSQL database."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    episode_title = data.get("episode_title", "Lenny's Podcast Episode")
    guest = data.get("guest", "Guest")
    episode_url = data.get("episode_url")
    episode_num = data.get("episode_num")
    publish_date = data.get("publish_date")
    transcript_text = data.get("transcript", "")

    # Check if transcript already ingested (by title & guest)
    existing = db.query(TranscriptModel).filter(
        TranscriptModel.episode_title == episode_title,
        TranscriptModel.guest == guest
    ).first()

    if existing:
        db.delete(existing)
        db.commit()

    # Create new transcript
    transcript = TranscriptModel(
        episode_title=episode_title,
        guest=guest,
        episode_url=episode_url,
        episode_num=episode_num,
        publish_date=publish_date,
        content=transcript_text
    )
    db.add(transcript)
    db.commit()
    db.refresh(transcript)

    # Chunk transcript
    text_chunks = chunk_text(transcript_text)
    chunk_models = []
    for idx, chunk_content in enumerate(text_chunks):
        emb = get_embedding(chunk_content)
        chunk_model = TranscriptChunkModel(
            transcript_id=transcript.id,
            chunk_index=idx,
            content=chunk_content,
            metadata_json={
                "episode_title": episode_title,
                "guest": guest,
                "episode_url": episode_url,
                "chunk_index": idx
            },
            embedding=emb
        )
        chunk_models.append(chunk_model)

    db.add_all(chunk_models)
    db.commit()

    return {
        "transcript_id": transcript.id,
        "episode_title": episode_title,
        "chunks_count": len(chunk_models)
    }


def run_full_ingestion(db: Session, data_dir: str = SAMPLE_DATA_DIR) -> Dict[str, Any]:
    """Ingests all JSON sample transcript files from data_dir."""
    Base.metadata.create_all(bind=engine)
    
    if not os.path.exists(data_dir):
        logger.warning(f"Ingestion directory {data_dir} does not exist.")
        return {"episodes_ingested": 0, "chunks_created": 0}

    files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith(".json")]
    total_episodes = 0
    total_chunks = 0

    for file_path in files:
        res = ingest_transcript_file(db, file_path)
        total_episodes += 1
        total_chunks += res["chunks_count"]

    return {
        "success": True,
        "episodes_ingested": total_episodes,
        "chunks_created": total_chunks,
        "message": f"Successfully ingested {total_episodes} transcripts ({total_chunks} total chunks)."
    }


if __name__ == "__main__":
    db = SessionLocal()
    try:
        print("Starting Lenny Growth Assistant transcript ingestion...")
        result = run_full_ingestion(db)
        print(f"Ingestion completed: {result}")
    finally:
        db.close()
