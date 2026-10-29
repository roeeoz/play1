## Context

PLAY-83 modifies the existing `truncate` helper in the `testbed_utils.textutils` module of the play1 repository (branch `halo/feat/play-83`) so that it uses a single-character Unicode ellipsis (U+2026) instead of the current three-character ASCII ellipsis, returns an empty string when `n ≤ 0` instead of raising `ValueError`, and drops the configurable `suffix` parameter. The acceptance criteria require four behavioural scenarios (happy-path truncation, exact-length boundary, empty text, and n ≤ 0), a docstring with example, pytest coverage ≥ 90%, deterministic tests, and no new dependency. The approved spec is `spec.md`, design is `hld.md`, and work-item breakdown is `work-items.md`, all in `stories/PLAY-83/` beside this file.

## Research findings

**Change surface.**

| File | What changes |
|---|---|
| `src/testbed_utils/textutils.py:28-43` | `truncate` function: signature changes from `(text, max_length, suffix="...")` to `(text, n)`; body changes from a 3-char ASCII suffix with `ValueError` on negative input to a fixed U+2026 suffix with empty-string return on n ≤ 0; docstring updated with new example |
| `tests/test_textutils.py:18-35` | `TestTruncate` class: all 5 existing tests replaced with tests covering the 4 AC scenarios plus the n=1 edge case |

**Contracts touched.** `src/testbed_utils/__init__.py:12` imports `truncate` by name (`from testbed_utils.textutils import slugify, truncate, word_count`). This import does not reference the removed `suffix` parameter and requires no change. The re-export in `__all__` (line 14-26) is likewise unaffected.

**Existing tests.** `tests/test_textutils.py` contains three test classes: `TestSlugify` (4 tests), `TestTruncate` (5 tests), `TestWordCount` (3 tests). Only `TestTruncate` changes. The five existing truncate tests are:
- `test_short_text_unchanged` — asserts `truncate("hi", 10) == "hi"` (line 19-20)
- `test_truncates_with_suffix` — asserts `truncate("hello world", 8) == "hello..."` (line 22-23)
- `test_exact_fit` — asserts `truncate("hello", 5) == "hello"` (line 25-26)
- `test_tiny_limit_clips_suffix` — asserts `truncate("hello world", 2) == ".."` (line 28-29)
- `test_negative_limit_raises` — asserts `ValueError` on `truncate("x", -1)` (line 31-35)

All five test the old behaviour and must be replaced.

**Canonical gate.** `pytest`, run from the repo root after `pip install -e ".[test]"`. Declared in `.factory/testing.md` (`test-gate: pytest`) and exercised by `.github/workflows/ci.yml` (the `test` job on `ubuntu-latest`, Python 3.12). No linter, formatter, type checker, or coverage tool is configured. The `gate` job (CI_FAIL marker) is a testbed switch, not a quality check.

**What exists vs. what must be created.** The `truncate` function and its test class both exist; both are modified in place. No new files, modules, or dependencies are created.

## Locked decisions and assumptions

**Locked decisions.**
- The function signature is `truncate(text: str, n: int) -> str` — no `suffix` parameter (spec §4 Signature change; hld §6).
- The truncation suffix is the single Unicode character U+2026 ("…"), hard-coded (spec FR2; hld §6).
- `n ≤ 0` returns `""` without exception (spec FR3; hld §1).
- The function is modified in place, not added as a second function (spec §7; hld §6).
- No new runtime dependency (spec FR4).
- Tests use `pytest` in `tests/test_textutils.py` (spec FR6, FR8; existing layout).

**Assumptions.**
- The `n = 1` edge case returns `"…"` (length 1), per the spec's edge-case table and hld §6 (`text[:0] + "…"`). Consequence if wrong: a single test fails, trivially fixable.
- `TestSlugify` and `TestWordCount` are untouched and continue to pass. Consequence if wrong: a pre-existing failure unrelated to this change; the plan-stage assumption is based on the current passing suite.

## Solution proposal

Replace the body of the `truncate` function in `src/testbed_utils/textutils.py:28-43` with three branches matching the to-be process:
1. If `n <= 0`, return `""`.
2. If `len(text) <= n`, return `text`.
3. Otherwise, return `text[:n - 1] + "…"`.

