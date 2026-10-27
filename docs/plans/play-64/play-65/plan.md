# Implementation plan — PLAY-65: Health-check endpoint returning service status

## Context

PLAY-65 adds a GET `/healthz` endpoint to the play1 guestbook Flask application so that load balancers, orchestrators and monitoring systems can verify the service is running. The endpoint returns `{"status":"ok","service":"play1"}` with `Content-Type: application/json`, requires no authentication, responds in under 100 ms, rejects non-GET methods with 405, and is excluded from application request logging. The change lands in `roeeoz/play1` on branch `halo/feat/play-65`. The approved spec (`spec.md`), design (`hld.md`) and work-item breakdown (`work-items.md`) sit alongside this file in `docs/plans/play-64/play-65/`.

## Research findings

**Change surface.** The sole production file to modify is `src/guestbook/app.py`:34–66 — the `create_app()` factory. It currently registers two routes (`POST /api/guestbook/entries` at line 46, `GET /api/guestbook/entries` at line 62) and returns the `Flask` app with no request hooks or logging configuration. No `import logging` or `after_request` hook exists anywhere in `src/guestbook/`.

**Contracts touched.** The change adds one new HTTP contract (`GET /healthz → 200 + JSON`) and one internal hook (an `after_request` handler that emits access log records, skipping `/healthz`). No existing contract is modified; the two guestbook routes are untouched.

**Existing tests and gate.** The test suite lives in `tests/` (nine test files, no `conftest.py`). The guestbook tests in `tests/test_guestbook_api.py` define three self-contained fixtures (`db_path`, `app`, `client`) at lines 16–28 — the pattern the new test file will replicate. The canonical gate is `pytest` (declared in `.factory/testing.md:3`), invoked by `.github/workflows/ci.yml` job `test` on Python 3.12 after `pip install -e ".[test]"`. No linter, formatter or type checker is configured.

**What exists vs. what must be created.** `src/guestbook/app.py` exists and needs two additions inside `create_app()`: the route and the logging hook. `tests/test_healthz.py` is new.

**No unknowns remain.** Flask's `@app.get()` decorator (available since Flask 2.0, declared `>=3` in `pyproject.toml:13`) returns 405 automatically for non-GET methods. Python's `logging` module is stdlib; no new dependency is required.

## Locked decisions and assumptions

**Locked decisions**

- The endpoint path is `/healthz` and the response body is `{"status":"ok","service":"play1"}` — spec FR1, FR2.
- The endpoint is registered inside `create_app()` using `@app.get("/healthz")` — hld.md §6.
- Logging exclusion uses an `after_request` hook that emits to the `guestbook.access` logger for all requests except those where `request.path == "/healthz"` — hld.md §2, §3, §6.
- Tests go in a new file `tests/test_healthz.py` with self-contained fixtures (no `conftest.py` change) — hld.md §6.
- The handler function carries a docstring — spec §6, G2.

**Assumptions**

- The `after_request` hook logs at `INFO` level using `logging.getLogger("guestbook.access")`. Evidence: hld.md §3 names the logger; INFO is the conventional level for access logging. Consequence if wrong: the test's `caplog` level must match — a single-line fix.
- The log format includes the request method, path and response status code. Evidence: standard access-log practice; the spec requires enough content to distinguish logged from non-logged requests. Consequence if wrong: the positive-control assertion text changes but the exclusion test remains valid.

## Solution proposal

Add two constructs inside `create_app()` in `src/guestbook/app.py`, after the existing route registrations and before `return app`:

1. **Route:** `@app.get("/healthz")` returning `jsonify({"status": "ok", "service": "play1"})`. The decorator restricts to GET and returns 405 for other methods automatically. The handler carries a one-line docstring. No database access, no authentication, no computation.

2. **Logging hook:** An `@app.after_request` function that, for every request whose path is not `/healthz`, emits an INFO record to the `guestbook.access` logger containing the method, path and status code, then returns the response unchanged. This makes FR6 testable via `caplog`: a request to a guestbook route produces a log record; a request to `/healthz` does not.

The new `tests/test_healthz.py` replicates the three-fixture pattern from `test_guestbook_api.py` (no shared `conftest.py` needed) and covers all five acceptance scenarios plus the docstring requirement (AC6).

**Alternatives rejected.** A `logging.Filter` on the werkzeug logger was rejected because werkzeug's logger is not active during test-client requests, making the exclusion untestable without a running server (hld.md §6). A shared `conftest.py` was rejected to avoid modifying existing test infrastructure for a self-contained addition.

## Ordered implementation steps

1. **Add `import logging` to `src/guestbook/app.py`.** Add the stdlib import at the top of the file (after line 3, alongside existing stdlib imports). No acceptance criterion directly; prerequisite for step 3. Covered by: `tests/test_healthz.py` (created in step 4).

2. **Register the `/healthz` route inside `create_app()`.** Add `@app.get("/healthz")` with a handler named `healthz` that returns `jsonify({"status": "ok", "service": "play1"})` and carries a one-line docstring. Place it after the existing `get_entries` route (after `app.py:64`) and before `return app`. Advances: AC1 (200 + JSON body + content type), AC2 (no auth required), AC3 (under 100 ms), AC5 (405 for POST), AC6 (docstring). Covered by: `tests/test_healthz.py`.

