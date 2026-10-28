# Work-item breakdown — Add a tested and documented word_count helper to the guestbook package

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Add word_count function and tests to the guestbook package | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Add word_count function and tests to the guestbook package",
    "summary": "**Intent:** Deliver the `word_count` pure helper function in a new module within the guestbook package, with a docstring containing a usage example, and a companion pytest test file exercising all acceptance scenarios. The PR description must reference story PLAY-69 and the Sanity R2b epic PRD, and note the relationship to `testbed_utils.textutils.word_count` and the reason for separate placement.\n\n**Owns:** `src/guestbook/text_utils.py` (new), `tests/test_text_utils.py` (new).\n**Consumes:** existing `src/guestbook/__init__.py` (read-only, no modification).\n\n**Plan-level note:** Implementation uses a red-green commit split — commit 1 adds the test file (red), commit 2 adds the helper module (green).\n\n**Acceptance criteria:**\n1. A module `src/guestbook/text_utils.py` exists and exports a public function importable as `from guestbook.text_utils import word_count`.\n2. `word_count(\"The quick brown fox\")` returns `4`.\n3. A string with words separated by mixed spaces, tabs, and newlines returns the correct count; leading and trailing whitespace does not inflate the count.\n4. `word_count(\"\")` returns `0`; `word_count(\"   \\t\\n\")` returns `0`.\n5. `word_count(None)` and `word_count(42)` each raise `TypeError` or `AttributeError`, not a numeric result.\n6. The function's docstring contains at least one usage example showing a sample call and the expected integer result.\n7. The function uses only the Python standard library — no new runtime dependency added to `pyproject.toml`.\n8. No existing file in the repository is modified.\n9. `pip install -e \".[test]\" && pytest` passes with all existing and new tests succeeding.\n10. All new tests are pure string-in / int-out with no network, clock, or file-system dependency.",
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
        "scope_clarity": "Fully defined: function signature, behavior, edge cases, and test scenarios are all specified in the acceptance criteria.",
        "technical_design_decisions": "None: follows existing patterns in the repo (see testbed_utils.textutils.word_count for the identical pattern).",
        "system_impact": "Single new module in one package; no change to any existing component.",
        "async_distributed_complexity": "None: pure synchronous function with no I/O.",
        "validation_complexity": "Straightforward unit tests only — pure string-in / int-out assertions and pytest.raises checks.",
        "risk_unknowns": "Low and predictable: trivial stdlib-only function with well-understood behavior."
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