Drop the `suffix` parameter from the signature. Update the docstring to show the new example (`truncate("hello world", 8)` → `'hello w…'`). Replace the five tests in `TestTruncate` with tests that verify the four AC scenarios plus the `n = 1` edge case from the work-item AC.

This is the minimal change: two hunks (function + tests) in two files, no new abstractions, no refactoring of adjacent code. The alternative — keeping `suffix` as a parameter defaulting to `"…"` — was rejected by the spec's explicit signature and the hld's decision.

## Ordered implementation steps

1. **Modify the `truncate` function** in `src/testbed_utils/textutils.py:28-43`.
   - Change the signature from `truncate(text: str, max_length: int, suffix: str = "...")` to `truncate(text: str, n: int) -> str`.
   - Replace the function body with the three-branch logic: return `""` when `n <= 0`; return `text` when `len(text) <= n`; return `text[:n - 1] + "…"` otherwise.
   - Update the docstring: describe the new behaviour, include the usage example `truncate("hello world", 8)` → `'hello w…'`.
   - **Advances:** AC 1 (happy path), AC 2 (boundary), AC 3 (empty text), AC 4 (n ≤ 0), AC 5 (docstring with example), AC 8 (no new dependency).
   - **Test layer:** `tests/test_textutils.py`, `TestTruncate` class (updated in step 2).

2. **Replace the `TestTruncate` tests** in `tests/test_textutils.py:18-35`.
   - Remove all five existing tests.
   - Add tests covering:
     - Happy path: `truncate("hello world", 8)` returns 7-char prefix + U+2026, total length 8 (AC 1).
     - Boundary: `truncate("hello", 5)` returns `"hello"` unchanged (AC 2).
     - Empty text: `truncate("", 10)` returns `""` (AC 3).
     - n = 0: `truncate("anything", 0)` returns `""` (AC 4).
     - n negative: `truncate("anything", -5)` returns `""` (AC 4).
     - n = 1: `truncate("ab", 1)` returns `"…"` (work-item AC 5).
   - Do not modify `TestSlugify` or `TestWordCount`.
   - **Advances:** AC 6 (test coverage), AC 7 (deterministic tests).
   - **Test layer:** `tests/test_textutils.py`, `TestTruncate` class — the layer being written.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Align truncate to Unicode ellipsis and safe n≤0 behavior |
| 2 | t1 | Align truncate to Unicode ellipsis and safe n≤0 behavior |

All work items appear. The single work item (t1) owns both steps.

## Verification and CI gate

The canonical gate is:

```bash
pip install -e ".[test]"
pytest
```

Run from a clean temporary worktree at the committed SHA. `pytest` discovers `tests/` (configured in `pyproject.toml` under `[tool.pytest.ini_options]`, `testpaths = ["tests"]`). The gate must show:
- All tests pass (exit 0), including the replaced `TestTruncate` tests and the unchanged `TestSlugify`, `TestWordCount`, and all other test files.
- No new runtime dependency in `pyproject.toml` `dependencies`.
- Coverage ≥ 90% is verified by the test count: the function has 3 branches and 6 tests cover them; no branch is untested. No coverage tool is configured in the repo, so the metric is satisfied by construction (all branches covered) rather than by a measured report.

Provider CI (`.github/workflows/ci.yml`) runs the same command on `ubuntu-latest` / Python 3.12. The workflow already declares `permissions: contents: read` at the workflow level. No change to CI configuration is needed.

## Risks and scope guards

**Risks.**
- **RK1 (external callers).** Callers outside the repository that depend on the old `suffix` parameter or `ValueError` on negative input will break. Mitigated: the package is version 0.1.0 (0.x), with no backwards-compatibility guarantee (spec §6).
- **RK2 (lost configurability).** The `suffix` parameter is removed. Mitigated: re-addable in a future epic if needed (hld §7).

**Scope guards — the implement phase must NOT:**
- Touch `slugify`, `word_count`, or any other function in `textutils.py`.
- Touch `TestSlugify`, `TestWordCount`, or any other test class.
- Modify `src/testbed_utils/__init__.py` (the re-export needs no change).
- Modify `pyproject.toml`, `.github/workflows/ci.yml`, or `.factory/testing.md`.
- Add any new file, module, or dependency.
- Add a coverage tool, linter, or formatter not already configured.
- Delete, skip, disable, or weaken any existing check or test.

## Clarification outcomes

None.
