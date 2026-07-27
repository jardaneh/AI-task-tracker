### ADR-002: Assignee Data Source and Task Filter Validation

_Context_:
A new feature is to be added to the Python/FastAPI Task Tracker application that allows users to search for tasks that contains a fragment of text in their title/details, of a specific priority, of a specific status or with a particular assignee. The priority and status values for tasks are clearly defined in a finite set of values that can be specified using fixed dropdown lists. The fragment of text in the title/details field of tasks can be free text.
When specifying text for the assignee field or criteria for a task search operation, one can have the system maintain a list of assignees that different tasks have been assigned to and find an exact match for any text supplied. An alternative approach would be to have the assignee field accept any free text which would be normalized to lower case, trimmed for whitespace and matched as a substring of any defined assignees. Yet another alternative is a mix of both and add autocomplete functionality where values extracted from a compiled list of assignees is provided as suggestions depending on a few characters entered manually.

_Decision_:
Go with the free text approach with no compilation of assignee list and no autocomplete functionality.

This is clearly the less demanding in terms of coding effort. It will avoid hiding search results due to assignee misspellings. No need to maintain a list of assignees or introduce amendments to the task creation and update code to place new assignees in the list. And no need for working on a dropdown list in the frontend or any autocomplete functionality. And as it most likely only encounter small datasets, especially during testing, the cost in computer resources will remain negligible. The downsides of this approach can be overlooked as long as the dataset remains small and the application will not be used for production where data hygiene can suffer.

The other approaches are definitely more costly with respect to time, effort and computer resources. Both during implementation or testing. If the system was to be upgraded to run in production, and have mutli-user and authentication implemented, the list of assignees will most likely depend on a set of user accounts defined in the system and no compilation of a list of assignees will have to be carried out.


### ADR-003: Maintaining Activity Logs in Memory

_Context_:
A new feature is to be added to the Python/FastAPI Task Tracker application where activity logs will be maintained listing create, update, delete and status update operations on tasks. The activity log entries can be viewed by users and should be retrievable using a time range, type (i.e. create, update, delete, status-update) and task identifier. Requesting activity log entries for a specific task will return those pertaining to that task only.
Three approaches have been identified for the data structure design that will maintain the activity log entries and allow reasonably quick means of retrieving them:
A. A single global list of activity log objects sorted by their timestamp values.
B. A single sorted global list along with a task-list map.
C. A single sorted global list, a task-list map and an additional type-list map allowing indexing by both task identifiers and activity types.

_Decision_: Approach B

This approach is a good compromise between the simplicity and inefficiency of approach A and the complexity and speed of approach C with only a little extra effort. Should allow fast retrieval of activity log entries filtered by a time range and by task identifiers; albeit retrieval by type will remain linear and require a full traversal of the list. This should be convenient as it is assumed filtering by task identifier will be quite common. Might entail a little extra effort testing it to ensure consistency between the global list and per-task map; but still significantly less than the test workload for approach C. Approach B shouldn't demand much more space than approach A as long as activity log object references are used in the per-task map instead of full duplication of activity log objects in the global sorted list.
In case of moving the system into production to be employed by a large team of developers create thousands of tasks, the most appropriate course of action would be to use a proper DBMS system that will handle all indexing operations. Maintaining any global lists will become redundant.

