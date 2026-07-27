## Baseline Check

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 20 items

tests/test_tasks.py ....................                                 [100%]

============================== 20 passed in 0.13s ==============================
```

# Feature 1

## pytest Tests
Add 6 additional pytest tests.

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 26 items

tests/test_tasks.py .........................F                           [100%]

=================================== FAILURES ===================================
________________ test_list_tasks_filter_by_comments_returns_422 ________________

client = <starlette.testclient.TestClient object at 0x7d25ea6eb0a0>

    def test_list_tasks_filter_by_comments_returns_422(client: TestClient):
        # 'comments' is not a supported query parameter; sending it should yield a 422 from FastAPI
        r = client.get("/tasks", params={"comments": "something"})
>       assert r.status_code == 422
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_tasks.py:311: AssertionError
=========================== short test summary info ============================
FAILED tests/test_tasks.py::test_list_tasks_filter_by_comments_returns_422 - ...
========================= 1 failed, 25 passed in 0.25s =========================
```
One failed because 200 and an empty list of tasks was returned when using 'comments' as a query string parameter. Should have yielded a 422 HTTP error.

After fix:
```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 26 items

tests/test_tasks.py ..........................                           [100%]

============================== 26 passed in 0.19s ==============================

```

### Intentional Code Break
A line of code that normalized text in the description field of task objects when matching the text parameter was tampered with. This yielded the following results:

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src
plugins: anyio-4.14.1
collected 26 items / 25 deselected / 1 selected

backend/tests/test_tasks.py F                                            [100%]

=================================== FAILURES ===================================
_________ test_list_tasks_filter_by_text_returns_200_and_only_matches __________

client = <starlette.testclient.TestClient object at 0x7b58f2f176a0>

    def test_list_tasks_filter_by_text_returns_200_and_only_matches(client: TestClient):
        # create tasks where only one contains the text 'crash' in description
        client.post("/tasks", json={"title": "Fix bug", "description": "crash on load"})
        client.post("/tasks", json={"title": "Unrelated", "description": "nothing to see"})
        r = client.get("/tasks", params={"text": "crash"})
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)
>       assert len(data) == 1
E       assert 0 == 1
E        +  where 0 = len([])

backend/tests/test_tasks.py:188: AssertionError
=========================== short test summary info ============================
FAILED backend/tests/test_tasks.py::test_list_tasks_filter_by_text_returns_200_and_only_matches
======================= 1 failed, 25 deselected in 0.30s =======================
```
Code restored to its proper form. This resulted in the following pytest result for the single test that failed previously.

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src
plugins: anyio-4.14.1
collected 26 items / 25 deselected / 1 selected

backend/tests/test_tasks.py .                                            [100%]

======================= 1 passed, 25 deselected in 0.27s =======================
```

# Feature 2

