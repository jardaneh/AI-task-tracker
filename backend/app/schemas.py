"""
Pydantic schemas for the Task Tracker API.

These schemas define the shape of task data used when the
CRUD endpoints are implemented in a later development phase.
No request/response wiring exists yet.
"""
from typing import Optional

from pydantic import BaseModel

from app.models import Priority, Status


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: Status = Status.TODO
    priority: Priority = Priority.MEDIUM


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None


class TaskRead(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    status: Status
    priority: Priority
