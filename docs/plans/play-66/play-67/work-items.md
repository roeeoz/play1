# Work-item breakdown — Verify testbed-hello prints a usage line on --help and exits 0

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Assert program name in testbed-hello --help test | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Assert program name in testbed-hello --help test",
    "summary": "**Intent:** Add a single assertion to the existing `test_help` method in the CLI test suite so it verifies that the program name \"testbed-hello\" appears in the `--help` output, closing the only gap between the current test and FR3.\n\n**Owns / Consumes:**\n- Owns: `tests/test_hello_cli.py` (adds one assertion line to `TestHelp.test_help`)\n- Consumes (read-only): `src/testbed_utils/hello.py`, `pyproject.toml`\n\n**Acceptance criteria:**\n1. When `testbed-hello --help` is invoked, stdout contains a usage line that includes the program name \"testbed-hello\" and the exit code is 0 (FR1 — already true, verified by existing + new assertion).\n2. When `testbed-hello` is invoked without arguments, stdout is \"Hello, world!\\n\" and exit code is 0 (FR2 — already true, verified by existing `test_prints_greeting`).\n3. The `TestHelp.test_help` test asserts that stdout contains the substring \"testbed-hello\" in addition to its existing assertions for \"usage:\", exit code 0, and empty stderr (FR3 gap closure).\n4. `pytest` passes with no failures.\n5. No file outside `tests/test_hello_cli.py` is modified.\n6. The change is under 300 changed lines (G3) and the test is pure with no network, clock, or filesystem dependency (G4).",
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
        "scope_clarity": "Fully defined: add one assertion to one existing test method. No ambiguity.",
        "technical_design_decisions": "None: follows the exact pattern of the adjacent assertions in the same method.",
        "system_impact": "Single file, single test method. No other component affected.",
        "async_distributed_complexity": "None: pure synchronous in-process test.",
        "validation_complexity": "Straightforward: run pytest, one new assertion on deterministic argparse output.",
        "risk_unknowns": "Zero risk: the output is deterministic (prog='testbed-hello' is hardcoded in argparse), the assertion is a substring check."
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
