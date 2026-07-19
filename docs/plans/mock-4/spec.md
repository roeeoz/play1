# Feature Specification Document

## 1. Feature Overview
- **Summary**: Add two HTTP endpoints to the play1 package — `POST /notes` for creating notes and `GET /search` for retrieving them by substring match — backed by an in-process memory store.
- **Problem statement**: API consumers have no way to store notes or search their content. The reported "search feels off" complaint was caused by missing results; case-insensitive substring matching across title and body directly addresses it.
- **Target users / actors**: Any HTTP API consumer (no UI, no browser required).

---

## 2. Goals & Non-Goals

### Goals
- Expose `POST /notes` to create a note with a title and body.
- Expose `GET /search?q=` to retrieve notes whose title or body contains the query string (case-insensitive substring match).
- Maintain an in-memory store of notes for the lifetime of the process.
- Meet a p95 latency target of < 200 ms with up to 10,000 stored notes, measured in-process.

### Non-Goals
- No UI of any kind.
- No fuzzy or relevance-ranked search.
- No pagination.
- No persistence beyond process memory.
- No authentication or authorisation.
- No i18n or accessibility features.
- No enforced field-length or note-count limits.

---

## 3. Functional Requirements

### POST /notes
- **FR1**: Accepts an HTTP POST to `/notes` with a JSON body containing `title` (string) and `body` (string).
- **FR2**: Both `title` and `body` are required and must be non-empty strings. A missing field and an empty string are both violations.
- **FR3**: If a required field is missing or empty, the endpoint returns HTTP 400 with a JSON error response that names the offending field.
- **FR4**: On success, the endpoint returns HTTP 201 with a JSON object `{id, title, body}` representing the newly created note.
- **FR5**: Each created note is assigned a unique `id` and stored in the in-memory note store.

### GET /search
- **FR6**: Accepts an HTTP GET to `/search` with a query parameter `q` containing the search text.
- **FR7**: Performs a case-insensitive substring match against the `title` and `body` of every stored note.
- **FR8**: Returns HTTP 200 with a JSON array of matching notes, each as `{id, title, body}`, ordered by insertion order (the order in which notes were created via POST /notes).
- **FR9**: Returns HTTP 200 with an empty JSON array `[]` when no notes match. Never returns 404 for an empty result set.

### Performance
- **FR10**: The p95 latency of `GET /search` must be < 200 ms with up to 10,000 notes in the store, measured in-process.

---

## 4. User Experience & Behavior

### Creating a note — happy path
1. Consumer sends `POST /notes` with `{"title": "My note", "body": "Some content"}`.
2. Server responds `201 Created` with `{"id": 1, "title": "My note", "body": "Some content"}`.

### Creating a note — validation failure
1. Consumer sends `POST /notes` with `{"title": "", "body": "Some content"}`.
2. Server responds `400 Bad Request` with a JSON body identifying `title` as the invalid field.

### Searching notes — matches found
1. Consumer sends `GET /search?q=content`.
2. Server responds `200 OK` with a JSON array of notes whose title or body contains "content" (case-insensitive), in insertion order.

### Searching notes — no matches
1. Consumer sends `GET /search?q=zzznomatch`.
2. Server responds `200 OK` with `[]`.

### User-facing edge cases
- A query that matches only the title, only the body, or both fields is a valid match.
- Search is case-insensitive: querying "NOTE" matches a note whose body contains "A note about things".
- Results appear in note-creation order regardless of where within the title or body the match occurs.

---

## 5. Acceptance Criteria

- **AC1**: `POST /notes` with a valid `{title, body}` JSON body returns 201 and a JSON object with `id`, `title`, and `body`.
- **AC2**: `POST /notes` with a missing `title` field returns 400 and a JSON error response that references the `title` field by name.
- **AC3**: `POST /notes` with an empty-string `body` returns 400 and a JSON error response that references the `body` field by name.
- **AC4**: `GET /search?q=<text>` returns 200 and a JSON array of every note whose title or body contains `<text>` as a case-insensitive substring.
- **AC5**: `GET /search?q=<text>` returns 200 and `[]` when no stored note matches.
- **AC6**: Search results are ordered by note insertion order, not by relevance or any other ranking.
- **AC7**: The p95 response time of `GET /search` is < 200 ms with 10,000 notes in the store, measured in-process.
- **AC8**: Notes are retained only for the lifetime of the process; a fresh process starts with an empty store.

---

## 6. Dependencies & Constraints (product-level)

- The feature is entirely net-new; no existing play1 code is being modified for functional reasons.
- No external services, databases, or file-system persistence may be introduced.
- The implementation must pass the existing `pytest` test suite without regressions.
- The repository CI `gate` job must not be triggered (no `CI_FAIL` marker file may be created or left behind).
- Python version must remain ≥ 3.10 as required by the existing `pyproject.toml`.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, HTTP framework selection, `id` type and generation strategy, error-response JSON schema, in-memory data-structure choice, performance verification approach (benchmark harness), security posture, observability, and the PR breakdown are all owned by the tech lead in the STRUCTURE stage.

**Product-imposed technical constraints the tech lead must respect:**
- Python ≥ 3.10.
- In-process memory only; no external persistence.
- p95 < 200 ms at 10,000 notes must be verifiable by a test or benchmark included in the PR.

---

## 8. Open Questions

- **OQ1 — `id` format**: The spec requires notes to have an `id` but does not specify the type (sequential integer, UUID, opaque string, etc.). The STRUCTURE stage should decide and document this.
- **OQ2 — `GET /search` with missing `q` parameter**: Behaviour when `q` is absent from the request is not defined (e.g. 400 error, or treat as empty string returning all notes). The STRUCTURE stage should define and document the response.
