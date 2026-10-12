from typing import List, Dict, Any, Tuple
from app.services.providers.base import BaseLLMProvider


SHIP30_SYSTEM_PROMPT = """You are an elite growth strategist and master copywriter specializing in the 'Ship 30 for 30' writing methodology.
Your mission is to produce an approximately 1,250-word, high-density, publication-ready growth essay based on product strategy advice from Lenny's Podcast transcripts.

Structure Requirements for Ship 30 for 30 Essays:
1. **Strong Opening Hook**: A short 1-2 sentence atomic statement that challenges conventional product/growth wisdom and grabs immediate attention.
2. **The Core Problem**: Explain why traditional frameworks fail product leaders in high-growth environments.
3. **3-4 Actionable Framework Pillars**:
   - Subheading with a clear numerical or framework title (e.g. 'Pillar 1: The LNO Prioritization Matrix').
   - High-density narrative explanations.
   - Bullet points highlighting tactical steps.
   - Selective bold emphasis on critical rules.
4. **Grounded Podcast Evidence & Verbatim Quotes**:
   - Integrate exact quotes and strategic advice from the provided podcast transcript passages.
   - Cite the guest name and episode title directly in the text (e.g., *As Brian Chesky shared in Lenny's Podcast...*).
5. **Actionable Takeaway Checklist**: A 5-point immediate execution checklist for product managers to implement tomorrow morning.

DO NOT invent quotes, guests, or podcast episodes not included in the provided evidence.
Ensure the output is authoritative, dense, actionable, and publication-ready.
"""


def generate_ship30_essay(
    provider: BaseLLMProvider,
    topic: str,
    evidence_chunks: List[Dict[str, Any]],
    model: str = None
) -> Tuple[str, Dict[str, Any]]:
    """
    Executes the Ship 30 for 30 writing skill tool.
    Returns (essay_text, artifact_dict).
    """
    evidence_text = ""
    for idx, c in enumerate(evidence_chunks, 1):
        evidence_text += f"\n--- Evidence Passage {idx} ---\n"
        evidence_text += f"Guest: {c['guest']}\n"
        evidence_text += f"Episode Title: {c['episode_title']}\n"
        evidence_text += f"Snippet: {c['snippet']}\n"

    user_prompt = f"""Write a comprehensive Ship 30 for 30 style growth essay on the following topic:

TOPIC: {topic}

TRANSCRIPT EVIDENCE PASSAGES:
{evidence_text if evidence_text else 'Base content on core principles from Lenny Podcast guests (Brian Chesky, Shreyas Doshi, Elena Verna, Elad Gil).'}

Remember to follow all Ship 30 for 30 structural guidelines: Hook, Problem, 3-4 Pillars with bullets/bold, Grounded Podcast Quotes with citations, and Actionable Checklist.
"""

    messages = [
        {"role": "system", "content": SHIP30_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

    essay_content = provider.generate_completion(messages=messages, model=model, temperature=0.7, max_tokens=1500)

    # Prepare artifact
    artifact_data = {
        "title": f"Ship 30 Essay: {topic[:50]}",
        "artifact_type": "markdown",
        "content": essay_content
    }

    return essay_content, artifact_data
