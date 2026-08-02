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
    """Create and store a new task, recording a CREATE activity entry.

    Args:
        payload (TaskCreate): Validated task fields to persist.

    Returns:
        TaskResponse: The stored task, with a new UUID ``id`` and
        ``created_at``/``updated_at`` both set to the current UTC time.
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
    """Return stored tasks matching all provided filters (AND semantics).

    Args:
        status (TaskStatus | None): Exact-match filter on task status.
        priority (TaskPriority | None): Exact-match filter on task priority.
        text (str | None): Substring filter matched against the task's
            title or description after normalizing both sides (lowercase,
            stripped, non-alphanumeric characters removed).
        assignee (str | None): Substring filter matched against the task's
            assignee after the same normalization as ``text``.

    Returns:
        List[TaskResponse]: Tasks satisfying every provided filter. Returns
        all tasks if no filters are provided.
    """
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
    """Look up a single task by id.

    Args:
        task_id (str): UUID of the task to look up.

    Returns:
        Optional[TaskResponse]: The matching task, or ``None`` if no task
        with ``task_id`` exists.
    """
    return _tasks.get(task_id)



def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to a stored task and record activity entries.

    Only fields explicitly set on ``payload`` are considered (via
    ``model_dump(exclude_unset=True)``); a ``status`` value equal to the
    task's current status is treated as a no-op and not counted as a
    change. Note: when called through ``PATCH /tasks/{id}``, the route
    handler already rejects a same-status update with a 422 via
    ``business_rules.validate_status_transition`` before this function is
    invoked, so that no-op branch here mainly guards direct/internal calls.

    Args:
        task_id (str): UUID of the task to update.
        payload (TaskUpdate): Fields to change; unset fields are ignored.

    Returns:
        Optional[TaskResponse]: The updated task, or ``None`` if no task
        with ``task_id`` exists. If ``payload`` contains no actual changes,
        the existing task is returned unmodified (``updated_at`` untouched).

    Side Effects:
        Writes a STATUS_UPDATE activity entry if ``status`` changed, and/or
        an UPDATE activity entry if any other field changed, each keyed by
        the new ``updated_at`` timestamp.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None
    data = payload.model_dump(exclude_unset=True, exclude_none=True)
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
    """Delete a stored task and record a DELETE activity entry.

    Args:
        task_id (str): UUID of the task to delete.

    Returns:
        bool: ``True`` if a task with ``task_id`` was found and removed,
        ``False`` if no such task existed.

    Side Effects:
        Writes a DELETE activity entry containing a snapshot of the task's
        fields (title, description, status, priority, assignee) as they
        were immediately before removal.
    """
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
    """Return activity log entries matching all provided filters (AND semantics).

    Args:
        task (str | None): If provided, only this task's activity entries
            are considered (looked up via the per-task index); otherwise
            all entries in the global index are considered.
        from_ts (datetime | None): Inclusive lower bound on ``timestamp``.
        to_ts (datetime | None): Inclusive upper bound on ``timestamp``.
        type (ActivityType | None): Exact-match filter on activity type.

    Returns:
        List[Activity]: Matching entries, ordered most-recent-first by
        ``timestamp``. Empty list if ``task`` is unknown or nothing matches.
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
