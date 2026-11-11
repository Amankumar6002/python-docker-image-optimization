from __future__ import annotations

import psycopg

from app.config import get_settings


def get_db_connection():
    settings = get_settings()
    return psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    )


def database_ready() -> bool:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            return cur.fetchone() == (1,)


def fetch_notes() -> list[dict]:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, description, created_at FROM notes ORDER BY created_at DESC"
            )
            rows = cur.fetchall()
            columns = [column[0] for column in cur.description]

    notes = []
    for row in rows:
        note = dict(zip(columns, row))
        if note["created_at"] is not None:
            note["created_at"] = note["created_at"].isoformat()
        notes.append(note)
    return notes


def insert_note(title: str, description: str) -> dict:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO notes (title, description) VALUES (%s, %s) RETURNING id, title, description, created_at",
                (title, description),
            )
            row = cur.fetchone()
            conn.commit()

    note = {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "created_at": row[3].isoformat() if row[3] is not None else None,
    }
    return note


def delete_note(note_id: int) -> bool:
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM notes WHERE id = %s RETURNING id", (note_id,))
            deleted = cur.fetchone()
            conn.commit()

    return deleted is not None
