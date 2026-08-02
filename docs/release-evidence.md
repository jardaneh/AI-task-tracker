# Release Evidence

## Baseline
- Branch: final-project
- Date: 8/2/2026
- Local app run command:
  ```bash
  source venv/bin/activate
  cd backend
  uvicorn app.main:app
  ```
- /health result:
  ```json
  {"status":"ok","timestamp":"2026-08-02T15:25:01.137666+00:00"}
  ```
- Frontend check:
  - Kanban board renders correctly.
  - Task creation/edit cycle appears functional.
- Test command:
  ```bash
  source venv/bin/activate
  cd backend
  pytest tests/
  ```
- Test result:
  ```
  ============================= test session starts ==============================
  platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
  rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
  plugins: anyio-4.14.1
  collected 30 items

  tests/test_tasks.py ..............................                       [100%]

  ============================== 30 passed in 0.15s ==============================
  ```


## CI evidence
- Workflow file: [ci.yml](../.github/workflows/ci.yml)
- Broken run link: [Red Workflow](https://github.com/jardaneh/AI-task-tracker/actions/runs/30757328509)
- Latest run link or note: [Green Workflow](https://github.com/jardaneh/AI-task-tracker/actions/runs/30757451473)
- Test command used by CI:
```bash
cd backend
pytest -v
```
- Shortcut check: no continue-on-error / no || true / pytest is not skipped.

## Docker evidence
- Build command:
  ```bash
  docker build -t task-tracker:prod .
  ```
- Run command:
  ```bash
  docker run -d --name tt-prod -p 8000:8000 task-tracker:prod
  ```
- /health check:
  ```bash
  curl -i http://localhost:8000/health
  ```
  This should print the following to the console:
  ```
  HTTP/1.1 200 OK
  date: Sun, 02 Aug 2026 18:00:55 GMT
  server: uvicorn
  content-length: 62
  content-type: application/json

  {"status":"ok","timestamp":"2026-08-02T18:00:55.269100+00:00"}
  ```
- Non-root check, if implemented:
  ```bash
  docker exec tt-prod whoami
  ```
  Should print **app** and not any user such as **root**
- No-baked-secrets check:
  ```bash
  printf 'FROM alpine\nWORKDIR /ctx\nCOPY . .\nCMD ["sh","-c","find /ctx -maxdepth 3"]\n' | docker build -q -t context-check -f - .
  docker run --rm context-check | grep -E '\.env$|\.env\.|/\.git|venv/|__pycache__|\.pytest_cache|\.mypy_cache|\.ruff_cache'
  docker rmi context-check
  grep -n '^COPY' Dockerfile
  ```
  The grep in the second line should come up empty
  The grep in the fourth line should NOT come up with anything other than:
  - requirements.txt
  - /opt/venv
  - backend/app

## Documentation claim-vs-reality log
| Claim checked | Evidence used | Result | Change made, if any |
|---|---|---|---|
| allowed status transitions are ToDo→InProgress, InProgress→Done, InProgress→ToDo | PATCH a task from Done to InProgress → 200; from InProgress to ToDo → 422 ("Allowed transitions: ['Done->InProgress', 'InProgress->Done',  'ToDo->InProgress']") | False | Fix the documentation in README.md, CLAUDE.md & the docstring for the validate_status_transition function |
| README frames this as a mature "Module 4" project with full CRUD operations for tasks | The openapi.json info block I pulled (title, description, version) metions a "Module 1" | False | Update the FastAPI constructor and the README.md file. |
| README describes backend/app/schemas.py as "Older, unused TaskCreate/TaskUpdate/TaskRead models (dead code)." | It is worst than "unused"; the module would raise ImportError if anything ever tried to import it because it imports definitions that do not exist in models.py | Inaccurate | Modify the README file to make it clear that it would be catastrophic to import from the schemas.py file. |