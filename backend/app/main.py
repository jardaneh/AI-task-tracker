import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi import status

from app.models import TaskCreate, TaskResponse, TaskStatus, TaskPriority
from app import storage

# Load environment variables from a local .env file if present.
load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development")

app = FastAPI(
    title="Task Tracker API",
    description=f"Module 1 Task Tracker REST API - skeleton project (env: {APP_ENV})",
    version="0.1.0",
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
def list_tasks(status: TaskStatus | None = None, priority: TaskPriority | None = None) -> list[TaskResponse]:
    """Return a list of tasks, optionally filtered by status and/or priority."""
    return storage.get_all_tasks(status=status, priority=priority)
