import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException, Request
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
    """Basic liveness check for the API."""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task by delegating to the storage layer.

    Validation (missing/blank/too long title, invalid status/priority,
    unknown fields) is handled by Pydantic via the TaskCreate schema.
    """
    return storage.add_task(payload)

@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    request: Request,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    text: str | None = None,
    assignee: str | None = None,
) -> list[TaskResponse]:
    """Return a list of tasks, optionally filtered by status, priority, text, and assignee.

    Reject unknown query parameters with a 422 and an error message naming the offending parameter.
    """
    # allowed query param names (FastAPI will have already validated enum/typing for known params)
    allowed = {"status", "priority", "text", "assignee"}
    # fastapi's Request.query_params is a MultiDict-like object; convert to set of keys
    received = set(request.query_params.keys())
    # remove params that are allowed and may be absent
    unknown = received - allowed
    if unknown:
        # return 422 with an error message pointing out the first unknown param
        param = sorted(list(unknown))[0]
        raise HTTPException(status_code=422, detail=f"Unknown query parameter: {param}")

    return storage.get_all_tasks(status=status, priority=priority, text=text, assignee=assignee)


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Return a single task by id or raise 404 if not found."""
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
    """Delete a task by id or raise 404 if not found."""
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return None