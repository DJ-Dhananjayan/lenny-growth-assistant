from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.db.models import TranscriptChunkModel, TranscriptModel
from app.services.embedding import get_embedding, cosine_similarity


def search_chunks(db: Session, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
    """
    Search transcript chunks using vector cosine similarity.
    Evaluates similarity across chunk content, guest name, and episode title.
    Returns ranked chunk dicts with episode metadata.
    """
    query_vector = get_embedding(query)
    
    # Query all chunks from DB
    chunks = db.query(TranscriptChunkModel).all()
    if not chunks:
        return []

    results = []
    query_words = set(query.lower().split())

    for chunk in chunks:
        chunk_vector = chunk.embedding
        if not chunk_vector:
            continue
        
        sim = cosine_similarity(query_vector, chunk_vector)
        
        # Retrieve parent transcript for metadata
        transcript = db.query(TranscriptModel).filter(TranscriptModel.id == chunk.transcript_id).first()
        
        guest_name = transcript.guest if transcript else ""
        episode_title = transcript.episode_title if transcript else ""
        
        # Keyword match boost for guest name or specific terms
        boost = 0.0
        if guest_name and any(w in guest_name.lower() for w in query_words if len(w) > 2):
            boost += 0.35
        if episode_title and any(w in episode_title.lower() for w in query_words if len(w) > 2):
            boost += 0.20

        final_score = min(1.0, float(sim) + boost)

        results.append({
            "chunk_id": chunk.id,
            "episode_title": episode_title or "Lenny's Podcast",
            "guest": guest_name or "Guest",
            "episode_url": transcript.episode_url if transcript else None,
            "snippet": chunk.content,
            "score": round(final_score, 3),
            "metadata": chunk.metadata_json or {}
        })

    # Sort descending by similarity score
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]
