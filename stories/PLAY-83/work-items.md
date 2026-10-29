# Work-item breakdown — Align truncate helper to single-character Unicode ellipsis and safe zero-length behavior

| # | Ref | Title | Tier | Depends on |
|---|---|---|---|---|
| 1 | t1 | Align truncate to Unicode ellipsis and safe n≤0 behavior | T1 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "0fcb6992-968b-4373-a63d-0575b37433ef",
    "title": "Align truncate to Unicode ellipsis and safe n≤0 behavior",
    "summary": "**Intent.** Modify the existing `truncate` function to use a single-character Unicode ellipsis (U+2026), return empty string for n ≤ 0, and drop the configurable `suffix` parameter. Update all existing tests to match the new behaviour and add new tests for full coverage.\n\n**Owns:** `src/testbed_utils/textutils.py` (the `truncate` function and its docstring), `tests/test_textutils.py` (the `TestTruncate` class).\n**Consumes (read-only):** `src/testbed_utils/__init__.py` (re-export; no change needed).\n\n**Acceptance criteria:**\n1. Calling `truncate(\"hello world\", 8)` returns a 7-character prefix followed by the single Unicode character U+2026, with total output length exactly 8.\n2. Calling `truncate(\"hello\", 5)` returns `\"hello\"` unchanged — no ellipsis appended.\n3. Calling `truncate(\"\", 10)` returns `\"\"`.\n4. Calling `truncate(\"anything\", 0)` and `truncate(\"anything\", -5)` each return `\"\"` without raising an exception.\n5. Calling `truncate(\"ab\", 1)` returns `\"…\"` (the single Unicode ellipsis, length 1).\n6. The function signature is `truncate(text: str, n: int) -> str` — no `suffix` parameter.\n7. The function has a docstring containing a usage example.\n8. pytest tests exist covering scenarios 1–5 above; all pass.\n9. Package test-suite coverage remains ≥ 90%.\n10. No new runtime dependency is introduced.\n11. Tests do not depend on the network, clock, or file-system state.",
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
        "scope_clarity": "Fully defined: exact signature, exact behavior for every branch, exact edge cases enumerated in the spec.",
        "technical_design_decisions": "None: the spec dictates the exact algorithm (three branches), the exact suffix character, and the exact signature. No design choices remain.",
        "system_impact": "Single function in a single module; no other component or service is affected.",
        "async_distributed_complexity": "None: pure synchronous string function.",
        "validation_complexity": "Unit tests only: pure function with deterministic string inputs/outputs, no integration or external dependencies.",
        "risk_unknowns": "Low and predictable: the function is self-contained, the package is 0.x with no compat guarantee, and the change is well-understood."
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
