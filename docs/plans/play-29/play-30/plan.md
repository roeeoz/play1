# Implementation plan — s1: CLI subcommand: parse two ISO dates and report the day count

## Context

Story s1 (play-30) adds a CLI subcommand to testbed-utils that accepts two ISO 8601 dates (with optional trailing Z), computes the absolute calendar-day count between them, and prints it. The change is backed by a new public helper function in `dateutils.py`, following the existing console-script pattern. The acceptance criteria require happy-path, zero-day, invalid-date, trailing-Z, and help-text scenarios, with a docstring containing a runnable example and full pytest coverage. The target repository is `roeeoz/play1`, branch `halo/feat/play-30`. The planning inputs (`spec.md`, `hld.md`, `work-items.md`) sit beside this file in `docs/plans/play-29/play-30/`.

## Research findings

**Change surface — existing code:**

- `src/testbed_utils/dateutils.py:1-55` — three functions (`days_between` at line 12, `is_weekend` at line 21, `humanize_delta` at line 26). No `main()`, no `argparse` import, no `sys` import. Uses `from __future__ import annotations` and imports `from datetime import date, timedelta`.
- `src/testbed_utils/__init__.py:8` — imports `days_between, humanize_delta, is_weekend` from `dateutils`. `__all__` at line 14 is alphabetically sorted. `main()` functions are never imported or listed here.
- `pyproject.toml:14-18` — four `[project.scripts]` entries; none yet for `dateutils:main`. `requires-python = ">=3.10"` at line 10.
- `tests/test_dateutils.py:1-46` — unit tests for the three existing functions, organized as one class per function. Imports directly from `testbed_utils.dateutils`.

**Established CLI pattern (`hello.py:1-24`, `pdfutils.py:52-65`, `numsummary.py`):**

- Module-level `_DESCRIPTION` constant, kept at or under 76 characters.
- `main()` uses `argparse.ArgumentParser(prog="<script-name>", description=_DESCRIPTION)`.
- Positional args via `parser.add_argument()`.
- Error handling: catch `ValueError`, print `f"Error: {exc}"` to stderr, `sys.exit(1)`.

**Established CLI test pattern (`tests/test_hello_cli.py:1-51`):**

- Local `run_main(args)` helper: patches `sys.argv` with `["<script-name>"] + args`, redirects stdout/stderr via `io.StringIO` + `redirect_stdout`/`redirect_stderr`, catches `SystemExit`, returns `(exit_code, stdout, stderr)`.
- Separate test file per CLI (e.g. `test_hello_cli.py`, `test_pdf_extract_cli.py`).
- Classes: `TestHelp` (exit 0, `_DESCRIPTION` in stdout), `TestBadOption` (exit 2, `"usage:"` and `"error"` in stderr).

**Established docstring/export test pattern (`tests/test_hello.py:17-30`):**

- `TestDocstringExamples` class using `doctest.DocTestFinder()` to verify `>>>` examples exist, and `doctest.testmod()` to verify they pass.
- `TestPackageExports` (seen in `test_numutils.py`) verifying root-level import and `__all__` membership.

**Canonical gate:** `pytest` (from `.factory/testing.md` and `pyproject.toml:26-28`). CI runs `pip install -e ".[test]"` then `pytest` on Python 3.12. No linter, formatter, or type checker.

**Python 3.10 constraint:** `date.fromisoformat()` on 3.10 accepts only `YYYY-MM-DD`; a trailing Z must be stripped before parsing.

**What exists vs. what must be created:**

| Artifact | Status |
|---|---|
| `dateutils.py` public helper for string-based absolute day count | New |
| `dateutils.py` `main()` entry point | New |
| `_DESCRIPTION` constant in `dateutils.py` | New |
| `__init__.py` re-export of the new function | New line in existing file |
| `pyproject.toml` `[project.scripts]` entry | New line in existing file |
| `tests/test_dateutils.py` — tests for the new function | New classes in existing file |
| `tests/test_date_range_cli.py` — CLI tests | New file |

## Locked decisions and assumptions

**Locked decisions:**

