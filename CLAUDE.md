# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Task Tracker: a FastAPI backend (`backend/app`) with a single-page vanilla JS/HTML frontend (`frontend/index.html`), backed by pure in-memory storage (no DB, no file persistence despite what older docs may imply).

## Commands

Run all commands from `backend/` — the app is the `app` package rooted there (`app.main`, `app.storage`, etc.), and `backend/tests/conftest.py` imports it as such.

```bash
# Setup (from repo root)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # PORT, APP_ENV

# Run the server (from backend/)
cd backend
uvicorn app.main:app --reload --port 8000
# Swagger UI: http://localhost:8000/docs

# Run tests (from backend/)
cd backend
pytest
pytest tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200  # single test

# Frontend: no build step — open frontend/index.html directly in a browser,
# or serve it (e.g. `python3 -m http.server 8080` from frontend/) since it
# calls the API via CORS from a separate origin.
```

There is also a standalone script `tests/verify_a.py` (repo root, not part of the pytest suite) that exercises `TaskCreate`/`TaskUpdate` validation directly and prints PASS/FAIL lines — run with `python -m tests.verify_a` from the repo root if asked to re-verify schema validation behavior outside of pytest.

## Architecture

**Request flow:** `frontend/index.html` (fetch calls, `API_BASE = "http://localhost:8000"`) → `backend/app/main.py` (route handlers) → `backend/app/business_rules.py` (status-transition validation) → `backend/app/storage.py` (in-memory dict keyed by task id, `_tasks: dict[str, TaskResponse]`).

**Status model is a one-way-ish Kanban flow, not a free dropdown.** `TaskStatus` is `ToDo` / `InProgress` / `Done`. Allowed transitions live in `business_rules.VALID_TRANSITIONS`: `ToDo→InProgress`, `InProgress→Done`, `Done→InProgress`. Any other transition (including same→same, or `ToDo→Done` directly) raises HTTP 422 from `validate_status_transition`. This is enforced only in `PATCH /tasks/{id}` in `main.py`, and only when `payload.status is not None` — i.e. the frontend must not send the current status back unchanged as part of an edit, or it will trip this check (this exact bug was fixed once already, per git history).

**Validation lives on the Pydantic models, not in route handlers.** `app/models.py` defines `TaskCreate`/`TaskUpdate`/`TaskResponse` with `extra="forbid"` (unknown fields → 422) and a `title` validator (strips whitespace, rejects blank, caps at 200 chars). `main.py` handlers are thin — they delegate straight to `storage` and only add the transition check and 404s.

**Known dead/stale code — do not treat as the source of truth:**
- `backend/app/schemas.py` defines its own `TaskCreate`/`TaskUpdate`/`TaskRead` importing `Priority`/`Status` from `app.models`, but `app/models.py` actually defines `TaskPriority`/`TaskStatus`. This module is unused (nothing imports it) and would fail if imported. The real schemas are in `app/models.py`.
- `backend/app/routes/tasks.py` defines an empty, unmounted `APIRouter` — all task endpoints are actually declared directly on `app` in `main.py`, not via this router.
- `README.md` describes an earlier project stage (JSON file persistence, no CRUD yet) that has been superseded by the current in-memory-only, fully-CRUD implementation — don't rely on the README for current behavior.

**Frontend structure (`frontend/index.html`, single file):** rendering (`renderBoard`, `createColumn`, `createTaskCard`), drag-and-drop handlers (`handleTaskCardDragStart/End`, `handleBoardColumnDragOver/Leave/Drop`) that PATCH status on drop, and a create/edit modal (`openTaskModal`/`closeTaskModal`) that PATCHes/POSTs task fields and surfaces 422 errors inline via `getErrorMessage`/`getFieldErrors`. When editing a task through the modal, only send fields that actually changed — sending back the unchanged `status` on an edit is what previously caused spurious 422s from the transition check above.

**Testing conventions:** `backend/tests/conftest.py` provides a `client` fixture (`TestClient(app)`) and an autouse fixture that calls `storage._reset()` before/after every test, so tests never need to manage state manually. New endpoint tests should follow the existing pattern in `test_tasks.py` (one behavior per test, named `test_<verb>_<condition>_returns_<code>`).
