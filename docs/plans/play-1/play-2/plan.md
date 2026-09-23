# Implementation Plan — US-01: `sentence_count` and `reading_time_minutes` helpers in `textutils`

**Repo:** `roeeoz/play1` (id `971bf272-f661-4343-ba13-83764c3aec1f`), branch `halo/feat/591b4c18` from `main`
**Work item:** t1 (T1, single item, no dependencies)
**Traces to:** R3, R4 · process step 3 · risks RK1, RK2 · open question Q2 (non-blocking)
**Inputs:** `spec.md`, `hld.md`, `work-items.md` in this folder (read, not edited)

## 1. Context

`src/testbed_utils/textutils.py` currently exposes three helpers (`slugify`, `truncate`, `word_count`) and nothing that counts sentences or estimates reading time. The upcoming `text-stats` CLI (US-02) needs both. This story adds two pure, stdlib-only functions after `word_count`, re-exports them from the package root, and covers the six acceptance scenarios in `tests/test_textutils.py`. No CLI, file I/O, packaging, README or CI changes.

## 2. Solution proposal

**Chosen approach:** append two single-expression pure functions to `textutils.py`, mirroring `word_count` exactly in style, and pin their contract with unit tests.

- `sentence_count(text: str) -> int` returns `sum(text.count(ch) for ch in ".!?")`. Each `.`, `!`, `?` character counts once; runs such as `"..."` count 3 and decimals such as `"3.14"` count 1. This is the literal reading of Scenario 1 and the working assumption recorded for Q2 / RK1.
- `reading_time_minutes(word_count: int) -> int` returns `max(1, -(-word_count // _WORDS_PER_MINUTE))` with a private module constant `_WORDS_PER_MINUTE = 200`. Integer ceiling division avoids a `math` import and float rounding; the `max(1, …)` floor satisfies RK2 (Scenarios 5 and 6).
- Both names are added to the `textutils` import line and to `__all__` in `src/testbed_utils/__init__.py` in alphabetical position. This is the repo's documented convention (README canned Task B says "Export it from testbed_utils/__init__.py") and gives US-02 a stable import from either path.
- Tests follow the existing per-function `TestX` class style with plain `assert` methods, one method per acceptance scenario plus one pinning the literal punctuation count and one asserting package-root importability.

**Key design decisions**

| Decision | Choice | Why | Rejected alternative |
| --- | --- | --- | --- |
| Sentence heuristic | Count `.`, `!`, `?` characters literally | Spec FR1 and HLD §5 state it; NLP parsing is out of scope | Regex for punctuation runs / abbreviation handling (would change `"..."` from 3 to 1, contradicting FR1) |
| Ceiling division | `-(-n // 200)` integer arithmetic | No new import, exact for ints, matches "stdlib-minimal" in HLD §6 | `math.ceil(n / 200)` (works, but adds an import and float division) |
| Input validation | None | Matches `word_count`; spec defines only non-negative ints; negative input returns 1 by the floor rule | `raise ValueError` like `truncate` (untested surface, not required) |
| Parameter name | `word_count`, shadowing the module function | Spec and HLD freeze this signature for US-02 | Rename to `words` (diverges from frozen contract) |
| Constant | Private `_WORDS_PER_MINUTE = 200` above the function | Names the magic number without widening the public API | Inline literal `200` (acceptable; the constant is a readability preference) |
| Doctests | One `>>>` example per function | Module convention; CI does not run doctests, so pytest remains the verified gate | None |

## 3. Research findings

**Change surface (three files, all additive):**

| File | Current state | Change |
| --- | --- | --- |
| `src/testbed_utils/textutils.py` | 4 imports/constants, 3 functions; `word_count` at lines 48–54 is last | Append `_WORDS_PER_MINUTE`, `sentence_count`, `reading_time_minutes` after `word_count` |
| `src/testbed_utils/__init__.py` | Line 10 imports `slugify, truncate, word_count`; `__all__` has 7 names alphabetically | Extend import; insert `"reading_time_minutes"` after `"is_weekend"` and `"sentence_count"` after `"reading_time_minutes"`, before `"slugify"` |
| `tests/test_textutils.py` | Line 1 imports 3 names; classes `TestSlugify`, `TestTruncate`, `TestWordCount` (12 tests) | Extend import; append `TestSentenceCount` and `TestReadingTimeMinutes` |

**Contracts:** `sentence_count(text: str) -> int` and `reading_time_minutes(word_count: int) -> int` are the interface US-02 will import from `testbed_utils.textutils` (and optionally from `testbed_utils`). Names, parameter order and return semantics are frozen at merge.

**Resolved unknowns:**

