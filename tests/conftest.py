import uuid
from pathlib import Path

import psycopg
import pytest

from app import create_app
from app.config import get_settings


@pytest.fixture(scope="session", autouse=True)
def initialize_test_schema():
    settings = get_settings()
    schema = Path(__file__).parents[1] / "db" / "init.sql"
    with psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    ) as connection:
        connection.execute(schema.read_text(encoding="utf-8"))
        connection.commit()


@pytest.fixture()
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def unique_title():
    return f"pytest-{uuid.uuid4()}"


@pytest.fixture()
def cleanup_notes():
    titles = []
    yield titles

    settings = get_settings()
    with psycopg.connect(
        host=settings.db_host,
        port=settings.db_port,
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE title = ANY(%s)", (titles,))
        connection.commit()
