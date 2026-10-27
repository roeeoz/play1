# Implementation plan — PLAY-59: Add a GET /healthz liveness endpoint returning status, version, and uptime

| Field | Value |
| --- | --- |
| Work item | t1 — Add GET /healthz liveness endpoint with tests |
| Repo | `roeeoz/play1` — checkout at `/Users/roeeoz/.halo/workspaces/delivery-f7043e9bf9fc23d1f3f0d432cd090e3d/workspace/play1-79db628f23`, branch `halo/feat/play-59` |
| Tier | T1 (single work item, no dependencies) |
| Traces | R1–R10 · spec AC1–AC4 · HLD §1–§7 |
| Inputs read | `docs/plans/play-58/play-59/spec.md`, `hld.md`, `work-items.md`; `src/guestbook/app.py`; `src/guestbook/__init__.py`; `tests/test_guestbook_api.py`; `pyproject.toml`; `.github/workflows/ci.yml`; `.factory/testing.md` |

## Context

PLAY-59 adds a liveness endpoint at `GET /healthz` to the guestbook Flask application in `roeeoz/play1`. The endpoint returns a fixed JSON body with `"status"` (`"ok"`), `"version"` (the package version from `pyproject.toml`), and `"uptimeSeconds"` (whole seconds since process start). Non-GET methods return 405. Probe requests log at DEBUG only. The change is covered by automated tests for the happy path, a boundary case (mocked uptime), an error case (405), and a logging assertion. The spec (`spec.md`), design (`hld.md`), and breakdown (`work-items.md`) sit beside this file in `docs/plans/play-58/play-59/`.

## Research findings

### Change surface

| Path | Action | Current state |
| --- | --- | --- |
| `src/guestbook/app.py` | **edit** | 72 lines. `create_app()` factory at `:34` registers two routes (`POST` and `GET /api/guestbook/entries`). Imports: `os`, `datetime`, `Flask`, `jsonify`, `request`, storage, validation. No `time` or `importlib` imports today. |
| `tests/test_healthz.py` | **create** | Does not exist. Follows the convention of `tests/test_guestbook_api.py` (pytest classes, `app`/`client` fixtures, plain asserts). |

No other files change. Specifically not touched: `pyproject.toml`, `src/guestbook/__init__.py`, `src/guestbook/storage.py`, `src/guestbook/validation.py`, `.github/workflows/ci.yml`, `.factory/testing.md`, existing test files.

### Contracts and APIs

- **Package name:** `testbed-utils` (`pyproject.toml:6`). The HLD (§6) specifies `importlib.metadata.version("testbed-utils")` as the version source — this returns the `version = "0.1.0"` declared at `pyproject.toml:7`.
- **Flask app factory:** `create_app()` at `src/guestbook/app.py:34` returns a `Flask` instance. New routes register inside this function using decorators (`@app.get()`), matching the existing `@app.post()` and `@app.get()` at `:46` and `:62`.
- **Endpoint contract:** `GET /healthz` → 200 `application/json` `{"status":"ok","version":"<semver>","uptimeSeconds":<int>}`. Any non-GET method → 405.
- **Test fixtures:** `tests/test_guestbook_api.py` defines `db_path`, `app`, and `client` fixtures at `:16–:28`. The healthz endpoint needs no database, so the test file uses a simpler `app` fixture calling `create_app()` with a throwaway `db_path` (the factory requires it for the guestbook routes).

### Existing test layers and gate

- **Gate:** `pip install -e ".[test]"` then `pytest` (`.factory/testing.md:3`, `.github/workflows/ci.yml:18–21`). No linter, formatter, type checker, or coverage tool.
- **CI:** GitHub Actions, Python 3.12, `ubuntu-latest`. Two jobs: `test` (runs pytest) and `gate` (fails iff `CI_FAIL` exists at root). Workflow-level `permissions: contents: read` at `ci.yml:9–10`.
- **Test convention:** one `Test<Subject>` class per concern, plain `assert` statements, `pytest.raises` for error cases. No `conftest.py`.

### Key stdlib APIs

- `time.monotonic()` — monotonic clock, unaffected by system clock adjustments. Captured once at module-import time as the process start reference.
- `importlib.metadata.version("testbed-utils")` — reads the installed package version at runtime. Raises `PackageNotFoundError` if the package is not installed; acceptable since the app requires installation (console script entry point at `pyproject.toml:18`).
- `logging.Filter` — attached to the `werkzeug` logger to suppress INFO-level request-log records containing `/healthz`.

### Unknowns

None remaining. The HLD resolved all design questions (version source, uptime clock, log suppression mechanism, 405 handling).

## Locked decisions and assumptions

### Locked decisions

