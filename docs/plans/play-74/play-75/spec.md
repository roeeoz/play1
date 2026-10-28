# Feature Specification Document

## 1. Feature Overview

**Summary:** Add a `clamp(value, low, high)` function to the testbed-utils package that returns the input value bounded to the closed interval [low, high], raising `ValueError` when the range is invalid (low > high). The function lives in a new module with full test coverage, following the established pattern of the package's existing helpers.

**Problem statement:** Developers using testbed-utils lack a composable numeric primitive for range-clamping. Bounding a value to a range is a common operation that currently requires inline `min(max(...))` idioms, which are easy to write in the wrong order and carry no validation of the range itself.

**Target users / actors:** Developers using the testbed-utils package to perform numeric operations. The developer calls `clamp(value, low, high)` with a numeric value and lower/upper bounds and receives the bounded result, or a clear error when the bounds are inverted.

---

## 2. Goals & Non-Goals

### Goals
- Provide a single, well-named function that bounds a numeric value to a given range.
- Validate that the range is well-formed (low ≤ high) and raise `ValueError` when it is not.
- Ship the function with full test coverage: happy path, boundary, and error cases (product goal G1).
- Make the function discoverable: docstring with a worked `>>>` example, importable from the package root, listed in `__all__` (product goal G2).
- Keep the change small and composable: one new module plus one new test file, within the 300-changed-line limit (product goal G3).
- Maintain fast, deterministic CI: pure-arithmetic tests with no network, clock, or filesystem dependencies (product goal G4).

### Non-Goals
- Console script or CLI entry point for clamp — not needed for a pure helper.
- Changes to existing modules or helpers — this story adds one new module only.
- Performance optimization or C extensions — excluded by the product non-goals.
- Backwards-compatibility guarantees — the package version stays 0.x.
- Type enforcement or coercion (e.g., rejecting strings) — Python's comparison operators naturally handle int and float; the function accepts any comparable numeric type without explicit type checking.

---

## 3. Functional Requirements

- **FR1 (traces to R1):** The system shall provide a function `clamp(value, low, high)` that accepts three numeric arguments.
- **FR2 (traces to R2):** The function shall return `low` when the value is less than `low`.
- **FR3 (traces to R3):** The function shall return `high` when the value is greater than `high`.
- **FR4 (traces to R4):** The function shall return the value unchanged when it is between `low` and `high`, inclusive.
- **FR5 (traces to R5):** The function shall raise `ValueError` when `low` is strictly greater than `high`.
- **FR6 (traces to R6):** The function shall have a docstring containing a worked `>>>` example that is runnable by doctest.
- **FR7 (traces to R7):** The function shall be tested with cases covering: the happy path (value within bounds, value below lower bound, value above upper bound), at least one boundary (value equals `low` or `high`), and the error case (`low` greater than `high`).
- **FR8 (traces to R8):** The function shall be importable from the package root (`from testbed_utils import clamp`) and shall appear in the package's `__all__` list.
- **FR9 (traces to R9):** No new runtime dependency shall be introduced.

**Inputs:** Three numeric values — `value` (the number to clamp), `low` (the lower bound), `high` (the upper bound).

**Outputs:** A single numeric value: the input value bounded to [low, high].

**Core workflow:**
1. Developer calls `clamp(value, low, high)`.
2. The function validates that `low` is not greater than `high`; raises `ValueError` if it is.
3. The function returns `low` if value < low, `high` if value > high, or value if low ≤ value ≤ high.

**Edge cases:**
- When `low == high`, the function returns that single valid value (natural consequence of FR2–FR4; e.g., `clamp(5, 3, 3)` returns `3`).
- Float arguments work identically to int arguments — Python's comparison operators handle both.

---

## 4. User Experience & Behavior

**Key user flow:** A developer imports `clamp` from `testbed_utils` (or from the submodule directly), calls it with three numeric arguments, and receives the clamped result. The function is a pure, synchronous call with no side effects.

**States the user observes:**
- **Success:** The function returns a numeric value silently — no output beyond the return value.
- **Error:** When `low > high`, the function raises `ValueError` with a message indicating the range is invalid. The developer sees a standard Python traceback.

**User-facing edge cases and error messages:**
- Inverted bounds (`low > high`): `ValueError` is raised. The message communicates that the lower bound must not exceed the upper bound.
- No special error for non-numeric types; standard Python `TypeError` from the comparison operators applies if non-comparable types are passed.

**Discoverability:**
- The function appears in `help(testbed_utils)` and in the package's `__all__`.
- The docstring contains a worked `>>>` example so that `help(clamp)` and doctest both work.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: value within bounds.** Given a numeric value of 5 and bounds of 1 and 10, When `clamp(5, 1, 10)` is called, Then the function returns 5 unchanged.

2. **Scenario 2 — Happy path: value below lower bound.** Given a numeric value of −3 and bounds of 0 and 10, When `clamp(-3, 0, 10)` is called, Then the function returns 0.

3. **Scenario 3 — Happy path: value above upper bound.** Given a numeric value of 15 and bounds of 0 and 10, When `clamp(15, 0, 10)` is called, Then the function returns 10.

4. **Scenario 4 — Boundary: value equals lower bound.** Given a numeric value equal to the lower bound, When `clamp(1, 1, 10)` is called, Then the function returns 1 unchanged.

5. **Scenario 5 — Boundary: value equals upper bound.** Given a numeric value equal to the upper bound, When `clamp(10, 1, 10)` is called, Then the function returns 10 unchanged.

6. **Scenario 6 — Error case: inverted bounds.** Given a lower bound of 10 and an upper bound of 5, When `clamp(7, 10, 5)` is called, Then the function raises `ValueError`.

7. **Scenario 7 — Edge case: function discoverable from package root.** Given the testbed-utils package is installed, When `clamp` is imported from the package root, Then the import succeeds, And `clamp` appears in the package's public API (`__all__`), And the function's docstring contains a runnable `>>>` example.

---

## 6. Dependencies & Constraints (product-level)

**Dependencies:**
- Existing testbed-utils package structure and CI pipeline (already live; no cross-team coordination needed).

**Constraints:**
- No new runtime dependency (engineering requirement R2 / functional requirement R9).
- Package-level test coverage must stay at or above 90% (product goal G1).
- Total changed lines must not exceed 300 (product goal G3).
- Tests must be deterministic — no network, clock, or filesystem dependencies (product goal G4).
- The pull request must name story PLAY-75 and the epic PRD for traceability (engineering requirement R7).
- The new module must follow the established package convention: module-level docstring, `from __future__ import annotations`, Google-style function docstring with `>>>` example, pure Python with no third-party imports.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, module naming, internal implementation strategy, error message wording, and the PR-level breakdown are produced by the tech lead in the STRUCTURE stage from this approved product spec.

Product-imposed technical constraints to carry forward:
- Pure Python, no new runtime dependencies.
- Must register in `__init__.py` and `__all__` following the existing pattern.
- Must follow existing module conventions (docstring style, `from __future__ import annotations`).

---

## 8. Open Questions

None. All product-level behavior is pinned by the functional requirements and acceptance criteria. The following are noted as assumptions that carry negligible risk:
- Float arguments are supported identically to int (natural consequence of Python's comparison operators).
- Equal bounds (`low == high`) return that single value (natural consequence of FR2–FR4).
- The exact wording of the `ValueError` message is an implementation choice for STRUCTURE.
