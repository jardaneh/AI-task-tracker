# Task Tracker

A minimal FastAPI + vanilla JavaScript Task Tracker application, built as a
learning project for the "AI Assisted Coding" course. It exposes
a REST API for creating, updating, and deleting tasks on a Kanban-style
board (`ToDo` / `InProgress` / `Done`), plus an activity log of task
changes. The app is intentionally single-user and non-concurrent — see
[Project Conventions and Current Limitations](#project-conventions-and-current-limitations)
for what is deliberately out of scope.

## Prerequisites

- Python 3.10.12 (matches the interpreter pinned in `Dockerfile` and
  `.github/workflows/ci.yml`)
- pip
- Docker, only if you want to run the containerized build (see
  [Run with Docker](#run-with-docker))
- A modern web browser, to use the frontend

## Local Setup

Run from the repo root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Windows PowerShell: replace the second line with `.\venv\Scripts\Activate.ps1`.

`.env` currently sets `APP_ENV=development` and `PORT=8000`. `[VERIFY]`
`PORT` is not read anywhere in `backend/app/main.py` — the actual listen
port is set by the `--port` flag on the `uvicorn` command below, not by
this variable.

## Run the App Locally

Backend, from the repo root:

```bash
source venv/bin/activate
cd backend
uvicorn app.main:app --reload --port 8000
```

Check it's up:

```bash
curl http://localhost:8000/health
```

Interactive API docs: http://localhost:8000/docs

Frontend, in a separate terminal, also from the repo root:

```bash
cd frontend
python3 -m http.server 8080
```

Open http://localhost:8080/index.html. The frontend calls the backend at
`http://localhost:8000`; CORS in `backend/app/main.py` only allows
`http://localhost:8080` and `http://127.0.0.1:8080`, so serving the
frontend from any other origin will be blocked by the browser.

## Run Tests

From the repo root:

```bash
source venv/bin/activate
cd backend
pytest -v
```

Tests must be run with `backend/` as the working directory: there is no
root `conftest.py` or `pyproject.toml`, and `backend/tests/__init__.py` is
what makes pytest resolve the `app` package. Every test resets the
in-memory store automatically via the autouse fixture in
`backend/tests/conftest.py`.

## Run with Docker

From the repo root:

```bash
docker build -t task-tracker .
docker run --rm -p 8000:8000 --name task-tracker task-tracker
```

Check it's up:

```bash
curl http://localhost:8000/health
```

Stop it:

```bash
docker stop task-tracker
```

Notes, read from `Dockerfile`:
- Base image is `python:3.10.12-slim`, built in two stages (install
  dependencies, then copy into a minimal runtime image).
- The container runs as a non-root `app` user and has a built-in
  `HEALTHCHECK` against `/health`.
- Only `backend/app` is copied into the image — the container serves the
  API only. `frontend/`, `tests/`, and `docs/` are not included and are not
  needed to run it.
- `[VERIFY]` these commands are derived directly from `Dockerfile`; they
  were not executed in this session to confirm the image builds and
  `/health` responds. A prior manual verification is recorded in
  [`docs/release-evidence.md`](docs/release-evidence.md) and in the
  [Final Project](#final-project) section below.

This project does not include deployment, orchestration, or
production-hosting configuration — the Docker image is for local use only.

## CI Workflow Summary

[`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on every `push`
and `pull_request`:

1. Checks out the repository (`actions/checkout@v4`).
2. Sets up Python, pinned to `3.10.12` (`actions/setup-python@v5`) — not
   `latest` or an unspecified version.
3. Installs dependencies with `python -m pip install --upgrade pip` and
   `pip install -r requirements.txt`.
4. Runs `pytest -v` with `working-directory: backend`.

There is no deployment step, and no `continue-on-error`, `|| true`, or
output-suppressing step — a failing test fails the workflow.

## Project Structure

```
backend/
  app/
    main.py           # FastAPI app instance and all live route handlers (/health, /tasks*, /activity)
    models.py          # Pydantic models/enums: TaskStatus, TaskPriority, TaskCreate, TaskUpdate, TaskResponse, Activity, ActivityType
    business_rules.py  # validate_status_transition — the allowed Kanban status graph
    storage.py          # In-memory task store + activity log (module-level dict, no persistence)
    utils.py             # Small helpers (trim_title; currently unused — see limitations)
    routes/tasks.py       # Unused APIRouter skeleton, not mounted on the app
    schemas.py             # Older, unused TaskCreate/TaskUpdate/TaskRead models (dead code)
    static/                 # Reserved, currently empty
  tests/
    conftest.py          # Shared fixtures; autouse in-memory storage reset
    test_tasks.py          # pytest suite for /tasks and /activity
frontend/
  index.html             # Self-contained Kanban board + activity-log modal (HTML/CSS/JS, no build step)
docs/
  midcourse/              # ADRs, user stories, prompt log, reflection from an earlier course milestone
  release-evidence.md       # Manual verification notes (local run, tests, Docker, CI)
tests/
  verify_a.py               # Standalone ad-hoc validation script, not part of the pytest suite
Dockerfile                  # Two-stage build, non-root runtime user, built-in HEALTHCHECK
.dockerignore
.github/workflows/ci.yml    # CI: checkout, setup Python 3.10.12, install deps, pytest -v
requirements.txt
.env.example
CLAUDE.md                   # Guidance for AI coding agents working in this repo
README.md
```

## Project Conventions and Current Limitations

- **In-memory storage only.** All tasks and activity log entries live in a
  module-level dict in `backend/app/storage.py`. Restarting the server or
  container clears all data. `[VERIFY]` an earlier draft of this README
  described planned JSON-file persistence; reading `storage.py` confirms
  that was never implemented — there is no file I/O of any kind here.
- **No authentication.** Every endpoint is open; this app is not meant to
  be exposed beyond local/trusted use.
- **No production deployment.** The Dockerfile produces a runnable local
  image, but there is no orchestration, TLS, secrets management, or
  scaling story — do not treat this as production-ready.
- **Single-user, non-concurrent design.** Task status transitions and
  activity logging assume one user at a time; there are no safeguards
  against concurrent writes.
- **Status transitions are restricted**, enforced in
  `backend/app/business_rules.py`: only `ToDo → InProgress`,
  `InProgress → Done`, and `Done → InProgress` are allowed. Status changes
  are meant to be driven by moving cards on the board, not a free dropdown.
- **CORS is restricted** to `http://localhost:8080` and
  `http://127.0.0.1:8080` in `backend/app/main.py` — update it if you serve
  the frontend elsewhere.
- **Some files are dead code**: `backend/app/schemas.py` and
  `backend/app/routes/tasks.py` are leftovers from early scaffolding and
  are not imported or mounted anywhere live. Furthermore, `backend/app/schemas.py`
  can cause an ImportError if it is ever imported from. It import types that
  are not found in the file it is imported from.
- See [`CLAUDE.md`](CLAUDE.md) for a fuller architecture map, aimed at AI
  coding agents working in this repo.

## Related Docs

- [`docs/midcourse/mini-adr.md`](docs/midcourse/mini-adr.md) — architecture
  decision records for this project (e.g. assignee search design, activity
  log data structure). This repo has no separate `docs/decisions/` folder;
  `mini-adr.md` is the closest equivalent.
- [`docs/midcourse/user-stories.md`](docs/midcourse/user-stories.md),
  [`docs/midcourse/prompt-log.md`](docs/midcourse/prompt-log.md),
  [`docs/midcourse/reflection.md`](docs/midcourse/reflection.md),
  [`docs/midcourse/verification.md`](docs/midcourse/verification.md) —
  supporting notes from an earlier course milestone.
- [`docs/release-evidence.md`](docs/release-evidence.md) — manual
  verification log for this branch (local run, tests, Docker, CI).

## Final Project
Branch reviewed: final-project

### What this submission demonstrates
- Existing Task Tracker app still runs inside the intended course scope.
- CI runs the pytest suite on push and/or pull request.
- Docker image builds and runs with /health returning 200.
- AI review, security, and ownership evidence is in docs/.

### How to run locally
```bash
source venv/bin/activate
cd backend
uvicorn app.form:app
```

### How to run tests
```bash
source venv/bin/activate
cd backend
pytest tests/
```

### How to run with Docker
```bash
docker build -t task-tracker:prod .
docker run -d --name tt-prod -p 8000:8000 task-tracker:prod
```
To stop and remove the docker image
```bash
docker rm -f tt-prod
```

### Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary
AI helped draft or review: docs.
I verified the work by: manual scan.
One AI suggestion I rejected or corrected: [brief note].
