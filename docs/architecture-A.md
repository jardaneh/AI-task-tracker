# Task Tracker Architecture

## What the app does

Task Tracker is a learning-oriented Kanban application for creating, viewing, updating, moving, and deleting tasks across `ToDo`, `InProgress`, and `Done` columns. It uses a vanilla JavaScript frontend and a FastAPI REST backend.

## Data model

The primary entity is `Task`:

- `id`: generated UUID string
- `title`: required, trimmed, maximum 200 characters
- `description`: optional string, default empty
- `status`: `ToDo`, `InProgress`, or `Done`; defaults to `ToDo`
- `priority`: `Low`, `Medium`, or `High`; defaults to `Medium`
- `assignee`: optional string
- `created_at`, `updated_at`: UTC timestamps

## Request flow: create a task

1. The frontend collects form values and sends `POST /tasks` as JSON.
2. FastAPI/Pydantic validates the request, including required title, enum values, and rejected unknown fields.
3. The route delegates to the in-memory storage module.
4. Storage generates the task UUID and UTC timestamps, applies defaults, and stores the task in a dictionary.
5. The API returns the created task with HTTP `201`.
6. The frontend closes the form and reloads the task list with `GET /tasks`.

## Key files

- `backend/app/main.py` — FastAPI app, CORS configuration, health check, and task routes.
- `backend/app/models.py` — Task enums, request models, validation, and response model.
- `backend/app/business_rules.py` — Allowed status-transition rules.
- `backend/app/storage.py` — In-memory task dictionary and CRUD operations.
- `backend/app/utils.py` — Shared title-trimming utility.
- `frontend/index.html` — Single-file HTML/CSS/JavaScript Kanban frontend.
- `backend/tests/test_tasks.py` — API tests for creation, validation, updates, transitions, and deletion.
- `backend/tests/conftest.py` — Test client setup and storage reset fixture.
- `README.md` — Setup, runtime, structure, and limitation documentation.

## Conventions

- Validation is performed primarily by Pydantic; invalid input returns HTTP `422`.
- Request models forbid unknown fields.
- Status changes are restricted to `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`.
- Data is stored only in process memory and is lost on restart.
- Missing task IDs return HTTP `404`; successful deletion returns `204`.
- The frontend communicates with the backend using `fetch` and JSON over HTTP.
- CORS permits frontend origins at `localhost:8080` and `127.0.0.1:8080`.
- The frontend displays loading, validation, server-error, and retry feedback.

## Not visible or assumptions

- Authentication and authorization are not implemented or confirmed.
- No database, durable persistence, deployment service, or production scaling architecture is confirmed.
- The document treats `backend/app/main.py` and `backend/app/models.py` as authoritative; the unused `backend/app/schemas.py` and `backend/app/routes/tasks.py` are not part of the active request path.
- The exact intended behavior for explicitly sending `null` in update payloads is not fully confirmed by the implementation.