def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["database"] == "ok"
    assert "active_provider" in data
    assert isinstance(data["providers"], list)
