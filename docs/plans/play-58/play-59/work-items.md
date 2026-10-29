# Work-item breakdown — Add a GET /healthz liveness endpoint returning status, version, and uptime

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add GET /healthz liveness endpoint with tests | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Add GET /healthz liveness endpoint with tests",
    "summary": "**Intent:** Add a liveness endpoint at GET /healthz to the guestbook Flask application, returning a JSON body with service status, build version, and process uptime. Set a Cache-Control: no-store response header. Suppress probe request logs to DEBUG level only. Ship with automated tests covering all acceptance scenarios.\n\n**Owns:** `src/guestbook/app.py` (edits: add imports, module-level start timestamp, log filter, route registration inside `create_app()`), `tests/test_healthz.py` (creates: new test file).\n**Consumes:** `pyproject.toml` (reads package name for metadata lookup — no edits).\n\n**Acceptance criteria:**\n1. GET /healthz returns HTTP 200 with Content-Type application/json. The body contains exactly three keys: `\"status\"` (string `\"ok\"`), `\"version\"` (the package version string from pyproject.toml, currently `\"0.1.0\"`), and `\"uptimeSeconds\"` (a non-negative integer representing whole seconds since process start, truncated not rounded).\n2. The GET /healthz response includes the header `Cache-Control: no-store`.\n3. A request to /healthz using any HTTP method other than GET (e.g. POST, PUT, DELETE) returns HTTP 405.\n4. When time is mocked so that a known interval elapses between process start and the request, `\"uptimeSeconds\"` equals that interval truncated to a whole integer.\n5. A GET /healthz request produces no log records at INFO level or higher.\n6. The endpoint makes no database queries and no external service calls.\n7. The endpoint requires no authentication.\n8. All existing tests continue to pass.\n9. The total change is under 300 lines.",
    "dependsOn": [],
    "requirementRefs": [],
    "complexity": {
      "scores": {
        "scope_clarity": 0,
        "technical_design_decisions": 0,
        "system_impact": 0,
        "async_distributed_complexity": 0,
        "validation_complexity": 0,
        "risk_unknowns": 0
      },
      "justifications": {
        "scope_clarity": "Every behavior is fully defined in the spec with exact JSON keys, types, values, status codes, headers, and logging level — zero ambiguity.",
        "technical_design_decisions": "No design decisions: follow the existing @app.get() pattern, use stdlib importlib.metadata and time.monotonic(), add a standard logging.Filter, set one response header.",
        "system_impact": "Single component only — adds a route to one Flask app file; touches nothing else.",
        "async_distributed_complexity": "No async or distributed behavior; pure synchronous request-response.",
        "validation_complexity": "Straightforward unit tests using Flask test client and pytest caplog; mock time.monotonic for the boundary case.",
        "risk_unknowns": "All technical questions resolved by research; no unknowns remain."
      },
      "total_score": 0,
      "tier": "T1",
      "engineer_level": "junior",
      "reasoning_effort": "Low",
      "token_budget": "Small",
      "human_decision_required": false
    }
  }
]
```
