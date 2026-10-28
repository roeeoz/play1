# Implementation plan — PLAY-79

## Context

PLAY-79 adds a `clamp(value, low, high)` helper to the `testbed_utils` package in the `play1` repository (branch `halo/feat/play-79`). The function returns `value` bounded to `[low, high]` and raises `ValueError` on an inverted range. Acceptance criteria cover six input paths (within range, equal-to-low, equal-to-high, below-low, above-high, inverted-range error) plus package-root importability with a docstring example. The spec (`spec.md`), design (`hld.md`) and work-item breakdown (`work-items.md`) sit in `docs/plans/play-78/play-79/` beside this file.

## Research findings

**Package layout.** Setuptools `src/` layout (`pyproject.toml:24` `where = ["src"]`). Existing modules: `numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, `hello.py`, `numsummary.py` under `src/testbed_utils/`.

**`__init__.py` convention** (`src/testbed_utils/__init__.py:1-28`). Each module's public names are imported at the top and added to `__all__` in alphabetical order. Current first entry is `"days_between"`. Alphabetically, `"clamp"` precedes `"days_between"` (`c` < `d`), so the new entry is inserted as the first element of `__all__`, and the new import line `from testbed_utils.clamp import clamp` is inserted before the `dateutils` import (line 8).

**Module style** (`src/testbed_utils/numutils.py:1-64`). `from __future__ import annotations`; module-level private constants for error messages (`_EMPTY_MSG`, `_RANGE_MSG`); type-hinted parameters; docstrings with `>>>` examples; pure functions, no I/O.

**Test style** (`tests/test_numutils.py:1-99`). One class per public function (`TestMean`, `TestMedian`, `TestPercentile`). A `TestPackageExports` class verifying root import and `__all__` membership. A `public_functions()` helper enumerating public functions in the module. A `TestDocstringExamples` class that (a) asserts the exact set of public function names, (b) checks each has a `>>>` example via `doctest.DocTestFinder`, and (c) runs `doctest.testmod()`. Error paths use `pytest.raises(ValueError, match="...")`.

**Gate** (`.factory/testing.md:1-51`). `pip install -e ".[test]"` followed by `pytest`. No linter, formatter, type checker, or coverage tool. CI at `.github/workflows/ci.yml:1-39` runs on Python 3.12.

**Change surface.** Three files total: one new module (`src/testbed_utils/clamp.py`), one new test file (`tests/test_clamp.py`), one edit (`src/testbed_utils/__init__.py`). No change to `pyproject.toml`, CI, or any other module.

**HLD placement note.** The HLD (`hld.md`, section 6) states the `clamp` entry is "inserted alphabetically between `days_between` and `extract_fields`". Alphabetically `clamp` precedes `days_between`, so the correct position is before `days_between` — first in `__all__`. The import line is also first, before the `dateutils` line. This is a minor HLD inaccuracy; the correct alphabetical ordering is used here.

## Locked decisions and assumptions

**Locked decisions.**

- The function lives in a new module `clamp.py`, not in `numutils.py` (spec FR3; HLD section 6 — `test_numutils.py:79` asserts the exact public set of `numutils` is `{mean, median, percentile}`, so adding there would break the existing suite).
- `ValueError` on inverted range, no custom exception class (spec FR2; HLD section 5 — no custom exceptions exist in the package).
- Error message names the constraint violated and shows the values received (spec section 4).
- Re-export from package root via `__init__.py` and `__all__` (spec FR4; HLD section 2).
- Docstring with a runnable `>>>` example (spec FR5).
- No new runtime dependency (spec FR7; `pyproject.toml:13` `dependencies` unchanged).
- Gate is `pytest` only (`.factory/testing.md`).

**Assumptions.**

- The module-level error-message constant follows the `_RANGE_MSG` naming pattern from `numutils.py`. If the convention has changed elsewhere in the package, the constant name is trivially adjustable.
- The test file follows the `test_numutils.py` three-class structure (`TestClamp`, `TestPackageExports`, `TestDocstringExamples`). If the test convention has shifted, only class names change.
- `clamp` returns the same numeric type as its inputs (int in, int out) per HLD section 5. The implementation `max(low, min(high, value))` preserves this natively in Python.

## Solution proposal

Add `src/testbed_utils/clamp.py` containing a single public function `clamp(value, low, high)` that validates `low <= high` (raising `ValueError` with a descriptive message otherwise) and returns `max(low, min(high, value))`. The module follows the `numutils.py` style: `from __future__ import annotations`, a private `_INVERTED_RANGE_MSG` constant, type hints, and a docstring with a `>>>` example.

Add `tests/test_clamp.py` mirroring `test_numutils.py` structure: `TestClamp` with one method per AC scenario (within range, equals low, equals high, below low, above high, inverted range error), `TestPackageExports` verifying root import and `__all__` membership, and `TestDocstringExamples` verifying the docstring example exists and passes via `doctest`.

Edit `src/testbed_utils/__init__.py` to import `clamp` from `testbed_utils.clamp` and add `"clamp"` as the first entry in `__all__`.

No alternatives were seriously considered: the design is fully constrained by the spec and HLD, the function is trivially small, and the repository conventions are unambiguous.

## Ordered implementation steps

1. **Create `tests/test_clamp.py`.**
   - New file. Import `doctest`, `inspect`, `pytest`, `testbed_utils`, and `from testbed_utils.clamp import clamp`. Define:
     - `TestClamp`: `test_value_within_range` (AC 1: `clamp(5, 1, 10) == 5`), `test_value_equals_low` (AC 2: `clamp(1, 1, 10) == 1`), `test_value_equals_high` (AC 3: `clamp(10, 1, 10) == 10`), `test_value_below_low` (AC 4: `clamp(-3, 1, 10) == 1`), `test_value_above_high` (AC 5: `clamp(15, 1, 10) == 10`), `test_inverted_range_raises` (AC 6: `pytest.raises(ValueError, match="low must not exceed high")` for `clamp(5, 10, 1)`).
     - `TestPackageExports`: `test_root_import_and_all` — import `clamp` from `testbed_utils`, verify identity with the direct import, verify `"clamp"` in `testbed_utils.__all__` (AC 7).
     - `public_functions()` helper filtering `vars(clamp_module)` to public functions defined in the module.
     - `TestDocstringExamples`: `test_every_public_function_is_covered` (assert public set is `{"clamp"}`), `test_every_public_function_has_a_runnable_example` (via `doctest.DocTestFinder`), `test_doctests_pass` (via `doctest.testmod`) (AC 7).
   - Advances: AC 1–7 (all scenarios verified).
   - Test layer: `package-api` (`pytest`).

2. **Create `src/testbed_utils/clamp.py`.**
   - New file. Add `from __future__ import annotations`. Define a module-level `_INVERTED_RANGE_MSG` constant (e.g. `"low must not exceed high, got low={low!r}, high={high!r}"`). Define `def clamp(value: float, low: float, high: float) -> float:` with a docstring containing a `>>>` example (`clamp(5, 1, 10)` → `5`). Body: validate `low <= high`, raise `ValueError(_INVERTED_RANGE_MSG.format(low=low, high=high))` if not; return `max(low, min(high, value))`.
   - Advances: AC 1–6 (function behavior), AC 7 (docstring example).
   - Test layer: `package-api` (`pytest`).

3. **Edit `src/testbed_utils/__init__.py`.**
   - Add `from testbed_utils.clamp import clamp` as the first import line (before the `dateutils` import at current line 8). Add `"clamp"` as the first entry in `__all__` (before `"days_between"` at current line 15).
   - Advances: AC 7 (importable from package root, listed in `__all__`).
   - Test layer: `package-api` (`pytest`).

## Work-item mapping

| Step | Work item | Title |
|------|-----------|-------|
| 1 | t1 | Add clamp module with tests and package re-export |
| 2 | t1 | Add clamp module with tests and package re-export |
| 3 | t1 | Add clamp module with tests and package re-export |

All steps belong to the single work item t1. No planning gap.

## Verification and CI gate

**Canonical gate** (`.factory/testing.md`): `pytest`, run after `pip install -e ".[test]"`.

**Required verification sequence** from a clean temporary worktree at the committed SHA:

1. `pip install -e ".[test]"`
2. `pytest`

**What the gate must show.** All existing tests pass (no regression). The new `tests/test_clamp.py` tests pass, covering all six function branches and the package-export/docstring checks. No new test framework, CI pipeline change, or coverage tool is introduced.

**Provider CI.** No change to `.github/workflows/ci.yml`; the existing workflow already runs `pip install -e ".[test]"` then `pytest` on Python 3.12 and picks up new test files automatically. No `.factory/testing.md` update needed (gate command unchanged).

**No delivery-assets obligation.** No binary deliverable introduced.

## Risks and scope guards

**Risks.**

- Coverage target (≥90%) is an epic goal but has no `pytest-cov` gate in the repository. The six-branch test suite provides full branch coverage of the new module, but the percentage is not machine-verified. Mitigation: the test file covers every code path; adding a coverage gate is out of scope per HLD section 7.

**Scope guards — the implement phase must NOT:**

- Modify `pyproject.toml` (no new dependencies, no new console scripts).
- Modify any existing module (`numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, `hello.py`, `numsummary.py`) or any existing test file.
- Modify `.github/workflows/ci.yml` or `.factory/testing.md`.
- Add a coverage tool, linter, formatter, or type checker.
- Add type-specific overloads, generic numeric protocol support, or CLI entry points.
- Delete, skip, disable, or weaken any existing test or CI check.

## Clarification outcomes

**Developer feedback: "Split the implementation into two commits: tests first, then the helper; name them in the plan."** The factory commits one change set per work item in `work-items.md`, so the single work item t1 produces one commit. The requested test-first ordering is reflected in the order of the implementation steps: step 1 creates the test file, steps 2–3 create the helper module and its package registration.
