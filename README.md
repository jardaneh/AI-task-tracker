# Task Tracker API (Module 4)

A FastAPI backend and vanilla-JS Kanban frontend for tracking tasks
(create/read/update/delete, with status moved between `ToDo`, `InProgress`,
and `Done` columns). Built as a learning project; storage is in-memory only
and the app is not intended for production use.

[VERIFY]: `backend/app/main.py` still sets the FastAPI `description` to
"Module 1 Task Tracker API - skeleton project" — the in-code string hasn't
been updated to match the current module number.

## Prerequisites

- Python **3.10.12** (matches `venv`, `Dockerfile`, and
  `.github/workflows/ci.yml`). [VERIFY]: confirm whether the course expects
  3.11 instead — not stated in `requirements.txt` or elsewhere in the repo.
- `pip`
- A way to serve static files for the frontend, e.g. Python's built-in
  `http.server` (used below).
- Docker, only if you want to run the containerized backend (optional).

## Local setup

Run from the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optionally copy the example env file:

```bash
cp .env.example .env
```

[VERIFY]: `.env.example` defines `PORT=8000`, but `app/main.py` only reads
`APP_ENV` via `os.getenv` — `PORT` does not appear to be wired to anything
(the run command below hardcodes `--port 8000`). Confirm whether `PORT` is
meant to be consumed somewhere, or should be removed from `.env.example`.

## Run the app locally

The FastAPI app lives at `backend/app/main.py`, so `uvicorn` is run from
inside `backend/`:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Swagger / interactive API docs: http://localhost:8000/docs

Health check:

```bash
curl http://localhost:8000/health
```

### Run the frontend

The frontend is a single static file. CORS in `app/main.py` only allows
`http://localhost:8080` and `http://127.0.0.1:8080`, so it must be served
from one of those origins — opening `index.html` directly (`file://`) will
be blocked by the browser.

```bash
cd frontend
python3 -m http.server 8080
```

Then open http://localhost:8080 in a browser, with the backend from the
previous step still running.

## Run tests

From the repository root:

```bash
cd backend
pytest -v
```

Single test:

```bash
pytest -v tests/test_tasks.py::test_patch_valid_transition_todo_to_inprogress_returns_200
```

There is also a standalone script (not part of the pytest suite) that
exercises `TaskCreate`/`TaskUpdate` validation directly and prints PASS/FAIL
lines. Run it from the repository root:

```bash
python -m tests.verify_a
```

## Run with Docker

The `Dockerfile` lives at the repository root and expects to be built with
the repo root as build context (it copies `backend/app` into the image), so
build and run from the repository root:

```bash
docker build -t task-tracker-api .
docker run --rm -p 8000:8000 task-tracker-api
```

```bash
curl http://localhost:8000/health
```

Notes:
- The image packages the backend only (`backend/app`) — the frontend and
  test suite are not included and are not started by the container.
- Storage is in-memory, so all data is lost when the container stops or
  restarts.
- The image runs as a non-root `app` user and defines a container
  `HEALTHCHECK` against `/health`.

## CI workflow summary

`.github/workflows/ci.yml` runs on every `push` and `pull_request`:

1. Checks out the repository.
2. Sets up Python 3.10.12.
3. Installs dependencies from `requirements.txt`.
4. Runs `pytest -v` with `backend` as the working directory.

There is no linting step, no Docker image build/push, and no deployment
step in this workflow.

## Project structure

```
backend/
  app/
    main.py           # FastAPI app instance, CORS config, route handlers
    models.py          # TaskStatus/TaskPriority enums, TaskCreate/TaskUpdate/TaskResponse models
    business_rules.py  # validate_status_transition, VALID_TRANSITIONS
    storage.py          # in-memory task store (dict), no DB, no file persistence
    utils.py             # trim_title helper
    schemas.py            # stale/unused — imports names that no longer exist in models.py
    routes/
      tasks.py            # stale/unused — empty APIRouter, never mounted on app
    static/                # reserved, currently empty (.gitkeep only)
  tests/
    conftest.py         # TestClient fixture, autouse storage._reset() between tests
    test_tasks.py         # endpoint tests
frontend/
  index.html           # single-file vanilla JS/HTML Kanban board (no framework, no build step)
tests/
  verify_a.py          # standalone schema-validation script, not part of the pytest suite
Dockerfile
.dockerignore
requirements.txt
.env.example
CLAUDE.md
README.md
```

## Project conventions and current limitations

- **Storage**: in-memory only (`backend/app/storage.py`), no database, no
  file persistence. All data is lost on restart. Tests reset storage
  automatically between runs via an autouse fixture in `conftest.py`.
- **Status transitions**: only `ToDo → InProgress`, `InProgress → Done`, and
  `Done → InProgress` are allowed (`business_rules.VALID_TRANSITIONS`). Any
  other transition, including sending back the same status or `ToDo → Done`
  directly, returns `422` from `PATCH /tasks/{id}`.
- **Validation**: task titles are required, whitespace-stripped, cannot be
  blank after stripping, and are capped at 200 characters. All request
  models use `extra="forbid"`, so unknown fields in a request body return
  `422`.
- **CORS**: locked to `http://localhost:8080` and `http://127.0.0.1:8080`.
  Serve the frontend from one of these origins or requests will be blocked
  by the browser.
- **Dead code**: `backend/app/schemas.py` and `backend/app/routes/tasks.py`
  are not imported or mounted anywhere; `main.py` and `models.py` are the
  source of truth for routes and data models.
- **Not implemented** (by design, not oversight): authentication/
  authorization, a database or persistence layer, deployment
  infrastructure, and no production-readiness guarantees are made or
  intended at this stage.

## Technical notes / decisions

[Technical Note](../Module4/Video6/TechNote.md)
