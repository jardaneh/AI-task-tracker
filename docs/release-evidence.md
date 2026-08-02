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
- Run command:
- /health check:
- Non-root check, if implemented:
- No-baked-secrets check:

## Documentation claim-vs-reality log
| Claim checked | Evidence used | Result | Change made, if any |