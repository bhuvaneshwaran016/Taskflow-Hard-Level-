from fastapi.testclient import TestClient
from taskflow.api import app, store

client = TestClient(app)

def setup_function():
    store.tasks.clear()
    store.audit.clear()
    store.next_id = 1

def test_claim_returns_conflict_when_task_already_claimed():
    task = client.post("/tasks", json={"title": "Ship release"}).json()
    first = client.post(f"/tasks/{task['task_id']}/claim", json={"worker": "alice"})
    second = client.post(f"/tasks/{task['task_id']}/claim", json={"worker": "bob"})

    assert first.status_code == 200
    assert second.status_code == 409
    assert client.get(f"/tasks/{task['task_id']}").json()["owner"] == "alice"

def test_missing_task_returns_404():
    response = client.post("/tasks/999/claim", json={"worker": "alice"})
    assert response.status_code == 404
