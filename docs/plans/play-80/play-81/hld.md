# HLD — PLAY-81: Clamp helper that bounds a value to an inclusive range

## 1. System Overview
- **What:** A new `clamp` module inside the existing `testbed_utils` package exposing one pure function — `clamp(value, low, high)` — that returns the input value bounded to the inclusive range `[low, high]`.
- **Problem:** Developers using testbed-utils write repeated inline `min(max(value, low), high)` expressions; a tested, documented helper eliminates this repetition.
- **Responsibilities:** Validate that `low <= high` (raise `ValueError` otherwise); return the value clamped to the inclusive range; document the function with a runnable `>>>` example; ship pytest coverage for the happy path, a boundary case, and an error case.
- **Out of scope:** Multi-value/batch clamping, CLI wrapper, changes to existing modules/tests, performance optimisation.

## 2. Architecture Overview
- **Repository:** `play1` (`2a3d4d68-6e17-4c25-bd24-4c5d64979af3`), the sole repo in scope.
- **Package layout:** Setuptools `src/` layout. The new module lives at `src/testbed_utils/clamp.py`, alongside `numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, and `hello.py`.
- **Public surface:** `testbed_utils.clamp` (submodule) plus re-export of `clamp` from `testbed_utils/__init__.py` and addition to `__all__` in alphabetical position (between `"days_between"` and `"extract_fields"`).
- **External dependencies:** Python standard library only. No new runtime or test dependency.

## 3. Data Flow Design
- Caller passes three numeric arguments (`value`, `low`, `high`) → function validates `low <= high` → computes `max(low, min(value, high))` synchronously → returns a number or raises `ValueError`.
- Fully synchronous, stateless, no I/O, no events.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `src/testbed_utils/clamp.py` (new) | Clamp with validation and docstring example | Three numbers → number or `ValueError` | play1 |
| `tests/test_clamp.py` (new) | Pytest coverage for acceptance scenarios 1–7; verifies docstring example | Literal numeric values only | play1 |
| `src/testbed_utils/__init__.py` (edit) | Import `clamp` + add to `__all__` | — | play1 |

## 5. Interface Contracts
- **Function signature:** `clamp(value: float, low: float, high: float) -> float`. Accepts any numeric type supporting comparison (`int`, `float`); `float` annotation accepts `int` per PEP 484.
- **Return contract:** `clamp(5, 0, 10) == 5`; `clamp(-3, 0, 10) == 0`; `clamp(15, 0, 10) == 10`; `clamp(42, 7, 7) == 7`.
- **Error contract:** `ValueError` when `low > high`. Message in a private module-level constant (matching `numutils.py`'s `_EMPTY_MSG`/`_RANGE_MSG` pattern).

## 6. Key Technical Decisions
- **`max(low, min(value, high))` over if/elif/else.** Single expression, correct for all cases when `low <= high`.
- **Private constant for error message.** Follows `numutils.py` pattern; gives tests a stable substring to match.
- **Test structure mirrors `test_numutils.py`.** `TestClamp`, `TestPackageExports`, `TestDocstringExamples` — three-section layout.
- **`from __future__ import annotations` at top.** Matches every existing module.

## 7. Risks & Constraints
- **Coverage target unenforced:** No `pytest-cov` gate in repo; adding one is out of scope. The fully-tested new module cannot decrease coverage.
- **No lint/format tooling:** Only pre-PR check is `pip install -e ".[test]" && pytest`.
- **Size:** ~15–20 source lines + ~50–60 test lines + 2 lines in `__init__.py`, well under the 300-line cap.
- **Naming conflict (RK1):** Package is 0.x with no backward-compat guarantee; function can be renamed without a breaking-change process.
