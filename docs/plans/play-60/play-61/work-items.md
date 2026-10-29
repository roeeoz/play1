# Work-item breakdown — QA-B: add an `initials(name)` helper to play1 with unit tests

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | PLAY-61: add initials(name) helper to textutils with export and tests | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "PLAY-61: add initials(name) helper to textutils with export and tests",
    "summary": "**Intent:** Add the `initials(name)` pure-Python helper to the testbed-utils package, export it from the public API, and ship unit tests — delivering the complete PLAY-61 story in a single PR.\n\n**Owns:** `src/testbed_utils/textutils.py` (append new function after existing functions), `src/testbed_utils/__init__.py` (add to import and `__all__`), `tests/test_textutils.py` (add new test class at end of file).\n**Consumes:** Existing content of the three files above (read, extend in-place).\n\n**Acceptance criteria:**\n1. `from testbed_utils import initials` succeeds — the function is importable from the package's public API.\n2. `initials(\"Ada Lovelace\")` returns `\"AL\"` — first letter of each whitespace-separated word, uppercased, concatenated without separators.\n3. `initials(\"Ada\")` returns `\"A\"` — single-word input yields one initial.\n4. `initials(\"\")` returns `\"\"` — empty input yields an empty string.\n5. `initials(\"  Ada   Lovelace  \")` returns `\"AL\"` — leading, trailing, and repeated whitespace are ignored.\n6. The function's docstring contains a usage example showing input and expected output.\n7. Running `pytest` passes all new tests AND all existing tests for `slugify`, `truncate`, and `word_count` — no regressions.\n8. No new runtime dependencies are added to `pyproject.toml`.\n9. Total changed lines are under 300.",
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
        "scope_clarity": "Fully defined — exact input/output pairs specified in acceptance criteria, existing pattern to follow.",
        "technical_design_decisions": "None — the implementation follows the identical pattern used by word_count in the same module.",
        "system_impact": "Single module in a single package; no cross-component effects.",
        "async_distributed_complexity": "None — pure synchronous function with no I/O.",
        "validation_complexity": "Unit tests only, using plain asserts with literal inputs; no integration or external dependencies.",
        "risk_unknowns": "Low and predictable — the approach (str.split) is already proven in the same module by word_count."
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
