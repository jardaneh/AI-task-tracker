AI findings:

| ID | Severity | File / location | Finding | Evidence | Suggested next step | Confidence |
|---|---|---|---|---|---|---|
| SEC-01 | Medium | `backend/app/storage.py:90-111`; `backend/app/models.py:47-54` | Explicit JSON `null` values can corrupt stored task fields despite their response types being non-nullable. | `exclude_unset=True` preserves explicitly supplied `null`; `setattr()` writes it without assignment validation. The source comments document that `{"title": null}` can store `None` in a `str` field. | Reject explicit `null` for non-nullable update fields, or enable assignment validation and add regression tests for every optional update field. | High |
| SEC-02 | Medium | `backend/app/models.py:28,31,50-54` | `description` and `assignee` have no server-side length limits. | Pydantic validates title length only (`:42-43`, `:65-66`). Description and assignee are unconstrained strings; frontend limits do not protect direct API callers. | Add explicit maximum lengths and consider request-body/rate limits at the deployment layer. | High |
| SEC-03 | Medium | `backend/app/main.py:55-181`; `README.md` project limitations | No authentication or authorization protects task CRUD operations. Any reachable client can create, read, modify, or delete all tasks. | All routes lack auth dependencies. README explicitly states authentication/authorization is not implemented and the app is not intended for production. | Acceptable for course scope; before deployment, add identity, ownership/tenant checks, and authorization on every task operation. | High |
| SEC-04 | Low | `backend/app/main.py:25-34`; `frontend/index.html:404` | Deployment assumes an unauthenticated HTTP API on a fixed localhost origin and enables credentials, all methods, and all headers. | CORS permits credentials with wildcard methods/headers; frontend hardcodes `http://localhost:8000`. This is suitable for local development but unsafe/incompatible for a hosted HTTPS deployment. | Make API origin configurable, use HTTPS in deployed environments, and narrow CORS methods/headers and credential behavior. | High |
| SEC-05 | Low | `requirements.txt:1-6`; `.github/workflows/ci.yml:11-22` | Direct dependencies are pinned, but transitive dependencies are not locked or hash-pinned; CI performs no dependency/security scanning. | CI installs from `requirements.txt` directly and upgrades pip. No lockfile, hashes, audit, or vulnerability scan is present. | Generate a reproducible lockfile or hash-pinned requirements and add dependency scanning. | High |
| SEC-06 | Low | `.github/workflows/ci.yml:12,15` | CI action references use mutable major tags. | `actions/checkout@v6` and `actions/setup-python@v6` are not pinned to immutable commit SHAs. | Pin third-party actions to reviewed commit SHAs or centrally managed trusted tags. | High |
| SEC-07 | Low | `frontend/index.html:363,391,404,904-1024` | Frontend validation is weaker than backend validation and the API endpoint is fixed in source. | Frontend limits title to 120 and assignee to 80, but description has no limit; direct API requests bypass all UI limits. Errors are logged with `console.error`. | Treat frontend checks as usability only; centralize configurable API settings and enforce all security/resource constraints server-side. | High |

