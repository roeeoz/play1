# Work-item breakdown — Clamp helper that bounds a value to an inclusive range

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
    "summary": "**Intent:** Deliver PLAY-81 in full — a stdlib-only clamp module in the testbed_utils package with pytest coverage for the happy path, boundary and error cases, and a docstring example, in the repo's established style.\n\n**Owns:** `src/testbed_utils/clamp.py` (new), `tests/test_clamp.py` (new), `src/testbed_utils/__init__.py` (edit: import clamp and add to `__all__`).\n**Consumes (read-only):** existing style/conventions in `src/testbed_utils/numutils.py`, `src/testbed_utils/textutils.py`, `src/testbed_utils/dateutils.py`, and `tests/test_numutils.py`. Does NOT touch `pyproject.toml`, CI, or any other module or test file.\n\n**Acceptance criteria:**\n- `clamp(5, 0, 10)` returns `5` (value within range returned unchanged).\n- `clamp(-3, 0, 10)` returns `0` (value below range clamped to low).\n- `clamp(15, 0, 10)` returns `10` (value above range clamped to high).\n- `clamp(42, 7, 7)` returns `7` (boundary: low equals high, any value returns that bound).\n- `clamp(5, 10, 5)` raises `ValueError` (low strictly greater than high).\n- `from testbed_utils import clamp` succeeds and `'clamp'` appears in `testbed_utils.__all__`.\n- The function has a docstring with at least one `>>>` example; the example is verified by running `doctest.testmod` on the clamp module in the test file.\n- `tests/test_clamp.py` follows the existing layout: `TestClamp` class with happy-path, boundary, and error tests; `TestPackageExports` class checking import and `__all__`; `TestDocstringExamples` class verifying the docstring example runs and passes.\n- Module uses `from __future__ import annotations` and only the standard library; no change to `pyproject.toml` dependencies.\n- Full pytest suite passes; all tests use only literal numeric inputs with no network, clock, or filesystem dependencies.",
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
        "scope_clarity": "Seven concrete acceptance scenarios with exact input/output values; module path, test path, and __init__.py edit are all specified.",
        "technical_design_decisions": "Follows the established numutils/textutils/dateutils pattern exactly; the clamping expression is a single well-known idiom.",
        "system_impact": "One new module plus a one-line import and one __all__ entry in the same package.",
        "async_distributed_complexity": "Pure synchronous function, no I/O.",
        "validation_complexity": "Plain pytest unit tests over literal numeric values.",
        "risk_unknowns": "Stdlib only, exact numeric results verified, no external surface."
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
