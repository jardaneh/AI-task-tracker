from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from .models import TaskCreate, TaskUpdate, TaskResponse, TaskStatus, TaskPriority, Activity, ActivityType
import uuid
import re

_tasks: dict[str, TaskResponse] = {}
# global mapping timestamp -> Activity
_activities_by_timestamp: dict[datetime, Activity] = {}
# mapping task_uuid -> (mapping timestamp -> Activity)
_activities_by_task: dict[str, dict[datetime, Activity]] = {}


def _normalize_string(value: Optional[str]) -> str:
    """Normalize a string for matching: return lowercase, stripped, and
    with all non-alphanumeric a-z0-9 characters removed. Returns empty string
    for None or when normalization yields nothing.
    """
    if value is None:
        return ""
    v = value.strip().lower()
    v = re.sub(r"[^a-z0-9]+", "", v)
    return v


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

    # create activity entry for creation
    details_obj = {
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value,
        "assignee": task.assignee,
    }
    activity = Activity(
        task_uuid=task_id,
        timestamp=task.created_at,
        type=ActivityType.CREATE,
        details=__import__('json').dumps(details_obj),
    )
    _activities_by_timestamp[activity.timestamp] = activity
    # store reference in per-task mapping
    if task_id not in _activities_by_task:
        _activities_by_task[task_id] = {}
    _activities_by_task[task_id][activity.timestamp] = activity

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
        text_norm = _normalize_string(text)
        if text_norm:
            filtered: List[TaskResponse] = []
            for task in results:
                title_norm = _normalize_string(task.title)
                description_norm = _normalize_string(task.description)
                if text_norm in title_norm or text_norm in description_norm:
                    filtered.append(task)
            results = filtered

    # Normalize and apply assignee filter if provided
    if assignee is not None:
        assignee_norm = _normalize_string(assignee)
        if assignee_norm:
            filtered: List[TaskResponse] = []
            for task in results:
                a_norm = _normalize_string(task.assignee)
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
    status_changed = False
    old_status = existing.status
    for key, value in data.items():
        # only update allowed fields
        if key in {"title", "description", "status", "priority", "assignee"}:
            # detect status change
            if key == "status":
                if value != existing.status:
                    status_changed = True
                else:
                    # no-op for status
                    continue
            setattr(existing, key, value)
            changed = True
            updated_fields[key] = value
    if changed:
        existing.updated_at = datetime.now(timezone.utc)
        _tasks[task_id] = existing

        # create activities depending on what changed
        # status_change activity
        if status_changed:
            details_obj = {"previous_status": old_status.value, "new_status": existing.status.value}
            activity_status = Activity(
                task_uuid=task_id,
                timestamp=existing.updated_at,
                type=ActivityType.STATUS_UPDATE,
                details=__import__('json').dumps(details_obj),
            )
            _activities_by_timestamp[activity_status.timestamp] = activity_status
            if task_id not in _activities_by_task:
                _activities_by_task[task_id] = {}
            _activities_by_task[task_id][activity_status.timestamp] = activity_status

        # update activity for other fields (exclude status)
        other_changed = {k: v for k, v in updated_fields.items() if k != "status"}
        if other_changed:
            # details only include new values
            details_obj = {}
            for k, v in other_changed.items():
                # if it's an Enum, use its value
                if hasattr(v, "value"):
                    details_obj[k] = v.value
                else:
                    details_obj[k] = v
            activity_update = Activity(
                task_uuid=task_id,
                timestamp=existing.updated_at,
                type=ActivityType.UPDATE,
                details=__import__('json').dumps(details_obj),
            )
            _activities_by_timestamp[activity_update.timestamp] = activity_update
            if task_id not in _activities_by_task:
                _activities_by_task[task_id] = {}
            _activities_by_task[task_id][activity_update.timestamp] = activity_update

    return existing


def delete_task(task_id: str) -> bool:
    if task_id in _tasks:
        # capture snapshot before deletion
        task = _tasks.get(task_id)
        if task is None:
            return False
        details_obj = {
            "title": task.title,
            "description": task.description,
            "status": task.status.value,
            "priority": task.priority.value,
            "assignee": task.assignee,
        }
        activity = Activity(
            task_uuid=task_id,
            timestamp=datetime.now(timezone.utc),
            type=ActivityType.DELETE,
            details=__import__('json').dumps(details_obj),
        )
        _activities_by_timestamp[activity.timestamp] = activity
        if task_id not in _activities_by_task:
            _activities_by_task[task_id] = {}
        _activities_by_task[task_id][activity.timestamp] = activity

        _tasks.pop(task_id)
        return True
    return False

def get_activity_entries(
    task: Optional[str] = None,
    from_ts: Optional[datetime] = None,
    to_ts: Optional[datetime] = None,
    type: Optional[ActivityType] = None,
) -> List[Activity]:
    """Return a list of Activity entries matching optional filters.

    If 'task' is provided, the per-task mapping is queried first. The returned
    list is ordered from most recent to least recent by timestamp.
    """
    # choose the appropriate source mapping
    if task is not None:
        entries = _activities_by_task.get(task, {})
    else:
        entries = _activities_by_timestamp

    results: List[Activity] = []
    for ts, act in entries.items():
        if from_ts is not None and ts < from_ts:
            continue
        if to_ts is not None and ts > to_ts:
            continue
        if type is not None and act.type != type:
            continue
        results.append(act)

    # sort by timestamp descending (most recent first)
    results.sort(key=lambda a: a.timestamp, reverse=True)
    return results


def _reset() -> None:
    _tasks.clear()
    _activities_by_timestamp.clear()
    _activities_by_task.clear()
