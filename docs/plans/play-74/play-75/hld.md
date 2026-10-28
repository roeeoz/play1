# High-Level Design — PLAY-75: Range-clamping helper

## 1. System Overview

- **What is being built:** A `clamp(value, low, high)` pure-Python function in the testbed-utils package that returns the input value bounded to [low, high], raising `ValueError` on inverted bounds.
- **Problem:** Developers lack a validated, composable numeric primitive for range-clamping; inline `min(max(...))` idioms are error-prone and carry no range validation.
- **Key responsibilities:** Validate bounds, clamp value, surface clear errors.

## 2. Architecture Overview

- **New module:** `src/testbed_utils/clamputils.py` — owns the `clamp` function.
- **Registration:** `src/testbed_utils/__init__.py` — re-exports `clamp` and adds it to `__all__`.
- **Test module:** `tests/test_clamputils.py` — full coverage: happy path, boundary, error, package-export, and docstring tests.
- **Boundaries:** The new module is self-contained; it imports nothing from the package and no existing module imports it. The only integration point is the package root `__init__.py`.
- **External dependencies:** None added. Existing runtime deps unchanged.
- **Build order:** Two tickets — tests and module first (t1), then package-root registration (t2).

## 3. Data Flow Design

- Synchronous, single-call flow: `clamp(value, low, high)` → validate → return bounded value or raise.
- No async, no events, no I/O.

## 4. Component Breakdown

| Component | Responsibility | Inputs | Outputs | Repository |
|---|---|---|---|---|
| `clamputils.clamp` | Bound a numeric value to [low, high] with validation | three numerics | one numeric or ValueError | play1 |
| `__init__.py` update | Make `clamp` importable from package root | — | — | play1 |
| `test_clamputils.py` | Verify all acceptance scenarios + docstring + export | — | pytest pass/fail | play1 |

## 5. Interface Contracts

- **Public API:** `clamp(value, low, high)` — accepts three numeric arguments, returns one of its three inputs unchanged; raises `ValueError` when `low > high`.
- No cross-repo contracts. No event schemas.

## 6. Key Technical Decisions

- **New module (`clamputils.py`) rather than extending `numutils.py`:** Existing `test_numutils.py` asserts the exact set of public functions in that module; adding `clamp` there would break it.
- **`*utils.py` naming convention:** 4 of 4 non-CLI utility modules use this pattern.
- **Two-ticket split (tests first, then registration):** Matches the requested TDD-style ordering; the test suite and module land first, package-root wiring follows as a separate commit.

## 7. Risks & Constraints

- **Low risk:** Adding to `numutils.py` would break existing tests → mitigated by using a new module.
- **Constraint:** No `pytest-cov` gate exists; coverage target (≥90%) is informational. Full branch coverage is trivial for this function.
- **Constraint:** Total change must stay under 300 lines (~80–100 expected).