3. **Add the `after_request` logging hook inside `create_app()`.** Add `@app.after_request` that obtains `logging.getLogger("guestbook.access")` and, when `request.path != "/healthz"`, logs an INFO record with method, path and status code. Place it after the healthz route, before `return app`. Advances: AC4 (logging exclusion). Covered by: `tests/test_healthz.py`.

4. **Create `tests/test_healthz.py`.** New file with self-contained `db_path`, `app` and `client` fixtures (same pattern as `test_guestbook_api.py:16–28`). Test classes/functions covering all acceptance criteria:
   - **AC1:** `test_healthz_returns_200_with_expected_json` — assert status 200, JSON body `{"status":"ok","service":"play1"}`, content type `application/json`.
   - **AC2:** `test_healthz_no_auth_required` — send GET with no auth headers, assert same 200 + JSON (may be combined with AC1 since the test client sends no credentials by default; a separate test makes the intent explicit).
   - **AC3:** `test_healthz_response_time_under_100ms` — measure round-trip via `time.perf_counter()` around a `client.get("/healthz")`, assert < 0.1 s.
   - **AC4:** `test_healthz_excluded_from_request_log` — use `caplog` at INFO level on the `guestbook.access` logger; send GET to `/api/guestbook/entries` and assert a log record appears (positive control); clear; send GET to `/healthz` and assert no record appears.
   - **AC5:** `test_healthz_post_returns_405` — send POST to `/healthz`, assert status 405, assert response body does not contain `"status"` key.
   - **AC6:** `test_healthz_handler_has_docstring` — import `create_app`, retrieve the `healthz` view function from `app.view_functions`, assert `__doc__` is truthy.
   - **AC7:** Run the full `pytest` suite and verify all existing tests still pass (implicit — step 5).
   Advances: all ACs. Covered by: this is the test layer itself (`package-api` layer, `pytest`).

5. **Run the canonical gate.** Execute `pip install -e ".[test]" && pytest` from the repo root and verify all tests pass — existing and new. Advances: AC7 (all existing tests continue to pass). This step is the implement phase's responsibility; the plan names it so the gate obligation is explicit.

**Implicit invariants.** No authorization or tenancy contract applies (the endpoint is unauthenticated by design — FR3). No concurrency or idempotency concern (static response, no shared state). Validation and error paths are handled by Flask's built-in 405 for non-GET methods.

## Work-item mapping

| Step | Work item | Title |
|------|-----------|-------|
| 1 | t1 | Add GET /healthz endpoint with logging exclusion and tests |
| 2 | t1 | Add GET /healthz endpoint with logging exclusion and tests |
| 3 | t1 | Add GET /healthz endpoint with logging exclusion and tests |
| 4 | t1 | Add GET /healthz endpoint with logging exclusion and tests |
| 5 | t1 | Add GET /healthz endpoint with logging exclusion and tests |

All steps belong to the single work item. No planning gap.

## Verification and CI gate

The canonical gate is `pytest`, declared in `.factory/testing.md:3` and invoked by `.github/workflows/ci.yml` job `test` (Python 3.12, `ubuntu-latest`).

**Gate sequence (from a clean temporary worktree at the committed SHA):**

1. `pip install -e ".[test]"`
2. `pytest`

**Required test layer:** `package-api` (production-path, required, run by the canonical gate). The new `tests/test_healthz.py` is discovered by pytest automatically via `[tool.pytest.ini_options] testpaths = ["tests"]` in `pyproject.toml:27`.

**What green means:** All existing tests pass unchanged. All six new test functions pass. No new CI configuration is needed — the existing workflow already runs `pytest` on every pull request.

**No `.factory/testing.md` update needed** — the gate command (`pytest`) is unchanged. No `.factory/delivery-assets` obligation — no binary deliverable is introduced.

## Risks and scope guards

**Risks**

- **Log-test fragility (low).** The AC4 test asserts on the absence of a log record for `/healthz` and presence for another route. If the logger name or level is changed without updating the test, the positive control catches the drift. Mitigation: the logger name `guestbook.access` is a constant in the hook, not a magic string; `caplog` captures at the named level.
- **Timing test flakiness (negligible).** A 100 ms bound on a static `jsonify` call through the in-process test client is extremely generous; typical round-trip is under 1 ms. Mitigation: none needed.

**Scope guards — the implement phase must NOT:**

- Modify any existing route or its behaviour.
- Add, remove or change any dependency in `pyproject.toml`.
- Create or modify `conftest.py` or any existing test file.
- Add a readiness probe, dependency check, metrics endpoint or any functionality beyond the static `/healthz` response and its logging exclusion.
- Modify `.github/workflows/ci.yml` or `.factory/testing.md`.
- Delete, skip, disable or weaken any existing test or CI check.

## Clarification outcomes

None — no clarifying question was needed. All requirements are unambiguous and consistent with the repository.
