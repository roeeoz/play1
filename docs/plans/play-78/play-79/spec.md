# Feature Specification Document

## 1. Feature Overview

**Summary.** Add a `clamp` helper function to the testbed-utils package that bounds a numeric value to an inclusive range defined by a low and high bound.

**Problem statement.** Developers consuming testbed-utils must write inline `min(high, max(low, value))` expressions every time they need to bound a number. This is repetitive, easy to get wrong (argument order), and less readable than a named helper.

**Target users / actors.** Developers (human or agent) consuming the testbed-utils package who need to constrain numeric values to a range.

---

## 2. Goals & Non-Goals

### Goals

- Provide a single, readable function call that replaces inline min/max clamping expressions (epic goal G2 — discoverability; epic goal G1 — trustworthiness via full test coverage).
- Ship with a complete test suite covering every branch: value below low, above high, within range, equal to each bound, and the inverted-range error (epic goal G1).
- Keep the addition small and composable: one new module plus its tests and a package-registration update, well within the 300-line ceiling (epic goal G3).
- Keep tests pure and deterministic with no I/O, network, clock, or external file-system dependency (epic goal G4).

### Non-Goals

- Console script or CLI entry point — the function is a library helper only.
- Type-specific overloads or advanced numeric-protocol support.
- Performance optimization or C extensions.
- Backwards-compatibility guarantees — the package stays at version 0.x.

---

## 3. Functional Requirements

- **FR1 (traces to R1, step 3).** The `clamp` function shall accept three numeric arguments — `value`, `low`, `high` — and return the value bounded to the inclusive range [low, high].
- **FR2 (traces to R2, step 2).** When `low` is strictly greater than `high`, the function shall raise a `ValueError`.
- **FR3 (traces to R3).** The function shall live in a new module `clamp.py` under the testbed-utils source package.
- **FR4 (traces to R4).** The function shall be importable from the package root (`from testbed_utils import clamp`) and listed in the package's `__all__`.
- **FR5 (traces to R5).** The function shall have a docstring containing a runnable `>>>` example.
- **FR6 (traces to R6, R7, RK1).** Unit tests shall cover: value within range, value equal to low, value equal to high, value below low, value above high, and the inverted-range `ValueError`. Package-level test coverage shall remain at or above 90 percent.
- **FR7 (traces to R8).** No new runtime dependency shall be introduced.
- **FR8 (traces to R9).** The change shall touch at most one new module, its test file, and the package registration file, within 300 changed lines.

---

## 4. User Experience & Behavior

**Primary flow.** A developer adds `from testbed_utils import clamp` to their code and calls `clamp(value, low, high)`. The call returns immediately with the bounded value. No setup, configuration, or side effects.

**States the user observes:**

| Input condition | What the developer sees |
|---|---|
| `low <= value <= high` | The original value, returned unchanged |
| `value < low` | `low` is returned |
| `value > high` | `high` is returned |
| `low > high` | A `ValueError` is raised with a descriptive message |

**Discoverability.** The function appears in the package's `__all__`, so IDE autocompletion and `help(testbed_utils)` surface it. Its docstring contains a runnable example so `help(clamp)` is self-explanatory.

**Edge cases and error messages.** The only user-facing error is the `ValueError` when the caller provides an inverted range (low > high). The message must make the mistake obvious — it should name the constraint that was violated and show the values received.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: value within range.** Given a value of 5 and a range from 1 to 10, when `clamp` is called, then 5 is returned unchanged.
2. **Scenario 2 — Boundary: value equals low bound.** Given a value of 1 and a range from 1 to 10, when `clamp` is called, then 1 is returned unchanged.
3. **Scenario 3 — Boundary: value equals high bound.** Given a value of 10 and a range from 1 to 10, when `clamp` is called, then 10 is returned unchanged.
4. **Scenario 4 — Edge case: value below low bound.** Given a value of −3 and a range from 1 to 10, when `clamp` is called, then 1 is returned.
5. **Scenario 5 — Edge case: value above high bound.** Given a value of 15 and a range from 1 to 10, when `clamp` is called, then 10 is returned.
6. **Scenario 6 — Error case: inverted range.** Given a low bound of 10 and a high bound of 1, when `clamp` is called, then a `ValueError` is raised.
7. **Scenario 7 — Happy path: importable from package root with docstring.** Given the package is installed, when a consumer writes `from testbed_utils import clamp`, then the import succeeds, and `clamp` is listed in the package's `__all__`, and its docstring contains a runnable `>>>` example.

---

## 6. Dependencies & Constraints (product-level)

- **No external dependencies.** The function is pure arithmetic; no new runtime package is introduced.
- **Package convention.** The testbed-utils package registers every public function in `__init__.py` and `__all__`; this addition must follow that convention.
- **Coverage constraint.** Package-level test coverage must remain at or above 90 percent after the addition (epic goal G1).
- **Size constraint.** The total change must stay within 300 changed lines (epic goal G3).
- **Traceability.** The pull request must name story PLAY-79 and the epic PRD it traces to (engineering compliance requirement R7).

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, module internals, type annotations, error-message constants, and test-file structure are owned by the tech lead in the STRUCTURE stage. Product constraints carried forward: the function is a single pure function in its own module; it follows existing module conventions visible in the repository; tests must cover every branch listed in the acceptance criteria.

---

## 8. Open Questions

None. All product-level behavior is fully specified by the acceptance criteria and the epic's functional requirements.
