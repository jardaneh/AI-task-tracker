"""
Task routes.

This module defines the APIRouter that will eventually expose
CRUD endpoints for tasks (create, read, update, delete, and
status changes triggered by Kanban card moves).

No endpoints are implemented yet. This router is not currently
included in the main FastAPI app.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["tasks"])