| Decision | Source |
| --- | --- |
| Version comes from `importlib.metadata.version("testbed-utils")` | HLD §6 |
| Uptime clock is `time.monotonic()` captured at module-import time | HLD §6 |
| Log suppression via `logging.Filter` on the `werkzeug` logger, checking for `/healthz` in the message | HLD §6 |
| 405 handling delegated to Flask's built-in method routing (`@app.get`) | HLD §6 |
| Response body has exactly three keys: `"status"`, `"version"`, `"uptimeSeconds"` | spec FR3 |
| `"uptimeSeconds"` is truncated (`int()`), not rounded | spec FR3 |
| No authentication | spec FR4 |
| No database queries, no external calls | spec FR5 |

### Assumptions

| Assumption | Evidence | Consequence if wrong |
| --- | --- | --- |
| The `werkzeug` logger's request-log message contains the request path as a substring | Standard Werkzeug request-log format `"<method> <path> ..."`. HLD §7 notes this is stable. | The log filter stops matching; probe requests appear at INFO. Impact is cosmetic (log noise), not functional. Fix: adjust the filter's match string. |
| The `app` fixture in the healthz test file can reuse the same `create_app(db_path=...)` pattern | `tests/test_guestbook_api.py:21–22` | If `create_app()` fails without a DB path, the fixture needs a `tmp_path`-based path. Low risk: the factory always succeeds today. |

## Solution proposal

Add the `/healthz` route, its uptime tracking, and its log filter inside the existing `create_app()` factory in `src/guestbook/app.py`. The change is four additions to that one file:

1. **Imports** (module top): `import time`, `import importlib.metadata`, and `import logging`.
2. **Start timestamp** (module level, below imports): `_START = time.monotonic()` — captured once at import time, measuring process lifetime.
3. **Log filter** (inside `create_app()`, before route registration): a `logging.Filter` subclass (or lambda-style filter function) attached to `logging.getLogger("werkzeug")` that returns `False` for records at INFO level whose message contains `"/healthz"`. This keeps probe requests at DEBUG only without affecting other routes.
4. **Route** (inside `create_app()`): `@app.get("/healthz")` returning `jsonify({"status": "ok", "version": importlib.metadata.version("testbed-utils"), "uptimeSeconds": int(time.monotonic() - _START)})`.

The version string can be read once at module level (cached) or on every request. Module-level is simpler and avoids a per-request metadata lookup; the value cannot change during a process's lifetime.

Flask's `@app.get()` decorator automatically returns 405 for non-GET methods — no custom code needed.

A new test file `tests/test_healthz.py` covers all four acceptance scenarios using the Flask test client, `unittest.mock.patch` for `time.monotonic`, and `caplog` for log-level assertions.

**Alternatives rejected:**
- A separate Blueprint module (`src/guestbook/health.py`): unnecessary indirection for a single three-line route; the existing app has no blueprints.
- Reading version from `__version__` in `src/testbed_utils/__init__.py:28`: couples the guestbook package to the testbed_utils package at import time; `importlib.metadata` is the standard, decoupled accessor.

## Ordered implementation steps

1. **Add imports to `src/guestbook/app.py`.** Add `import time`, `import logging`, and `import importlib.metadata` to the import block (after `from __future__ import annotations`, before the Flask imports). Files: `src/guestbook/app.py:1–8`. Advances: prerequisite for all ACs. Test layer: existing pytest suite (no regression).

2. **Add module-level start timestamp to `src/guestbook/app.py`.** Add `_START = time.monotonic()` below the existing module-level constants (after `_TIMESTAMP_FORMAT` at `:18`). Files: `src/guestbook/app.py`. Advances: AC2 (uptimeSeconds reflects elapsed time). Test layer: `tests/test_healthz.py` (step 5).

3. **Add log filter inside `create_app()` in `src/guestbook/app.py`.** At the start of `create_app()`, after `init_db(resolved)`, attach a `logging.Filter` to `logging.getLogger("werkzeug")` that drops records whose `getMessage()` contains `"/healthz"` and whose level is `INFO` or lower. Files: `src/guestbook/app.py:34–44`. Advances: AC4 (no INFO-level log output for probe requests). Test layer: `tests/test_healthz.py` (step 5).

4. **Add `GET /healthz` route inside `create_app()` in `src/guestbook/app.py`.** Register `@app.get("/healthz")` returning `jsonify({"status": "ok", "version": _VERSION, "uptimeSeconds": int(time.monotonic() - _START)})`, where `_VERSION = importlib.metadata.version("testbed-utils")` is computed once at module level. Files: `src/guestbook/app.py`. Advances: AC1 (happy path — 200 with correct JSON), AC3 (405 for non-GET). Test layer: `tests/test_healthz.py` (step 5).

