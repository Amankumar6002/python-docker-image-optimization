def test_note_create_list_delete_flow(client, unique_title, cleanup_notes):
    description = "PostgreSQL integration test record"
    cleanup_notes.append(unique_title)

    create_response = client.post(
        "/api/notes",
        json={"title": unique_title, "description": description},
    )
    assert create_response.status_code == 201
    created_note = create_response.get_json()["note"]
    assert created_note["title"] == unique_title
    assert created_note["description"] == description
    assert isinstance(created_note["id"], int)

    list_response = client.get("/api/notes")
    assert list_response.status_code == 200
    assert any(note["id"] == created_note["id"] for note in list_response.get_json())

    delete_response = client.delete(f"/api/notes/{created_note['id']}")
    assert delete_response.status_code == 200

    list_after_delete = client.get("/api/notes")
    assert all(
        note["id"] != created_note["id"] for note in list_after_delete.get_json()
    )
