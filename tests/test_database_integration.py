def test_health_and_database_readiness(client):
    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert health_response.get_json()["status"] == "ok"

    ready_response = client.get("/ready")
    assert ready_response.status_code == 200
    assert ready_response.get_json() == {
        "status": "ready",
        "database": "connected",
    }