- Existing test count is 38 (`test_textutils` 12, `test_dateutils` 12, `test_pdfutils` 5, `test_pdf_extract_cli` 9), matching HLD §7. The baseline must stay green.
- `word_count` has no callers outside `textutils.py`, `__init__.py` and its test; shadowing the name inside `reading_time_minutes` affects nothing.
- CI (`.github/workflows/ci.yml`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12, plus the `CI_FAIL` gate. No linter, formatter or doctest run is configured. Local Python is 3.14; project floor is 3.10. Nothing planned uses syntax above 3.10.
- `pyproject.toml` `addopts = "-q"` and `testpaths = ["tests"]`; no pytest config change needed.
- There is no `AGENTS.md`, `CLAUDE.md` or `.factory/memory/` in the repo. The README instructs new textutils helpers to be exported from `__init__.py`.
- The `plan` skill named in the stage instructions is not installed in this session; this document follows the template of the platform's prior plan artefact (context, solution proposal, findings, ordered steps, verification, risks).

## 4. Ordered implementation tasks

All tasks belong to work item **t1**. Spec acceptance criteria are cited as AC1–AC8 (spec §5).

| # | Task | AC | File |
| --- | --- | --- | --- |
| 1 | Install `pip install -e ".[test]"`, run `pytest`, confirm 38 passed before any change | AC8 (baseline) | — |
| 2 | Add `_WORDS_PER_MINUTE = 200` and `sentence_count` after `word_count`. Docstring: one-line summary ("Estimate the number of sentences in *text* by counting terminal punctuation"), a note that each `.`, `!`, `?` counts individually and abbreviations/decimals are not special-cased, doctest `>>> sentence_count("Is this fast? Yes! It works.")` → `3` | AC1, AC2, AC7 | `textutils.py` |
| 3 | Add `reading_time_minutes` after `sentence_count`. Body `return max(1, -(-word_count // _WORDS_PER_MINUTE))`. Docstring: one-line summary (whole minutes at 200 wpm, rounded up, minimum 1), a note that no validation is performed to match `word_count`, doctest `>>> reading_time_minutes(450)` → `3` | AC3–AC7 | `textutils.py` |
| 4 | Extend the textutils import to `reading_time_minutes, sentence_count, slugify, truncate, word_count` (wrap in parentheses if over the file's line width) and insert both names into `__all__` alphabetically; leave existing entries untouched | AC7 | `__init__.py` |
| 5 | Extend line-1 import; append `class TestSentenceCount` with `test_counts_each_terminal_mark` (AC1), `test_no_terminal_punctuation_returns_zero` using `"just some words here"` (AC2), `test_run_of_punctuation_counts_each_character` asserting `sentence_count("Wait...") == 3` (FR1 literal-count contract) | AC1, AC2, AC8 | `tests/test_textutils.py` |
| 6 | Append `class TestReadingTimeMinutes` with `test_exact_multiple` (200 → 1, AC3), `test_rounds_up_fraction` (450 → 3, AC4), `test_minimum_one_minute_for_short_text` (10 → 1, AC5), `test_minimum_one_minute_for_zero_words` (0 → 1, AC6) | AC3–AC6, AC8 | `tests/test_textutils.py` |
| 7 | Add `test_importable_from_package_root` asserting `testbed_utils.sentence_count` and `testbed_utils.reading_time_minutes` resolve and both names are in `testbed_utils.__all__` | AC7 | `tests/test_textutils.py` |
| 8 | Run the verification table (§5), then commit with the work-item id in the message and open a small PR against `main` linking US-01 and listing Scenarios 1–6 | — | — |

Do not modify `slugify`, `truncate`, `word_count`, any existing test, `pdfutils.py`, `dateutils.py`, `pyproject.toml`, `README.md` or `.github/workflows/ci.yml`.

## 5. Verification (test gate)

| Check | Command | Must show |
| --- | --- | --- |
| Baseline | `pytest` (before changes) | `38 passed` |
| Unit tests | `pytest` (after changes) | `46 passed` (38 existing + 8 new), 0 failed, no existing test edited |
| Doctests (manual; CI does not run them) | `python -m doctest src/testbed_utils/textutils.py -v` | 5 examples, 0 failed (3 existing + 2 new) |
| Package-root import | `python -c "from testbed_utils import sentence_count, reading_time_minutes; print(sentence_count('Is this fast? Yes! It works.'), reading_time_minutes(450))"` | `3 3` |
| Blast radius | `git diff --stat main -- . ':!docs'` | exactly `src/testbed_utils/textutils.py`, `src/testbed_utils/__init__.py`, `tests/test_textutils.py` |
| CI | PR checks | `test` green on Python 3.12; `gate` green (no `CI_FAIL` file) |

**Acceptance mapping:** AC1–AC6 map one-to-one to the test methods in tasks 5–6. AC7 is covered by task 7 plus the fact that both bodies are single pure expressions with no I/O. AC8 is satisfied by the two new `TestX` classes in the existing style.

**Test layers touched:** unit tests in `tests/test_textutils.py` only. No fixtures, no CLI tests (`test_pdf_extract_cli.py` is untouched), no integration layer exists or is needed.

## 6. Risks & scope guards

- **Literal punctuation count (RK1 / Q2).** `"..."` → 3, `"3.14"` → 1. This is the spec's explicit reading; the docstring states it and `test_run_of_punctuation_counts_each_character` pins it so US-02 cannot be surprised. If Q2 is later answered differently, only `sentence_count`'s body and that one test change.
- **Minimum reading time (RK2).** Enforced by `max(1, …)` and verified by Scenarios 5–6.
- **Signature lock-in.** US-02 imports these exact names; do not rename after merge.
- **Parameter shadowing.** `word_count` the parameter hides `word_count` the function inside `reading_time_minutes`. Harmless because the body never calls it; a comment is unnecessary since the docstring explains the input.
- **No validation.** Negative input returns 1; a non-string to `sentence_count` raises `AttributeError` naturally. Consistent with `word_count`.
- **No formatter/linter.** Match PEP 8 and double quotes by hand; `pytest` is the only automated gate.
- **Scope guards.** Purely additive change to three files. Anything touching the CLI, `--json`, file reading, `pyproject.toml` or `README.md` belongs to US-02/US-03 and must be refused in this PR. Never create a `CI_FAIL` file.
- **Python floor.** Local 3.14, CI 3.12, project `>=3.10`; use no syntax newer than 3.10.
