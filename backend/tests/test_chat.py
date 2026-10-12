from unittest.mock import patch


def test_chat_unsupported_question_abstention(client):
    # Ask an out-of-domain / unsupported question
    res = client.post(
        "/api/v1/chat/new",
        json={"content": "What is the quantum physics formula for black hole thermodynamics?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "do not contain sufficient evidence" in data["content"]
    assert data["role"] == "assistant"


def test_chat_grounded_answer(client, db_session):
    # Mock LLM provider completion to return predictable grounded response
    with patch("app.services.providers.ollama_provider.OllamaProvider.is_available", return_value=(True, None)):
        with patch("app.services.providers.ollama_provider.OllamaProvider.generate_completion", return_value="According to Shreyas Doshi on Lenny's Podcast, the LNO framework categorizes tasks into Leverage, Neutral, and Overhead."):
            res = client.post(
                "/api/v1/chat/new",
                json={"content": "Explain the LNO framework from Shreyas Doshi"}
            )
            assert res.status_code == 200
            data = res.json()
            assert "Shreyas Doshi" in data["content"]
            assert data["citations_json"] is not None
            assert len(data["citations_json"]) > 0
