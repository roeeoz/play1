# High-Level Design — PLAY-69: Add `word_count` helper to the guestbook package

## 1. System Overview

- **What is being built:** A pure helper function `word_count(text: str) -> int` in a new module within the guestbook package, with pytest tests and a docstring containing a usage example.
- **Problem statement:** Developers using the guestbook package lack a local word-count utility and must depend on the sibling `testbed_utils` package or write their own.
- **Key responsibilities:** Accept a string, return the count of whitespace-separated words (0 for empty/whitespace-only input), raise on non-string input.

## 2. Architecture Overview

- **New module:** `src/guestbook/text_utils.py` — single public function, stdlib only.
- **New test file:** `tests/test_text_utils.py` — pytest cases for happy path, mixed whitespace, boundary, error case.
- **No changes to existing modules.** The spec's non-goals explicitly exclude changes to existing guestbook modules, so `__init__.py` is not modified. The function is importable as `from guestbook.text_utils import word_count`.
- **No new dependencies.** Uses `str.split()` from the standard library.

## 3. Data Flow Design

- **Input:** `text: str` — any Python string.
- **Processing:** Split on whitespace (Python's default `str.split()`), count the resulting list.
- **Output:** `int` — word count, or 0 for empty/whitespace-only strings.
- **Error path:** Non-string input raises `TypeError` or `AttributeError`.
- No async, no events, no persistence.

## 4. Component Breakdown

| Component | Responsibility | Repository |
|---|---|---|
| `guestbook.text_utils` module | Exposes `word_count` function with docstring and example | roeeoz/play1 |
| `tests/test_text_utils.py` | Pytest cases covering all acceptance scenarios | roeeoz/play1 |

## 5. Interface Contracts

- **Public API:** `word_count(text: str) -> int` — the only new public symbol.
- No cross-repo contracts, no event schemas, no API endpoints.

## 6. Key Technical Decisions

- **Module placement:** `src/guestbook/text_utils.py` as named by the initiative input. Separate from `testbed_utils.textutils` per PRD rationale (independent evolution).
- **No `__init__.py` re-export:** Avoids changing an existing module; respects G3 (one new module + tests) and the spec's non-goals.
- **Error handling:** The coding agent decides between an explicit `TypeError` guard or natural `AttributeError` from `.split()` — both satisfy AC4.
- **Test file name:** `test_text_utils.py` — follows `test_<module>.py` convention; visually distinct from `test_textutils.py`.

## 7. Risks & Constraints

- **Name collision risk (RK2):** Mitigated by different package and module names; PR description notes the relationship.
- **No coverage tooling (RK1):** Accepted risk per PRD; the required test cases cover the function's behaviour.
- **Line budget:** Well under 300 lines (~50 total).
