import pytest


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "", "description": "present"},
        {"title": "present", "description": ""},
        {"title": None, "description": "present"},
        {"title": "present", "description": 12},
    ],
)
def test_invalid_note_payloads_are_rejected(client, payload):
    response = client.post("/api/notes", json=payload)
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_deleting_nonexistent_note_returns_not_found(client):
    response = client.delete("/api/notes/2147483647")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Note not found."
