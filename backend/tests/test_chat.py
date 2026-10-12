from unittest.mock import patch


def test_cookie_recipe_out_of_scope_rejection(client):
    """
    Test that asking for a cookie recipe returns a polite out-of-scope response
    without attaching any irrelevant podcast transcript sources.
    """
    res = client.post(
        "/api/v1/chat/new",
        json={"content": "Give me a chocolate chip cookie recipe."}
    )
    assert res.status_code == 200
    data = res.json()
    content = data["content"]

    assert "I'm designed to answer product, growth, and startup questions" in content
    assert "I can't provide a cookie recipe, but I can help with a product or growth question" in content
    # Irrelevant citations must NOT be present
    assert not data.get("citations_json")
    assert not data.get("citations")


def test_chat_unsupported_question_abstention(client):
    """
    Test that an out-of-domain science/physics question is politely rejected
    without citations.
    """
    res = client.post(
        "/api/v1/chat/new",
        json={"content": "What is the quantum physics formula for black hole thermodynamics?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "I'm designed to answer product, growth, and startup questions" in data["content"] or "do not contain sufficient evidence" in data["content"]
    assert not data.get("citations_json")
    assert not data.get("citations")


def test_in_scope_product_growth_grounded_answer(client, db_session):
    """
    Test that a relevant product/growth question returns a grounded answer
    with relevant citations.
    """
    with patch("app.services.providers.ollama_provider.OllamaProvider.is_available", return_value=(True, None)):
        with patch("app.services.providers.ollama_provider.OllamaProvider.generate_completion", return_value="According to Shreyas Doshi on Lenny's Podcast, the LNO framework categorizes tasks into Leverage, Neutral, and Overhead."):
            res = client.post(
                "/api/v1/chat/new",
                json={"content": "Explain the LNO framework from Shreyas Doshi"}
            )
            assert res.status_code == 200
            data = res.json()
            assert "Shreyas Doshi" in data["content"]
            assert data.get("citations_json") is not None
            assert len(data["citations_json"]) > 0
            # Citation must genuinely point to Shreyas Doshi
            assert any(c["guest"] == "Shreyas Doshi" for c in data["citations_json"])


def test_in_scope_question_with_insufficient_evidence_abstention(client, db_session):
    """
    Test that an in-scope product question for which transcripts have no evidence
    returns an honest abstention and suggestions, with no citations.
    """
    res = client.post(
        "/api/v1/chat/new",
        json={"content": "What does Lenny say about hardware supply chain factories in Shenzhen?"}
    )
    assert res.status_code == 200
    data = res.json()
    assert "do not contain sufficient evidence to answer this question reliably" in data["content"]
    assert "Try asking about one of these topics" in data["content"]
    assert not data.get("citations_json")
    assert not data.get("citations")


def test_follow_up_question_preserves_context_without_irrelevant_sources(client, db_session):
    """
    Test that follow-up questions preserve previous conversation context
    and only cite genuinely relevant sources without adding irrelevant ones.
    """
    # 1. Create a session
    s_res = client.post("/api/v1/sessions", json={"title": "Founder Mode Thread"})
    assert s_res.status_code == 201
    session_id = s_res.json()["id"]

    # 2. First turn: Ask about Brian Chesky
    with patch("app.services.providers.ollama_provider.OllamaProvider.is_available", return_value=(True, None)):
        with patch("app.services.providers.ollama_provider.OllamaProvider.generate_completion", return_value="Brian Chesky explained that founder-led mode requires being in the product details."):
            r1 = client.post(
                f"/api/v1/chat/{session_id}",
                json={"content": "Explain founder-led mode according to Brian Chesky"}
            )
            assert r1.status_code == 200
            assert any(c["guest"] == "Brian Chesky" for c in r1.json().get("citations_json", []))

    # 3. Follow-up turn: Ask how it contrasts with traditional management
    with patch("app.services.providers.ollama_provider.OllamaProvider.is_available", return_value=(True, None)):
        with patch("app.services.providers.ollama_provider.OllamaProvider.generate_completion", return_value="In contrast to traditional management which delegates everything, founder-led mode keeps the founder involved directly."):
            r2 = client.post(
                f"/api/v1/chat/{session_id}",
                json={"content": "How does this contrast with traditional professional management advice?"}
            )
            assert r2.status_code == 200
            citations = r2.json().get("citations_json", [])
            assert len(citations) > 0
            # Must cite Brian Chesky and NOT cite unrelated guests like Shreyas or Elena
            guests = {c["guest"] for c in citations}
            assert "Brian Chesky" in guests
            assert "Elena Verna" not in guests
