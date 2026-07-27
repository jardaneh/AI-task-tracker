# Feature 1

## Weak Prompt for ADR Review

Please review the following ADR:

ADR-002: Assignee Data Source and Task Filter Validation

Context:
A new feature is to be added to the Python/FastAPI Task Tracker application that allows users to search for tasks that contains a fragment of text in their title/details, of a specific priority, of a specific status or with a particular assignee. The priority and status values for tasks are clearly defined in a finite set of values that can be specified using fixed dropdown lists. The fragment of text in the title/details field of tasks can be free text.
When specifying text for the assignee field or criteria for a task search operation, one can have the system maintain a list of assignees that different tasks have been assigned to and find an exact match for any text supplied. An alternative approach would be to have the assignee field accept any free text which would be normalized to lower case, trimmed for whitespace and matched as a substring of any defined assignees. Yet another alternative is a mix of both and add autocomplete functionality where values extracted from a compiled list of assignees is provided as suggestions depending on a few characters entered manually.

Decision:
Go with the free text approach with no compilation of assignee list and no autocomplete functionality.

This is clearly the less demanding in terms of coding effort. It will avoid hiding search results due to assignee misspellings. No need to maintain a list of assignees or introduce amendments to the task creation and update code to place new assignees in the list. And no need for working on a dropdown list in the frontend or any autocomplete functionality. And as it most likely only encounter small datasets, especially during testing, the cost in computer resources will remain negligible. The downsides of this approach can be overlooked as long as the dataset remains small and the application will not be used for production where data hygiene can suffer.

The other approaches are definitely more costly with respect to time, effort and computer resources. Both during implementation or testing. If the system was to be upgraded to run in production, and have mutli-user and authentication implemented, the list of assignees will most likely depend on a set of user accounts defined in the system and no compilation of a list of assignees will have to be carried out.

### Reply Summary

Quite long reply. replied by saying that the ADR was clear about the picked approach and the rationale behind it and tradeoffs considered. It pointed out a few items it liked, before listing 7 point issues, ommissions and clarifications that mainly suggested making some items less vague and discussing testing the selected approach in the ADR.
It listed some proposed amendments and made a number of implementation considerations in addition to examples of text that can be "pasted" into the ADR. A brief conclusion followed before the AI offered further help rewriting parts of the ADR or providing code fragments that may be needed in the ADR implementation.
I did not take any into consideration and immediately began working on more constrained version of the prompt.


## Enhanced Prompt for ADR Review

You are a senior software architect reviewing an ADR containing a decision on the input of text into the assignee field of a new search feature.

Context:
A new search feature is to be added to the Python/FastAPI task tracker system that allow users to search for or filter tasks depending on title/details fields, the status, the priority and the assignee.

Task:
Review this ADR authored by a software architect and check it for completeness.
It should include:
  - A decision.
  - Reasons backing the decision focusing on the following criteria:
    - Simplicity and speed of the implementation.
    - Ease of use by users in finding specific tasks assuming they may NOT know the exact spelling for the name of an assignee.
    - Testability of the assignee search as a single search criteria or combined with others.
    - Space/time demands on computer resources while handling both modes of search.
    - Scalability if the system had to be upgraded to handle a large number of tasks for a large team and in a production environment.
  - Some reasoning behind rejecting the alternatives.
  - Proper action to take if the project went into production and was employed by a large team.

Constraints:
  - Do not rewrite it.
  - Do not paraphrase it.
  - Leave out technical details such as how the text is normalized before substring matching and returned HTTP error codes.
  - Keep suggested amendments and feedback brief.

Output Format:
A table with:
- Requirement
- Present/Missing flag
- Minimal amendments

ADR:

ADR-002: Assignee Data Source and Task Filter Validation

Context:
A new feature is to be added to the Python/FastAPI Task Tracker application that allows users to search for tasks that contains a fragment of text in their title/details, of a specific priority, of a specific status or with a particular assignee. The priority and status values for tasks are clearly defined in a finite set of values that can be specified using fixed dropdown lists. The fragment of text in the title/details field of tasks can be free text.
When specifying text for the assignee field or criteria for a task search operation, one can have the system maintain a list of assignees that different tasks have been assigned to and find an exact match for any text supplied. An alternative approach would be to have the assignee field accept any free text which would be normalized to lower case, trimmed for whitespace and matched as a substring of any defined assignees. Yet another alternative is a mix of both and add autocomplete functionality where values extracted from a compiled list of assignees is provided as suggestions depending on a few characters entered manually.

