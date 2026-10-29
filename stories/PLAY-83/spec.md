# Feature Specification Document

## 1. Feature Overview

**Summary.** Modify the existing `truncate` helper in play1's textutils module so that it uses a single-character Unicode ellipsis ("…", U+2026) instead of the current three-character ASCII ellipsis ("..."), returns an empty string when the requested length is zero or negative instead of raising an error, and drops the configurable `suffix` parameter. The function's signature changes from `truncate(text, max_length, suffix="...")` to `truncate(text, n)`.

**Problem statement.** The current `truncate` helper uses a three-character ASCII ellipsis as its default suffix, which consumes three characters of the allowed length — an unpredictable trade-off for display-truncation use cases. It also raises `ValueError` on negative input, forcing every caller to guard against exceptions on edge-case input. Both behaviors make the helper less predictable than it should be for its intended purpose.

**Target users.** Developers using the play1 textutils package to truncate user-facing strings for display.

## 2. Goals & Non-Goals

### Goals

- **Predictable truncation output.** The truncated string always ends with a single-character ellipsis (U+2026) and its total length is exactly `n`, making display-width calculations straightforward.
- **Safe edge-case behavior.** Zero or negative lengths return an empty string without raising an exception, eliminating caller-side guards.
- **Trustworthy helper (G1).** The modified function ships with pytest tests covering the happy path, the exact-length boundary, `n ≤ 0`, and empty text; package coverage stays at or above 90%.
- **Discoverable helper (G2).** The function keeps a docstring with a usage example.
- **Small, composable change (G3).** One module changed plus its tests; well under the 300-line limit.
- **Fast, deterministic CI (G4).** Pure string operation; no external dependencies; tests do not depend on the network, the clock, or file-system state.

### Non-Goals

- A configurable suffix parameter — the function uses a fixed single-character ellipsis; configurability belongs to a future epic if needed.
- Other textutils functions (`slugify`, `word_count`) — unchanged by this feature.
- Console scripts or CLI entry points — the function is a library helper only.
- Performance optimization beyond pure Python — a non-goal of the project (play1 — goals and success metrics, Non-goals section).

## 3. Functional Requirements

- **FR1 (R1).** The function shall return text unchanged when `len(text) <= n`. (To-be process step 3; without this the helper corrupts short strings.)
- **FR2 (R2).** The function shall return the first `n − 1` characters followed by a single Unicode ellipsis character ("…", U+2026) when `len(text) > n`, for a total output length of exactly `n` characters. (To-be process step 4; this is the helper's core purpose.)
- **FR3 (R3).** The function shall return an empty string when `n <= 0`. (To-be process step 2; without this the caller must guard against errors on zero or negative input.)
- **FR4 (R4).** The function shall be a pure-Python implementation using only the standard library, introducing no new runtime dependency. (Engineering requirements, Infrastructure section.)
- **FR5 (R5).** The function shall ship with a docstring containing a usage example. (play1 — goals and success metrics, Goals table.)
- **FR6 (R6).** The function shall ship with pytest unit tests covering: the happy path (text longer than `n`), the exact-length boundary (`len(text) == n`), `n <= 0`, and empty text. (play1 — goals and success metrics, Goals table.)
- **FR7 (R7).** Package test-suite coverage shall stay at or above 90% after the change. (play1 — goals and success metrics, Goals table.)
- **FR8 (R8).** Tests shall not depend on the network, the clock, or file-system state outside `tests/fixtures`. (play1 — goals and success metrics, Goals table.)

**Inputs.** `text` (a string) and `n` (an integer maximum character length).

**Outputs.** A string whose length is at most `n`.

**Core workflow (to-be process).**

| Step | Actor | Action |
| --- | --- | --- |
| 1 | Caller | Invokes `truncate(text, n)` with a string and a maximum character length |
| 2 | System | If `n ≤ 0`, returns an empty string |
| 3 | System | If `len(text) ≤ n`, returns text unchanged |
| 4 | System | Otherwise, returns the first `n − 1` characters of text followed by a single-character ellipsis ("…"), for a total length of exactly `n` |

**Edge cases.**

- `n = 1` with text longer than 1: returns "…" (length 1). Deterministically resolved by step 4.
- Empty text with any positive `n`: returns "" (empty string). Resolved by step 3 (`len("") == 0 ≤ n`).
- `n = 0`: returns "" (empty string). Resolved by step 2.
- Negative `n`: returns "" (empty string). Resolved by step 2.

## 4. User Experience & Behavior

**Key user flow.** A developer imports `truncate` from `testbed_utils.textutils` and calls it with a string and a maximum length. The return value is always a string of at most `n` characters, ending with a single-character ellipsis when truncation occurred.

**States the user observes.**

| Input condition | Output |
| --- | --- |
| `n ≤ 0` | `""` (empty string) |
| `len(text) ≤ n` | `text` (unchanged) |
| `len(text) > n` | first `n − 1` characters + "…" (total length `n`) |

**User-facing edge cases.** No exception is raised for any combination of inputs. The function always returns a string.

**Signature change.** The function's signature changes from `truncate(text, max_length, suffix="...")` to `truncate(text, n)`. The configurable `suffix` parameter is removed. The package is version 0.x with no backwards-compatibility guarantee (play1 — goals and success metrics, Non-goals section).

## 5. Acceptance Criteria

1. **Scenario 1 — Happy path: text longer than n is truncated with ellipsis.** Given text of 11 characters and `n = 8`, when `truncate` is called, then it returns the first 7 characters followed by a single Unicode ellipsis character (U+2026), and the total output length is exactly 8.
2. **Scenario 2 — Boundary: text exactly n characters is unchanged.** Given text of exactly 5 characters and `n = 5`, when `truncate` is called, then it returns the text unchanged with no ellipsis appended.
3. **Scenario 3 — Edge case: empty text is unchanged.** Given an empty string and any positive `n`, when `truncate` is called, then it returns an empty string.
4. **Scenario 4 — Error case: n is zero or negative.** Given any text and `n <= 0`, when `truncate` is called, then it returns an empty string without raising an exception.
5. **Cross-cutting: docstring with example.** The function has a docstring containing a usage example (FR5).
6. **Cross-cutting: test coverage.** The function ships with pytest tests covering scenarios 1–4, and package test-suite coverage stays at or above 90% (FR6, FR7).
7. **Cross-cutting: deterministic tests.** Tests do not depend on the network, the clock, or file-system state outside `tests/fixtures` (FR8).
8. **Cross-cutting: no new dependency.** No new runtime dependency is introduced (FR4).

## 6. Dependencies & Constraints (product-level)

- **No dependencies.** This story has no dependencies on other stories or external systems.
- **No backwards-compatibility guarantee.** The package is version 0.x (play1 — goals and success metrics, Non-goals section). Callers outside the repository who depend on the old behavior must pin the version or adapt.
- **Traceability (R7 — Engineering requirements).** The pull request must name this story (PLAY-83) and the Epic PRD it came from.

## 7. Technical Design (deferred to STRUCTURE)

Architecture, implementation approach, error-handling internals, and the PR-level breakdown are produced by the tech lead in the STRUCTURE stage from this approved product spec.

**Technical constraints the product imposes:**
- Pure Python, standard library only (FR4).
- The function already exists in `textutils.py` and is modified in place — not added as a second function (Epic PRD, Assumptions and decisions).
- The existing five tests must be updated or replaced to match the new behavior.

## 8. Open Questions

None.
