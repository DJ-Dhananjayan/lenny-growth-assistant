from app.db.models import SessionModel, MessageModel


def test_artifact_retrieval(client, db_session):
    # Setup session & message with artifact
    session = SessionModel(title="Artifact Session", provider="ollama", model="llama3.2")
    db_session.add(session)
    db_session.commit()

    msg = MessageModel(
        session_id=session.id,
        role="assistant",
        content="Here is your artifact.",
        artifact_json={
            "title": "Growth Checklist",
            "artifact_type": "markdown",
            "content": "# Checklist\n- Step 1\n- Step 2"
        }
    )
    db_session.add(msg)
    db_session.commit()

    res = client.get(f"/api/v1/artifacts/{msg.id}")
    assert res.status_code == 200
    art = res.json()
    assert art["title"] == "Growth Checklist"
    assert art["artifact_type"] == "markdown"
    assert "Step 1" in art["content"]
