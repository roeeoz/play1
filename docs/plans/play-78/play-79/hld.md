# HLD — PLAY-79 Clamp helper that bounds a numeric value to a given range

## 1. System Overview
- **What:** a new `clamp` module inside the existing `testbed_utils` package exposing a single pure function: `clamp(value, low, high)`.
- **Problem:** developers consuming testbed-utils must write inline `min(high, max(low, value))` expressions to bound a number; a named helper is more readable and less error-prone.
- **Responsibilities:** return the value bounded to the inclusive range [low, high]; reject inverted ranges (low > high) with a descriptive `ValueError`; document the function with a runnable `>>>` example; ship pytest coverage for every branch (six paths).
- **Explicitly not here:** CLI entry points, type-specific overloads, performance optimization, backwards-compatibility guarantees.

## 2. Architecture Overview
- **Repository:** `play1` (`2a3d4d68-6e17-4c25-bd24-4c5d64979af3`), the only repo in scope.
- **Package layout:** setuptools `src/` layout (`pyproject.toml` `where = ["src"]`). The new module lives at `src/testbed_utils/clamp.py`, alongside `numutils.py`, `textutils.py`, `dateutils.py`, etc.
- **Public surface:** `testbed_utils.clamp` (submodule) plus re-export of the `clamp` name from `testbed_utils/__init__.py` and `__all__`, matching the convention every other public helper follows.
- **External dependencies:** Python standard library only. No new runtime or test dependency.

## 3. Data Flow Design
- Caller passes three numeric arguments (value, low, high) → function validates low ≤ high → computes bounded result synchronously → returns a number or raises `ValueError`.
- Fully synchronous, stateless, no I/O, no events.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| `src/testbed_utils/clamp.py` (new) | clamp function with validation and docstring example | three numbers → bounded number, or `ValueError` | play1 |
| `tests/test_clamp.py` (new) | pytest coverage for all six branches; verifies package export and docstring examples | in-memory values only | play1 |
| `src/testbed_utils/__init__.py` (edit) | import `clamp` and add to `__all__` | — | play1 |

## 5. Interface Contracts
- **Public API:** `clamp` importable from both `testbed_utils.clamp` and `testbed_utils`.
- **Error contract:** `ValueError` only; inverted-range message names the constraint violated and shows the values received. No custom exception classes (none exist in the package).
- **Numeric type:** results compare equal (`==`) to the spec's expected integer values. `clamp(5, 1, 10)` returns `5` (int when inputs are int).

## 6. Key Technical Decisions
- **Own module rather than adding to numutils.** The spec explicitly requires a new module (`clamp.py`). The existing `test_numutils.py` asserts the exact set of public functions in `numutils` is `{mean, median, percentile}` — adding `clamp` there would break the existing test suite.
- **Re-export from package root.** Follows the existing `__init__.py` convention; the `clamp` entry is inserted alphabetically between `days_between` and `extract_fields` in `__all__`.
- **Module-level private constant for error message.** Matches `numutils.py` style (`_EMPTY_MSG`, `_RANGE_MSG` pattern).
- **Docstring examples verified by tests, not CI config.** CI does not run doctests; the test file checks the examples produce their shown output, following the `test_numutils.py` pattern.
- **Two-commit implementation order.** Commit 1 lands the test file; commit 2 lands the helper module and the `__init__.py` registration. This follows the developer's requested TDD commit discipline while keeping the PR atomic and CI-green on merge.

## 7. Risks & Constraints
- **Coverage target unenforced:** the epic's ≥90% goal has no `pytest-cov` gate in the repo; flagged in PR body, not added.
- **No lint/format tooling in repo:** the only pre-PR check is `pip install -e ".[test]" && pytest`.
- **Size:** ~20 source lines + ~60 test lines + 2 init lines ≈ ~80 changed lines, well under the 300-line cap.