Decision:
Go with the free text approach with no compilation of assignee list and no autocomplete functionality.

This is clearly the less demanding in terms of coding effort. It will avoid hiding search results due to assignee misspellings. No need to maintain a list of assignees or introduce amendments to the task creation and update code to place new assignees in the list. And no need for working on a dropdown list in the frontend or any autocomplete functionality. And as it most likely only encounter small datasets, especially during testing, the cost in computer resources will remain negligible. The downsides of this approach can be overlooked as long as the dataset remains small and the application will not be used for production where data hygiene can suffer.

The other approaches are definitely more costly with respect to time, effort and computer resources. Both during implementation or testing. If the system was to be upgraded to run in production, and have mutli-user and authentication implemented, the list of assignees will most likely depend on a set of user accounts defined in the system and no compilation of a list of assignees will have to be carried out.


### AI Reply Summary

AI Replied with a 3-column table similar to what was requested. It included the requirements listed in the prompt, whether they were mentioned in the ADR or not and minimal proposed amendments. It did increase the mentioned requirements a little in the table. I took a small number of items in the table into consideration rejecting all others.

## Request Backend Changes Prompt

You are a Python backend software engineer. Update the get_all_tasks method in @backend/app/storage.py.

Context:
- A new feature is to be added to an existing Python/FastAPI Task Tracker system.
- This new feature can be implemented by extending or upgrading an existing method that allows callers to retrieve all tasks of a specific status or specific priority or both.
- The new feature demands retrieving tasks with a partial match of a string in their title and details field and retrieving them by partially matching free text with the values in their assignee field.
- Here are some user stories for the new feature:

| ID   | Story | Acceptance Criteria | Notes / Assumptions |
|------|-------|---------------------|---------------------|
| S001 | As a team member, I want to search tasks by text in title or description so that I can quickly find tasks related to a topic or keyword. | 1. Given tasks A (title: "Deploy API"), B (description: "Fix deployment script"), and C (title: "Update docs"), when I search for "deploy" using a (GET /tasks?text=deploy) HTTP request, the API returns tasks A and B (case-insensitive, partial match) with HTTP 200 and a JSON array of matching tasks. Input text is trimmed of surrounding whitespace and case-insensitive substring matching is carried out. 2. When the text search input is empty or only whitespace, the API treats it as "no text filter" and returns all tasks (subject to any other filters supplied) with HTTP 200. 3. Searching with punctuation or special characters returns matches if the raw substring appears in title/description (no error). 4. If the request contains any unknown query parameter (not one of text, status, priority, assignee) the API responds HTTP 400 with JSON error naming the parameter. | - Text search is applied to title OR description (OR within text fields) and is case-insensitive and supports substring matches. - Frontend exposes a text input; backend endpoint example: GET /tasks?text=... . - Single-user environment; no concurrency concerns. |
| S002 | As a team member, I want to filter tasks by assignee so I can see work assigned to a specific person. | 1. Given tasks assigned to "alice" and "bob", when I filter assignee=alice the API returns only tasks whose assignee equals "alice", after trimming whitespace and case normalization, with HTTP 200. 2. When the supplied assignee does not match any task (e.g., assignee="carol"), the API returns HTTP 200 with an empty array (no results). 3. Combining assignee with another filter (e.g., status=InProgress & assignee=alice) returns tasks matching both criteria. 4. Including an unknown field in the filter will return 400 HTTP code and a JSON error naming the unknown field. | - Assignee is a free-text string; frontend may present a simple dropdown of known assignees when possible but backend accepts any string. - Matching for assignee is exact on the normalized string (trimmed, case-insensitive) or allows substring matching (to be determined). - Endpoint would be in the form GET /tasks?assignee=alice. |
| S003 | As a team member, I want to combine two or more search criteria (text, priority, status, assignee) so that I can precisely narrow down the task list. | 1. Given tasks A..N with varying fields, when the client calls GET /tasks?text=payment&priority=High&status=ToDo&assignee=bob the API responds with HTTP 200 and a JSON array containing only tasks that match all provided filters (each task must match text AND priority AND status AND assignee). If there are no tasks matching the specified filter, HTTP 200 should still be returned with an empty list. 2. Given a request containing an invalid status value (e.g., GET /tasks?status=Waiting), the API responds with HTTP 422 and a JSON body with the {"error":"invalid status"} and the invalid value supplied. 3. Given a request that includes any unknown query parameter outside the allowed set (text, status, priority, assignee), for example GET /tasks?milestone=1, the API responds with HTTP 400 and a JSON body naming the invalid parameter, for example: {"error":"unknown query parameter: milestone"}. | - Multiple filters are combined with logical AND (a task must match every supplied filter). - Status allowed values: ToDo, InProgress, Done; backend validates status similarly to priority and returns HTTP 400 on invalid values. - Endpoint supports any subset of filters; unspecified filters are ignored. |

