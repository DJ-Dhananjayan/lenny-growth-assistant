from unittest.mock import MagicMock
from app.agent.ship30_skill import generate_ship30_essay


def test_ship30_essay_generation():
    mock_provider = MagicMock()
    mock_provider.generate_completion.return_value = (
        "# Hook Statement\nMost product teams waste 80% of their effort on low leverage tasks.\n\n"
        "## Problem\nConventional wisdom tells PMs to make everything 10/10 perfect.\n\n"
        "## Pillar 1: LNO Framework\n"
        "Spend 80% of creative energy on Leverage tasks as Shreyas Doshi explained in Lenny's Podcast.\n\n"
        "## Actionable Checklist\n1. Categorize your backlog.\n2. Delegate overhead tasks."
    )

    evidence = [
        {
            "chunk_id": "c1",
            "guest": "Shreyas Doshi",
            "episode_title": "LNO Framework",
            "snippet": "LNO stands for Leverage, Neutral, Overhead."
        }
    ]

    essay, artifact = generate_ship30_essay(mock_provider, "Product Prioritization using LNO", evidence)

    assert "Hook Statement" in essay
    assert "Shreyas Doshi" in essay
    assert artifact["artifact_type"] == "markdown"
    assert "LNO" in artifact["title"]
