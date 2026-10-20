# HLD — US-01: `sentence_count` and `reading_time_minutes` helpers in `textutils`

## 1. System Overview
- **What:** Two new pure helper functions added to the existing `textutils` module of `testbed-utils` (repo `roeeoz/play1`), alongside `word_count`.
- **Problem:** `textutils` only counts words. The upcoming `text-stats` CLI (US-02) needs a sentence count and a reading-time estimate, and no such logic exists.
- **Responsibilities:** compute a sentence count from raw text by terminal-punctuation count; compute whole-minute reading time from a word count at 200 wpm, rounded up, minimum 1. Nothing else.

## 2. Architecture Overview
- **Single component:** `src/testbed_utils/textutils.py`, a stdlib-only module whose docstring names it as the intended extension point for new text helpers.
- **Package surface:** `src/testbed_utils/__init__.py` re-exports every public `textutils` function through `__all__` in alphabetical order; the README's own canned task instructs new helpers to be exported there. The new names follow that convention.
- **Tests:** `tests/test_textutils.py`, one `TestX` class per function with plain `assert` methods, importing directly from `testbed_utils.textutils`.
- **External dependencies:** none. No new imports beyond the standard library; integer arithmetic suffices for ceiling division.
- **Untouched:** `pdfutils.py`, `pyproject.toml`, `README.md`, `.github/workflows/ci.yml`.

## 3. Data Flow Design
- Fully synchronous, in-memory, side-effect free.
- Caller (US-02, later) passes raw text to `sentence_count` and the result of `word_count` to `reading_time_minutes`. The two new functions do not call each other or `word_count`.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| `textutils.sentence_count` | Count `.`, `!`, `?` characters in a string | `str` → non-negative `int` | 971bf272-f661-4343-ba13-83764c3aec1f |
| `textutils.reading_time_minutes` | Ceiling of words ÷ 200, floored at 1 | non-negative `int` → positive `int` | 971bf272-f661-4343-ba13-83764c3aec1f |
| Package re-export | Expose both names from `testbed_utils` root | — | 971bf272-f661-4343-ba13-83764c3aec1f |
| Unit tests | Cover the six acceptance scenarios | — | 971bf272-f661-4343-ba13-83764c3aec1f |

## 5. Interface Contracts
- `sentence_count(text: str) -> int` and `reading_time_minutes(word_count: int) -> int` are the call contract US-02 will consume. Names, parameter order, and return semantics are frozen at merge.
- Both names are importable from `testbed_utils.textutils` and from the `testbed_utils` package root.
- Punctuation counting is literal: each `.`, `!`, `?` character counts once, so `"..."` yields 3 and `"3.14"` yields 1. This is the accepted estimate per the spec and epic risk RK1.

## 6. Key Technical Decisions
- **Re-export from `__init__.py`:** yes. It is the documented repo convention, costs two lines, and gives US-02 a stable import path either way.
- **Ceiling division via integer arithmetic** rather than `math.ceil`, to keep the module stdlib-minimal and avoid float rounding. Implementer may choose either; behavior is identical for integer inputs.
- **No input validation** beyond what the spec requires. `word_count` does not validate; matching it is the simplest consistent choice. A negative word count is out of contract and will return 1 by the floor rule.
- **Doctests included for consistency** with the module's style, but CI does not run `--doctest-modules`, so all verified coverage lives in `tests/test_textutils.py`.
- **Alternatives considered:** regex-based sentence detection (rejected: spec forbids NLP-aware parsing); raising on negative input like `truncate` (deferred: not required, would add untested surface).

## 7. Risks & Constraints
- **Signature lock-in:** US-02 depends on these exact names and semantics; do not rename after merge.
- **Parameter shadowing:** the parameter `word_count` shadows the module-level function inside `reading_time_minutes`. Harmless since the body never calls it; renaming would diverge from the spec's stated signature.
- **Python version:** local 3.14, CI 3.12, project floor 3.10. Use no syntax newer than 3.10.
- **No formatter/linter configured:** match existing PEP 8, double-quote style by hand. Only `pytest` runs in CI.
- **Blast radius:** purely additive; the existing 38 tests must remain green untouched.
