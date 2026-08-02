## 1. Draft `architecture-C.md`

# Task Tracker Architecture

## What the app does

The app exposes a REST API for creating, listing, retrieving, updating, and deleting task records. It validates task data, assigns identifiers and timestamps, and stores tasks in an in-memory collection.

## Data model

The primary entity is `Task`.

- `id`: generated UUID string
- `title`: required, trimmed string, maximum 200 characters
- `description`: string, default `""`
- `status`: `ToDo`, `InProgress`, or `Done`; defaults to `ToDo`
- `priority`: `Low`, `Medium`, or `High`; defaults to `Medium`
- `assignee`: optional string, default `null`
- `created_at`, `updated_at`: UTC timestamps

`TaskCreate` defines creation input, `TaskUpdate` defines partial update input, and `TaskResponse` defines the returned task shape.

## Request flow

When a user creates a task, a request is sent to `POST /tasks`. The request is validated against `TaskCreate`: unknown fields are rejected, the title is trimmed and checked, and default values are applied. The API then delegates to storage. Storage generates a UUID, assigns current UTC timestamps, constructs a `TaskResponse`, stores it in the in-memory task dictionary, and returns it with HTTP 201.

## Key files

- `backend/app/main.py` — API application, routes, CORS configuration, and request delegation.
- `backend/app/models.py` — task schemas, enums, fields, defaults, and title validation.
- `backend/app/storage.py` — in-memory task storage and CRUD operations.
- `backend/app/business_rules.py` — not visible from the files I read; imported for status-transition validation.
- `frontend/index.html` — not visible from the files I read; likely frontend entry point, but its behavior is unconfirmed.
- `backend/tests/test_tasks.py` — not visible from the files I read; test coverage is unconfirmed.

## Conventions

- Validation is explicitly defined with Pydantic models and field validators.
- Unknown input fields are rejected through `extra="forbid"`.
- Storage is an in-memory dictionary named `_tasks`; durability across process restarts is not visible from the files I read.
- Missing tasks produce HTTP 404 responses in the API routes.
- Invalid request data is documented as producing HTTP 422 through API validation.
- The API explicitly configures CORS for `localhost:8080` and `127.0.0.1:8080`, allowing credentials, methods, and headers. Actual frontend/backend request code is not visible from the files I read.
- Task creation and retrieval are routed through `storage`; status-transition validation for updates is delegated to `business_rules`.

## Not visible or assumptions

- The implementation of status-transition rules is not visible from the files I read.
- Frontend behavior and API calls are not visible from the files I read.
- Tests, dependency versions, deployment, authentication, authorization, concurrency behavior, and persistence beyond process memory are not visible from the files I read.
- The exact behavior of explicitly supplied `null` values during updates is not fully confirmed by these files.

## 2. Files read

- `backend/app/main.py`
- `backend/app/models.py`
- `backend/app/storage.py`

## 3. Items marked not visible

- `backend/app/business_rules.py`
- `frontend/index.html`
- `backend/tests/test_tasks.py`
- Frontend request implementation
- Test coverage
- Dependency and deployment configuration
- Durable persistence
- Authentication and authorization

## 4. What this targeted strategy likely missed

This strategy omits business-rule implementation, frontend integration details, tests, configuration, deployment, and operational behavior.