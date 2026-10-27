# Feature Specification Document

## 1. Feature Overview

**Summary.** Add a dedicated liveness endpoint at `GET /healthz` to the play1 guestbook application, returning a small JSON body with the service status, build version, and process uptime in seconds.

**Problem statement.** Operators and automated health-check systems (load balancers, Kubernetes kubelets) currently have no lightweight, purpose-built way to verify the guestbook service is alive. Probing business endpoints generates unnecessary database queries, log noise, and couples monitoring to application logic.

**Target users / actors.**
- **Primary:** Automated health-check systems — load balancers, Kubernetes liveness probes — that poll the endpoint at high frequency.
- **Secondary:** Human operators reviewing service status during incident response or deployment verification.

---

## 2. Goals & Non-Goals

### Goals
- Provide a single, stable HTTP endpoint that confirms the service process is running and responsive.
- Return machine-readable metadata (status, version, uptime) so operators can distinguish between instances and detect process restarts.
- Avoid log noise: probe traffic must not pollute operational logs at INFO level or above.
- Ship with automated tests covering the happy path, a boundary case, and an error case, satisfying the play1 success metric that every new capability is trustworthy ("Goals and success metrics", G1).

### Non-Goals
- **Readiness probes or deep health checks** that verify database connectivity or downstream service availability — a separate epic if needed.
- **Authentication or rate limiting** on the health endpoint — the endpoint is explicitly unauthenticated.
- **Metrics or observability endpoints** (such as `/metrics`) — a separate initiative.
- **Custom or configurable response fields** — the response schema is fixed.
- **Performance beyond what pure Python gives** — no C extensions, no async ("Goals and success metrics", Non-goals).

---

## 3. Functional Requirements

**FR1 — Route and method.** The system shall expose an HTTP endpoint at the path `/healthz`. Only the `GET` method is allowed; any other HTTP method shall return HTTP 405 (Method Not Allowed). *(Traces to: R1, R7)*

**FR2 — Response status and content type.** A `GET /healthz` request shall return HTTP 200 with `Content-Type: application/json`. *(Traces to: R1)*

**FR3 — Response body schema.** The JSON response body shall contain exactly three keys — no more, no fewer:
- `"status"` — always the string `"ok"`.
- `"version"` — the package version string declared in `pyproject.toml` (currently `"0.1.0"`).
- `"uptimeSeconds"` — the number of whole seconds (truncated integer, not rounded) since the application process started, as a non-negative integer.

*(Traces to: R1, R2, R3, R4)*

**FR4 — No authentication.** The endpoint shall require no authentication. *(Traces to: R5)*

**FR5 — No side effects.** The endpoint shall make no database queries and no external service calls. *(Traces to: R6)*

**FR6 — Logging level.** Probe requests to `/healthz` shall be logged at `DEBUG` level only. No log record at `INFO` level or higher shall be produced for a `/healthz` request. *(Traces to: R9; mitigates RK1)*

**FR7 — Latency.** The endpoint shall respond in under 50 ms at p95 on an idle instance. *(Traces to: R8)*

**FR8 — Test coverage.** The endpoint shall be covered by automated tests asserting: (a) the happy-path response, (b) at least one boundary case, and (c) at least one error case. Tests shall use the framework test client with no network calls and shall mock the clock for uptime assertions. *(Traces to: R10; satisfies G1 and G4)*

---

## 4. User Experience & Behavior

### Key user flow

| Step | Actor | What happens |
|------|-------|-------------|
| 1 | Load balancer or Kubernetes | Sends `GET /healthz` to the service. |
| 2 | System | Returns HTTP 200 with the fixed JSON body. The caller confirms the service is alive. |

### States the user observes

The endpoint has a single state: **alive.** There is no degraded or unhealthy state — the endpoint either responds (process is alive) or the connection fails (process is down). This is by design: a liveness probe answers "is the process running?", not "are all dependencies healthy?"

### Edge cases and error messages

- **Wrong HTTP method:** The caller receives HTTP 405 with no JSON body. This signals a client misconfiguration, not a service problem.
- **Process restart:** `uptimeSeconds` resets to 0. This is the correct signal — it tells the operator the process restarted, which is exactly what a liveness probe should surface.

### Output format

Example response:
```json
{
  "status": "ok",
  "version": "0.1.0",
  "uptimeSeconds": 3742
}
```

The response body is always a flat JSON object with exactly three keys, in no guaranteed order. Values are a string, a string, and a non-negative integer, respectively.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: GET /healthz returns 200 with the correct JSON body.** Given the application is running, When a GET request is sent to `/healthz`, Then the response status code is 200, the Content-Type is `application/json`, and the body contains exactly the keys `"status"`, `"version"`, and `"uptimeSeconds"`, And `"status"` is `"ok"`, `"version"` is the package version string from pyproject.toml, and `"uptimeSeconds"` is a non-negative integer.

2. **Scenario 2 — Boundary: uptimeSeconds reflects elapsed process time.** Given the application started at a known point in time, When a GET request is sent to `/healthz` after a known interval has elapsed, Then `"uptimeSeconds"` equals the number of whole seconds elapsed since the application started.

3. **Scenario 3 — Error case: non-GET method returns 405.** Given the application is running, When a POST request is sent to `/healthz`, Then the response status code is 405.

4. **Scenario 4 — Edge case: probe requests do not produce INFO-level log output.** Given the application is running with logging captured, When a GET request is sent to `/healthz`, Then no log record at INFO level or higher is produced for that request.

---

## 6. Dependencies & Constraints (product-level)

**Dependencies:**
- Flask (>= 3) — already a declared runtime dependency. No new runtime dependencies are introduced.
- The package version in `pyproject.toml` (currently `"0.1.0"`) is the authoritative source for the `"version"` field.

**Constraints:**
- The change must fit within one module plus its tests and must not exceed 300 changed lines ("Goals and success metrics", G3).
- Tests must finish within the existing CI budget (test job under 60 seconds total) and must not depend on the network, the clock, or file-system state outside test fixtures ("Goals and success metrics", G4).
- No secrets in code, tests, fixtures, or commit messages ("Engineering requirements", R4).
- The pull request must name the story (PLAY-59) and the PRD (PLAY-58) it traces to ("Engineering requirements", R7).

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, data model, error-handling strategy, performance/scaling, security, observability, and the PR-level breakdown are produced by the tech lead in the STRUCTURE stage from this approved product spec.

Product-imposed technical constraints to carry forward:
- The version must come from the package metadata declared in `pyproject.toml`, not from a hardcoded string or environment variable.
- Uptime must measure process lifetime (not container lifetime or wall-clock time of day).
- The logging suppression must be scoped to `/healthz` requests only — it must not affect logging for other routes.

---

## 8. Open Questions

None. All product-level questions have been settled by the epic PRD and the PO's approval of its assumptions.
