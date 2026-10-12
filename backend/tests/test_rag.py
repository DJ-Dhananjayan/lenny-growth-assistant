from app.services.vector_store import search_chunks


def test_transcript_search_relevance(db_session):
    # Search for LNO framework
    results = search_chunks(db_session, query="What is the LNO framework by Shreyas Doshi?", top_k=3)
    assert len(results) > 0
    top_result = results[0]
    assert "Shreyas" in top_result["guest"] or "LNO" in top_result["snippet"] or "Leverage" in top_result["snippet"]


def test_transcript_search_brian_chesky(db_session):
    results = search_chunks(db_session, query="What is founder-led mode according to Brian Chesky?", top_k=3)
    assert len(results) > 0
    assert any("Brian Chesky" in r["guest"] or "Founder" in r["snippet"] for r in results)
