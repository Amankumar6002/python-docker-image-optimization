from unittest.mock import patch

import pytest

from app import create_app


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_ready_checks_database(client):
    with patch("app.routes.database_ready", return_value=True):
        response = client.get("/ready")
        assert response.status_code == 200
        assert response.get_json()["status"] == "ready"

    with patch("app.routes.database_ready", return_value=False):
        response = client.get("/ready")
        assert response.status_code == 503
        assert response.get_json()["status"] == "error"


def test_create_and_get_note(client):
    payload = {"title": "First note", "description": "This is a test note."}
    created_note = {"id": 1, "title": payload["title"], "description": payload["description"], "created_at": "2024-01-01T00:00:00+00:00"}

    with patch("app.routes.insert_note", return_value=created_note), patch("app.routes.fetch_notes", return_value=[created_note]):
        create_response = client.post("/api/notes", json=payload)
        assert create_response.status_code == 201
        assert create_response.get_json()["note"]["title"] == payload["title"]

        list_response = client.get("/api/notes")
        assert list_response.status_code == 200
        notes = list_response.get_json()
        assert any(note["id"] == created_note["id"] for note in notes)


def test_delete_note(client):
    with patch("app.routes.delete_note", return_value=True):
        delete_response = client.delete("/api/notes/1")
        assert delete_response.status_code == 200

    with patch("app.routes.delete_note", return_value=False):
        missing_response = client.delete("/api/notes/99")
        assert missing_response.status_code == 404


def test_invalid_note_payload(client):
    response = client.post("/api/notes", json={"title": "", "description": ""})
    assert response.status_code == 400
    assert "required" in response.get_json()["error"].lower()
