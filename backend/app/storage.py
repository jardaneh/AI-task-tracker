from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from .models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority
import uuid
import re

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


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    text: Optional[str] = None,
    assignee: Optional[str] = None,
) -> List[TaskResponse]:
    results = list(_tasks.values())
    if status is not None:
        results = [t for t in results if t.status == status]
    if priority is not None:
        results = [t for t in results if t.priority == priority]

    # Normalize and apply text filter (title or description) if provided
    if text is not None:
        text_norm = text.strip().lower()
        # remove any character that is not a-z or 0-9
        text_norm = re.sub(r"[^a-z0-9]+", "", text_norm)
        if text_norm:
            filtered: List[TaskResponse] = []
            for task in results:
                title = (task.title or "").strip().lower()
                title_norm = re.sub(r"[^a-z0-9]+", "", title)
                description = (task.description or "").strip().lower()
                description_norm = re.sub(r"[^a-z0-9]+", "", description)
                if text_norm in title_norm or text_norm in description_norm:
                    filtered.append(task)
            results = filtered

    # Normalize and apply assignee filter if provided
    if assignee is not None:
        assignee_norm = assignee.strip().lower()
        assignee_norm = re.sub(r"[^a-z0-9]+", "", assignee_norm)
        if assignee_norm:
            filtered: List[TaskResponse] = []
            for task in results:
                a = (task.assignee or "").strip().lower()
                a_norm = re.sub(r"[^a-z0-9]+", "", a)
                if assignee_norm in a_norm:
                    filtered.append(task)
            results = filtered

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