Task:
- Use Pydantic v2 syntax only.
- Modify the get_all_tasks method to accept 2 additional optional parameters as follows:
  - A parameter for free text to find in the title/details fields of tasks.
  - A parameter for free text to find in teh assignee field of tasks.
- Modify the code inside the method to:
  - Ensure turning the new parameters into lower-case strings, trim any whitespace at their start and end and strip any punctuation mark characters or any characters that are not alphabetic (i.e. a..z) or numbers (i.e. 0..9).
  - Check every member of the "results" list for a substring case-insensitive match of the normalized form of the first parameter with their title and details field values.
  - Check every member of the "results" list for a substring case-insensitive match of the normalized form of the second parameter with their assignee field value.

Constraints:
- DO NOT use SQLAlchemy, SQLModel, Alembic, a database, or an ORM.
- DO NOT use Pydantic v1 syntax: no @validator, no class Config, no .dict().
- DO NOT add print or logging statements.
- DO NOT create API routes in this step.
- DO NOT wrap the answer in long explanation.
- DO NOT add any additional method or functions and no new files.
- DO NOT offer anything after completing the code changes.

Output format:
Code changes to the get_all_tasks method in the @backend/app/storage.py file.

### AI Reply Summary

Modified the *get_all_tasks* function in the _storage.py_ file as requested by the prompt. Added 2 new parameters to 2 existing ones allowing the function to return tasks by _priority_, _status_, text in the _title/description_ fields or text in the _assignee_ field. Accepted all changes as they are.


## Frontend Updates Request Prompt

You are a senior web developer working on updates to an existing single webpage that interacts with a Python/FastAPI backend.

Context Files:
@frontend/index.html

- The UI includes the following:
  - 3 columns for the 3 status values showing the defined tasks under their respective status. Tasks under a specific column are ordered from the highest to lowest priority.
  - A new task button at the top right corner used to define new tasks.
  - Each task is represented with a card or box with an 'Edit' button.
  - The 'New Task' button in the top-right corner and the 'Edit' button on the cards opens a modal box populated with the tasks data or to filled with the data for a new task.
  - Task cards can be dragged and dropped over another column to quickly change their status.

Task:
- Add a box as wide as the page and over the 3 columns but under the title with the following fields and controls to filter the tasks displayed in the Kanban board:
  - Dropdown list labelled 'Status'.
  - Dropdown list labelled 'Priority'.
  - Text field labelled 'Assignee'.
  - Text field labelled 'Title/Details'.
  - A button labelled 'Clear Filter'.
  - Another button labelled 'Apply Filter'.
- The dropdown lists should be populated with the defined values for status and priority defined in the system (i.e. (ToDo, InProgress, Done) and (Low, Medium, High)). The same values should be a replica of the values in the dropdown lists for the status and priority in the existing modal box for editing tasks.
- The assignee text field should accept any text up to 50 characters long.
- The title/details text field should accept any text up to 100 characters long.
- The 'Clear Filter' button should clear the dropdown lists and text fields of any data and retrieve all tasks using the GET /tasks endpoint and render the Kanban board.
- The 'Apply Filter' button should build a query string based on the values selected or entered into the dropdown lists and text fields and pass it to the GET /tasks endpoint to retrieve tasks that fit the criteria specified by the dropdown lists and text fields and populate the Kanban board with them.
- All dropdown lists and text fields should be blank when the page is first loaded.

Constraints:
- Do not add any code outside the main frontend file that is index.html.
- Avoid using the innerHTML property and build everything using DOM.
- Keep code modifications at a minimum and try to reuse as much as possible of existing Javascript and CSS in the index.html file.
- Keep the box visible at all times and under different statuses of the page.
- Keep the height of the box at a minimum and keep its width as wide as possible; a little less than the width of the page.

Output:
HTML/CSS/Javascript in the index.html file for the new filtering box.


### AI Reply Summary

The reply consisted of HTML/CSS/Javascript updates in the index.html file as requested. All changes were accepted and none were done manually.


# Feature 2

## Help with Architecture Prompt

You are a senior backend developer helping me evaluate lightweight architectures for a learning project.

