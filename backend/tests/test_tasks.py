from tokenize import String

from fastapi.testclient import TestClient
from app.models import TaskStatus, TaskPriority


def test_create_task_valid_returns_201_with_full_body(client: TestClient):
    payload = {
        "title": "A task",
        "description": "details",
        "status": TaskStatus.TODO.value,
        "priority": TaskPriority.HIGH.value,
        "assignee": "alice",
    }
    r = client.post("/tasks", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "A task"
    assert data["description"] == "details"
    assert data["status"] == TaskStatus.TODO.value
    assert data["priority"] == TaskPriority.HIGH.value
    assert data["assignee"] == "alice"
    assert "id" in data
    assert "created_at" in data and "updated_at" in data


def test_create_task_missing_title_returns_422(client: TestClient):
    payload = {"description": "no title"}
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


def test_create_task_blank_title_returns_422(client: TestClient):
    payload = {"title": "   "}
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


def test_create_task_invalid_priority_returns_422(client: TestClient):
    payload = {"title": "t", "priority": "NotARealPriority"}
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


def test_create_task_unknown_field_returns_422(client: TestClient):
    payload = {"title": "t", "unknown": 123}
    r = client.post("/tasks", json=payload)
    assert r.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client: TestClient):
    r = client.get("/tasks")
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client: TestClient):
    # create one task with default status TODO
    client.post("/tasks", json={"title": "t1"})
    # filter by Done which should not match
    r = client.get("/tasks", params={"status": TaskStatus.DONE.value})
    assert r.status_code == 200
    assert r.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client: TestClient):
    client.post("/tasks", json={"title": "low", "priority": TaskPriority.LOW.value})
    client.post("/tasks", json={"title": "high", "priority": TaskPriority.HIGH.value})
    r = client.get("/tasks", params={"priority": TaskPriority.HIGH.value})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["priority"] == TaskPriority.HIGH.value


def test_get_task_by_id_returns_task(client: TestClient, created_task):
    tid = created_task["id"]
    r = client.get(f"/tasks/{tid}")
    assert r.status_code == 200
    data = r.json()
    assert data["id"] == tid


def test_get_task_by_id_not_found_returns_404_with_detail(client: TestClient):
    r = client.get("/tasks/not-a-real-id")
    assert r.status_code == 404
    data = r.json()
    assert "detail" in data


def test_patch_partial_update_keeps_other_fields(client: TestClient, created_task):
    tid = created_task["id"]
    original = client.get(f"/tasks/{tid}").json()
    r = client.patch(f"/tasks/{tid}", json={"description": "updated"})
    assert r.status_code == 200
    data = r.json()
    assert data["description"] == "updated"
    # other fields remain
    assert data["title"] == original["title"]
    assert data["status"] == original["status"]


def test_patch_not_found_returns_404(client: TestClient):
    r = client.patch("/tasks/no-id", json={"title": "x"})
    assert r.status_code == 404


def test_patch_valid_transition_todo_to_inprogress_returns_200(client: TestClient):
    # create task with default TODO
    r = client.post("/tasks", json={"title": "t"})
    tid = r.json()["id"]
    r2 = client.patch(f"/tasks/{tid}", json={"status": TaskStatus.IN_PROGRESS.value})
    assert r2.status_code == 200
    assert r2.json()["status"] == TaskStatus.IN_PROGRESS.value


def test_patch_valid_transition_inprogress_to_done_returns_200(client: TestClient):
    create_response = client.post("/tasks", json={"title": "t"})
    task_id = create_response.json()["id"]

    first_patch = client.patch(f"/tasks/{task_id}", json={"status": TaskStatus.IN_PROGRESS.value})
    assert first_patch.status_code == 200

    second_patch = client.patch(f"/tasks/{task_id}", json={"status": TaskStatus.DONE.value})
    assert second_patch.status_code == 200
    assert second_patch.json()["status"] == TaskStatus.DONE.value


def test_patch_unknown_field_returns_422(client: TestClient):
    create_response = client.post("/tasks", json={"title": "t"})
    task_id = create_response.json()["id"]

    response = client.patch(f"/tasks/{task_id}", json={"owner": "alice"})
    assert response.status_code == 422
    assert "extra inputs are not permitted" in response.text.lower()

def test_patch_empty_json_object_returns_existing_task_unchanged(client: TestClient):
    create_response = client.post("/tasks", json={"title": "t"})
    assert create_response.status_code == 201
    created_task = create_response.json()

    response = client.patch(f"/tasks/{created_task['id']}", json={})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_task["id"]
    assert data["title"] == created_task["title"]
    assert data["description"] == created_task["description"]
    assert data["status"] == created_task["status"]


def test_patch_invalid_transition_todo_to_done_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "t"})
    tid = r.json()["id"]
    r2 = client.patch(f"/tasks/{tid}", json={"status": TaskStatus.DONE.value})
    assert r2.status_code == 422


def test_patch_same_status_returns_422(client: TestClient):
    r = client.post("/tasks", json={"title": "t"})
    tid = r.json()["id"]
    # attempting to set same status
    r2 = client.patch(f"/tasks/{tid}", json={"status": TaskStatus.TODO.value})
    assert r2.status_code == 422


def test_delete_existing_returns_204_no_body(client: TestClient):
    r = client.post("/tasks", json={"title": "todel"})
    tid = r.json()["id"]
    r2 = client.delete(f"/tasks/{tid}")
    assert r2.status_code == 204
    assert r2.content == b""


def test_delete_missing_returns_404(client: TestClient):
    r = client.delete("/tasks/missing")
    assert r.status_code == 404
