# Work-item breakdown — Clamp helper that bounds a numeric value to a given range

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add clamp module with tests and package re-export | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "2a3d4d68-6e17-4c25-bd24-4c5d64979af3",
    "title": "Add clamp module with tests and package re-export",
    "summary": "Intent: Deliver PLAY-79 in full — a stdlib-only clamp module in the testbed_utils package with full branch pytest coverage and a docstring example. The implementation is split into two named commits: tests first, then the helper module and package registration.\n\nOwns: tests/test_clamp.py (new, commit 1), src/testbed_utils/clamp.py (new, commit 2), src/testbed_utils/__init__.py (edit, commit 2). Consumes: existing style and conventions in src/testbed_utils/numutils.py, tests/test_numutils.py (read only). Does NOT touch pyproject.toml, CI, or any other module.\n\nCommits:\n- Commit 1 — \"Add tests for clamp helper\": creates tests/test_clamp.py with all test classes and cases.\n- Commit 2 — \"Add clamp module and register in package API\": creates src/testbed_utils/clamp.py and edits src/testbed_utils/__init__.py to import and re-export clamp.\n\nAcceptance criteria:\n- clamp(5, 1, 10) returns 5 (value within range, returned unchanged).\n- clamp(1, 1, 10) returns 1 (value equals low bound, returned unchanged).\n- clamp(10, 1, 10) returns 10 (value equals high bound, returned unchanged).\n- clamp(-3, 1, 10) returns 1 (value below low bound, clamped to low).\n- clamp(15, 1, 10) returns 10 (value above high bound, clamped to high).\n- clamp(any, 10, 1) raises ValueError whose message names the violated constraint and shows the received values.\n- from testbed_utils import clamp works and \"clamp\" appears in testbed_utils.__all__.\n- The clamp function's docstring contains a runnable >>> example with literal expected output; the test file verifies the example is correct.\n- tests/test_clamp.py covers all six branches using in-memory values only and the full pytest suite passes.\n- Module uses only the standard library; no change to pyproject.toml dependencies; no new files outside the owned set.",
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
        "scope_clarity": "Six concrete input/output scenarios plus a package-export check pin every behaviour; all paths are settled.",
        "technical_design_decisions": "Follows the existing numutils/textutils module pattern exactly; the arithmetic is trivial.",
        "system_impact": "One new module plus a two-line re-export in the same package; no cross-component effect.",
        "async_distributed_complexity": "Pure synchronous function, no I/O, no events.",
        "validation_complexity": "Plain pytest unit tests over literal numeric values; no integration or external systems.",
        "risk_unknowns": "Stdlib only, exact integer results, no external surface, no unknowns."
      },
      "total_score": 0,
      "tier": "T1",
      "engineer_level": "junior",
      "reasoning_effort": "Very Low",
      "token_budget": "Small",
      "human_decision_required": false
    }
  }
]
```
