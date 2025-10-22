import sys
import os
import pytest
from app import app

# Ensure the parent directory is in sys.path for module import
sys.path.insert(
    0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
        )
    )


@pytest.fixture
def client(monkeypatch):
    """Create a Flask test client and mock DB connection."""

    class DummyCursor:
        def execute(self, *args, **kwargs):
            pass

        def fetchall(self):
            return [
                {"id": 1, "name": "Test User", "task": "Sample Task"}
            ]

        def close(self):
            pass

    class DummyConnection:
        def cursor(self, dictionary=False):
            return DummyCursor()

        def commit(self):
            pass

        def close(self):
            pass

    def dummy_get_db_connection():
        return DummyConnection()

    monkeypatch.setattr("app.get_db_connection", dummy_get_db_connection)

    with app.test_client() as client:
        yield client


def test_index_route(client):
    """Test if index route returns 200 and expected content."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Test User" in response.data
    assert b"Sample Task" in response.data


def test_add_todo_redirect(client):
    """Test POST /add triggers redirect (no DB errors)."""
    response = client.post(
        '/add',
        data={"name": "John", "task": "Do homework"},
    )
    assert response.status_code in (301, 302)
