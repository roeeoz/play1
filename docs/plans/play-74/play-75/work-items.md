# Work-item breakdown — Range-clamping helper with full test coverage

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add clamp helper module with tests and package registration | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "2a3d4d68-6e17-4c25-bd24-4c5d64979af3",
    "title": "Add clamp helper module with tests and package registration",
    "summary": "**Intent:** Deliver the `clamp(value, low, high)` function as a new module in the testbed-utils package, with full test coverage and package-root registration, following existing module and test conventions.\n\n**Owns:**\n- `src/testbed_utils/clamputils.py` (creates)\n- `tests/test_clamputils.py` (creates)\n- `src/testbed_utils/__init__.py` (edits: adds import and `__all__` entry)\n\n**Consumes:** Nothing from a prerequisite ticket; reads existing modules only as convention reference.\n\n**Acceptance criteria:**\n1. `clamp(5, 1, 10)` returns `5`.\n2. `clamp(-3, 0, 10)` returns `0`.\n3. `clamp(15, 0, 10)` returns `10`.\n4. `clamp(1, 1, 10)` returns `1` (boundary: value equals lower bound).\n5. `clamp(10, 1, 10)` returns `10` (boundary: value equals upper bound).\n6. `clamp(7, 10, 5)` raises `ValueError`.\n7. `from testbed_utils import clamp` succeeds, `\"clamp\"` appears in `testbed_utils.__all__`, and the function's docstring contains a runnable `>>>` example that passes `doctest`.\n8. No new runtime dependency is added to `pyproject.toml`.\n9. `pytest` passes with no failures.\n10. Total changed lines ≤ 300.",
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
        "scope_clarity": "All behavior is fully defined by 7 acceptance scenarios with exact inputs and outputs; no ambiguity.",
        "technical_design_decisions": "No design decisions needed — follow the established module, docstring, test, and registration patterns exactly.",
        "system_impact": "Single package, single new module; no cross-component or cross-service impact.",
        "async_distributed_complexity": "Pure synchronous function; no async or distributed concerns.",
        "validation_complexity": "Unit tests only; all cases are deterministic arithmetic comparisons with exact equality.",
        "risk_unknowns": "Zero unknowns — implementation is a one-liner with a guard clause; all conventions are documented by existing code."
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