5. **Create `tests/test_healthz.py`.** Four test classes covering the four acceptance scenarios:

   | Class | Test | Assertion | AC |
   | --- | --- | --- | --- |
   | `TestHealthzHappyPath` | `test_get_returns_200_with_correct_json` | GET `/healthz` → 200, `Content-Type: application/json`, body has exactly keys `"status"`, `"version"`, `"uptimeSeconds"`; `"status" == "ok"`, `"version" == "0.1.0"`, `"uptimeSeconds"` is a non-negative `int`. | AC1 |
   | `TestHealthzUptime` | `test_uptime_reflects_elapsed_time` | Patch `time.monotonic` so that `_START` returns 1000.0 and the request-time call returns 1042.7; assert `"uptimeSeconds" == 42` (truncated, not rounded). | AC2 |
   | `TestHealthzMethodNotAllowed` | `test_post_returns_405` | POST `/healthz` → 405. | AC3 |
   | `TestHealthzMethodNotAllowed` | `test_put_returns_405` | PUT `/healthz` → 405. | AC3 |
   | `TestHealthzLogging` | `test_no_info_log_for_healthz` | With `caplog` at DEBUG level, GET `/healthz`, then assert no captured record at `INFO` or higher. | AC4 |

   Fixtures: `db_path` (via `tmp_path`), `app` (calls `create_app(db_path=...)`), `client` (calls `app.test_client()`), matching the pattern in `tests/test_guestbook_api.py:16–28`. No network calls, no file-system state beyond the test DB, mocked clock for uptime.

   Files: `tests/test_healthz.py` (new). Advances: AC1, AC2, AC3, AC4. Test layer: pytest (`package-api` layer in `.factory/testing.md`).

6. **Verify the gate.** Run `pip install -e ".[test]" && pytest` from the repo root. Confirm: all existing tests still pass; all new tests pass; `git diff --stat` shows exactly two files (`src/guestbook/app.py`, `tests/test_healthz.py`); total change is well under 300 lines; no `CI_FAIL` file exists.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1 | t1 | Add GET /healthz liveness endpoint with tests |
| 2 | t1 | Add GET /healthz liveness endpoint with tests |
| 3 | t1 | Add GET /healthz liveness endpoint with tests |
| 4 | t1 | Add GET /healthz liveness endpoint with tests |
| 5 | t1 | Add GET /healthz liveness endpoint with tests |
| 6 | t1 | Add GET /healthz liveness endpoint with tests |

All steps belong to the single work item t1. No planning gap.

## Verification and CI gate

Run from a clean temporary worktree at the committed SHA:

```bash
pip install -e ".[test]"
pytest
```

This is the repository's canonical gate (`.factory/testing.md`, `test-gate: pytest`; `.github/workflows/ci.yml` `test` job).

The gate must show:

- `pytest` passes — all existing tests (`test_guestbook_api`, `test_dateutils`, `test_textutils`, `test_numutils`, `test_pdfutils`, `test_pdf_extract_cli`, `test_hello`, `test_hello_cli`, `test_num_summary_cli`) still green.
- `tests/test_healthz.py` — all new tests pass (5 tests across 4 classes).
- `git diff --stat` against the base branch shows exactly `src/guestbook/app.py` (edited) and `tests/test_healthz.py` (new).
- Total changed lines well under the 300-line cap (spec §6).
- No `CI_FAIL` file at the repo root.

No change to `.factory/testing.md` or `.github/workflows/ci.yml` is needed — the gate and CI are unchanged.

## Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **Werkzeug log format change.** If Werkzeug changes its request-log message format, the filter may stop matching `/healthz`. | Impact is cosmetic (log noise returns), not functional. The substring match on the path is the most stable approach (HLD §7). |
| **`PackageNotFoundError` at import.** If the package is run without `pip install`, `importlib.metadata.version()` raises. | Acceptable: the app's console entry point (`pyproject.toml:18`) requires installation. Not a new failure mode. |
| **Test client vs Werkzeug request logging.** The Flask test client may not produce Werkzeug request-log records the same way a live server does. | AC4's test verifies the handler itself does not log at INFO+. The filter's live-server behaviour is verified by inspection (HLD §7, accepted limitation). |
| **Scope lock — do NOT:** | Touch `pyproject.toml`, `src/guestbook/storage.py`, `src/guestbook/validation.py`, `src/guestbook/__init__.py`, `src/testbed_utils/`, existing test files, `.github/workflows/ci.yml`, `.factory/testing.md`, or `README.md`. Do not add readiness/deep health checks, authentication, rate limiting, metrics endpoints, configurable response fields, or new runtime dependencies. Do not create `CI_FAIL`. Do not delete, skip, disable, or weaken any existing check. |

## Clarification outcomes

None. All design questions were resolved by the HLD, and no conflict between locked sources and the repository was found.