Context:
- A Task Tracker web application with a Python/FastAPI backend and a simple web frontend consisting of a single HTML file with vanilla Javascript and CSS. Uses Pydantic for data validation.
- Meant to be used by a single developer or a very small development team consisting of a few individuals.
- Tasks have the following fields defined: title, description, status, priority and assignee.
- Tasks can have 3 status values (ToDo, InProgress, Done) and 3 priority levels (Low, Medium, High).
- Implements CRUD operations for tasks whereby tasks can be:
  - Created.
  - Updated.
  - Deleted.
  - Retrieved as a whole or those under a specific status or/and a specific priority.
  - A single one retrieved by its UUID.
- Already includes endpoints to:
  - Define a new task.
  - Retrieve all tasks and optionally all tasks with a specific status or priority.
  - Retrieve a specific task by its UUID.
  - Update a specific task's data.
  - Delete a specific task.
  - Inspect the health or the status of the application.
- Intentionally left out features considered out of scope:
  - authentication
  - user accounts
  - multi-tenancy or per-user task lists
  - real-time updates
  - mobile app
  - notifications
  - production database or deployment

User Stories for new Feature:
| ID | Story | Acceptance Criteria | Notes / Assumptions |
|---|---|---|---|
| ACT-1 | As a team member, I want every task creation to produce an activity log entry so that I can see the initial values for a task and when it was created. | - After a successful task creation (POST /tasks → 201), the response body is the full task JSON and includes the task's uuid in a field named "id" and the created values for title, description, status, priority and assignee. - After the 201 response is returned, a corresponding activity entry with type = "create" exists: it includes task_uuid, timestamp, and a details object containing title, description, status, priority and assignee equal to the created values. <br>- The activity.timestamp is recorded in ISO8601 UTC and is within 5 seconds of the task creation response time. <br>- Querying activities for the new task (GET /activities?task_uuid={uuid}) returns at least one activity entry with type="create" for the newly-created task_uuid. | - Activity object shape: { id, type, task_uuid, timestamp, details } (details is JSON). <br>- Timestamps use ISO8601 UTC. <br>- Activity types include: "create", "update", "status_change", "delete". |
| ACT-2 | As a team member, I want updates to a task's non-status fields to be logged so that I can track what changed and when. |- When a task is successfully updated (PATCH/PUT /tasks/{id} → 200) and one or more non-status fields (title, description, priority, assignee) change, an activity entry with type = "update" is created for that request; the entry contains task_uuid, a timestamp in ISO8601 UTC, and a details JSON object mapping changed field names with their new values (previous values are not recorded). Example details: { "title": "New title", "priority": "High" }. <br>- Each successful update request that makes changes results in exactly one "update" activity entry (no duplicates or multiple entries per request). <br>- If an update request succeeds but results in no effective change to any non-status field (no-op), no "update" activity entry is created. | - "status" changes are not handled here (see ACT-3). <br>- Details for updates must only include new values. Old values can be derived from other entries |
| ACT-3 | As a team member, I want status changes to be recorded as a distinct activity type so that I can quickly audit transitions between ToDo, InProgress and Done. | - When a task's status is changed successfully (via PATCH/PUT /tasks/{id} or a dedicated status endpoint), a "status_change" activity entry is created including task_uuid, timestamp and details that explicitly contain previous_status and new_status. The activity entry's timestamp MUST be in ISO8601 UTC. The timestamp MUST be recorded at the server and be within 5 seconds of the status change response time.<br>- The details.previous_status and details.new_status values must match the actual stored task record before and after the operation. <br>- If a request attempts to set status to the current value (no effective change), no "status_change" activity entry is created. | - Status values allowed: "ToDo", "InProgress", "Done". <br>- Status changes are treated as a distinct activity type and stored separately from "update" activities. |
| ACT-4 | As a team member, I want task deletions to be logged so that I can see when a task was removed and what the task looked like prior to deletion. | - After a successful deletion (DELETE /tasks/{id} → 204), a "delete" activity entry exists containing task_uuid, timestamp and a details object with the task's last-known values for title, description, status, priority and assignee. The delete activity.details MUST equal the task fields as returned by GET /tasks/{id} immediately prior to the DELETE request (title, description, status, priority, assignee). The activity.timestamp MUST be ISO8601 UTC.<br>- After deletion, attempting to retrieve the task by UUID (GET /tasks/{id}) returns 404. <br>- Attempting to delete a non-existent task returns 404 and does not create any activity entry. | - The "delete" activity stores the snapshot of the task immediately prior to deletion. <br>- Activities are durable and retained after task deletion. |
| ACT-5 | As a team member, I want to retrieve and filter the activity log so that I can inspect recent operations, narrow to a task, type, or time range, and fetch single activity entries. |- GET /activities returns an array of activity entries sorted by timestamp descending (most recent first). Each returned entry includes only: type, task_uuid, timestamp (ISO8601 UTC) and details. Activity entries returned by the API must not include a publicly-visible id or any other internal identifier field. <br>- Filtering works as follows and returns only matching entries (still sorted newest-first): GET /activities?task_uuid={uuid} returns only activities for that task_uuid; GET /activities?type=status_change returns only activities with type="status_change"; GET /activities?start={ISO8601}&end={ISO8601} returns only activities whose timestamp is within the inclusive [start,end] range. <br>- The API does not surface a per-activity public identifier in responses; if an internal identifier exists for storage, it must not be present in JSON responses or in the documented/public API. <br>-GET /activities MUST return HTTP 200 and a JSON array (possibly empty) of activity entries. If no activities match the filters, the response body MUST be an empty array. Responses MUST not include any publicly-visible activity id field.| - Default sort order is newest-first (descending). <br>- Pagination is out of scope unless otherwise requested (small-team scale). <br>- Time-range filter expects ISO8601 UTC strings. <br>- Single-user environment: activities do not record user identity (no auth). |

