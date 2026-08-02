# Task Tracker API (Module 1)

A minimal FastAPI backend skeleton for a Task Tracker application, built as
part of a learning project. This stage of the project only includes the
application scaffold, folder structure, and a `/health` endpoint. CRUD
endpoints, storage logic, and the frontend will be added in later phases.

## Architecture Notes

- **Storage:** The project will use in-memory storage with JSON file
  persistence instead of a database like SQLite. This keeps the project
  dependency-free, easy to reset/seed for testing, and simple to reason
  about for a single-user, non-concurrent learning project.
- **Persistence timing:** Writes to the JSON file will occur immediately
  after each create/update/delete operation rather than on an interval,
  since the app is intended for single-user, non-concurrent use.
- **Status updates:** Task status changes are intended to be driven by
  moving cards on a Kanban-style board (not a dropdown control).
- **Production considerations (not implemented here):** A real persistent
  datastore and safeguards against race conditions/concurrent writes would
  be required before this design could be used in a multi-user or
  production setting.

## Project Structure

backend/
  app/
    main.py           # FastAPI app instance, /health endpoint
    routes/
      tasks.py         # Placeholder router for future task CRUD endpoints
    schemas.py          # Pydantic schemas (TaskCreate, TaskUpdate, TaskRead)
    storage.py           # In-memory repository skeleton
    models.py            # Status/Priority enums
    utils.py              # Validation helpers
    static/                # Reserved for future frontend files
README.md
requirements.txt
.env.example
.gitignore

## Setup Instructions

1. Clone or copy this project to your local machine.
2. Create a virtual environment and install dependencies (see commands below).
3. Copy `.env.example` to `.env` and adjust values if needed.
4. Run the development server.

### Create virtual environment and install dependencies

**Linux / macOS:**

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt


**Windows (PowerShell):**

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt


### Run the server

The FastAPI app lives at `backend/app/main.py`, so run uvicorn from inside
the `backend/` directory:

cd backend
uvicorn app.main:app --reload --port 8000


## Testing the Health Endpoint

With the server running, test it with curl:

curl http://localhost:8000/health


Expected response shape:

{
  "status": "ok",
  "timestamp": "2025-01-01T12:00:00.000000+00:00"
}


## Swagger / Interactive API Docs

Once the server is running, open the following URL in your browser:

http://localhost:8000/docs


## Running the frontend

```bash
source venv/bin/activate
cd frontend
python3 -m http.server 8080
```

Once the Python HTTP server is running under the frontend directory, open the following URL in your browser:

http://localhost:8080/index.html


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


### Evidence files
- docs/release-evidence.md
- docs/final-ai-review.md
- docs/ai-playbook.md

### AI assistance summary
AI helped draft or review: docs.
I verified the work by: manual scan.
One AI suggestion I rejected or corrected: [brief note].
