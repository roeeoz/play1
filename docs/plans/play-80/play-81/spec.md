# Feature Specification — PLAY-81

## 1. Feature Overview

**Summary:** Add a new `testbed_utils/clamp.py` module providing a single pure-Python function — `clamp(value, low, high)` — that bounds a numeric value to an inclusive range `[low, high]`, re-exported from the package root.

**Problem statement:** Developers using testbed-utils currently write repeated inline `min(max(value, low), high)` expressions to bound a numeric value. A tested, documented helper eliminates this repetition.

**Target users:** Developers using testbed-utils who need to bound a numeric value to an inclusive range.

---

## 2. Goals & Non-Goals

### Goals
- Provide `clamp(value, low, high)` in a new `testbed_utils/clamp.py` module.
- The function carries a docstring with a runnable `>>>` example, matching the style of `numutils.py`, `textutils.py`, and `dateutils.py`.
- The function is covered by pytest cases for its happy path, boundary condition, and error condition (as enumerated in the acceptance criteria below).
- The function is re-exported from `testbed_utils/__init__.py` and added to `__all__`, following the convention every existing module in the package uses.
- Introduce no new runtime dependency.

### Non-Goals
- Multi-value or batch clamping (clamping a list of values in one call).
- A console script or CLI wrapper for the clamp function.
- Changes to any existing module or test file.
- Performance optimisation beyond what pure Python gives.

---

## 3. Functional Requirements

- **FR1 (traces R1):** `clamp(value, low, high)` returns the input value bounded to the inclusive range `[low, high]`: values below `low` return `low`, values above `high` return `high`, and values within the range return unchanged.
- **FR2 (traces R2):** `clamp(value, low, high)` raises `ValueError` when `low` is strictly greater than `high`.
- **FR3 (traces R3):** The function lives in a new module `clamp.py` under `src/testbed_utils/`.
- **FR4 (traces R4, G2):** The function has a docstring containing at least one runnable `>>>` example, matching the established style of `numutils.py`/`textutils.py`/`dateutils.py`.
- **FR5 (traces R5, G1):** The function ships with unit tests covering the happy path, at least one boundary case, and at least one error case.
- **FR6 (traces R6, G1):** Package test coverage remains at or above 90% after the change.
- **FR7 (traces R7, G4):** No test depends on the network, the clock, or file-system state outside test fixtures. All test inputs are literal numeric values.

### Core workflow
1. A developer imports `clamp` from `testbed_utils` (or from `testbed_utils.clamp` directly).
2. The developer calls `clamp(value, low, high)` with numeric arguments.
3. If `low > high`, the function raises `ValueError`.
4. Otherwise, the function returns the value bounded to `[low, high]` — below-low values return low, above-high values return high, values within the range return unchanged.

### Edge cases (from acceptance criteria)
- Value exactly equal to `low` — returns unchanged.
- Value exactly equal to `high` — returns unchanged.
- `low == high` — any value returns `low` (== `high`).
- `low > high` — raises `ValueError`.

---

## 4. User Experience & Behavior

This is a developer-facing library function. The "user experience" is the calling code's experience of the API surface.

- **Key flow:** `from testbed_utils import clamp` then `result = clamp(value, low, high)`.
- **States observed:** either a numeric return value or a raised `ValueError` — no intermediate state.
- **Error behavior:** invalid bounds (`low > high`) surface as `ValueError` with a descriptive message. No silent failure or sentinel return value.
- **Discoverability:** the function's docstring contains a working `>>>` example, visible via `help(clamp)` or source reading. The function appears in `testbed_utils.__all__`, making it visible to IDE auto-complete and `from testbed_utils import *`.

---

## 5. Acceptance Criteria

1. **Happy path — value within range returned unchanged.** Given a value of 5, a low bound of 0 and a high bound of 10, when `clamp(5, 0, 10)` is called, then it returns `5`.
2. **Happy path — value below range clamped to low.** Given a value of -3 with low bound 0 and high bound 10, when `clamp(-3, 0, 10)` is called, then it returns `0`.
3. **Happy path — value above range clamped to high.** Given a value of 15 with low bound 0 and high bound 10, when `clamp(15, 0, 10)` is called, then it returns `10`.
4. **Boundary — low equals high.** Given a low bound and high bound that are both 7, when `clamp` is called with any value, then it returns `7`.
5. **Error — low strictly greater than high.** Given a low bound of 10 and a high bound of 5, when `clamp` is called, then it raises `ValueError`.
6. **Happy path — function discoverable from the package root.** Given `from testbed_utils import clamp`, the import succeeds and `clamp` is in `testbed_utils.__all__`.
7. **Happy path — docstring contains a runnable example.** Given the `clamp` function's docstring, when it is executed as a doctest, then at least one example runs and passes.
8. **Boundary — package test coverage stays at or above 90%.** Given the full test suite including the new clamp tests, when it runs with coverage measurement, then overall package coverage is at or above 90%.

---

## 6. Dependencies & Constraints (product-level)

- **Depends on:** nothing — this is the sole story in the epic with no predecessors.
- **Depended on by:** nothing — no other story in the epic.
- **Constraint — style consistency:** the module's docstring/example style must match the existing `numutils.py`, `textutils.py`, and `dateutils.py` modules.
- **Constraint — no new dependency:** must not introduce any new runtime or test dependency.
- **Constraint — test determinism (G4):** all tests use only literal numeric inputs; no external state.
- **Constraint — 300-line limit (G3):** the change must not exceed 300 changed lines.
- **Compliance/security:** not applicable — this is pure in-memory numeric computation with no I/O surface.
- **Traceability (R7):** the pull request must name the story (PLAY-81) and the epic PRD (PLAY-80) it implements.

---

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. Architecture, data model, type annotations, exact error message text, and the PR-level breakdown are produced by the tech lead in the STRUCTURE stage from this approved product spec. Product-imposed constraints for STRUCTURE to satisfy:
- The module must live at `src/testbed_utils/clamp.py` and use only built-in Python operations.
- The function must be re-exported from `testbed_utils/__init__.py` and added to `__all__`, following the established pattern.
- Tests must live in `tests/test_clamp.py`, following the existing naming convention.
- Exact `ValueError` message text, type annotations, and whether to use a private constant for the error message are implementation choices for STRUCTURE.

---

## 8. Open Questions

None. All product-level decisions are resolved by the story, the epic PRD, and the codebase conventions.

---

*Source: Epic — "e2e-commit-layout clamp helper" (PLAY-80); User Story US-01 (PLAY-81).*
