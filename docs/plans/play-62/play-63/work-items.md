# Work-item breakdown — testbed-hello prints its version when invoked with --version

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add --version flag to testbed-hello and test all acceptance scenarios | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Add --version flag to testbed-hello and test all acceptance scenarios",
    "summary": "**Intent:** Register a `--version` argument on the existing argparse parser in the `testbed-hello` console script so it prints `0.1.0` to stdout and exits 0, then add tests covering all four acceptance scenarios.\n\n**Owns:** `src/testbed_utils/hello.py` (modify), `tests/test_hello_cli.py` (modify — new test class).\n**Consumes:** existing `run_main` test helper in `tests/test_hello_cli.py`.\n\n**Acceptance criteria:**\n1. `testbed-hello --version` prints exactly `0.1.0` to stdout, exits with code 0, and prints nothing to stderr.\n2. `testbed-hello` with no arguments prints `Hello, world!` to stdout and exits 0 (unchanged).\n3. `testbed-hello --help` prints a usage message containing the one-line description to stdout and exits 0 (unchanged).\n4. `testbed-hello --bogus` prints a usage error to stderr and exits with code 2 (unchanged).\n5. All existing tests in `tests/test_hello_cli.py` continue to pass without modification.\n6. Total diff is under 300 changed lines.",
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
        "scope_clarity": "Fully defined — the spec names the exact file, the exact string, and the exact behavior. No ambiguity.",
        "technical_design_decisions": "None — argparse's built-in version action is the single obvious, idiomatic approach.",
        "system_impact": "Single module, single test file, no other component affected.",
        "async_distributed_complexity": "None — pure synchronous CLI flag, no async or distributed behavior.",
        "validation_complexity": "Unit tests only, using the existing run_main helper. Straightforward.",
        "risk_unknowns": "Zero unknowns — argparse version action behavior is well-documented and stable."
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
