from fastapi import HTTPException, status
from app.models import TaskStatus

VALID_TRANSITIONS: frozenset[tuple[TaskStatus, TaskStatus]] = frozenset({
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS),
    (TaskStatus.IN_PROGRESS, TaskStatus.DONE),
    (TaskStatus.DONE, TaskStatus.IN_PROGRESS),
})


def validate_status_transition(current: TaskStatus, new: TaskStatus) -> None:
    """Validate a task status transition against the allowed Kanban graph.

    Allowed transitions are exactly: ToDo->InProgress, InProgress->Done,
    and InProgress->ToDo. Any other pair, including a status transitioning
    to itself, is rejected.

    Args:
        current (TaskStatus): The task's status before the change.
        new (TaskStatus): The requested new status.

    Returns:
        None: Returns nothing when the transition is allowed.

    Raises:
        HTTPException: 422 if ``(current, new)`` is not one of the allowed
            transitions; the error detail lists all allowed transitions.
    """
    # Same -> same is invalid. Anything not in VALID_TRANSITIONS is invalid.
    if (current, new) not in VALID_TRANSITIONS:
        allowed = sorted({f"{f.value}->{t.value}" for f, t in VALID_TRANSITIONS})
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid status transition from {current.value} to {new.value}. Allowed transitions: {allowed}",
        )
