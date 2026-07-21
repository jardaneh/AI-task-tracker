# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech stack

- **Python**: venv reports 3.10.12 — [VERIFY] if the course expects 3.11; not stated in `requirements.txt` or `README.md`, so do not assume 3.11 without checking the environment you're actually running in.
- **FastAPI** 0.115.0 (`requirements.txt`)
- **Pydantic** v2 (2.9.2, `requirements.txt`) — models use `ConfigDict`/`field_validator`, the v2 API.
- **Uvicorn** 0.30.6 with `[standard]` extra (`requirements.txt`)
- **pytest** — installed in `venv` (9.1.1) but **not pinned in `requirements.txt`** [VERIFY] whether that's intentional or a missing dev-dependency entry.
- **httpx** — installed in `venv` (0.28.1), also not in `requirements.txt`; used transitively by FastAPI's `TestClient` in `backend/tests/conftest.py`.
- **python-dotenv** 1.0.1 (`requirements.txt`) — loads `.env` in `main.py`.
- **Frontend**: vanilla JavaScript + HTML, single file `frontend/index.html`, no framework, no build step.

## Run command

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Swagger UI: http://localhost:8000/docs

## Test command

```bash
cd backend
pytest -v
```

Single test: `pytest -v tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200`

Run all commands from `backend/` — the app is the `app` package rooted there (`app.main`, `app.storage`, etc.), and `backend/tests/conftest.py` imports it as such.

There is also a standalone script `tests/verify_a.py` (repo root, not part of the pytest suite) that exercises `TaskCreate`/`TaskUpdate` validation directly and prints PASS/FAIL lines — run with `python -m tests.verify_a` from the repo root if asked to re-verify schema validation behavior outside of pytest.

## Architecture

**Backend** (`backend/app/`):
- `main.py` — FastAPI app instance, CORS config, and all route handlers (`/health`, `POST/GET/PATCH/DELETE /tasks`, `GET /tasks/{id}`). Handlers are thin — they delegate to `storage` and add only the transition check and 404s.
- `models.py` — `TaskStatus`/`TaskPriority` enums and the `TaskCreate`/`TaskUpdate`/`TaskResponse` Pydantic models (validation lives here: `extra="forbid"`, title stripping/blank/length checks).
- `business_rules.py` — `validate_status_transition` and `VALID_TRANSITIONS`; this is where task status rules live (see Business rules below).
- `storage.py` — in-memory dict keyed by task id (`_tasks: dict[str, TaskResponse]`); no DB, no file persistence. `_reset()` clears it for tests.
- `utils.py` — `trim_title` helper.
- `schemas.py` and `routes/tasks.py` — **stale/unused**. `schemas.py` imports `Priority`/`Status` from `app.models`, which no longer exist there (`app/models.py` defines `TaskPriority`/`TaskStatus`); nothing imports this module. `routes/tasks.py` defines an empty `APIRouter` that is never mounted on `app`. Treat `main.py` + `models.py` as the source of truth, not these two files.

**Frontend** (`frontend/index.html`, single file): rendering (`renderBoard`, `createColumn`, `createTaskCard`), drag-and-drop handlers (`handleTaskCardDragStart/End`, `handleBoardColumnDragOver/Leave/Drop`) that PATCH status on drop, and a create/edit modal (`openTaskModal`/`closeTaskModal`) that POSTs/PATCHes task fields and surfaces 422 errors inline via `getErrorMessage`/`getFieldErrors`.

**Tests** (`backend/tests/`): `conftest.py` provides a `client` fixture (`TestClient(app)`) and an autouse fixture that calls `storage._reset()` before/after every test. `test_tasks.py` holds the endpoint tests, one behavior per test, named `test_<verb>_<condition>_returns_<code>`.

`README.md` describes an earlier project stage (JSON file persistence, no CRUD yet) that the current code has superseded — don't rely on it for current behavior.

## Business rules

As implemented in `backend/app/models.py` and `backend/app/business_rules.py`:

- **Task status values** (`TaskStatus`): `ToDo`, `InProgress`, `Done`.
- **Task priority values** (`TaskPriority`): `Low`, `Medium`, `High`.
- **Allowed status transitions** (`business_rules.VALID_TRANSITIONS`): `ToDo → InProgress`, `InProgress → Done`, `Done → InProgress`. Any other transition — including same-status and `ToDo → Done` directly — raises `HTTP 422` from `validate_status_transition`.
- This check runs only in `PATCH /tasks/{id}`, and only when `payload.status is not None` — sending back the current status unchanged as part of an edit will trip it (this exact bug was fixed once already, per git history).
- Title validation (`TaskCreate`/`TaskUpdate`): required, whitespace-stripped, cannot be blank after stripping, max 200 characters.
- All four models use `extra="forbid"` — unknown fields on request bodies return 422.

## UI states and CORS

- CORS (`main.py`): `allow_origins` is restricted to `http://localhost:8080` and `http://127.0.0.1:8080` — the frontend must be served from one of these origins (e.g. `python3 -m http.server 8080` from `frontend/`) or requests will be blocked by the browser.
- Frontend defines explicit UI states in `index.html`: `createLoadingState()`, `createErrorState()`, and `createEmptyPlaceholder()` (empty column), alongside the normal populated-column render path in `renderBoard`/`createColumn`.
- Form/edit errors from the API (422s) are surfaced inline in the modal via `getErrorMessage`/`getFieldErrors`/`showFormBanner`, not as raw alerts.

## Do-not rules

- Do not add authentication/authorization.
- Do not add a database or persistence layer.
- Do not add deployment steps or infrastructure config.
- Do not make major UI changes.

...without asking first.
