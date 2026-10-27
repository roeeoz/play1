# High-Level Design — PLAY-61: `initials(name)` helper

## 1. System Overview

- **What is being built:** A pure-Python `initials(name: str) -> str` function added to the existing `testbed_utils.textutils` module.
- **Problem statement:** Consumers of the play1 package lack a built-in way to extract uppercase initials from a name string, forcing ad-hoc logic or unnecessary dependencies.
- **Key responsibilities:** Accept a name string, split on whitespace, return the uppercase first letter of each word concatenated. Handle empty and whitespace-only input by returning an empty string.

## 2. Architecture Overview

- **Components:** Single new function in the existing `textutils` module — no new modules, services, or packages.
- **Boundaries:** The function is a pure transform with no I/O, no side effects, and no dependencies beyond Python builtins.
- **Ownership:** The `textutils` module and its test file are the only touched components; all owned by this story.
- **External dependencies:** None. Standard library only (`str.split`, `str.upper`, `str.join`).

## 3. Data Flow Design

- **Input:** A `str` (name).
- **Processing:** `str.split()` → take first character of each word → `str.upper()` → `str.join()`.
- **Output:** A `str` (uppercase initials, concatenated without separators).
- No async, no events, no persistence.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `initials` function in `textutils.py` | Extract and return uppercase initials | `str` → `str` | roeeoz/play1 |
| Export in `__init__.py` | Make `initials` importable from `testbed_utils` | — | roeeoz/play1 |
| `TestInitials` in `test_textutils.py` | Verify happy path, single word, empty input, extra whitespace | — | roeeoz/play1 |

## 5. Interface Contracts

- **Public API:** `from testbed_utils import initials` — follows the existing export pattern.
- **Function signature:** `def initials(name: str) -> str` — consistent with `slugify`, `truncate`, `word_count`.
- No cross-repo contracts; no event schemas; no external APIs.

## 6. Key Technical Decisions

- **Use `str.split()` (no arguments):** Splits on any whitespace run and strips leading/trailing whitespace — handles all specified edge cases in one call. This is the same approach used by `word_count`.
- **Generator expression over explicit loop:** `"".join(w[0].upper() for w in name.split())` — concise, idiomatic, and correct for empty input (`split()` returns `[]`, `join` returns `""`).
- **No new imports:** The implementation uses only builtins; no `re` or other module needed.

## 7. Risks & Constraints

| Risk | Severity | Mitigation |
|---|---|---|
| RK1 — Regression in existing helpers | Low | Existing tests for `slugify`, `truncate`, `word_count` remain untouched and run in the same pytest suite. |
| Line count cap (G3 ≤ 300) | None | Estimated ~32 changed lines, well under cap. |
| No coverage tool | Accepted | Four test methods achieve 100% branch coverage of the function; no `pytest-cov` to enforce mechanically. |
