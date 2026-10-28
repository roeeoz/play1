# Feature Specification Document

## 1. Feature Overview

**Summary:** Add a single pure helper function `word_count(text: str) -> int` to the guestbook package in a new module. The function returns the number of whitespace-separated words in the input string, returning 0 for empty or whitespace-only input. It ships with a docstring containing a usage example and pytest tests covering the happy path, a boundary case and an error case.

**Problem statement:** Developers using the guestbook package who need a simple word-count utility must currently either write their own or depend on the sibling `testbed_utils` package, which may evolve on a different trajectory. A tested, documented helper within the guestbook package removes that coupling.

**Target users / actors:** Developers using the guestbook package for text processing.

---

## 2. Goals & Non-Goals

### Goals

- Provide a public, tested `word_count` function in the guestbook package that counts whitespace-separated words (epic goal G1 — trustworthy helpers).
- Ship the function with a docstring containing a usage example (epic goal G2 — discoverable helpers).
- Keep the change to one new module plus its test file, well under 300 changed lines (epic goal G3 — small, composable additions).
- Ensure all tests are pure string-in / int-out with no external dependencies, finishing in under 60 seconds (epic goal G4 — fast, deterministic CI).

### Non-Goals

- API routes, UI or persistence changes.
- Configuration or environment variable support.
- Adding coverage tooling to the repository.
- Modifying or deprecating the existing `word_count` in the `testbed_utils` package.
- Console script or CLI entry point for the function.
- Any change to existing modules in the guestbook package.

---

## 3. Functional Requirements

- **FR1 — Function signature and return value.** The system shall provide a public function `word_count(text: str) -> int` in a new module within the guestbook package that returns the number of whitespace-separated words in the input string. *(traces to R1)*
- **FR2 — Empty and whitespace-only input.** The function shall return 0 when the input is an empty string or contains only whitespace characters (spaces, tabs, newlines). *(traces to R2)*
- **FR3 — No new runtime dependencies.** The function shall use only the Python standard library, introducing no new runtime dependency. *(traces to R3)*
- **FR4 — Docstring with usage example.** The function shall include a docstring with at least one usage example showing the function called with a sample string and the expected integer result. *(traces to R4)*
- **FR5 — Test coverage.** The test suite shall include: (a) a happy-path test — a normal sentence returns the correct word count; (b) an edge-case test — mixed whitespace separators (spaces, tabs, newlines) are handled correctly with leading/trailing whitespace ignored; (c) a boundary test — empty string and whitespace-only string both return 0; (d) an error-case test — non-string input (e.g. None, an integer) raises TypeError or AttributeError rather than returning a numeric result. *(traces to R5)*
- **FR6 — No test side effects.** All new and existing tests shall pass without depending on the network, clock or file-system state outside test fixtures. *(traces to R6)*
- **FR7 — Pull request traceability.** The pull request shall name story PLAY-69 and the PRD it traces to (Sanity R2b epic PRD). The PR description shall note the relationship to `testbed_utils.textutils.word_count` and the reason for the separate placement. *(traces to R7, RK2)*

**Inputs:** A string value (`text`).

**Outputs:** An integer representing the count of whitespace-separated words, or an error (TypeError / AttributeError) for non-string input.

**Core workflow:** `word_count("The quick brown fox")` → `4`.

**Edge cases:**
- Mixed whitespace (tabs, newlines) between words → each word counted once.
- Leading/trailing whitespace → does not inflate the count.
- Empty string → 0.
- Whitespace-only string → 0.
- Non-string input (None, int) → raises TypeError or AttributeError.

---

## 4. User Experience & Behavior

The user is a developer importing from the guestbook package.

**Key user flow:**
1. Developer imports `word_count` from the guestbook package's new module.
2. Developer calls `word_count(some_string)` and receives an integer.
3. Developer reads the docstring (via IDE tooltip or `help()`) and sees a usage example with expected output.

**States the user observes:**
- Normal operation: function returns an integer ≥ 0.
- Error state: function raises TypeError or AttributeError when given a non-string value — the developer sees a standard Python exception with a clear traceback.

**User-facing edge cases:**
- Passing `""` or `"   \t\n"` returns 0, not an error — the developer can safely call the function on any string without pre-checking for emptiness.
- Passing `None` or `42` raises an exception — the developer is informed immediately rather than receiving a misleading numeric result.

---

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: normal sentence.** Given a string containing multiple whitespace-separated words such as `"The quick brown fox"`, When `word_count` is called with that string, Then it returns the exact number of words (`4`).

2. **Scenario 2 — Edge case: mixed whitespace separators.** Given a string containing words separated by a mix of spaces, tabs and newline characters, When `word_count` is called, Then it counts each word once regardless of the whitespace type between them, And leading and trailing whitespace does not add to the count.

3. **Scenario 3 — Boundary: empty and whitespace-only input.** Given an empty string or a string containing only whitespace characters (spaces, tabs, newlines), When `word_count` is called, Then it returns `0`.

4. **Scenario 4 — Error case: non-string input.** Given a non-string value such as `None` or an integer, When `word_count` is called with that value, Then it raises an error (`TypeError` or `AttributeError`) rather than returning a numeric result.

5. **Scenario 5 — Happy path: docstring with usage example.** Given the `word_count` function in the guestbook package, When a developer reads its docstring, Then the docstring contains at least one usage example showing the function called with a sample string and the expected integer result.

---

## 6. Dependencies & Constraints (product-level)

- **Pre-condition satisfied:** pytest is available as a test-only dependency in the repository's optional test extra (`pyproject.toml` declares `test = ["pytest>=8"]`).
- **No new runtime dependencies** — the function uses only the Python standard library.
- **Relationship to sibling function:** A function with identical semantics exists at `testbed_utils.textutils.word_count`. This is intentional duplication per the PRD (risk RK2): the guestbook package may evolve independently. The PR description must note this relationship.
- **Repository conventions:** Test files live in `tests/` at root, named `test_<module>.py`. No linter, formatter, type checker or coverage tool is configured; `pip install -e ".[test]" && pytest` is the complete pre-merge check.
- **Story size constraint (G3):** The change must not exceed 300 changed lines and must touch at most one new module plus its test file.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, module placement, error-handling strategy (explicit TypeError guard vs. natural AttributeError from `.split()`), test file naming convention, and any `__init__.py` re-export decisions are deferred to the STRUCTURE stage.

---

## 8. Open Questions

None. All product-level requirements are fully specified by the story, the epic PRD, and the epic's goals and success metrics.