## pytest Tests
Add 4 additional pytests for the second feature.
```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 30 items

tests/test_tasks.py ...........................FFF                       [100%]

=================================== FAILURES ===================================
___ test_list_activities_filter_by_from_to_type_returns_200_and_only_matches ___

client = <starlette.testclient.TestClient object at 0x76f2297f0e50>

    def test_list_activities_filter_by_from_to_type_returns_200_and_only_matches(client: TestClient):
        # create two tasks; capture their creation timestamps
        r1 = client.post("/tasks", json={"title": "task-a"})
        assert r1.status_code == 201
        a = r1.json()
        r2 = client.post("/tasks", json={"title": "task-b"})
        assert r2.status_code == 201
        b = r2.json()

        # cause some additional activity: update task-a and delete task-b
        client.patch(f"/tasks/{a['id']}", json={"status": TaskStatus.IN_PROGRESS.value})
        client.delete(f"/tasks/{b['id']}")

        # filter activity to only include the creation entry for task-b using exact from/to timestamps and type
        params = {"from": b["created_at"], "to": b["created_at"], "type": ActivityType.CREATE.value}
        r = client.get("/activity", params=params)
>       assert r.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_tasks.py:337: AssertionError
___ test_list_activities_filter_by_task_from_to_returns_200_and_only_matches ___

client = <starlette.testclient.TestClient object at 0x76f22946fdf0>

    def test_list_activities_filter_by_task_from_to_returns_200_and_only_matches(client: TestClient):
        # create a task and then update it to generate multiple activities for that task
        r = client.post("/tasks", json={"title": "task-x"})
        assert r.status_code == 201
        t = r.json()

        # update the task to add another activity
        r_up = client.patch(f"/tasks/{t['id']}", json={"description": "updated"})
        assert r_up.status_code == 200

        # create an unrelated task to ensure it is not returned
        client.post("/tasks", json={"title": "other"})

        params = {"task": t["id"], "from": t["created_at"], "to": r_up.json()["updated_at"]}
        r2 = client.get("/activity", params=params)
>       assert r2.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_tasks.py:361: AssertionError
_______________ test_list_activities_filter_by_start_returns_422 _______________

client = <starlette.testclient.TestClient object at 0x76f22946eec0>

    def test_list_activities_filter_by_start_returns_422(client: TestClient):
        r = client.get("/activity", params={"from": "not-a-date"})
>       assert r.status_code == 422
E       assert 200 == 422
E        +  where 200 = <Response [200 OK]>.status_code

tests/test_tasks.py:372: AssertionError
=========================== short test summary info ============================
FAILED tests/test_tasks.py::test_list_activities_filter_by_from_to_type_returns_200_and_only_matches
FAILED tests/test_tasks.py::test_list_activities_filter_by_task_from_to_returns_200_and_only_matches
FAILED tests/test_tasks.py::test_list_activities_filter_by_start_returns_422
========================= 3 failed, 27 passed in 0.35s =========================
```
Had 3 out of 4 tests failed. Changed the time query string parameters from 'from' & 'to' to 'start' and 'end' manually to fix one of the failed tests. Asked for the AI agent's help with the other problems. The agent added code to check for a terminating 'Z' character at the end of the date/time strings and replace it with '+00:00'. This took care of the other 2 pytest failures.

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 30 items

tests/test_tasks.py ..............................                       [100%]

============================== 30 passed in 0.23s ==============================
```

### Intentional Code Break
Replaced a line of code with one that returned an empty list of activity log entries except of a list of entries for a specific task whose uuid was passed in the query string.

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 30 items

tests/test_tasks.py ............................F.                       [100%]

=================================== FAILURES ===================================
___ test_list_activities_filter_by_task_from_to_returns_200_and_only_matches ___

client = <starlette.testclient.TestClient object at 0x7bce7d339d50>

    def test_list_activities_filter_by_task_from_to_returns_200_and_only_matches(client: TestClient):
        # create a task and then update it to generate multiple activities for that task
        r = client.post("/tasks", json={"title": "task-x"})
        assert r.status_code == 201
        t = r.json()

        # update the task to add another activity
        r_up = client.patch(f"/tasks/{t['id']}", json={"description": "updated"})
        assert r_up.status_code == 200

        # create an unrelated task to ensure it is not returned
        client.post("/tasks", json={"title": "other"})

        params = {"task": t["id"], "start": t["created_at"], "end": r_up.json()["updated_at"]}
        r2 = client.get("/activity", params=params)
        assert r2.status_code == 200
        data = r2.json()
        assert isinstance(data, list)
        # Should include the create and the update activity for this task
>       assert len(data) == 2
E       assert 0 == 2
E        +  where 0 = len([])

tests/test_tasks.py:366: AssertionError
=========================== short test summary info ============================
FAILED tests/test_tasks.py::test_list_activities_filter_by_task_from_to_returns_200_and_only_matches
========================= 1 failed, 29 passed in 0.14s =========================
```
Restored that particular line of code to its original proper form. This yielded these pytest results:

