def test_session_lifecycle(client):
    # Create session
    create_res = client.post("/api/v1/sessions", json={"title": "Test Session", "provider": "ollama"})
    assert create_res.status_code == 201
    s_data = create_res.json()
    session_id = s_data["id"]
    assert s_data["title"] == "Test Session"

    # List sessions
    list_res = client.get("/api/v1/sessions")
    assert list_res.status_code == 200
    sessions = list_res.json()
    assert any(s["id"] == session_id for s in sessions)

    # Get session details
    get_res = client.get(f"/api/v1/sessions/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == session_id

    # Delete session
    del_res = client.delete(f"/api/v1/sessions/{session_id}")
    assert del_res.status_code == 204

    # Verify deleted
    get_after = client.get(f"/api/v1/sessions/{session_id}")
    assert get_after.status_code == 404
