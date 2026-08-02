import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI, status, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from app.models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority, Activity, ActivityType
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
    """Report basic liveness of the API.

    Returns:
        dict: A JSON-serializable mapping with:
            status (str): Always ``"ok"`` when the service can respond.
            timestamp (str): Current UTC time as an ISO 8601 string.

    Example:
        GET /health -> 200
        {"status": "ok", "timestamp": "2026-08-02T15:25:01.137666+00:00"}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task by delegating to the storage layer.

    Args:
        payload (TaskCreate): Task fields supplied by the client. ``title``
            is required, trimmed, and 1-200 characters; ``status`` and
            ``priority`` default to ToDo/Medium when omitted.

    Returns:
        TaskResponse: The newly created task, including the server-assigned
        ``id``, ``created_at``, and ``updated_at``.

    Raises:
        HTTPException: 422, raised by FastAPI/Pydantic before this
            function body runs, if ``payload`` fails validation against the
            TaskCreate schema (missing/blank/too-long title, invalid
            status/priority value, or an unknown field).

    Example:
        POST /tasks {"title": "Fix bug"} -> 201
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

    Args:
        request (Request): Incoming request, inspected directly to detect
            any query parameter outside the allowed set.
        status (TaskStatus | None): Exact-match filter on task status.
        priority (TaskPriority | None): Exact-match filter on task priority.
        text (str | None): Substring filter (case-insensitive, normalized)
            matched against a task's title or description.
        assignee (str | None): Substring filter (case-insensitive,
            normalized) matched against a task's assignee.

    Returns:
        list[TaskResponse]: Tasks matching all of the provided filters
        (filters combine with AND). Empty list if none match.

    Raises:
        HTTPException: 422 if the request includes any query parameter
            other than ``status``, ``priority``, ``text``, or ``assignee``;
            the error detail names the first such offending parameter.
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
    """Return a single task by id.

    Args:
        task_id (str): UUID of the task to look up.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Update an existing task by delegating to the storage layer.

    Args:
        task_id (str): UUID of the task to update.
        payload (TaskUpdate): Fields to change; unset fields are left as-is
            (partial update semantics via ``exclude_unset``). If
            ``payload.status`` is provided, it is validated against the
            current status using business-rule transition checks before
            being applied; if it is ``None``, transition validation is
            skipped entirely.

    Returns:
        TaskResponse: The task after applying the update.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
        HTTPException: 422 if ``payload.status`` is provided and the
            transition from the task's current status is not allowed (see
            ``business_rules.validate_status_transition``).
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
    """Delete a task by id.

    Args:
        task_id (str): UUID of the task to delete.

    Returns:
        None: Responds with 204 No Content on success.

    Raises:
        HTTPException: 404 if no task with ``task_id`` exists.
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return None


@app.get("/activity", tags=["activity"], response_model=list[Activity])
def list_activity(
    request: Request,
    task: str | None = None,
    start: str | None = None,
    end: str | None = None,
    type: ActivityType | None = None,
) -> list[Activity]:
    """List activity log entries filtered by optional query params.

    Args:
        request (Request): Incoming request, inspected directly to detect
            any query parameter outside the allowed set.
        task (str | None): If provided, only entries for this task id are
            returned; the task must exist.
        start (str | None): ISO 8601 timestamp (a trailing ``Z`` is accepted
            and normalized to ``+00:00``); entries strictly before this are
            excluded.
        end (str | None): ISO 8601 timestamp (a trailing ``Z`` is accepted
            and normalized to ``+00:00``); entries strictly after this are
            excluded.
        type (ActivityType | None): Exact-match filter on activity type
            (create, update, status-update, delete).

    Returns:
        list[Activity]: Matching activity entries, ordered most-recent-first.

    Raises:
        HTTPException: 422 if the request includes any query parameter
            other than ``task``, ``start``, ``end``, or ``type``.
        HTTPException: 404 if ``task`` is provided but no task with that id
            exists.
        HTTPException: 422 if ``start`` or ``end`` is not a valid ISO 8601
            string.
    """
    allowed = {"task", "start", "end", "type"}
    received = set(request.query_params.keys())
    unknown = received - allowed
    if unknown:
        param = sorted(list(unknown))[0]
        raise HTTPException(status_code=422, detail=f"Unknown query parameter: {param}")

    # validate task exists if provided
    if task is not None:
        if storage.get_task_by_id(task) is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task} not found")

    # parse dates if provided
    from_ts: datetime | None = None
    to_ts: datetime | None = None
    if start is not None:
        try:
            s = start
            # accept UTC 'Z' suffix by converting it to an offset recognized by fromisoformat
            if s.endswith("Z"):
                s = s.replace("Z", "+00:00")
            from_ts = datetime.fromisoformat(s)
        except Exception:
            raise HTTPException(status_code=422, detail="the date/time values specified are in an incorrect format")
    if end is not None:
        try:
            e = end
            # accept UTC 'Z' suffix by converting it to an offset recognized by fromisoformat
            if e.endswith("Z"):
                e = e.replace("Z", "+00:00")
            to_ts = datetime.fromisoformat(e)
        except Exception:
            raise HTTPException(status_code=422, detail="the date/time values specified are in an incorrect format")

    # delegate to storage
    activities = storage.get_activity_entries(task=task, from_ts=from_ts, to_ts=to_ts, type=type)
    return activities