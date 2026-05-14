import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app


def test_index():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Hello DevOps" in response.data