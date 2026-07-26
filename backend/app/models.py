"""
Domain objects and enums for the Task Tracker API.
"""
from __future__ import annotations
from enum import Enum
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class TaskStatus(str, Enum):
    TODO = "ToDo"
    IN_PROGRESS = "InProgress"
    DONE = "Done"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    description: Optional[str] = ""
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee: Optional[str] = None

    @field_validator("title", mode="before")
    def _strip_and_validate_title(cls, v: str) -> str:
        if v is None:
            raise ValueError("Title is required and cannot be blank")
        if not isinstance(v, str):
            raise TypeError("title must be a string")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title is required and cannot be blank")
        if len(trimmed) > 200:
            raise ValueError("Title must be at most 200 characters")
        return trimmed


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assignee: Optional[str] = None

    @field_validator("title", mode="before")
    def _strip_and_validate_title_if_provided(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        if not isinstance(v, str):
            raise TypeError("title must be a string")
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Title is required and cannot be blank")
        if len(trimmed) > 200:
            raise ValueError("Title must be at most 200 characters")
        return trimmed


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    title: str
    description: str
    status: TaskStatus
    priority: TaskPriority
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime


class ActivityType(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    STATUS_UPDATE = "status-update"
    DELETE = "delete"


class Activity(BaseModel):
    model_config = ConfigDict(extra="forbid")

    task_uuid: str
    timestamp: datetime
    type: ActivityType
    details: str