Graded AI findings:
| Finding ID | Proposed grade | Reason | Evidence needed or evidence used | Student decision to confirm |
|---|---|---|---|---|
| SEC-01 | Valid | Explicit `null` updates can bypass intended field invariants and corrupt in-memory task data. | `backend/app/storage.py:90-111` uses `exclude_unset=True` and `setattr()` without assignment validation; `backend/app/models.py:47-54` permits nullable update fields. | Confirm whether `null` is intended to clear optional fields, and whether nullable values are acceptable for each field. |
| SEC-02 | Valid | Direct API callers can submit arbitrarily large descriptions and assignee values; frontend limits are not security controls. | `backend/app/models.py:28,31,50-54` has no length constraints for these fields. | Confirm whether resource limits are required for the module’s API scope. |
| SEC-03 | Valid, scope-qualified | The API has no access control, so any reachable client can operate on all tasks. It is documented as intentional for the course, but remains a production limitation. | `backend/app/main.py:55-181` has no authentication/authorization dependencies. `README.md` states auth is not implemented and the app is not production-ready. | Confirm whether grading treats documented course limitations as valid findings when they would matter in production. |
| SEC-04 | Noise | The fixed localhost HTTP origin and broad CORS settings are development assumptions explicitly documented by the repository. They are not evidence of a flaw in the intended local workflow. | `backend/app/main.py:25-34`; `frontend/index.html:404`; README’s local-serving instructions. | Confirm whether deployment hardening is within Module 5 scope. |
| SEC-05 | Valid, low confidence as a security action item | Direct dependencies are pinned, but transitive dependencies are not reproducibly locked or hash-pinned, and CI has no dependency scanning. This is legitimate supply-chain hygiene, though low impact for this learning repo. | `requirements.txt:1-6`; `.github/workflows/ci.yml:19-22`. | Confirm whether dependency reproducibility/scanning is expected in the course rubric. |
| SEC-06 | Valid, low severity | Mutable GitHub Action tags allow upstream tag changes to alter CI behavior. This is a real CI supply-chain hardening issue, but not necessarily a defect for this course. | `.github/workflows/ci.yml:11-17` uses `actions/checkout@v6` and `actions/setup-python@v6`. | Confirm whether CI supply-chain pinning is part of the grading scope. |
| SEC-07 | Noise | The frontend’s weaker limits do not bypass backend validation; the server remains the enforcement point. The hardcoded localhost API URL is documented for local use. | `frontend/index.html:363,391,404`; backend validation in `backend/app/models.py:24-67`. | Confirm whether frontend deployment portability, rather than API security, is being graded. |

### 1. Reconciliation

| Agreement | AI-only | You-only |
|---|---|---|
| **SECU-1 ↔ SEC-03 — Valid.** Both identified missing authentication/authorization. This is intentional course scope but remains a production risk. | **SEC-04 — Noise.** Localhost HTTP and broad CORS are documented development assumptions. | **SECU-4 — Needs evidence / likely Noise.** The concern was not raised by AI, but the frontend uses `textContent` for task data, which prevents the described HTML-rendering issue. |
| **SECU-2 ↔ SEC-01 — Valid.** Both identified explicit `null` updates bypassing intended field invariants. | **SEC-05 — Valid, low priority.** Dependency reproducibility and scanning were not in the manual findings. |  |
| **SECU-3 ↔ SEC-02 — Valid, narrowed.** Both identified missing length limits for description and assignee. The manual finding is too broad because title length is enforced server-side. | **SEC-06 — Valid, low severity.** Mutable GitHub Action tags were not in the manual findings. |  |
|  | **SEC-07 — Noise.** Frontend limits and fixed API configuration do not bypass backend validation in the documented local workflow. |  |

### 2. Observation

AI coverage aligned well with the main API control weaknesses: authentication, null handling, and unbounded text fields.  
The main manual-only concern was harmful-character handling, but available frontend evidence weakens that concern because task data is rendered with `textContent`.

### 3. Top-3 security backlog

| Rank | Finding | Why it matters | Suggested owner | Next action |
|---|---|---|---|---|
| 1 | **SECU-1 / SEC-03 — Missing authentication and authorization** | Any reachable caller can read, modify, or delete all tasks. | Backend / course-project owner | Decide whether auth is intentionally out of scope; if production-bound, add authentication and task ownership checks. |
| 2 | **SECU-2 / SEC-01 — Explicit `null` update corruption** | Invalid `null` values can enter fields intended to be non-nullable and may break downstream behavior. | Backend | Define null semantics per field, reject disallowed nulls, and add regression tests. |
| 3 | **SECU-3 / SEC-02 — Unbounded description and assignee strings** | Direct API callers can submit excessive payload data, creating resource and data-quality risks. | Backend | Add server-side maximum lengths and tests for oversized description and assignee values. |
