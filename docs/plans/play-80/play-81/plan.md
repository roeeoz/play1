# Implementation plan — PLAY-81

## Context

PLAY-81 adds a `clamp(value, low, high)` function to the `testbed-utils` package. The function bounds a numeric value to an inclusive range `[low, high]`, raising `ValueError` when `low > high`. It lives in a new module `src/testbed_utils/clamp.py`, is re-exported from the package root, and ships with pytest coverage for the happy path, a boundary case, and an error case, plus a docstring with a runnable `>>>` example. The change lands in `play1` on branch `halo/feat/play-81`. The planning inputs (`spec.md`, `hld.md`, `work-items.md`) sit in `docs/plans/play-80/play-81/` beside this file.

## Research findings

**Package layout.** `src/testbed_utils/` contains six modules: `numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, `hello.py`, `numsummary.py`. Every public-API module follows the same pattern: a module docstring, `from __future__ import annotations`, private constants for error messages, functions with `>>>` docstring examples. `__init__.py` (`src/testbed_utils/__init__.py:1–28`) re-exports every public function and lists them in `__all__` in alphabetical order.

**Existing conventions confirmed by reading source.**
- Private error-message constants: `numutils.py:10–11` defines `_EMPTY_MSG` and `_RANGE_MSG`.
- Docstring style: single `>>>` example per function, matching the pattern in `numutils.py:17–18`, `textutils.py:19–20`, `dateutils.py`.
- `from __future__ import annotations` at the top of every module (`numutils.py:6`, `textutils.py:6`).
- Type annotations use `float` for numeric parameters (accepts `int` per PEP 484).

**`__all__` insertion point.** Current entries in order: `"days_between"`, `"extract_fields"`, `"hello_world"`, …. `"clamp"` sorts before `"days_between"` and becomes the first entry.

**Import line insertion point.** Current imports in `__init__.py:8–12` are grouped by module in alphabetical order (`dateutils`, `hello`, `numutils`, `pdfutils`, `textutils`). The `clamp` import goes before the `dateutils` line at `__init__.py:8`.

**Test conventions.** `tests/test_numutils.py` uses three test-class sections: `TestMean`/`TestMedian`/`TestPercentile` (function tests), `TestPackageExports` (import and `__all__` checks), `TestDocstringExamples` (doctest verification via `doctest.testmod`). Error assertions use `pytest.raises(ValueError, match="…")` with a substring of the private constant.

**Canonical gate.** `.factory/testing.md` declares `test-gate: pytest`. CI (`.github/workflows/ci.yml`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12. No linter, formatter, type checker, or coverage tool is configured.

**Dependencies.** No new runtime or test dependency is needed. `pyproject.toml` declares `pytest>=8` in `[project.optional-dependencies] test`.

**No `.factory/memory/` directory, no `CLAUDE.md`, no `AGENTS.md`.**

## Locked decisions and assumptions

**Locked decisions.**
- The function signature is `clamp(value: float, low: float, high: float) -> float` (hld.md §5).
- The clamping expression is `max(low, min(value, high))` (hld.md §3, §6).
- The error message lives in a private module-level constant, matching `numutils.py`'s `_EMPTY_MSG`/`_RANGE_MSG` pattern (hld.md §6).
- The module uses `from __future__ import annotations` (hld.md §6).
- Test structure mirrors `test_numutils.py`: `TestClamp`, `TestPackageExports`, `TestDocstringExamples` (hld.md §6).
- `"clamp"` is inserted into `__all__` in alphabetical position, between the start of the list and `"days_between"` (hld.md §2).
- No changes to `pyproject.toml`, CI, or any existing module or test file (spec.md §3 non-goals; work-items.md t1).

**Assumptions.**
- The `ValueError` message text is an implementation choice (spec.md §7); the plan assumes a message like `"low must not be greater than high"`, stored in a constant named `_BOUNDS_MSG`. Consequence if wrong: the test `match=` substring must align with whatever text is chosen — a naming-only change.
- Coverage will stay at or above 90% after adding a fully-tested new module. The repository has no coverage tool configured, so AC-8 ("package test coverage stays at or above 90%") cannot be measured inside the pod. Consequence if wrong: none in-pod; CI likewise has no coverage gate. The new module is 100% covered by its own tests, so it cannot decrease overall coverage.

## Solution proposal

Add one new module (`src/testbed_utils/clamp.py`) containing a single function, one new test file (`tests/test_clamp.py`), and a two-line edit to `src/testbed_utils/__init__.py`. The approach is the minimal change that satisfies all seven acceptance criteria:

1. **`clamp.py`** follows the established module pattern exactly: future-annotations import, module docstring, a private `_BOUNDS_MSG` constant for the error message, and the `clamp` function with a `float`-annotated signature, a docstring containing a `>>>` example, a `low > high` guard raising `ValueError(_BOUNDS_MSG)`, and the single-expression return `max(low, min(value, high))`.

2. **`test_clamp.py`** mirrors the three-section layout of `test_numutils.py`: a `TestClamp` class with happy-path tests (value within range, value below range, value above range), a boundary test (low equals high), and an error test (low > high with `pytest.raises`); a `TestPackageExports` class verifying `from testbed_utils import clamp` succeeds and `"clamp"` is in `__all__`; and a `TestDocstringExamples` class verifying the docstring example via `doctest.testmod`.

3. **`__init__.py`** gains one import line (`from testbed_utils.clamp import clamp`) inserted before the `dateutils` import, and one `__all__` entry (`"clamp"`) inserted as the first element.

No alternative was considered because the design is fully specified by the HLD and the repository's existing conventions leave no ambiguity.

## Ordered implementation steps

1. **Create `src/testbed_utils/clamp.py`.**
   - Add module docstring, `from __future__ import annotations`, private constant `_BOUNDS_MSG = "low must not be greater than high"`.
   - Implement `clamp(value: float, low: float, high: float) -> float` with a docstring containing a `>>>` example (e.g., `clamp(15, 0, 10)` → `10`).
   - Guard: `if low > high: raise ValueError(_BOUNDS_MSG)`.
   - Return: `max(low, min(value, high))`.
   - Files: `src/testbed_utils/clamp.py` (new).
   - Advances: AC-1, AC-2, AC-3, AC-4, AC-5, AC-7.
   - Test layer: `package-api` (pytest).

2. **Create `tests/test_clamp.py`.**
   - `TestClamp`: `test_value_within_range` (AC-1), `test_value_below_range_clamped_to_low` (AC-2), `test_value_above_range_clamped_to_high` (AC-3), `test_low_equals_high` (AC-4), `test_low_greater_than_high_raises` (AC-5).
   - `TestPackageExports`: `test_root_import_and_all` (AC-6).
   - `TestDocstringExamples`: `test_every_public_function_has_a_runnable_example`, `test_doctests_pass` (AC-7).
   - All inputs are literal numeric values; no network, clock, or filesystem dependency.
   - Files: `tests/test_clamp.py` (new).
   - Advances: AC-1 through AC-7.
   - Test layer: `package-api` (pytest).

3. **Edit `src/testbed_utils/__init__.py`.**
   - Add `from testbed_utils.clamp import clamp` before the `dateutils` import line (`__init__.py:8`).
   - Add `"clamp",` as the first entry in `__all__` (before `"days_between"`, `__init__.py:15`).
   - Files: `src/testbed_utils/__init__.py` (edit, 2 lines added).
   - Advances: AC-6.
   - Test layer: `package-api` (pytest).

## Work-item mapping

| Step | Work item | Title |
|------|-----------|-------|
| 1 | t1 | Add clamp module with tests and package re-export |
| 2 | t1 | Add clamp module with tests and package re-export |
| 3 | t1 | Add clamp module with tests and package re-export |

All steps belong to the single work item t1. No planning gap.

## Verification and CI gate

The repository's canonical gate is `pytest`, run as:

```
pip install -e ".[test]"
pytest
```

This is the sole gate (`test-gate: pytest` in `.factory/testing.md`). No linter, formatter, type checker, or coverage tool is configured.

**Required test layer:** `package-api` (production-path, `runBy: canonical-gate`). The new `tests/test_clamp.py` is discovered by pytest's configured `testpaths = ["tests"]` and requires no additional configuration.

**What the gate must show:** all existing tests plus the new `test_clamp.py` tests pass. No new CI configuration, no `.factory/testing.md` update, and no `.factory/delivery-assets` entry is needed.

**Coverage (AC-8):** No coverage tool is configured in the repository. The new module is fully covered by its test file. A fully-tested new module cannot decrease an existing coverage ratio. This AC is satisfied by design but cannot be numerically verified in-pod or in CI.

## Risks and scope guards

**Risks.**
- *Coverage measurement (AC-8):* There is no `pytest-cov` configuration. Adding one is out of scope. The AC is satisfied structurally (every branch of the new function is tested) but not numerically verified. Mitigation: the new module has three code paths and at least five test cases covering all of them.

**Scope guards — the implement phase must NOT:**
- Modify any existing module (`numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, `hello.py`, `numsummary.py`) or any existing test file.
- Add or modify `pyproject.toml` (no new dependency, no new console script).
- Add or modify CI configuration (`.github/workflows/ci.yml`).
- Add or modify `.factory/testing.md`.
- Implement multi-value/batch clamping or a CLI wrapper.
- Delete, skip, disable, or weaken the existing `pytest` gate.

## Clarification outcomes

None.
