from flask import Blueprint, jsonify, request

from app.database import database_ready, delete_note, fetch_notes, insert_note

bp = Blueprint("routes", __name__)


@bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "image-optimization"})


@bp.get("/ready")
def ready():
    try:
        if database_ready():
            return jsonify({"status": "ready", "database": "connected"}), 200
        return jsonify({"status": "error", "database": "unavailable"}), 503
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return jsonify({"status": "error", "database": "unavailable", "message": str(exc)}), 503


@bp.get("/api/notes")
def get_notes():
    try:
        return jsonify(fetch_notes()), 200
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return jsonify({"error": "Could not fetch notes", "details": str(exc)}), 500


@bp.post("/api/notes")
def create_note():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "Request body must be a JSON object."}), 400

    title = payload.get("title")
    description = payload.get("description")

    if not isinstance(title, str) or not isinstance(description, str):
        return jsonify({"error": "Title and description must be strings."}), 400

    title = title.strip()
    description = description.strip()

    if not title or not description:
        return jsonify({"error": "Both title and description are required."}), 400

    if len(title) > 255:
        return jsonify({"error": "Title must be 255 characters or fewer."}), 400

    if len(description) > 2000:
        return jsonify({"error": "Description must be 2000 characters or fewer."}), 400

    try:
        note = insert_note(title, description)
        return jsonify({"message": "Note created successfully.", "note": note}), 201
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return jsonify({"error": "Could not create note.", "details": str(exc)}), 500


@bp.delete("/api/notes/<int:note_id>")
def delete_note_route(note_id: int):
    try:
        was_deleted = delete_note(note_id)
        if not was_deleted:
            return jsonify({"error": "Note not found."}), 404
        return jsonify({"message": "Note deleted successfully."}), 200
    except Exception as exc:  # pragma: no cover - defensive runtime guard
        return jsonify({"error": "Could not delete note.", "details": str(exc)}), 500
