from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from .models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
import uuid

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and store a new task.

    Args:
        payload (TaskCreate): Validated fields for the new task.

    Returns:
        TaskResponse: The stored task, with a generated UUID ``id``
        and ``created_at``/``updated_at`` set to the current UTC time.
    """
    now = datetime.now(timezone.utc)
    task_id = str(uuid.uuid4())
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    return task


def get_all_tasks(status: Optional[TaskStatus] = None, priority: Optional[TaskPriority] = None) -> List[TaskResponse]:
    """Return stored tasks, optionally filtered by status and/or priority.

    Args:
        status (Optional[TaskStatus]): If provided, only include tasks
            with this exact status.
        priority (Optional[TaskPriority]): If provided, only include
            tasks with this exact priority. Combined with ``status``
            using AND when both are given.

    Returns:
        List[TaskResponse]: Matching tasks in insertion order, or an
        empty list if none match.
    """
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Look up a task by id.

    Args:
        task_id (str): The task's unique id.

    Returns:
        Optional[TaskResponse]: The task, or ``None`` if no task with
        this id exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task.

    Only fields explicitly set on ``payload`` (per
    ``model_dump(exclude_unset=True)``) are applied, and only if they
    are among the allowed keys (``title``, ``description``, ``status``,
    ``priority``, ``assignee``). ``updated_at`` is refreshed only if at
    least one field was changed.

    Args:
        task_id (str): The id of the task to update.
        payload (TaskUpdate): Fields to update.

    Returns:
        Optional[TaskResponse]: The updated task, or ``None`` if no
        task with ``task_id`` exists.

    [VERIFY]: An explicitly-sent ``null`` (e.g. ``{"title": null}``)
    counts as "set" and is applied via ``setattr`` without re-running
    the title validator or ``TaskResponse`` field validation
    (attribute assignment doesn't revalidate by default), so it can
    put ``None`` into a field typed as ``str``. Confirm whether this
    edge case is intended or should be guarded against.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    changed = False
    updated_fields: dict = {}
    for key, value in data.items():
        # only update allowed fields
        if key in {"title", "description", "status", "priority", "assignee"}:
            setattr(existing, key, value)
            changed = True
            updated_fields[key] = value
    if changed:
        existing.updated_at = datetime.now(timezone.utc)
        _tasks[task_id] = existing
    return existing


def delete_task(task_id: str) -> bool:
    """Delete a task by id.

    Args:
        task_id (str): The id of the task to delete.

    Returns:
        bool: ``True`` if the task existed and was removed, ``False``
        if no task with ``task_id`` was found.
    """
    if task_id in _tasks:
        _tasks.pop(task_id)
        return True
    return False


def _reset() -> None:
    _tasks.clear()
