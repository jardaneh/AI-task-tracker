# Draft architecture-B.md

## What the app does

Task Tracker is a learning-oriented Kanban application. A vanilla JavaScript frontend lets users create, view, update, move, and delete tasks through a FastAPI REST API. Tasks are grouped by `ToDo`, `InProgress`, and `Done`; data is held in memory and is lost when the backend restarts.  
*(Sources: `README.md`, `backend/app/main.py`)*

## Data model

The primary entity is `Task`, represented by:

- `id`: generated UUID string
- `title`: required, trimmed, non-blank, maximum 200 characters
- `description`: optional, defaults to an empty string
- `status`: `ToDo`, `InProgress`, or `Done`; defaults to `ToDo`
- `priority`: `Low`, `Medium`, or `High`; defaults to `Medium`
- `assignee`: optional string, defaults to `null`
- `created_at` and `updated_at`: UTC timestamps

Request and response shapes are defined with Pydantic models.  
*(Source: `backend/app/models.py`)*

## Request flow

When a user submits a new task:

1. The frontend sends a `POST /tasks` request containing the form fields.
2. FastAPI validates the request using `TaskCreate`.
3. Validation trims and checks the title, applies defaults, validates enum values, and rejects unknown fields.
4. The route delegates the validated payload to the storage layer.
5. Storage generates the task ID and UTC timestamps, creates a `TaskResponse`, and stores it in the in-memory dictionary.
6. The API returns the created task with HTTP `201`.
7. The frontend refreshes its task collection and redraws the Kanban board.

*(Sources: `frontend/index.html`, `backend/app/main.py`, `backend/app/models.py`, `backend/app/storage.py`)*

## Key files

- `backend/app/main.py` — Creates the FastAPI app, configures CORS and health checks, and defines task routes.
- `backend/app/models.py` — Defines task statuses, priorities, request models, validation, and response fields.
- `backend/app/business_rules.py` — Defines and validates allowed status transitions.
- `backend/app/storage.py` — Implements in-memory task creation, lookup, filtering, updates, deletion, and test reset.
- `backend/app/utils.py` — Provides a shared title-trimming helper; its current usage is not confirmed.
- `frontend/index.html` — Contains the complete static HTML, CSS, and JavaScript Kanban frontend.
- `backend/tests/test_tasks.py` — Tests API creation, validation, updates, transitions, filtering, and deletion.
- `backend/tests/conftest.py` — Provides the API test client and resets in-memory storage around tests.
- `README.md` — Documents setup, runtime, structure, limitations, and supported commands.

## Conventions

- Validation is enforced at the API boundary with Pydantic; invalid input and invalid status transitions return HTTP `422`.
- Unknown request fields are rejected.
- Status changes are limited to `ToDo → InProgress`, `InProgress → Done`, and `Done → InProgress`.
- Storage is an in-memory Python dictionary with no database or file persistence.
- Missing tasks return HTTP `404`; successful deletion returns `204` with no body.
- Updates are partial, and successful changes refresh `updated_at`.
- The frontend communicates with the backend using browser `fetch` requests.
- CORS permits frontend origins at `http://localhost:8080` and `http://127.0.0.1:8080`.
- Tests reset storage between cases to avoid state leakage.

## Not visible or assumptions

- Authentication and authorization are not implemented or confirmed.
- Production deployment, persistence, concurrency behavior, and scalability are not confirmed.
- The frontend’s exact runtime API-base configuration is not fully documented here.
- Explicit `null` update behavior is not fully confirmed by the storage implementation.
- `backend/app/schemas.py` and `backend/app/routes/tasks.py` are documented as stale or unused; their role is not part of the active request flow.

## Which context item helped most

The file-by-file summary, especially the distinction between `main.py`, `models.py`, `business_rules.py`, and `storage.py`, provided the clearest architecture boundaries.

## Remaining assumptions or unsupported details

The document does not assume authentication, a database, deployment infrastructure, or production guarantees because these are not confirmed by the supplied context.
