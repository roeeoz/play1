# Feature Specification Document

## 1. Feature Overview

**Summary:** Add a pure-Python `initials(name)` helper function to the play1 testbed-utils package that extracts the first letter of each whitespace-separated word in a name string and returns them uppercased and concatenated.

**Problem statement:** Developers and factory agents consuming the play1 package currently have no built-in way to extract initials from a name string. They must write ad-hoc extraction logic or introduce a third-party dependency — both of which conflict with the package's goals of composable, tested, dependency-free helpers.

**Target users / actors:** Developers and factory agents consuming the play1 testbed-utils package.

---

## 2. Goals & Non-Goals

### Goals

- Provide a public `initials(name)` function in the testbed-utils package that returns uppercase initials of each whitespace-separated word (Epic PRD R1, R2).
- Handle extra whitespace (leading, trailing, repeated) gracefully, producing the same result as cleanly spaced input (R3).
- Handle empty input by returning an empty string (R4).
- Use only the Python standard library — no new runtime dependencies (R5).
- Include a docstring with a usage example for discoverability (R6, G2).
- Ship with unit tests covering the happy path, empty input, and extra whitespace that run under the existing pytest gate (R7, G1).
- Maintain all existing tests for other helpers (slugify, truncate, word_count) green — no regressions (RK1).

### Non-Goals

- Unicode or non-ASCII name handling (explicitly out of scope per the epic).
- Configurable separator or output format (e.g. dots between initials).
- Console script or CLI wrapper for the initials function.
- Backwards-compatibility guarantees — the package stays at version 0.x.
- Performance optimization or async support.

---

## 3. Functional Requirements

- **FR1 — Public function.** The system shall provide a public function `initials(name: str) -> str` in the testbed-utils package's `textutils` module.
- **FR2 — Initials extraction.** The function shall return the first character of each whitespace-separated word, uppercased and concatenated without separators. Example: `initials("Ada Lovelace")` returns `"AL"`.
- **FR3 — Whitespace tolerance.** The function shall ignore leading, trailing, and repeated whitespace between words, producing the same result regardless of spacing.
- **FR4 — Empty input.** The function shall return an empty string when given an empty string as input.
- **FR5 — Pure Python.** The function shall be implemented using only standard-library modules, adding no new runtime dependencies to the package.
- **FR6 — Discoverable docstring.** The function shall include a docstring containing a usage example that shows input and expected output.
- **FR7 — Public API export.** The function shall be exported from the package's public API (`__init__.py`), following the existing pattern used by `slugify`, `truncate`, and `word_count`.
- **FR8 — Unit tests.** Unit tests shall cover the happy path (multi-word name), single-word name, empty input, and extra whitespace, and shall run with the repository's existing `pytest` command alongside the existing test suite.

---

## 4. User Experience & Behavior

**Key user flow:**

1. The developer imports the `initials` function from the testbed-utils package (e.g. `from testbed_utils import initials`).
2. The developer calls `initials("Ada Lovelace")` and receives `"AL"`.
3. The developer uses the returned initials string as a compact identifier in their application.

**States and transitions:**

| Input state | Output |
|---|---|
| Multi-word name (`"Ada Lovelace"`) | First letter of each word, uppercased, concatenated (`"AL"`) |
| Single-word name (`"Ada"`) | First letter, uppercased (`"A"`) |
| Empty string (`""`) | Empty string (`""`) |
| Extra whitespace (`"  Ada   Lovelace  "`) | Same as clean input (`"AL"`) |

**Discoverability:** A developer inspecting the function's docstring (via `help(initials)` or IDE hover) sees a usage example showing `initials("Ada Lovelace")` returning `"AL"`.

**Edge cases visible to the user:**
- Whitespace-only input (e.g. `"   "`) behaves like empty input — returns `""`.
- ASCII-only scope: the function operates on ASCII input as stated by the PO; behavior on non-ASCII input is undefined and out of scope.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: multi-word name.** Given the `initials` function is available in the testbed-utils package, when `initials("Ada Lovelace")` is called, then `"AL"` is returned — the first letter of each whitespace-separated word, uppercased and concatenated without separators.

2. **Scenario 2 — Edge case: single-word name.** Given the `initials` function is available, when `initials("Ada")` is called, then `"A"` is returned.

3. **Scenario 3 — Error case: empty input.** Given the `initials` function is available, when `initials("")` is called, then `""` (an empty string) is returned.

4. **Scenario 4 — Edge case: extra whitespace.** Given a name string with leading, trailing and repeated spaces such as `"  Ada   Lovelace  "`, when `initials` is called with that string, then `"AL"` is returned, identical to the result without extra whitespace.

5. **Scenario 5 — Happy path: discoverable docstring.** Given the `initials` function is defined in the textutils module, when a developer inspects its docstring, then the docstring contains a usage example showing input and expected output.

6. **Scenario 6 — Happy path: test suite passes.** Given unit tests for `initials` are added to the existing test file covering the happy path, empty input and extra whitespace, when the repository's test command is run, then all tests pass including the existing tests for other helpers.

---

## 6. Dependencies & Constraints (product-level)

- **Existing test infrastructure:** pytest is already configured as a test extra in `pyproject.toml`. No new test tooling is required.
- **Existing module pattern:** The function follows the established pattern of the `textutils` module (function with type annotations, docstring with example, export in `__init__.py`, test class in `test_textutils.py`).
- **G1 constraint:** 100% of new public functions ship with pytest cases covering happy path, one boundary, and one error case; coverage at or above 90%.
- **G3 constraint:** The story must not exceed 300 changed lines.
- **G4 constraint:** Tests must finish in under 60 seconds with no network, clock, or filesystem dependencies.
- **R2 constraint:** No new runtime dependency without explicit PRD approval.
- **R3 constraint:** The pull request merges only with every required CI check green.
- **R7 constraint:** The pull request must name the story (PLAY-61) and the epic PRD (PLAY-60) it implements.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, implementation approach, and detailed design are produced by the tech lead in the STRUCTURE stage from this approved product spec. The product constraints that the technical design must respect:

- Pure Python, standard library only.
- Follows the existing module pattern in `textutils.py`.
- ASCII input only; Unicode handling is out of scope.
- The function is a pure transform with no side effects, no I/O, and no external calls.

---

## 8. Open Questions

None. All requirements are pinned by the epic PRD, the acceptance criteria specify exact input/output pairs, and the research brief confirms every assumption against the actual codebase.
