from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient

from app.main import app, items


client = TestClient(app)


def setup_function() -> None:
    items.clear()


def test_crud_flow() -> None:
    headers = {"X-API-Key": "dev-api-key"}
    created = client.post("/api/v1/items", json={"name": "A", "description": "B"}, headers=headers)
    assert created.status_code == 201
    item_id = created.json()["id"]

    listed = client.get("/api/v1/items", headers=headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 1

    updated = client.patch(
        f"/api/v1/items/{item_id}",
        json={"name": "A2", "description": "B2"},
        headers=headers,
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "A2"

    deleted = client.delete(f"/api/v1/items/{item_id}", headers=headers)
    assert deleted.status_code == 204


def test_auth_required() -> None:
    response = client.get("/api/v1/items")
    assert response.status_code == 401