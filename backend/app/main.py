import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import status
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
from app import storage
from app.business_rules import validate_status_transition

# Load environment variables from a local .env file if present.
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description=f"Module 1 Task Tracker REST API - skeleton project (env: {APP_ENV})",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Report basic liveness status of the API.

    Returns:
        dict: A JSON-serializable payload with a static ``status`` of
        ``"ok"`` and the current UTC timestamp in ISO 8601 format.

    Example:
        GET /health -> 200
        {"status": "ok", "timestamp": "2026-07-28T12:00:00+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task by delegating to the storage layer.

    Validation (missing/blank/too long title, invalid status/priority,
    unknown fields) is handled by Pydantic via the TaskCreate schema.

    Args:
        payload (TaskCreate): Validated task fields. ``title`` is
            required, stripped of surrounding whitespace, must be
            non-blank after stripping, and at most 200 characters.
            ``status`` and ``priority`` default to ``ToDo`` and
            ``Medium`` if omitted. Unknown fields are rejected.

    Returns:
        TaskResponse: The newly created task, including its generated
        ``id`` and ``created_at``/``updated_at`` timestamps.

    Raises:
        HTTPException: 422 if ``payload`` fails Pydantic validation
            (raised by FastAPI before this function body runs).

    Example:
        POST /tasks {"title": "Buy milk"} -> 201
        {"id": "...", "title": "Buy milk", "status": "ToDo", ...}
    """
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(status: TaskStatus | None = None, priority: TaskPriority | None = None) -> list[TaskResponse]:
    """Return a list of tasks, optionally filtered by status and/or priority.

    Args:
        status (TaskStatus | None): If provided, only tasks with this
            exact status are returned.
        priority (TaskPriority | None): If provided, only tasks with
            this exact priority are returned. Combined with ``status``
            using AND when both are given.

    Returns:
        list[TaskResponse]: Matching tasks, or an empty list if none
        match.

    Example:
        GET /tasks?status=ToDo&priority=High -> 200 [...]
    """
    return storage.get_all_tasks(status=status, priority=priority)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by id or raise 404 if not found.

    Args:
        task_id (str): The task's unique id.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        GET /tasks/{task_id} -> 200 {...}
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Update an existing task by delegating to the storage layer.

    Behavior changes:
    - If payload.status is None, skip transition validation.
    - If payload.status is provided, validate the transition against business rules.

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): Fields to update; only fields explicitly
            set are applied (see ``storage.update_task``). If
            ``status`` is provided, it is validated against
            ``business_rules.VALID_TRANSITIONS``.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
        HTTPException: 422 if ``status`` is provided and the
            transition from the task's current status is not allowed.

    Example:
        PATCH /tasks/{task_id} {"status": "InProgress"} -> 200 {...}
    """
    # Only validate transitions when a new status is provided.
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing.status, payload.status)

    updated = storage.update_task(task_id, payload)
    if updated is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return updated

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    """Delete a task by id or raise 404 if not found.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        None

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.

    Example:
        DELETE /tasks/{task_id} -> 204 (no body)
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return None