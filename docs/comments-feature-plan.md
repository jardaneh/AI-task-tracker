# Comments on Tasks Feature Plan

## 1. Data Model

The active data models are defined in `backend/app/models.py`. The existing pattern separates request models from response models:

- `TaskCreate` defines create-request fields.
- `TaskUpdate` defines partial-update fields.
- `TaskResponse` defines server-returned fields.
- Request models use `ConfigDict(extra="forbid")`.
- Server-generated identifiers and timestamps are created in `backend/app/storage.py`.

Add comment models following that pattern:

- `CommentCreate`
  - `author: str`
  - `body: str`
  - `extra="forbid"`
  - Validate `author` as 1–100 characters.
  - Validate `body` as 1–2,000 characters.
  - Decide whether surrounding whitespace should be trimmed, consistent with task-title handling.

- `CommentResponse`
  - `id: str`
  - `task_id: str`
  - `author: str`
  - `body: str`
  - `created_at: datetime`
  - `extra="forbid"`

The comment’s `id` and `created_at` should be generated in `backend/app/storage.py`, using the same UUID and UTC datetime conventions as `add_task`.

The `task_id` relationship should be checked by the route or storage layer before creating a comment. The current application does not use a database foreign-key mechanism.

The inactive `backend/app/routes/tasks.py` and stale `backend/app/schemas.py` should not be treated as the source of truth. `README.md` identifies `backend/app/main.py` and `backend/app/models.py` as the active implementation locations.

## 2. API Routes

The active routes are defined directly in `backend/app/main.py`; the router in `backend/app/routes/tasks.py` is not mounted.

### Create a comment

`POST /tasks/{task_id}/comments`

Request body:

- `author`: required string, 1–100 characters.
- `body`: required string, 1–2,000 characters.

Response:

- Status: `201 Created`
- Body: the created comment, including generated `id`, supplied `task_id`, normalized fields if applicable, and generated UTC `created_at`.

Error cases:

- `404 Not Found` if `task_id` does not identify an existing task.
- `422 Unprocessable Entity` for missing fields, blank values, invalid types, length violations, or unknown fields.
- The client should not supply `id`, `task_id`, or `created_at` in the request body.

### List comments for a task

`GET /tasks/{task_id}/comments`

Response:

- Status: `200 OK`
- Body: a list of comments belonging to the task.
- Return an empty list when the task exists but has no comments.
- Use a deterministic ordering, preferably insertion order or ascending `created_at`.

Error cases:

- `404 Not Found` if the task does not exist.

### Individual comment operations

Create and list operations are sufficient for the requested feature. `GET`, `PATCH`, and `DELETE` routes for individual comments are not currently required and should remain open design decisions.

To avoid changing existing task response behavior, comments should initially be exposed through dedicated routes rather than added to `TaskResponse`. The current `GET /tasks` and `GET /tasks/{task_id}` responses use `TaskResponse` from `backend/app/models.py`.

Storage functions would follow the existing delegation pattern in `main.py`, where route handlers call functions such as `storage.add_task`, `storage.get_task_by_id`, and `storage.delete_task`.

## 3. Tests

The current endpoint tests are in `backend/tests/test_tasks.py`, use `TestClient`, and reset the in-memory store through the autouse fixture in `backend/tests/conftest.py`. The following tests could be added there to match the existing style.

### Happy path

- `test_create_comment_valid_returns_201_with_generated_fields`
- `test_create_comment_for_existing_task_returns_task_reference`
- `test_list_comments_for_task_returns_200_and_comments`
- `test_list_comments_for_task_with_no_comments_returns_empty_list`
- `test_list_comments_preserves_creation_order`
- `test_comments_for_one_task_do_not_appear_for_another_task`

### Validation

- `test_create_comment_missing_author_returns_422`
- `test_create_comment_missing_body_returns_422`
- `test_create_comment_blank_author_returns_422`
- `test_create_comment_blank_body_returns_422`
- `test_create_comment_author_at_maximum_length_returns_201`
- `test_create_comment_body_at_maximum_length_returns_201`
- `test_create_comment_author_over_maximum_length_returns_422`
- `test_create_comment_body_over_maximum_length_returns_422`
- `test_create_comment_unknown_field_returns_422`
- `test_create_comment_client_supplied_id_is_rejected`
- `test_create_comment_client_supplied_created_at_is_rejected`

### Edge cases

