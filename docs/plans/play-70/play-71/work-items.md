# Work-item breakdown — Add a parameterized greeting helper to the package

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add greet(name) function with tests and package export | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0c37cf68-9f61-4770-8831-eff12a27d066",
    "title": "Add greet(name) function with tests and package export",
    "summary": "**Intent.** Deliver the `greet` parameterized greeting function to the testbed-utils package, covering implementation, type validation, docstring, package-root export, and full test coverage — the complete story in one PR.\n\n**Owns:**\n- `src/testbed_utils/hello.py` — adds the `greet` function (shared ownership with existing `hello_world`; extends the file).\n- `src/testbed_utils/__init__.py` — adds `greet` to the import line and `__all__` (extends the file).\n- `tests/test_hello.py` — adds test classes/cases for `greet` (extends the file).\n\n**Consumes:** existing module conventions, existing CI pipeline (`pytest`).\n\n**Acceptance criteria:**\n1. Calling the function with the string `\"World\"` returns the exact string `\"Hello, World!\"`.\n2. Calling the function with an empty string returns the exact string `\"Hello, !\"`.\n3. Calling the function with a non-string value (e.g. an integer or `None`) raises an error whose message indicates the input must be a string.\n4. The function is importable from the package root: `from testbed_utils import greet` succeeds.\n5. The function appears in `testbed_utils.__all__`.\n6. The function has a docstring containing a usage example showing a call with a name argument and its return value.\n7. The docstring example passes when verified via `doctest`.\n8. pytest test cases cover the happy path, boundary (empty string), and error (non-string) scenarios.\n9. No test depends on the network, clock, or filesystem state.\n10. No new runtime dependency is introduced.\n11. The total change is within one module plus its tests and under 300 changed lines.",
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
        "scope_clarity": "Fully defined: exact input/output format, error behavior, export convention, and test expectations are all specified.",
        "technical_design_decisions": "None: follows the existing hello_world pattern in the same module with the same conventions.",
        "system_impact": "Single component — one function added to one module in one package.",
        "async_distributed_complexity": "None: pure synchronous function with no I/O.",
        "validation_complexity": "Unit tests only — three pure-function assertions plus a doctest check.",
        "risk_unknowns": "Low and predictable: no unknowns, no side effects, name collision already ruled out."
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
