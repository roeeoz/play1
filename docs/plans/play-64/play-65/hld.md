# High-Level Design — PLAY-65: Health-check endpoint returning service status

## 1. System Overview

- **What is being built:** A GET `/healthz` endpoint in the play1 guestbook Flask application that returns a fixed JSON liveness response.
- **Problem:** No stable, side-effect-free liveness signal exists; callers must probe application routes that may change, require auth, or produce log noise.
- **Key responsibilities:** Return a static JSON body with HTTP 200, exclude the request from application-level logging, reject non-GET methods with 405.

## 2. Architecture Overview

- **Component:** A single new route registered inside the existing `create_app()` factory in `src/guestbook/app.py`.
- **Boundary:** The `/healthz` handler is a leaf route with no interaction with storage, validation, or any other module. It only uses `flask.jsonify`.
- **Logging hook:** A lightweight `after_request` hook inside `create_app()` that logs requests via Python's `logging` module, skipping requests where `request.path == "/healthz"`. This makes FR6 testable.
- **External dependencies:** None new. Flask >= 3 is already declared.

## 3. Data Flow Design

- **Flow:** HTTP GET `/healthz` → Flask route handler → `jsonify({"status":"ok","service":"play1"})` → HTTP 200 response. No database, no computation.
- **Logging flow:** Every request passes through the `after_request` hook. If `request.path != "/healthz"`, a log record is emitted to the `guestbook.access` logger. `/healthz` requests are silently skipped.
- **Sync only.** No async or event processing.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `/healthz` route handler | Return static JSON liveness response | HTTP GET → 200 + JSON | roeeoz/play1 |
| `after_request` logging hook | Log all requests except `/healthz` | Flask response → log record (or skip) | roeeoz/play1 |
| `tests/test_healthz.py` | Verify all five acceptance criteria | Flask test client assertions | roeeoz/play1 |

## 5. Interface Contracts

- **Endpoint:** `GET /healthz` → `200 OK`, body `{"status":"ok","service":"play1"}`, `Content-Type: application/json`.
- **Non-GET methods:** `405 Method Not Allowed` (Flask built-in behavior from `@app.get()`).
- **No cross-repo contracts.** Single-repo change.

## 6. Key Technical Decisions

- **`@app.get("/healthz")` decorator:** Follows the existing route registration pattern in `app.py` and automatically returns 405 for non-GET methods.
- **`after_request` hook for logging:** Chosen over a `logging.Filter` on the werkzeug logger because (a) it is testable via pytest's `caplog` fixture, (b) the werkzeug logger is not active during test-client requests, and (c) it is self-contained within `create_app()`.
- **New test file `tests/test_healthz.py`:** Keeps healthz tests separate from guestbook API tests. Fixtures are duplicated (3 small fixtures) rather than extracting to `conftest.py`, avoiding modifications to existing test infrastructure.

## 7. Risks & Constraints

- **Logging test proving a negative (AC4):** Mitigated by including a positive control — assert that a regular endpoint call DOES produce a log entry while `/healthz` does NOT.
- **CI timing for AC3:** A static `jsonify()` call through the test client takes microseconds; 100 ms is an extremely generous bound. Flakiness risk is negligible.
- **G3 line budget:** Estimated ~70–95 lines changed, well within the 300-line cap.