- The new public function raises `ValueError` on invalid input (spec FR5, hld §5).
- The CLI catches `ValueError` and prints `f"Error: {exc}"` to stderr, exits 1 (spec FR3; repo pattern at `pdfutils.py:61-63`).
- Trailing-Z stripping uses `arg.rstrip('Z')` before `date.fromisoformat()` (hld §6).
- The function returns `abs((d1 - d2).days)` — always non-negative (spec FR2, hld §3).
- The `main()` and argparse structure are co-located in `dateutils.py` (hld §2).
- A separate CLI test file follows the `test_hello_cli.py` pattern (hld §6).
- No new runtime dependency (spec FR8, epic R2).
- CPython 3.10+ compatibility (epic R1, `pyproject.toml:10`).
- The new public function is re-exported from `__init__.py` and listed alphabetically in `__all__` (spec FR6, AC7; repo convention at `__init__.py:8-26`).

**Assumptions:**

- **A1 — Console script name.** The spec and hld do not prescribe the exact script name. Assumption: `testbed-date-range`, following the `testbed-` prefix pattern of `testbed-hello` and `testbed-num-summary`. Consequence if wrong: rename in `pyproject.toml` and CLI tests; no functional impact.
- **A2 — New function name.** The spec says "day-count function"; the hld does not fix a name. Assumption: `date_range_days`, accepting two `str` arguments. Consequence if wrong: rename in all files; no structural change.
- **A3 — Output format.** Spec OQ1 defers the exact wording. Assumption: the subcommand prints a single integer on one line (e.g. `9`), matching the bare-value style. Consequence if wrong: adjust the `print()` call and CLI test assertions.

## Solution proposal

Add one new public function and one `main()` to `dateutils.py`, register the console script, re-export the function, and cover it with unit and CLI tests.

The new public function (`date_range_days(start: str, end: str) -> int`) strips an optional trailing Z from each argument, parses via `date.fromisoformat()`, and returns `abs((d1 - d2).days)`. It raises `ValueError` on unparseable input, wrapping the underlying exception with a user-friendly message. It carries a docstring with a `>>>` example.

The `main()` follows the `pdfutils.py` pattern: `argparse.ArgumentParser` with two positional arguments (`start_date`, `end_date`), a `_DESCRIPTION` constant, a `try/except ValueError` block that prints `f"Error: {exc}"` to stderr and exits 1, and `--help` support from argparse.

The existing `days_between` function is not modified — it takes `date` objects and returns a signed value, which is a different contract. The new function is a string-accepting, absolute-returning complement, not a replacement.

The `main()` and argparse structure are designed so that s2 can later add weekday-listing output after the day-count line without changing the argument parsing or error handling — the two positional args and the parsed `date` pair are the stable contract surface.

No alternative approach was considered: the hld prescribes this design, and it matches every established repo pattern exactly.

## Ordered implementation steps

1. **Add the new public function to `dateutils.py`.**
   Add `import argparse` and `import sys` to the imports at `dateutils.py:9`. Add `date_range_days(start: str, end: str) -> int` after the existing functions (after line 55). The function strips trailing Z from each argument, calls `date.fromisoformat()`, and returns `abs((d1 - d2).days)`. It raises `ValueError` with a message like `"Invalid date: '<input>'"` on parse failure. Include a docstring with a `>>>` example.
   Advances: AC1, AC2, AC4, AC6.
   Test layer: `package-api` (pytest).
   Files: `src/testbed_utils/dateutils.py`.

2. **Add `main()` and `_DESCRIPTION` to `dateutils.py`.**
   Add a module-level `_DESCRIPTION` constant (≤76 chars, e.g. `"Report the number of calendar days between two ISO 8601 dates."`). Add `main()` after the new function: `ArgumentParser(prog="testbed-date-range", description=_DESCRIPTION)`, two positional args (`start_date`, `end_date`), `try/except ValueError` calling `date_range_days`, error to stderr with `f"Error: {exc}"`, `sys.exit(1)` on error, `print(result)` on success.
   Advances: AC1, AC3, AC5.
   Test layer: `package-api` (pytest).
   Files: `src/testbed_utils/dateutils.py`.

3. **Re-export the new function from `__init__.py`.**
   Add `date_range_days` to the import at `__init__.py:8` and insert it alphabetically into `__all__` at `__init__.py:14` (between `"days_between"` and `"extract_fields"`).
   Advances: AC7.
   Test layer: `package-api` (pytest).
   Files: `src/testbed_utils/__init__.py`.

4. **Register the console script in `pyproject.toml`.**
   Add `testbed-date-range = "testbed_utils.dateutils:main"` to the `[project.scripts]` section at `pyproject.toml:14`.
   Advances: AC5, AC7.
   Test layer: `package-api` (pytest — the CLI tests exercise it via `run_main`).
   Files: `pyproject.toml`.