Task:
Propose approaches for maintaining the activity log entries. What kind of data structures or data collections should hold the activity entries? Is a single dictionary indexed by the entries timestamp, for example, sufficient?
The different proposed approaches should be compared using the following criteria:
- Simplicity and speed of the implementation.
- Ease and speed of retrieving activity log entries for a particular task or by type and date/time filtration.
- Testability of activity log.
- Space demands on computer resources.
- Scalability if the system had to be upgraded to handle a large number of tasks for a large team and in a production environment.

Constraints:
- This is a learning project, not production software.
- The backend must use Python, FastAPI, and Pydantic for validation.
- I want a REST API backend and a separate simple web frontend.
- Keep the tech stack simple, well-documented, and easy to run locally.
- No authentication or multi-tenancy.
- Only intrested in volatile memory. Do not suggest anything related to persistent storage, SQLite or any form of DBMS.
- Do not make the final decision for me.
- Do not add out-of-scope features such as auth, Docker, cloud deployment, microservices, or production database setup.
- Only propose 2 or 3 approaches for holding activity log data.

Output format:
A table with the first column for the criteria, a separate column for each approach and a another column for any questions that should be pondered before arriving at a decision.


### AI Reply Summary

The first reply compared 3 approaches and 2 of them were related to permanent storage and was immediately rejected. That was before the prompt was sent again with added constraints indicating all approaches are for holding data in memory and none for permanent storage. AI replied with a table comparing 3 approaches with respect to the criteria specified in the prompt and several other criteria added by AI at the bottom of the table. The table had the same structure as requested in the prompt and was followed by a list of notes provided by AI that discuss the different alternatives mentioned.
The items discussed helped in drafting the ADR and were generaly accepted.


## Request Backend Work Prompt

You are a senior Python software engineer. Implement a new method to access activity log entries and a new GET /activity route that calls that method.

Context files:
@backend/app/main.py
@backend/app/storage.py

Task:
1. Add a new method in @backend/app/storage.py that returns a list of activity log entries from the global dictionary _activities_by_timestmap or _activities_by_task that fit a certain criteria ordered by most recent to least. This new method should accept 4 OPTIONAL parameters to control what is included in the returned set:
   - task: The uuid of the task that the activity entry belongs to.
   - from: The start date/time value for the period where the timestamp of the activity entry lies.
   - to: the end date/time value for the period where the timestamp of the activity entry lies.
   - type: one of the ActivityType enumerator value indicating what type of entries should be included in the list.
   If all parameters are unspecified, the method should return ALL entries in the activity dictionary sorted by the timestamp in descending order. If 'from' was specified without 'to', all entries starting from the value of the 'from' field to the current moment should be returned. If the 'to' field was specified without the 'from' field, the method should return all earliest entries until the value of 'to' inclusive. If in any case the task parameter was specified, the _activities_by_task should be queried first and any other parameters should be applied on the resulting set. When the 'task' parameter is unspecified, the system should query the _activities_by_timestamp dictionary.
