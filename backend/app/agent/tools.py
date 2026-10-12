import re
from typing import List, Dict, Any


def is_essay_request(prompt: str) -> bool:
    """Detects if user is asking for a Ship 30 for 30 essay or longform strategic guide."""
    lowered = prompt.lower()
    keywords = [
        "ship 30", "essay", "article", "newsletter", "framework breakdown",
        "long-form", "write up", "write-up", "detailed guide", "blog post"
    ]
    return any(k in lowered for k in keywords)


def is_html_artifact_request(prompt: str) -> bool:
    """Detects if user is asking for an HTML page, UI widget, or interactive component artifact."""
    lowered = prompt.lower()
    keywords = [
        "html", "website", "landing page", "ui component", "dashboard html",
        "css card", "interactive widget", "mockup html"
    ]
    return any(k in lowered for k in keywords)


def format_citations(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Formats chunk list into clean Citation dict schema for frontend API response."""
    citations = []
    seen = set()
    for c in chunks:
        cid = c["chunk_id"]
        if cid in seen:
            continue
        seen.add(cid)
        citations.append({
            "episode_title": c["episode_title"],
            "guest": c["guest"],
            "episode_url": c.get("episode_url"),
            "chunk_id": cid,
            "snippet": c["snippet"][:250] + ("..." if len(c["snippet"]) > 250 else ""),
            "score": round(c.get("score", 0.0), 3)
        })
    return citations
