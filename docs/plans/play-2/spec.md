# Feature Specification Document

## 1. Feature Overview

**Summary:** Add two new pure helper functions, `sentence_count` and `reading_time_minutes`, to the existing `textutils` module in testbed-utils, placed alongside the existing `word_count` helper. Both functions are independently testable and carry no CLI, file-handling, or packaging logic — they are computational building blocks that a later story (the `text-stats` CLI) will wire together with the existing `word_count` helper.

**Problem statement:** testbed-utils' `textutils` module currently only knows how to count words. Downstream work (an upcoming `text-stats` command) needs to also report a sentence count and an estimated reading time for a piece of text, but no such logic exists yet anywhere in the repository.

**Target users / actors:** A testbed-utils maintainer/developer working directly in the `textutils` module. There is no end-user-facing surface in this story — the "user" of this feature is the next developer (in the following story) who will import and call these two functions.

---

## 2. Goals & Non-Goals

### Goals
- Provide a `sentence_count(text)` function that counts sentences in a string by counting terminal punctuation marks (`.`, `!`, `?`).
- Provide a `reading_time_minutes(word_count)` function that estimates reading time in whole minutes from a word count, assuming 200 words per minute, rounded up, with a minimum of 1 minute.
- Cover both functions with pytest unit tests for the happy path, edge cases, and boundary conditions named in the acceptance criteria.

### Non-Goals
- No CLI, console script, or `--json` flag (delivered in a later story).
- No file reading or file-existence handling (delivered in a later story).
- No `pyproject.toml` / packaging changes (delivered in a later story).
- No README changes (delivered in a later story).
- No linguistic/NLP-aware sentence parsing (e.g., handling abbreviations like "Dr." or decimals like "3.14" as non-sentence-ending punctuation) — the punctuation-count heuristic is the accepted approach for this story.
- No change to the existing `word_count` helper's behavior or definition of a "word."

---

## 3. Functional Requirements

- **FR1 — `sentence_count(text)`:** Given a string `text`, return an integer count of sentences, computed as the total number of terminal punctuation characters (`.`, `!`, `?`) found in `text`. Each occurrence of any of these three characters counts individually (e.g., a run of punctuation like `"..."` or `"?!"` counts each character separately, per the literal reading of Scenario 1's "one for each terminal punctuation mark ... found").
 - Input: a string (may contain zero or more of `.`, `!`, `?`).
 - Output: a non-negative integer.
 - Edge case: a string with words but none of `.`, `!`, `?` returns 0.

- **FR2 — `reading_time_minutes(word_count)`:** Given an integer `word_count`, return the estimated reading time in whole minutes, computed as `ceil(word_count / 200)`, with a floor of 1 minute regardless of how small (including zero) `word_count` is.
 - Input: a non-negative integer word count.
 - Output: a positive integer (minimum 1).
 - Edge case: `word_count = 0` returns 1 (minimum applies even with no words).
 - Boundary: `word_count = 200` returns exactly 1; `word_count = 450` returns 3 (2.25 rounded up).

- **FR3 — Test coverage:** Both functions must have pytest coverage exercising every acceptance-criteria scenario listed below (§5).

**Core workflow:** These are pure, stateless functions with no side effects, no I/O, and no dependency on each other beyond both living in `textutils` next to `word_count`. A caller (in a later story) will call `word_count()`, then pass its result into `reading_time_minutes()`, and separately call `sentence_count()` on the raw text.

---

## 4. User Experience & Behavior

This story has no end-user-facing UI, CLI output, or observable runtime behavior beyond the function call/return contract described above — it is a pure-code addition consumed by other developers/code, not by an end user. There are no visual, formatting, or interaction qualities to specify here; the "user" experience is the function signature and its documented return value, which is fully covered by the functional requirements and acceptance criteria.

---

## 5. Acceptance Criteria

1. **Happy path — mixed punctuation:** `sentence_count("Is this fast? Yes! It works.")` returns `3`.
2. **Edge case — no terminal punctuation:** `sentence_count(<a string with words but no ".", "!", or "?">)` returns `0`.
3. **Happy path — exact multiple:** `reading_time_minutes(200)` returns `1`.
4. **Boundary — rounds up fractional result:** `reading_time_minutes(450)` returns `3`.
5. **Boundary — minimum for short text:** `reading_time_minutes(10)` returns `1`.
6. **Edge case — minimum applies at zero:** `reading_time_minutes(0)` returns `1`.
7. Both functions are defined in the `textutils` module alongside `word_count`, are importable, and have no file-handling, CLI, or packaging side effects.
8. Pytest test cases exist covering scenarios 1–6 above, following the existing per-function `TestX` class test style already used in the module's test file.

---

## 6. Dependencies & Constraints (product-level)

- Depends on the existing `textutils` module and `word_count` helper already present in the repository — no other precondition.
- No dependency on or interaction with the `pdf-extract` console script or any other existing command.
- This story is a prerequisite for the later `text-stats` CLI story, which will consume both functions as-is; their function signatures and return semantics must not change once that story begins.
- Constraint: the sentence-counting approach is a documented, accepted estimate (punctuation-count heuristic) — not a request to build linguistically accurate sentence detection.

---

## 7. Technical Design (deferred to STRUCTURE)

Not addressed here. Implementation details such as exact algorithm expression (e.g., `sum(text.count(c) for c in ".!?")` vs. a regex), type hints/docstring/doctest conventions, whether the two new functions are added to `textutils/__init__.py`'s `__all__` re-export list, and exact test file structure are left to the STRUCTURE stage and implementer, provided the acceptance criteria in §5 are satisfied.

---

## 8. Open Questions (product-level)

- None blocking. One implementation-facing note carried forward for the implementer (not gating this story): the repository's existing convention re-exports every public `textutils` function through `textutils/__init__.py`'s `__all__`; whether `sentence_count` and `reading_time_minutes` should be added there is unspecified by this story's acceptance criteria and doesn't affect any of the six testable scenarios above, so it does not block readiness.