2. Add a new GET /activity route or endpoint to the @backend/app/main.py file. This should in its turn accept 4 optional fields in its query string that are optional but must be in the following set: (task, from, to, type). Passing any other field in the query string should return a 422 HTTP code and error message in a JSON object. The values for these fields should be passed as the parameters to the new method described above if supplied. The values for the 'from' and 'to' fields should be supplied as strings in the ISO8601 formt. If string values were provided that are not valid ISO8601 string representations of time moments, the 422 HTTP code should be returned with an error message stating that "the date/time values specified are in an incorrect format" in a JSON object. If the 'task' query string field specified a uuid value that doesn't exist among the global list of tasks named "_tasks" in @backend/app/storage.py, the 404 HTTP code should be returned.

Constraints:
- DO NOT use SQLAlchemy, SQLModel, Alembic, a database, or an ORM.
- DO NOT use Pydantic v1 syntax: no @validator, no class Config, no .dict().
- DO NOT add print or logging statements.
- DO NOT create API routes in this step.
- DO NOT wrap the answer in long explanation.
- DO NOT add any new files.
- DO NOT offer anything after completing the code changes.
- DO NOT add any additional imports.
- DO NOT return 404 for an empty list.
- DO NOT manually validate enum values; Pydantic/FastAPI handles invalid query values.
- DO NOT add try/except clauses.
- DO NOT place any modifications outside the main.py & storage.py files.
- DO NOT offer anything other than was is requested.
- Keep updates brief.

Output:
- New function definitions in the @backend/app/storage.py and @backend/app/main.py files.


### AI Reply Summary

Added a function for retrieving a list of activity log entry objects sorted by their timestamps in descending order in the storage.py file as requested. Also added a new GET /activity endpoint with code that calls the new function in the main.py file and passes it the received parameters.
The code updates were accepted but the name of one of the query string fields caused serious problems. It may have been becase its name is a Python reserved word.

The name of this parameter and another were changed manually to resolve this problem.

## Requesting Help with Failing PyTest Tests Prompt

My pytest output shows these failures:

```
==================================================== FAILURES ====================================================
____________________ test_list_activities_filter_by_from_to_type_returns_200_and_only_matches ____________________

client = <starlette.testclient.TestClient object at 0x78975aaf4430>

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

        print(b["created_at"])
        # filter activity to only include the creation entry for task-b using exact from/to timestamps and type
        params = {"start": b["created_at"], "end": b["created_at"], "type": ActivityType.CREATE.value}
        r = client.get("/activity", params=params)
>       assert r.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_tasks.py:338: AssertionError
---------------------------------------------- Captured stdout call ----------------------------------------------
2026-07-26T19:23:25.900461Z
____________________ test_list_activities_filter_by_task_from_to_returns_200_and_only_matches ____________________

client = <starlette.testclient.TestClient object at 0x78975a773c40>

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
>       assert r2.status_code == 200
E       assert 422 == 200
E        +  where 422 = <Response [422 Unprocessable Entity]>.status_code

tests/test_tasks.py:362: AssertionError
```

Relevant files:
- @backend/app/main.py
- @backend/app/storage.py
- @backend/tests/conftest.py
- @backend/tests/test_tasks.py

Expected Behavior:

The 'start' and 'end' query string parameters should be formatted as ISO8601 format.

Code for failing tests:

```python
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

    print(b["created_at"])
    # filter activity to only include the creation entry for task-b using exact from/to timestamps and type
    params = {"start": b["created_at"], "end": b["created_at"], "type": ActivityType.CREATE.value}
    r = client.get("/activity", params=params)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    item = data[0]
    assert item["type"] == ActivityType.CREATE.value
    assert item["task_uuid"] == b["id"]

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
    assert len(data) == 2
    for item in data:
        assert item["task_uuid"] == t["id"]
```

Task:
1. Identify the root cause.
2. State explicitly whether you are fixing the TEST or the PRODUCTION CODE.
3. Explain why in one sentence.
4. Provide only the file(s) that need to change.

Constraints:
- Do not add unrelated tests.
- Do not change public route paths or model names.
- Do not use try/except as a workaround.
- Do not weaken assertions just to make tests pass.

Output one code block per changed file, with a one-line comment at the top:
\# CHANGED: \<which test or function and why\>

### AI Replay Summary

The code for the list_activity function implementing the GET /activity endpoint was updated to replace any 'Z' at the end of the 'start' and 'end' string parameters with '+00:00' making them acceptable by the fromisoformat function. This was accepted as it allowed all pytest tests to pass.
