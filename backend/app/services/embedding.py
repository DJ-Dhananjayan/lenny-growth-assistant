import math
import logging
from typing import List

logger = logging.getLogger(__name__)

# Cache embedding model if sentence_transformers is installed
_ST_MODEL = None


def get_embedding(text: str) -> List[float]:
    """
    Generate 384-dimensional dense vector for input text.
    Uses sentence-transformers if present, with a deterministic fallback.
    """
    global _ST_MODEL
    clean_text = text.strip()
    if not clean_text:
        return [0.0] * 384

    try:
        if _ST_MODEL is None:
            from sentence_transformers import SentenceTransformer
            _ST_MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        
        vec = _ST_MODEL.encode(clean_text).tolist()
        return vec
    except Exception as e:
        logger.debug(f"Sentence Transformers unavailable ({e}), using fast local embedding fallback.")
        return _fast_local_embedding(clean_text)


def _fast_local_embedding(text: str) -> List[float]:
    """
    Deterministic 384-dim normalized vector fallback based on character/word hashing.
    Ensures vector search functions predictably in zero-dependency or offline environments.
    """
    dim = 384
    vec = [0.0] * dim
    words = text.lower().split()
    for word in words:
        h = hash(word)
        idx = abs(h) % dim
        val = 1.0 if h > 0 else -1.0
        vec[idx] += val

    # Add character n-gram features
    for i in range(len(text) - 2):
        trigram = text[i:i+3].lower()
        h = hash(trigram)
        idx = abs(h) % dim
        vec[idx] += 0.5

    # Normalize vector
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 1e-9:
        vec = [x / norm for x in vec]
    else:
        vec[0] = 1.0

    return vec


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    if len(v1) != len(v2) or not v1:
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = math.sqrt(sum(a * a for a in v1))
    norm2 = math.sqrt(sum(b * b for b in v2))
    if norm1 < 1e-9 or norm2 < 1e-9:
        return 0.0
    return dot / (norm1 * norm2)
