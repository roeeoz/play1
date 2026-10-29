# High-Level Design — PLAY-59: GET /healthz Liveness Endpoint

## 1. System Overview

- **What is being built:** A liveness endpoint at `GET /healthz` on the existing guestbook Flask application, returning a fixed JSON body with service status, build version, and process uptime.
- **Problem:** No lightweight probe path exists; monitoring tools must hit business endpoints, generating DB queries and log noise.
- **Key responsibilities:** Respond to GET with a fixed JSON body; reject other methods with 405; suppress probe log noise to DEBUG only; prevent caching of liveness replies.

## 2. Architecture Overview

- **Component:** Single new route registered inside the existing `create_app()` factory in `src/guestbook/app.py`.
- **Boundaries:** The health route is self-contained — no database, no external calls, no authentication. It reads only stdlib state (monotonic clock, package metadata).
- **External dependencies:** None new. Uses `importlib.metadata` and `time` from the stdlib; Flask (already declared) for routing and `jsonify`.

## 3. Data Flow Design

1. HTTP request arrives at `/healthz`.
2. Flask routes GET to the handler; non-GET methods get Flask's automatic 405.
3. Handler computes `int(time.monotonic() - _START)`, reads the cached package version, builds the JSON response via `jsonify`, sets `Cache-Control: no-store` on the response, and returns HTTP 200.
4. A `logging.Filter` on the `werkzeug` logger drops INFO-level request-log records whose message contains `/healthz`.

## 4. Component Breakdown

| Component | Responsibility | Repository |
|---|---|---|
| `/healthz` route + uptime tracking + log filter | Serve the liveness JSON with no-store caching; suppress probe log noise | roeeoz/play1 |
| `tests/test_healthz.py` | Automated tests for all acceptance scenarios | roeeoz/play1 |

## 5. Interface Contracts

- **Endpoint:** `GET /healthz` → 200 `application/json` `{"status":"ok","version":"<semver>","uptimeSeconds":<int>}`
- **Response headers:** `Cache-Control: no-store` on every 200 response.
- **Error:** Any non-GET method → 405.

## 6. Key Technical Decisions

- **Version source:** `importlib.metadata.version("testbed-utils")` — the only reliable runtime accessor for the pyproject.toml version; no new dependency.
- **Uptime clock:** `time.monotonic()` captured at module-import time — monotonic, platform-safe, measures process lifetime.
- **Log suppression:** A `logging.Filter` on the `werkzeug` logger checking for `/healthz` in the log message — scoped, non-invasive, no effect on other routes.
- **405 handling:** Delegated to Flask's built-in method routing — no custom code needed.
- **Cache-Control header:** `no-store` set on the Flask response object before returning — ensures load balancers and intermediate proxies never serve a stale liveness reply.

## 7. Risks & Constraints

- **Werkzeug log format stability:** If Werkzeug changes its request-log message format, the filter may stop matching. Impact is cosmetic (log noise returns), not functional. Mitigation: substring match on the request path, which is stable.
- **`PackageNotFoundError`:** If the package is not pip-installed, `importlib.metadata.version()` raises. Acceptable: the app cannot run un-installed anyway (console script entry point).
- **Test client produces no Werkzeug request logs:** AC4 test verifies the handler itself does not log at INFO+; the filter's dev-server behavior is verified by inspection. Accepted limitation.
