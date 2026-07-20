# Feature Specification Document

## 1. Feature Overview
- **Summary**: Add a `greet(name)` function to the `testbed_utils` Python package that returns a personalised greeting string.
- **Problem statement**: The testbed currently has no trivial, self-contained function to exercise in end-to-end developer-tooling tests. `greet(name)` fills this gap as the canonical "hello world" callable of the package.
- **Target users / actors**: Developers and CI pipelines using `testbed_utils` as a testbed fixture.

---

## 2. Goals & Non-Goals
### Goals
- Ship a public `greet(name)` function in the `testbed_utils` package.
- The function accepts a name string and returns a greeting in the form `Hello, {name}!`.
- A pytest test asserts the correct return value for `greet("Roee")`.
- All previously-passing tests continue to pass.

### Non-Goals
- Input validation, type-checking, or error-handling for non-string or empty inputs.
- Internationalisation, alternate greeting styles, or configurable templates.
- Changes to any part of the package beyond what is necessary to add the function and its test.

---

## 3. Functional Requirements

- **FR1**: `greet(name)` accepts a single positional argument `name`.
- **FR2**: `greet(name)` returns the string `"Hello, {name}!"` — comma after "Hello", exclamation mark at the end — where `{name}` is substituted by the value passed in.
- **FR3**: `greet` is accessible as a public symbol of the `testbed_utils` package (i.e. `from testbed_utils import greet` succeeds).
- **FR4**: A pytest test asserts `greet("Roee") == "Hello, Roee!"`.
- **FR5**: All tests in the existing suite pass without modification.

**Inputs**: A single string argument `name` (e.g. `"Roee"`).
**Outputs**: A string of the form `"Hello, {name}!"` (e.g. `"Hello, Roee!"`).

---

## 4. User Experience & Behavior

- A developer imports `greet` from `testbed_utils` and calls `greet("Roee")`; they receive back the string `"Hello, Roee!"`.
- No setup, configuration, or state is required before calling the function.
- The function is stateless and produces no side effects.

---

## 5. Acceptance Criteria

- **AC1**: `greet("Roee")` returns exactly `"Hello, Roee!"` (string equality, comma and exclamation mark included).
- **AC2**: A pytest test in the `testbed_utils` test suite asserts AC1 and passes under `pytest`.
- **AC3**: Running the full pytest suite produces no new failures compared to the current baseline.
- **AC4**: `from testbed_utils import greet` succeeds without error.

---

## 6. Dependencies & Constraints (product-level)

- Must integrate with the existing `testbed_utils` package without altering its current public API surface.
- CI pipeline runs `pytest`; the change must not introduce a `CI_FAIL` file or cause any existing test to fail.
- Python ≥ 3.10 compatibility required, consistent with the existing package constraint.

---

## 7. Technical Design (deferred to STRUCTURE)

Module placement (`textutils.py` vs. a new module), `__init__.py` export wiring, and test-file location are deferred to the STRUCTURE stage. The product constraint is simply that `greet` must be importable from the top-level `testbed_utils` package and covered by a passing pytest test.

---

## 8. Open Questions

None — all product-level requirements are fully specified by the acceptance criteria and scope statement.
