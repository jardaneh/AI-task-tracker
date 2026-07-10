from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from .models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
import uuid

_tasks: dict[str, TaskResponse] = {}


def add_task(payload: TaskCreate) -> TaskResponse:
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
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
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
    if task_id in _tasks:
        _tasks.pop(task_id)
        return True
    return False


def _reset() -> None:
    _tasks.clear()
