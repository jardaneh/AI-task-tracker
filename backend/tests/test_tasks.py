from tokenize import String

from fastapi.testclient import TestClient
from app.models import TaskStatus, TaskPriority, ActivityType


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


def test_list_tasks_filter_by_text_returns_200_and_only_matches(client: TestClient):
    # create tasks where only one contains the text 'crash' in description
    client.post("/tasks", json={"title": "Fix bug", "description": "crash on load"})
    client.post("/tasks", json={"title": "Unrelated", "description": "nothing to see"})
    r = client.get("/tasks", params={"text": "crash"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert "crash" in data[0]["description"].lower()


def test_list_tasks_filter_by_assignee_returns_200_and_only_matches(client: TestClient):
    client.post("/tasks", json={"title": "t1", "assignee": "Alice"})
    client.post("/tasks", json={"title": "t2", "assignee": "Bob"})
    r = client.get("/tasks", params={"assignee": "alice"})
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["assignee"] is not None
    assert data[0]["assignee"].lower() == "alice"


def test_list_tasks_filter_by_unknown_priority_returns_422(client: TestClient):
    # passing an invalid enum value for priority should result in a 422 from FastAPI
    r = client.get("/tasks", params={"priority": "NotARealPriority"})
    assert r.status_code == 422


def test_list_tasks_filter_by_assignee_and_text_and_priority_returns_200_and_only_matches(client: TestClient):
    # matching task
    client.post(
        "/tasks",
        json={
            "title": "Fix login",
            "description": "critical bug",
            "assignee": "alice",
            "priority": TaskPriority.HIGH.value,
        },
    )
    # non-matching by priority
    client.post(
        "/tasks",
        json={
            "title": "Fix login",
            "description": "critical bug",
            "assignee": "alice",
            "priority": TaskPriority.LOW.value,
        },
    )
    # non-matching by assignee
    client.post(
        "/tasks",
        json={
            "title": "Fix login",
            "description": "critical bug",
            "assignee": "bob",
            "priority": TaskPriority.HIGH.value,
        },
    )
    r = client.get(
        "/tasks",
        params={"assignee": "alice", "text": "login", "priority": TaskPriority.HIGH.value},
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item["assignee"].lower() == "alice"
    assert item["priority"] == TaskPriority.HIGH.value
    assert "login" in item["title"].lower() or "login" in item["description"].lower()


def test_list_tasks_filter_by_assignee_and_status_and_priority_returns_200_and_only_matches(client: TestClient):
    # matching task with explicit status and priority
    client.post(
        "/tasks",
        json={
            "title": "Implement feature",
            "description": "work in progress",
            "assignee": "carol",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": TaskPriority.MEDIUM.value,
        },
    )
    # non-matching: different status
    client.post(
        "/tasks",
        json={
            "title": "Implement feature",
            "description": "done",
            "assignee": "carol",
            "status": TaskStatus.DONE.value,
            "priority": TaskPriority.MEDIUM.value,
        },
    )
    # non-matching: different assignee
    client.post(
        "/tasks",
        json={
            "title": "Implement feature",
            "description": "work in progress",
            "assignee": "dave",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": TaskPriority.MEDIUM.value,
        },
    )

    r = client.get(
        "/tasks",
        params={
            "assignee": "carol",
            "status": TaskStatus.IN_PROGRESS.value,
            "priority": TaskPriority.MEDIUM.value,
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item["assignee"].lower() == "carol"
    assert item["status"] == TaskStatus.IN_PROGRESS.value
    assert item["priority"] == TaskPriority.MEDIUM.value


def test_list_tasks_filter_by_comments_returns_422(client: TestClient):
    # 'comments' is not a supported query parameter; sending it should yield a 422 from FastAPI
    r = client.get("/tasks", params={"comments": "something"})
    assert r.status_code == 422


def test_list_activities_returns_200_and_empty_list(client: TestClient):
    # no activity entries exist in fresh storage
    r = client.get("/activity")
    assert r.status_code == 200
    assert r.json() == []


def test_list_activities_filter_by_from_to_type_returns_200_and_only_matches(client: TestClient):
    # create two tasks; capture their creation timestamps
    r1 = client.post("/tasks", json={"title": "task-a"})
    assert r1.status_code == 201
    a = r1.json()
    r2 = client.post("/tasks", json={"title": "task-b"})
    assert r2.status_code == 201
    b = r2.json()

    # cause some additional activity: update task-a and delete task-b
    client.patch(f"/tasks/{a['id']}", json={"status": TaskStatus.IN_PROGRESS.value})
    client.delete(f"/tasks/{b['id']}")

    print(b["created_at"])
    # filter activity to only include the creation entry for task-b using exact from/to timestamps and type
    params = {"start": b["created_at"], "end": b["created_at"], "type": ActivityType.CREATE.value}
    r = client.get("/activity", params=params)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item["type"] == ActivityType.CREATE.value
    assert item["task_uuid"] == b["id"]


def test_list_activities_filter_by_task_from_to_returns_200_and_only_matches(client: TestClient):
    # create a task and then update it to generate multiple activities for that task
    r = client.post("/tasks", json={"title": "task-x"})
    assert r.status_code == 201
    t = r.json()

    # update the task to add another activity
    r_up = client.patch(f"/tasks/{t['id']}", json={"description": "updated"})
    assert r_up.status_code == 200

    # create an unrelated task to ensure it is not returned
    client.post("/tasks", json={"title": "other"})

    params = {"task": t["id"], "start": t["created_at"], "end": r_up.json()["updated_at"]}
    r2 = client.get("/activity", params=params)
    assert r2.status_code == 200
    data = r2.json()
    assert isinstance(data, list)
    # Should include the create and the update activity for this task
    assert len(data) == 2
    for item in data:
        assert item["task_uuid"] == t["id"]


def test_list_activities_filter_by_start_returns_422(client: TestClient):
    r = client.get("/activity", params={"start": "not-a-date"})
    assert r.status_code == 422
    assert r.json().get("detail") == "the date/time values specified are in an incorrect format"