# Work-item breakdown — Health-check endpoint returning service status

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add GET /healthz endpoint with logging exclusion and tests | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Add GET /healthz endpoint with logging exclusion and tests",
    "summary": "**Intent:** Add a GET `/healthz` health-check endpoint to the play1 guestbook Flask application and an application-level request-logging hook that excludes `/healthz` from logs, so deployment infrastructure can poll liveness without side effects or log noise.\n\n**Owns / Consumes:**\n- Owns (create): `tests/test_healthz.py` — new test file covering all acceptance criteria.\n- Owns (modify): `src/guestbook/app.py` — adds the `/healthz` route and an `after_request` logging hook inside `create_app()`.\n- Consumes (read-only): existing `create_app()` factory pattern, `flask.jsonify`, pytest fixtures pattern from `tests/test_guestbook_api.py`.\n\n**Ordered steps:**\n1. **Commit: \"Add tests for GET /healthz health-check endpoint\"** — creates `tests/test_healthz.py` with all acceptance-criteria test cases. Tests will not pass yet because the endpoint does not exist.\n2. **Commit: \"Add GET /healthz endpoint with logging exclusion\"** — modifies `src/guestbook/app.py` to register the `/healthz` route and the `after_request` logging hook inside `create_app()`. All new tests pass after this commit.\n3. **Verify: \"Run new healthz tests in isolation\"** — execute `pytest tests/test_healthz.py` and confirm all new healthz tests pass independently before the full gate.\n4. **Gate: \"Run full test suite\"** — execute `pytest` and confirm all existing and new tests pass with no regressions.\n\n**Acceptance criteria:**\n1. GET `/healthz` returns HTTP 200 with body `{\"status\":\"ok\",\"service\":\"play1\"}` and `Content-Type: application/json`.\n2. GET `/healthz` with no authentication headers or credentials returns HTTP 200 with the same JSON body (endpoint is accessible without authentication).\n3. The round-trip time of GET `/healthz` through the Flask test client is under 100 ms.\n4. When request logging is active, a GET to `/healthz` produces no log entry in the application request log, while a request to another endpoint (e.g. `/api/guestbook/entries`) does produce a log entry (positive control).\n5. POST `/healthz` returns HTTP 405 Method Not Allowed and the response body does not contain the health-check JSON object.\n6. The handler function carries a docstring.\n7. `pytest tests/test_healthz.py` passes (dedicated verification of new tests in isolation).\n8. `pytest` (full suite) passes — all existing tests continue to pass.",
    "dependsOn": [],
    "requirementRefs": [],
    "complexity": {
      "scores": {
        "scope_clarity": 0,
        "technical_design_decisions": 1,
        "system_impact": 0,
        "async_distributed_complexity": 0,
        "validation_complexity": 0,
        "risk_unknowns": 0
      },
      "justifications": {
        "scope_clarity": "All behavior is fully specified across FR1–FR7 and five acceptance scenarios; no ambiguity.",
        "technical_design_decisions": "The logging-exclusion mechanism (after_request hook vs. logging filter) requires a local design choice, but the research findings already recommend the after_request approach.",
        "system_impact": "Single component — one route and one hook added inside the existing Flask app factory.",
        "async_distributed_complexity": "None — synchronous static response, no distributed systems.",
        "validation_complexity": "Straightforward unit tests using the Flask test client and caplog; no integration or multi-system testing.",
        "risk_unknowns": "Low and predictable — static endpoint, existing framework patterns, no new dependencies."
      },
      "total_score": 1,
      "tier": "T1",
      "engineer_level": "junior",
      "reasoning_effort": "Low",
      "token_budget": "Small",
      "human_decision_required": false
    }
  }
]
```