- `test_create_comment_for_missing_task_returns_404`
- `test_list_comments_for_missing_task_returns_404`
- `test_create_multiple_comments_for_same_task_returns_distinct_ids`
- `test_created_comment_timestamp_is_utc`
- `test_comment_data_is_cleared_by_storage_reset`
- `test_deleting_task_handles_associated_comments_according_to_policy`

The last test depends on the team’s decision about task deletion. The current `delete_task` implementation only removes the task from `_tasks`; comment cleanup is not currently defined.

The existing standalone validation script `tests/verify_a.py` directly exercises task schemas. It could be extended for comment validation, but that is not required unless schema-level validation coverage is intended to remain there.

## 4. Frontend Changes

The frontend is a single vanilla HTML/JavaScript file: `frontend/index.html`. There is no confirmed frontend build system or separate component structure.

The task board currently:

- Loads tasks with `GET /tasks`.
- Renders task cards grouped by status.
- Opens a task create/edit modal.
- Uses `fetch` for API requests.
- Displays validation and server-error messages in the modal or board.

A minimal frontend design would:

- Add a comments area to the task edit modal or task-card detail view.
- Fetch comments with `GET /tasks/{task_id}/comments` when a task is opened for editing.
- Display author, body, and formatted `created_at`.
- Add author and body inputs for creating a comment.
- Enforce the 100-character author and 2,000-character body limits in the UI while retaining server validation.
- Submit comments with `POST /tasks/{task_id}/comments`.
- Refresh the comment list after successful creation.
- Display loading, empty, validation-error, and server-error states.
- Render comment text safely as text rather than interpreting it as HTML.

The existing task modal and board-rendering logic in `frontend/index.html` would need to be extended. No separate frontend file is currently confirmed.

## 5. Migration Notes

The repository uses in-memory storage only:

- Tasks are stored in `_tasks` in `backend/app/storage.py`.
- There is no database or file persistence.
- Data is lost when the process restarts.
- Tests clear storage through `storage._reset()`.

Therefore, no database migration is currently required.

The storage shape would need to gain a comment collection, such as a separate in-memory mapping keyed by comment ID. A separate collection is preferable to changing the existing `TaskResponse` shape because it preserves current task endpoints and allows comments to be queried by task.

The following storage behavior must be defined:

- Comments should only be created for existing task IDs.
- `_reset()` must clear comments as well as tasks.
- Deleting a task should either cascade-delete its comments or explicitly leave them inaccessible.
- Listing comments should filter by `task_id`.
- Comment ordering should be deterministic.

Because storage is non-persistent, existing task data cannot require a backfill. Any comments created during a process lifetime will disappear when the application restarts.

No changes should be made to the inactive `backend/app/routes/tasks.py` or stale `backend/app/schemas.py` unless the team intentionally decides to reactivate those modules.

## 6. Open Questions

1. Should comments support only creation and listing, or should users also be able to edit and delete them?
2. Should `author` remain free-form text, or should it reference an authenticated user? Authentication and authorization are not implemented or confirmed in the repository.
3. Should deleting a task cascade-delete its comments?
4. Should comments appear only through `/tasks/{task_id}/comments`, or should `TaskResponse` also include a comments field?
5. Should author and body whitespace be trimmed before validation and storage?
6. Should comment timestamps be returned in the same ISO 8601 UTC format as the task timestamps?
7. Should the frontend show comments directly on each Kanban card or only in the task edit modal?
8. Is pagination needed for tasks with many comments?
9. Should comment bodies support plain text only, or a formatting syntax such as Markdown?

## Files read

- `AGENTS.md`
- `README.md`
- `backend/app/models.py`
- `backend/app/main.py`
- `backend/app/storage.py`
- `backend/app/routes/tasks.py`
- `backend/app/schemas.py`
- `backend/tests/conftest.py`
- `backend/tests/test_tasks.py`
- `frontend/index.html`

## Assumptions to verify

- `backend/app/main.py`, `backend/app/models.py`, and `backend/app/storage.py` remain the intended active implementation files.
- Comments should initially use the same in-memory lifecycle as tasks.
- Dedicated comment endpoints are preferred over embedding comments in `TaskResponse`.
- Comment creation and listing are the minimum required operations.
- Free-form author strings are acceptable until authentication requirements are defined.
- The frontend implementation will remain within `frontend/index.html`.
- No production database or persistence migration is required for the current repository state.
