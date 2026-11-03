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
    "summary": "**Intent:** Add a single assertion to the existing `--help` test so the test suite verifies that the program name \"testbed-hello\" appears in the `--help` output, closing the only gap between the current test and FR3. The work is structured as two commits: the test assertion first, then any needed script change.\n\n**Owns / Consumes:**\n- Owns: `tests/test_hello_cli.py` (adds one assertion to the existing `--help` test)\n- Owns (conditional): `src/testbed_utils/hello.py` (modified only if the assertion from commit 1 fails)\n- Consumes (read-only otherwise): `src/testbed_utils/hello.py`, `pyproject.toml`\n\n**Commit plan:**\n- Commit 1 — `test(cli): assert program name in --help output`: adds the program-name assertion to the `--help` test and runs `pytest` to verify.\n- Commit 2 — `fix(cli): ensure testbed-hello --help includes program name`: if the test from commit 1 fails, makes the minimal change to the script so that `--help` output contains \"testbed-hello\". If the test already passes (research indicates `prog=\"testbed-hello\"` is already set), this commit is omitted.\n\n**Acceptance criteria:**\n1. When `testbed-hello --help` is invoked, stdout contains a usage line that includes the program name \"testbed-hello\" and the exit code is 0.\n2. When `testbed-hello` is invoked without arguments, stdout is \"Hello, world!\\n\" and exit code is 0.\n3. The project's test suite includes a test that invokes `testbed-hello --help`, asserts that stdout contains the substring \"testbed-hello\", asserts that stdout contains \"usage:\", and asserts that the exit code is 0.\n4. `pytest` passes with no failures.\n5. No file outside `tests/test_hello_cli.py` is modified unless the new assertion fails against the current script.\n6. The change is under 300 changed lines (G3) and the test is pure with no network, clock, or filesystem dependency (G4).",
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
        "scope_clarity": "Fully defined: add one assertion to one existing test method, conditionally adjust one line in the script. No ambiguity.",
        "technical_design_decisions": "None: follows the exact pattern of the adjacent assertions in the same method.",
        "system_impact": "Single file (possibly two). No other component affected.",
        "async_distributed_complexity": "None: pure synchronous in-process test.",
        "validation_complexity": "Straightforward: run pytest, one new assertion on deterministic argparse output.",
        "risk_unknowns": "Zero risk: the output is deterministic (prog is hardcoded in argparse), the assertion is a substring check."
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