```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 30 items

tests/test_tasks.py ..............................                       [100%]

============================== 30 passed in 0.12s ==============================
```
# Refactoring
Before refactoring, the behavior contract was run manually with the following results:
| ID | Behavior | How to check manually | Pass/Fail notes |
|---|---|---|---|
| BC1 | Three status columns render with correct counts. | Load the board and verify that the three columns appear for To Do, In Progress, and Done, with counts matching the current task list. | Pass |
| BC2 | Cards sort by priority inside each column. | In a column with multiple cards, confirm the order is High → Medium → Low, and that cards with the same priority are ordered consistently. | Pass |
| BC3 | Loading state appears before tasks load. | Refresh the page while the backend is responding; verify a loading indicator or loading card is shown before tasks appear. | Pass |
| BC4 | Empty columns remain visible. | Create a state where one or more columns have no tasks, then confirm those columns still render and remain visible. | Pass |
| BC5 | Error state appears when the backend is stopped. | Stop the backend service and refresh the board; confirm the board shows an error state instead of silently failing. | Pass |
| BC6 | Valid drag sends PATCH and updates the board. | Drag a task to another column, then confirm the board updates immediately and the server receives a PATCH request for the task status change. | Pass |
| BC7 | Invalid drag/server 422 reverts and shows the server message. | Trigger a drag action that causes the server to reject the update (for example, a 422 response), then confirm the card returns to its original column and the server message is shown. | Pass |
| BC8 | New Task and Edit modal flows still work, including title validation and dismissal. | Open New Task, save a valid task, then open Edit for an existing task; verify validation for a missing title, and confirm the modal closes correctly on cancel or successful save. | Pass |

After refactoring, running the set of pytests had this outcome:
```
============================= test session starts ==============================
platform linux -- Python 3.10.12, pytest-9.1.1, pluggy-1.6.0
rootdir: /home/amer/Documents/Courses/AI Assisted Coding/src/backend
plugins: anyio-4.14.1
collected 30 items

tests/test_tasks.py ..............................                       [100%]

============================== 30 passed in 0.12s ==============================
```
And the behavioral contract remained respected.
| ID | Behavior | How to check manually | Pass/Fail notes |
|---|---|---|---|
| BC1 | Three status columns render with correct counts. | Load the board and verify that the three columns appear for To Do, In Progress, and Done, with counts matching the current task list. | Pass |
| BC2 | Cards sort by priority inside each column. | In a column with multiple cards, confirm the order is High → Medium → Low, and that cards with the same priority are ordered consistently. | Pass |
| BC3 | Loading state appears before tasks load. | Refresh the page while the backend is responding; verify a loading indicator or loading card is shown before tasks appear. | Pass |
| BC4 | Empty columns remain visible. | Create a state where one or more columns have no tasks, then confirm those columns still render and remain visible. | Pass |
| BC5 | Error state appears when the backend is stopped. | Stop the backend service and refresh the board; confirm the board shows an error state instead of silently failing. | Pass |
| BC6 | Valid drag sends PATCH and updates the board. | Drag a task to another column, then confirm the board updates immediately and the server receives a PATCH request for the task status change. | Pass |
| BC7 | Invalid drag/server 422 reverts and shows the server message. | Trigger a drag action that causes the server to reject the update (for example, a 422 response), then confirm the card returns to its original column and the server message is shown. | Pass |
| BC8 | New Task and Edit modal flows still work, including title validation and dismissal. | Open New Task, save a valid task, then open Edit for an existing task; verify validation for a missing title, and confirm the modal closes correctly on cancel or successful save. | Pass |

# Manual Web Browser Testing

Testing was run at different intervals to check how the frontend changes introduced by the Copilot AI agent are working. Filtering tasks seems to be working fine after very minor amendments to the names of query string parameters.

Filtering activity log entries are still having serious problems when specifying date/time values. There seems to be problems parsing ISO8601 format date/time values when passed on from the browser.

Another serious problem that was observed was that modifying a task's data using the modal box and changing several fields including the status should generate 2 activity log entries; one of the "status-update" type and another with the "update" type. Only one is being generated. The "status-update" record could be overwritten by the second. This has to be investigated further when time permits.