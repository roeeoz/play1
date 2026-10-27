# Implementation plan — PLAY-61

## Context

PLAY-61 adds a pure-Python `initials(name: str) -> str` helper to the `testbed_utils.textutils` module in the roeeoz/play1 repository, branch `halo/feat/play-61`. The function returns the uppercase first letter of each whitespace-separated word, concatenated without separators. It must handle empty input (return `""`) and extra whitespace (leading, trailing, repeated). The change includes exporting the function from the package's public API and adding unit tests to the existing test file. The sibling documents `spec.md`, `hld.md` and `work-items.md` sit beside this file in `docs/plans/play-60/play-61/`.

## Research findings

**Change surface — existing files to extend:**

| File | Current state | Change |
|---|---|---|
| `src/testbed_utils/textutils.py:46–52` | Three functions: `slugify`, `truncate`, `word_count`. `word_count` is the last function (lines 46–52) and uses `str.split()` — the same approach `initials` will use. | Append `initials` after `word_count`. |
| `src/testbed_utils/__init__.py:12` | Imports `slugify`, `truncate`, `word_count` from `textutils`; lists them in `__all__` (lines 14–26). | Add `initials` to the import and to `__all__` (alphabetical order). |
| `tests/test_textutils.py:38–47` | Three test classes: `TestSlugify`, `TestTruncate`, `TestWordCount`. Imports the three functions on line 1. | Add `initials` to the import; append `TestInitials` class after `TestWordCount`. |

**Contracts touched:** The package's public API (`__all__` in `__init__.py`). No cross-repo contracts, no schemas, no external data.

**Canonical gate:** `pytest` (discovered from `pyproject.toml:27` `[tool.pytest.ini_options]` and `.factory/testing.md:3` `test-gate: pytest`). Precondition: `pip install -e ".[test]"`. No linter, formatter, type checker, or coverage tool is configured. CI runs in `.github/workflows/ci.yml:14–24` on Python 3.12.

**What already exists vs. what must be created:**
- Exists: the `textutils` module, the export pattern in `__init__.py`, the test file and its class-per-function convention, the pytest gate, CI configuration.
- Must be created: the `initials` function (new), its `__init__.py` export (addition), the `TestInitials` class (new).

**No unknowns remain.** The implementation is a single pure function following an established pattern (`word_count` at `textutils.py:46`). No external dependencies, no generated deliverables, no large binaries.

## Locked decisions and assumptions

**Locked decisions:**

- The function signature is `def initials(name: str) -> str` (spec FR1, hld §5).
- The implementation uses `str.split()` with no arguments to handle all whitespace variants in one call (hld §6).
- The function is appended to `textutils.py`, exported from `__init__.py`, and tested in `tests/test_textutils.py` (hld §4, work-items.md t1).
- ASCII input only; Unicode handling is out of scope (spec §2 Non-Goals).
- No new runtime dependencies (spec FR5, `pyproject.toml` unchanged).

**Assumptions:**

- The `initials` entry in `__all__` is inserted in alphabetical order between `humanize_delta` and `is_weekend`. Evidence: the existing `__all__` list follows import order, which groups by module; within the textutils group (`slugify`, `truncate`, `word_count`), the new entry follows alphabetical convention. Consequence if wrong: no runtime effect; a style nit at review.

## Solution proposal

Append a four-line `initials` function after `word_count` in `textutils.py`, using the generator-expression idiom `"".join(w[0].upper() for w in name.split())` identified in hld §6. This handles empty input (`.split()` returns `[]`, `"".join([])` returns `""`) and extra whitespace (`.split()` collapses all runs) with no branching. The function carries a one-line docstring with a `>>>` usage example, matching the docstring convention of `slugify`, `truncate`, and `word_count`. No alternative was considered; the design is locked in the hld.

Export the function by adding `initials` to the import line and to `__all__` in `__init__.py`. Add a `TestInitials` class with four test methods to `test_textutils.py`, covering AC 1–4. AC 5 (docstring) is verified by inspection. AC 6 (full suite green) is verified by the gate.

Total estimated change: ~25 lines across three files, well under the 300-line cap (G3).

## Ordered implementation steps

1. **Add `initials` to `src/testbed_utils/textutils.py` after `word_count` (line 52).** Define `def initials(name: str) -> str` with a docstring containing a `>>>` example. Body: `return "".join(w[0].upper() for w in name.split())`. No new imports needed. Advances AC 1–5. Covered by test layer `package-api` (pytest).

2. **Export `initials` from `src/testbed_utils/__init__.py`.** Add `initials` to the `from testbed_utils.textutils import …` line (line 12) and to `__all__` (alphabetical position after `humanize_delta`). Advances AC 1 (importable from public API). Covered by test layer `package-api`.

3. **Add `TestInitials` to `tests/test_textutils.py`.** Add `initials` to the import on line 1. Append a `TestInitials` class with four methods:
   - `test_multi_word` — `initials("Ada Lovelace") == "AL"` (AC 1).
   - `test_single_word` — `initials("Ada") == "A"` (AC 2).
   - `test_empty` — `initials("") == ""` (AC 3).
   - `test_extra_whitespace` — `initials("  Ada   Lovelace  ") == "AL"` (AC 4).

   Advances AC 1–4, 6. Covered by test layer `package-api`.

4. **Run `pytest` from the repo root** (after `pip install -e ".[test]"`). All new and existing tests must pass (AC 6). This is the canonical gate.

No implicit invariants apply (no authorization, no concurrency, no persistence, no validation beyond empty-string handling already covered). No dependencies to acquire beyond the existing `pytest` test extra. No generated deliverables, no large binaries, no CI changes, no `.factory/testing.md` update needed.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | PLAY-61: add initials(name) helper to textutils with export and tests |
| 2 | t1 | PLAY-61: add initials(name) helper to textutils with export and tests |
| 3 | t1 | PLAY-61: add initials(name) helper to textutils with export and tests |
| 4 | t1 | PLAY-61: add initials(name) helper to textutils with export and tests |

## Verification and CI gate

**Canonical gate:** `pytest`, run from the repository root after `pip install -e ".[test]"` (`.factory/testing.md:3`).

**Required test layer:**

| Layer | Class | Command | Run by |
|---|---|---|---|
| `package-api` | production-path | `pytest` | canonical-gate (`.github/workflows/ci.yml`, `test` job, Python 3.12) |

**Gate-green criteria:** All tests pass, including the existing `TestSlugify`, `TestTruncate`, and `TestWordCount` classes (no regressions — RK1). The `pytest` exit code is 0. No CI configuration changes are needed; the existing workflow already runs `pytest` on pull requests.

The gate can run locally in a pod (`pip install -e ".[test]" && pytest`). Provider proof comes from the CI run at the PR head.

## Risks and scope guards

**Risks:**

| Risk | Severity | Mitigation |
|---|---|---|
| RK1 — Regression in existing helpers | Low | The change is append-only in all three files. Existing test classes are untouched. The gate runs the full suite. |

**Scope guards — the implement phase must NOT:**

- Modify the existing `slugify`, `truncate`, or `word_count` functions or their tests.
- Add Unicode/non-ASCII handling, configurable separators, or a CLI wrapper.
- Add new runtime dependencies to `pyproject.toml`.
- Change CI configuration (`.github/workflows/ci.yml`).
- Change `.factory/testing.md`.
- Delete, skip, disable, or weaken any existing test or gate check.

## Clarification outcomes

None.
