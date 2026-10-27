# Work-item breakdown — CLI subcommand: parse two ISO dates and report the day count

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add day-count CLI subcommand and public helper to dateutils | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Add day-count CLI subcommand and public helper to dateutils",
    "summary": "**Intent:** Deliver the complete s1 feature — a new public helper function in `dateutils.py` that accepts two ISO 8601 date strings (with optional trailing Z), validates them, and returns the absolute calendar-day count, plus a CLI entry point registered as a console script, with full test coverage.\n\n**Owns:**\n- `src/testbed_utils/dateutils.py` — adds the new public function and `main()` (does NOT modify existing functions)\n- `src/testbed_utils/__init__.py` — adds the new function to the import and `__all__`\n- `pyproject.toml` — adds one `[project.scripts]` entry\n- `tests/test_dateutils.py` — adds unit tests for the new public function\n- A new CLI test file (e.g. `tests/test_date_range_cli.py`) — CLI-level tests following the repo's `run_main` helper pattern\n\n**Consumes:** existing `dateutils.py` module (read-only, no modification to existing functions), existing CLI and test patterns across the repo.\n\n**Acceptance criteria:**\n1. Given two valid ISO dates (e.g. `2024-01-01` and `2024-01-10`) supplied in either order, the subcommand prints the correct absolute day count and exits 0.\n2. Given two identical ISO dates, the subcommand prints `0` and exits 0.\n3. Given an invalid date argument, the subcommand prints an error message to stderr and exits with code 2, with no unhandled exception or traceback.\n4. Given a date with a trailing Z (e.g. `2024-01-10Z`), the subcommand treats it identically to `2024-01-10`.\n5. `--help` prints a one-line summary and exits 0.\n6. The new public function has a docstring with a runnable example.\n7. Pytest cases cover: happy path (two valid dates), zero-day boundary (identical dates), invalid-date error, trailing-Z acceptance.\n8. CLI-level tests cover the same scenarios through the registered entry point using the repo's `run_main` pattern, and verify exit code 2 on invalid input.\n9. The new public function is re-exported from `__init__.py` and listed in `__all__`.\n10. No new runtime dependency is introduced; stdlib only.\n11. The implementation works on CPython 3.10+.\n12. Total change is within 300 lines.",
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
        "scope_clarity": "Every AC is concrete and enumerated; behavior is fully specified including the exact exit code for invalid input.",
        "technical_design_decisions": "All patterns (argparse, entry point, test harness, __init__ re-export) are established in the repo; follow them exactly.",
        "system_impact": "Single module plus its tests; no cross-component effects.",
        "async_distributed_complexity": "Pure synchronous computation; no async or distributed concerns.",
        "validation_complexity": "Unit tests and CLI tests via the existing run_main harness; straightforward pytest.",
        "risk_unknowns": "Low risk; the trailing-Z strip is a known one-liner, and all integration points are documented in the research."
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
