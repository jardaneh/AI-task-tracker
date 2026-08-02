# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

A minimal FastAPI + vanilla JS Task Tracker app built as a learning project ("AI Assisted Coding" course, Module 4). Single-user, non-concurrent by design — there is no database and no authentication.

## 1. Tech stack

Pinned in `requirements.txt`:
- FastAPI 0.115.0
- Uvicorn 0.30.6 (`uvicorn[standard]`)
- Pydantic 2.9.2 (v2)
- python-dotenv 1.0.1
- pytest 9.1.1
- httpx 0.28.1 (used by FastAPI's `TestClient`)

Python: 3.10.12 (confirmed from the project venv interpreter; no `.python-version`/`runtime.txt` pins this in the repo).

Frontend: vanilla JavaScript, HTML, and CSS — no framework, no build step, no `package.json` (`frontend/index.html`).

## 2. Run command

Always run uvicorn from inside `backend/` (the app object is `backend/app/main.py`):
```bash
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

## 3. Test command

Always run pytest from inside `backend/`:
```bash
source venv/bin/activate
cd backend
pytest -v
```
There is no root `conftest.py` or `pyproject.toml`; `app` resolves because `backend/tests/__init__.py` makes pytest insert `backend/` onto `sys.path`. Every test gets a fresh in-memory store via the autouse `_reset_storage` fixture in `backend/tests/conftest.py` (`storage._reset()`) — don't rely on state persisting between tests.

Run a single test:
```bash
cd backend
pytest -v tests/test_tasks.py::test_patch_invalid_transition_todo_to_done_returns_422
```

Note: `tests/verify_a.py` at the repo root is a standalone ad-hoc verification script (imports via `backend.app.models`, prints PASS/FAIL) meant to be run directly with `python tests/verify_a.py` from the repo root — it is not part of the pytest suite and isn't collected by `pytest -v`.

## 4. Architecture summary

Request flow: `main.py` (routes) → `business_rules.py` (status-transition validation) → `storage.py` (in-memory repository + activity log) → `models.py` (Pydantic schemas/enums).

**Backend** (`backend/app/`):
- `main.py` — all live route handlers (`/health`, `/tasks*`, `/activity`) are defined directly on the `FastAPI` app, not via an `APIRouter`. Query-parameter validation is manual: each list endpoint checks `request.query_params.keys()` against an `allowed` set and raises 422 for anything unrecognized.
- `models.py` — the real domain models: `TaskStatus`, `TaskPriority`, `TaskCreate`, `TaskUpdate`, `TaskResponse`, `ActivityType`, `Activity`. All use `model_config = ConfigDict(extra="forbid")`, so unknown JSON fields in requests produce a 422 automatically. **This is where task field rules (status/priority enums, title validation) live.**
- `business_rules.py` — `validate_status_transition` enforces the allowed status graph (see Business Rules below). **This is where status-transition rules live.**
- `storage.py` — the entire persistence layer: a module-level `dict[str, TaskResponse]` for tasks, plus two activity-log indexes (`_activities_by_timestamp` global, `_activities_by_task` per-task), per ADR-003 (`docs/midcourse/mini-adr.md`). `_reset()` clears all state and exists purely for test isolation. Persistence is in-memory only — restarting the server loses all data.
- `routes/tasks.py` — an unused `APIRouter` skeleton from early scaffolding, not mounted on `app`. Don't assume routes defined here take effect.
- `schemas.py` — a second, older set of `TaskCreate`/`TaskUpdate`/`TaskRead` models importing `Priority`/`Status` names that no longer exist in `models.py`. Dead code, not imported anywhere live.
- `utils.py` — small helpers (e.g. `trim_title`).

**Frontend** (`frontend/`):
- `index.html` — a single self-contained file (~1500 lines: HTML/CSS/JS inline) implementing a Kanban board plus an activity-log modal. Edit directly and reload the browser.

**Tests** (`backend/tests/`):
- `conftest.py` — `client` and `created_task` fixtures, autouse storage reset.
- `test_tasks.py` — the full pytest suite for tasks and activity endpoints.

**Docs**: `docs/midcourse/` contains this project's ADRs, user stories, and prompt log — check `mini-adr.md` before changing filtering, activity-log, or status-transition behavior, since those designs were deliberate documented trade-offs rather than defaults.

## 5. Business rules

Task fields and values, as implemented in `models.py`:
- `status`: `TaskStatus` enum — `ToDo`, `InProgress`, `Done`.
- `priority`: `TaskPriority` enum — `Low`, `Medium`, `High`.
- `title`: required, trimmed, 1–200 characters (blank/whitespace-only rejected).
- `assignee`: free text, no fixed list (ADR-002).
- `id`, `created_at`, `updated_at`: server-assigned, not client-settable.

Status transition rules, as implemented in `business_rules.py` (`VALID_TRANSITIONS`) — this is the exact and complete set:
| From | To | Allowed? |
|---|---|---|
| ToDo | InProgress | ✅ |
| InProgress | Done | ✅ |
| Done | InProgress | ✅ |
| ToDo | Done | ❌ (no skipping) |
| InProgress | ToDo | ❌ |
| Done | ToDo | ❌ |
| any status | itself | ❌ (same-status "transition" is rejected, not a no-op) |

Any transition not in the table raises `HTTPException(422)` with the allowed-transitions list in the detail message. Status changes are intended to be driven by moving cards on the Kanban board, not a dropdown.

`GET /tasks` filters (`status`, `priority`, `text`, `assignee`) are optional and combine with AND. `text`/`assignee` matching normalizes both sides (lowercase, strip, drop non-alphanumerics) and does substring matching, not exact match.

`GET /activity` filters on `task`, `start`, `end` (ISO8601, `Z` suffix accepted), `type`; returns entries most-recent-first.

## 6. UI states and CORS notes

Frontend board state machine (`boardDisplayState` in `frontend/index.html`) has exactly four values:
- `loading` — initial state, renders a "Loading tasks…" placeholder.
- `ready` — tasks loaded successfully (set when `loadedTasks.length > 0`).
- `empty` — load succeeded but returned zero tasks.
- `error` — the tasks fetch failed.

The activity-log modal has its own loading/empty/error row rendering (`.activity-empty-state` CSS class), shown while fetching, when no entries match the filters, or when the fetch fails.

CORS (`CORSMiddleware` in `backend/app/main.py`) allows only:
- `http://localhost:8080`
- `http://127.0.0.1:8080`

If you serve the frontend on a different host/port, requests will be blocked by the browser until this allow-list is updated.

## 7. Do-not rules

Do not do any of the following without asking first:
- Add authentication or user accounts.
- Add a database or any persistence beyond the current in-memory store.
- Add deployment steps, CI/CD config, or containerization (Docker, etc.).
- Make major UI changes to `frontend/index.html` (new pages, redesigns, new frameworks/build tooling).
