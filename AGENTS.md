# AGENTS.md

## Project summary

This repository is a learning-oriented task tracker with:

- A FastAPI REST API in `backend/app/main.py`.
- A vanilla HTML/JavaScript Kanban frontend in `frontend/index.html`.
- In-memory task storage in `backend/app/storage.py`; there is no database or file persistence, so data is lost on restart.
- Automated API tests in `backend/tests/` and a standalone model-validation script in `tests/verify_a.py`.

The repository’s module identity is not confirmed: `README.md` describes it as “Module 4,” while the FastAPI description in `backend/app/main.py` still says “Module 1.” Treat the requested Module 5 workflow guardrails below as repository operating rules, not as a claim about the application’s internal module number.

## Tech stack and supported commands

### Stack

- Python 3.10.12 is specified by the README, Dockerfile, and CI workflow.
- FastAPI `0.115.0`
- Uvicorn `0.30.6`
- Pydantic `2.9.2`
- `python-dotenv` `1.0.1`
- pytest `9.1.1`
- httpx `0.28.1`
- Frontend: static HTML and vanilla JavaScript; no frontend build step is confirmed.
- Persistence: in-memory Python dictionary only.

Dependencies and versions are defined in `requirements.txt`.

### Local setup

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Python 3.11 is not confirmed by the repository; use Python 3.10.12 unless the project owner states otherwise.

### Run the backend

From the repository root:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API exposes interactive docs at `http://localhost:8000/docs` and a health endpoint at `http://localhost:8000/health`.

### Run the frontend

In a separate shell:

```bash
cd frontend
python3 -m http.server 8080
```

Use `http://localhost:8080` or `http://127.0.0.1:8080`. Opening `frontend/index.html` directly with `file://` is not supported by the configured CORS policy.

### Run tests

From the repository root:

```bash
cd backend
pytest -v
```

Single test:

```bash
cd backend
pytest -v tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200
```

Standalone validation script:

```bash
python -m tests.verify_a
```

The standalone script is not part of the pytest suite.

### Docker

The repository supports the documented container flow:

```bash
docker build -t task-tracker-api .
docker run --rm -p 8000:8000 task-tracker-api
```

The image runs the backend only. Frontend serving, deployment, linting, and production operation are not confirmed as supported.

## Visible business rules

Rules below are based on `backend/app/models.py`, `backend/app/business_rules.py`, `backend/app/main.py`, `backend/app/storage.py`, and `backend/tests/test_tasks.py`.

### Task fields and defaults

- `title` is required.
- Titles are trimmed, cannot be blank after trimming, and must be at most 200 characters.
- On creation, `status` defaults to `ToDo`.
- On creation, `priority` defaults to `Medium`.
- On creation, `description` defaults to an empty string.
- `assignee` defaults to `null`.
- Unknown request fields are rejected because request models use Pydantic `extra="forbid"`.
- Valid statuses are `ToDo`, `InProgress`, and `Done`.
- Valid priorities are `Low`, `Medium`, and `High`.
- Task IDs are generated as UUID strings; `created_at` and `updated_at` use current UTC timestamps.
- Updates are partial: only explicitly supplied fields are applied, and an empty JSON object leaves the task unchanged.
- A successful update refreshes `updated_at`.
- Explicit `null` update behavior for optional fields is not fully confirmed by the current storage implementation; verify before relying on it.

### Status transitions

The only allowed transitions are:

- `ToDo -> InProgress`
- `InProgress -> Done`
- `Done -> InProgress`

Same-status transitions and all other transitions, including `ToDo -> Done`, return HTTP `422`.

### API behavior

- `POST /tasks` creates a task and returns `201`.
- `GET /tasks` returns `200` and supports optional exact-match `status` and `priority` filters; both filters combine with AND.
- `GET /tasks/{task_id}` returns `200`, or `404` when missing.
- `PATCH /tasks/{task_id}` returns `200`, or `404` when missing; invalid request data or status transitions return `422`.
- `DELETE /tasks/{task_id}` returns `204` with no body, or `404` when missing.
- CORS allows `http://localhost:8080` and `http://127.0.0.1:8080`, with credentials, all methods, and all headers as configured in `backend/app/main.py`.

## Module 5 operating guardrails

- Docs-first: read the relevant repository documentation and source before proposing or making changes. Cite the files that support conclusions.
- Read-only by default: inspect, explain, and report unless a write is explicitly requested and within scope.
- One task per thread: keep each Codex task focused on one repository task; call out scope changes before proceeding.
- No `app/` changes unless explicitly approved. In this repository, treat `backend/app/` as the application directory and do not modify it without explicit approval.
- Preserve the repository’s existing behavior unless the task explicitly authorizes a behavior change.
- When a requested command, rule, or workflow is not visible in the repository, label it “not confirmed” rather than inventing it.

## Security and governance

- Never paste, print, commit, or expose secrets, tokens, credentials, or private environment values. Treat `.env` as sensitive; use `.env.example` only as a non-secret reference.
- Do not run destructive commands or irreversible operations. Do not delete, reset, overwrite, or mass-move files unless explicitly approved and the exact scope is verified.
- Cite repository files for claims, especially when describing behavior, commands, validation, or test coverage.
- Do not invent findings, supported commands, business rules, dependencies, or test results. Distinguish confirmed behavior from assumptions and items to verify.
- Keep changes limited to the requested scope and inspect the resulting diff before handoff.
