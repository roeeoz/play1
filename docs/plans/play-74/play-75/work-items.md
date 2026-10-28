# Work-item breakdown — Range-clamping helper with full test coverage

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add clamp test suite and module | T1 |  |
| 2 | t2 | Register clamp in package root | T1 | t1 |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "2a3d4d68-6e17-4c25-bd24-4c5d64979af3",
    "title": "Add clamp test suite and module",
    "summary": "**Intent:** Deliver the test suite for the `clamp` helper and the module that satisfies it, following TDD ordering — tests define the contract, the module implements it. The function lives in a new module following existing `*utils.py` conventions.\n\n**Owns:**\n- `tests/test_clamputils.py` (creates)\n- `src/testbed_utils/clamputils.py` (creates)\n\n**Consumes:** Nothing from a prerequisite ticket; reads existing modules only as convention reference.\n\n**Acceptance criteria:**\n1. `clamp(5, 1, 10)` returns `5`.\n2. `clamp(-3, 0, 10)` returns `0`.\n3. `clamp(15, 0, 10)` returns `10`.\n4. `clamp(1, 1, 10)` returns `1` (boundary: value equals lower bound).\n5. `clamp(10, 1, 10)` returns `10` (boundary: value equals upper bound).\n6. `clamp(7, 10, 5)` raises `ValueError`.\n7. The function's docstring contains a runnable `>>>` example that passes `doctest`.\n8. No new runtime dependency is added to `pyproject.toml`.\n9. `pytest` passes with no failures.",
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
        "scope_clarity": "All behavior is fully defined by acceptance scenarios with exact inputs and outputs; no ambiguity.",
        "technical_design_decisions": "No design decisions — follow the established module, docstring, and test patterns exactly.",
        "system_impact": "Single package, single new module; no cross-component or cross-service impact.",
        "async_distributed_complexity": "Pure synchronous function; no async or distributed concerns.",
        "validation_complexity": "Unit tests only; all cases are deterministic arithmetic comparisons with exact equality.",
        "risk_unknowns": "Zero unknowns — implementation is trivial; all conventions are documented by existing code."
      },
      "total_score": 0,
      "tier": "T1",
      "engineer_level": "junior",
      "reasoning_effort": "Very Low",
      "token_budget": "Small",
      "human_decision_required": false
    }
  },
  {
    "ref": "t2",
    "repoId": "2a3d4d68-6e17-4c25-bd24-4c5d64979af3",
    "title": "Register clamp in package root",
    "summary": "**Intent:** Wire the `clamp` function into the package's public API so it is importable from the package root and listed in `__all__`, completing discoverability.\n\n**Owns:**\n- `src/testbed_utils/__init__.py` (edits: adds import line and `__all__` entry)\n- `tests/test_clamputils.py` (edits: appends package-export and `__all__` verification tests — ownership handoff from t1)\n\n**Consumes:** `src/testbed_utils/clamputils.py` (created by t1; read-only).\n\n**Acceptance criteria:**\n1. `from testbed_utils import clamp` succeeds.\n2. `\"clamp\"` appears in `testbed_utils.__all__`.\n3. Package-root import and `__all__` membership are verified by tests added to the test file.\n4. `pytest` passes with no failures.\n5. No new runtime dependency is added to `pyproject.toml`.\n6. Total changed lines across both PRs ≤ 300.",
    "dependsOn": [
      "t1"
    ],
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
        "scope_clarity": "Fully mechanical — add one import line and one string to an existing list, following the exact pattern of every other module registration.",
        "technical_design_decisions": "None — the registration pattern is established and unambiguous.",
        "system_impact": "Single file edit in one package; no cross-component impact.",
        "async_distributed_complexity": "No async or distributed concerns.",
        "validation_complexity": "Straightforward import-succeeds and list-membership assertions.",
        "risk_unknowns": "Zero unknowns — the registration pattern is used by every existing module."
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
