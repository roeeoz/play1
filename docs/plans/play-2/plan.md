# Implementation Plan — US-01: `sentence_count` and `reading_time_minutes` helpers in `textutils`

**Repo:** `roeeoz/play1` (id `971bf272-f661-4343-ba13-83764c3aec1f`), branch from `main`
**Work item:** t1 (T1, single item, no dependencies)
**Traces to:** R3, R4 · step 3 · RK1, RK2

## 1. Context

The `textutils` module of testbed-utils currently only knows how to count words. The upcoming `text-stats` CLI (US-02) also needs a sentence count and a whole-minute reading-time estimate, and no such logic exists anywhere in the repository. This story adds two pure, stdlib-only helpers next to `word_count`, re-exports them from the package root, and covers the six acceptance scenarios with pytest. No CLI, file I/O, packaging, or README changes.

## 2. Approach

One work item, purely additive, three files. Work proceeds in a single pass: clone the repo (the local workspace is empty), record the baseline test count, append the two functions after `word_count` in `src/testbed_utils/textutils.py` following its existing style (`from __future__ import annotations` already present, full type hints, one-line summary docstring, one `>>>` doctest example), extend the re-export in `src/testbed_utils/__init__.py`, and append two `TestX` classes to `tests/test_textutils.py`.

Reused as-is: the `word_count` pattern for style, the alphabetical `__all__` convention in `__init__.py` (which the README's own canned Task B documents), and the per-function `TestX` class style with plain `assert` methods. Ceiling division uses integer arithmetic (`-(-n // 200)` or `(n + 199) // 200`) so no new import is needed and float rounding is avoided. No sequencing constraints: nothing depends on this item and it depends on nothing.

## 3. Steps

All steps belong to work item **t1**.

1. **Clone and baseline.** `git clone` `roeeoz/play1`, create a branch `halo/feat/<work-item-id>` from `main` (matching prior agent PR naming; no written convention exists). Run `pip install -e ".[test]"` then `pytest` and confirm 38 tests pass before any change.

2. **Add `sentence_count` to `src/testbed_utils/textutils.py`.** Append after `word_count` (currently the last function in the file):
   - Signature `def sentence_count(text: str) -> int:`.
   - Body: `return sum(text.count(ch) for ch in ".!?")`.
   - Docstring: one-line summary stating it counts terminal punctuation marks (`.`, `!`, `?`) as an estimate of sentence count, a note that each character counts individually (so `"..."` yields 3 and abbreviations/decimals are not special-cased), and one doctest: `>>> sentence_count("Is this fast? Yes! It works.")` → `3`.
   - No new imports. Do not touch `slugify`, `truncate`, or `word_count`.

3. **Add `reading_time_minutes` to `src/testbed_utils/textutils.py`.** Append after `sentence_count`:
   - Signature `def reading_time_minutes(word_count: int) -> int:` (the parameter name is fixed by the spec and intentionally shadows the module-level function; the body must not call `word_count()`).
   - Body: `return max(1, -(-word_count // 200))`.
   - Docstring: one-line summary (estimated reading time in whole minutes at 200 words per minute, rounded up, minimum 1), a note that no input validation is performed to match `word_count` and that a negative count is out of contract, and one doctest: `>>> reading_time_minutes(450)` → `3`.
   - Optionally define a module-level constant `_WORDS_PER_MINUTE = 200` immediately above the function; keep it private (underscore) so it is not part of the public surface.

4. **Re-export from `src/testbed_utils/__init__.py`.**
   - Change the textutils import line to `from testbed_utils.textutils import reading_time_minutes, sentence_count, slugify, truncate, word_count` (wrap in parentheses across lines if it exceeds the file's existing line width).
   - Insert `"reading_time_minutes"` and `"sentence_count"` into `__all__` at their alphabetical positions among the existing seven names. Do not reorder or remove existing entries.

5. **Extend `tests/test_textutils.py`.**
   - Extend the line-1 import to include `reading_time_minutes` and `sentence_count`.
   - Append `class TestSentenceCount:` after `TestWordCount` with methods:
     - `test_counts_each_terminal_mark`: `sentence_count("Is this fast? Yes! It works.") == 3` (Scenario 1).
     - `test_no_terminal_punctuation_returns_zero`: e.g. `sentence_count("just some words here") == 0` (Scenario 2).
     - `test_run_of_punctuation_counts_each_character`: `sentence_count("Wait...") == 3` (documents the literal-count contract from FR1).
   - Append `class TestReadingTimeMinutes:` with methods:
     - `test_exact_multiple`: `reading_time_minutes(200) == 1` (Scenario 3).
     - `test_rounds_up_fraction`: `reading_time_minutes(450) == 3` (Scenario 4).
     - `test_minimum_one_minute_for_short_text`: `reading_time_minutes(10) == 1` (Scenario 5).
     - `test_minimum_one_minute_for_zero_words`: `reading_time_minutes(0) == 1` (Scenario 6).
   - Optionally add `test_importable_from_package_root` asserting both names resolve via `import testbed_utils` and appear in `testbed_utils.__all__`, covering acceptance criterion 7.
   - Do not modify any existing test.

6. **Verify and open the PR.** Run the checks in §4, commit with a message prefixed by the work-item id, push, and open a small PR against `main` titled with the work-item id and story name, body linking the story and listing the six scenarios covered.

## 4. Verification

| Check | Command | Expected |
| --- | --- | --- |
| Baseline (before changes) | `pytest` | 38 passed |
| Unit tests (after changes) | `pytest` | 38 existing + 7–8 new passed, 0 modified |
| Doctests (CI does not run these; check by hand) | `python -m doctest src/testbed_utils/textutils.py -v` | both new examples pass, existing examples unchanged |
| Package-root import | `python -c "from testbed_utils import sentence_count, reading_time_minutes; print(sentence_count('Is this fast? Yes! It works.'), reading_time_minutes(450))"` | `3 3` |
| Blast radius | `git diff --stat main` | exactly three files: `textutils.py`, `__init__.py`, `tests/test_textutils.py` |
| CI | PR checks | `test` job green on Python 3.12; `gate` job green (no `CI_FAIL` file) |

**Acceptance mapping:** Scenarios 1–6 map one-to-one to the test methods in step 5. Criterion 7 (defined next to `word_count`, importable, no side effects) is covered by the import check and the fact that both bodies are single pure expressions. Criterion 8 (per-function `TestX` style) is satisfied by the two new classes.

## 5. Risks & open points

- **Literal punctuation count (RK1 / Q2).** `"..."` yields 3 and `"3.14"` yields 1. This is the spec's explicit reading and the epic's working assumption; the docstring states it, and a test pins it so US-02 cannot be surprised. If Q2 is later answered differently, only `sentence_count`'s body and that one test change.
- **No input validation.** Matches `word_count`. A negative word count returns 1 by the floor rule; a non-string passed to `sentence_count` raises `AttributeError` naturally. Raising `ValueError` like `truncate` was considered and deferred as untested surface.
- **Parameter shadowing.** `reading_time_minutes(word_count)` shadows the module-level `word_count` function inside its body. Harmless because the body never calls it; renaming would diverge from the spec's frozen signature that US-02 will consume.
- **Signature lock-in.** Names, parameter order, and return semantics become a contract for US-02 at merge. Do not rename afterward.
- **Python floor.** Local 3.14, CI 3.12, project `>=3.10`. Nothing planned uses syntax newer than 3.10.
- **No formatter or linter in the repo.** PEP 8 and double-quote style are matched by hand; the only automated gate is `pytest`.
- **Branch/PR naming.** Not specified anywhere in the repo; `halo/feat/<id>` follows recent history. Reviewer may prefer another convention.