5. **Add unit tests for `date_range_days` to `tests/test_dateutils.py`.**
   Add a new `TestDateRangeDays` class after the existing classes (after line 46). Tests: happy path (two dates, either order → correct absolute count), zero-day boundary (identical dates → 0), trailing-Z acceptance (`"2024-01-10Z"` parsed as `2024-01-10`), invalid-date error (`pytest.raises(ValueError)`). Add a `TestDateRangeDaysDocstring` class using `doctest.DocTestFinder` and `doctest.testmod` to verify the docstring example exists and passes. Add a `TestDateRangeDaysExport` class verifying `testbed_utils.date_range_days is dateutils.date_range_days` and `"date_range_days" in testbed_utils.__all__`.
   Advances: AC1, AC2, AC3, AC4, AC6.
   Test layer: `package-api` (pytest).
   Files: `tests/test_dateutils.py`.

6. **Create `tests/test_date_range_cli.py` with CLI-level tests.**
   New file following the `test_hello_cli.py` pattern. Local `run_main(args)` helper patching `sys.argv` with `["testbed-date-range"] + args`. Classes: `TestDayCount` (happy path: two dates → correct output, exit 0; reversed order → same count; zero-day: identical dates → `"0\n"`, exit 0; trailing Z → correct count), `TestHelp` (`--help` → exit 0, `_DESCRIPTION` in stdout), `TestInvalidInput` (bad date string → exit non-zero, `"Error:"` in stderr, stdout empty; wrong number of args → exit 2).
   Advances: AC1, AC2, AC3, AC4, AC5.
   Test layer: `package-api` (pytest).
   Files: `tests/test_date_range_cli.py` (new).

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add day-count CLI subcommand and public helper to dateutils |
| 2 | t1 | Add day-count CLI subcommand and public helper to dateutils |
| 3 | t1 | Add day-count CLI subcommand and public helper to dateutils |
| 4 | t1 | Add day-count CLI subcommand and public helper to dateutils |
| 5 | t1 | Add day-count CLI subcommand and public helper to dateutils |
| 6 | t1 | Add day-count CLI subcommand and public helper to dateutils |

All steps belong to the single work item t1. No work item is unmapped.

## Verification and CI gate

**Canonical gate:** `pytest` (from `.factory/testing.md` and `pyproject.toml:26-28`).

**Gate command sequence from a clean worktree:**

```
pip install -e ".[test]"
pytest
```

**Required test layers:**

| Layer | ID | Covers |
|---|---|---|
| `package-api` | Unit + CLI tests via pytest | All six steps |

**What the gate must show:** all existing tests pass (no regressions in `test_dateutils.py`, `test_hello.py`, `test_hello_cli.py`, etc.), all new tests in `test_dateutils.py` and `test_date_range_cli.py` pass, and no unhandled exceptions or warnings.

**Provider CI:** `.github/workflows/ci.yml` already runs `pytest` on push and PR; no change to CI is needed.

**`.factory/testing.md`:** no update required — pytest discovery is already configured and the new test files follow the existing `test_*.py` naming convention.

**No `.factory/delivery-assets` obligation:** no binary deliverables are introduced.

## Risks and scope guards

**Risks:**

- **`rstrip('Z')` over-stripping.** `rstrip` removes all trailing Z characters, so a pathological input like `"ZZZZ"` strips to an empty string rather than raising a date-parse error. Mitigation: `date.fromisoformat("")` raises `ValueError`, so the function still errors correctly. No functional risk.
- **s2 extensibility.** `main()` must remain cleanly extensible so s2 can add weekday output without refactoring argument parsing. Mitigation: the two positional args and the parsed `date` pair are computed before any output; s2 adds output lines after the day-count print, not inside it.

**Scope guards — the implement phase must NOT:**

- Modify the existing `days_between`, `is_weekend`, or `humanize_delta` functions.
- Modify any existing test class in `test_dateutils.py`.
- Modify `.github/workflows/ci.yml` or the `CI_FAIL` gate mechanism.
- Introduce any new runtime dependency.
- Add weekday-listing logic (delivered by s2).
- Add time-of-day or timezone-offset arithmetic.
- Use Python syntax or stdlib features unavailable in CPython 3.10.

## Clarification outcomes

None.
