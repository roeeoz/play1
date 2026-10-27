# Implementation plan — PLAY-69: Add `word_count` helper to the guestbook package

| Field | Value |
| --- | --- |
| Work item | t1 — Add word_count function and tests to the guestbook package |
| Repo | `roeeoz/play1` — checkout at `/Users/roeeoz/.halo/workspaces/delivery-6b134ec6f2ff4cc14954d95aa2b1cdc0/workspace/play1-79db628f23` |
| Tier | T1 (single work item, no dependencies) |
| Traces | R1–R7 · spec AC1–AC5 · HLD §2, §5, §6 |
| Inputs read | `docs/plans/play-68/play-69/spec.md`, `hld.md`, `work-items.md`; `src/guestbook/{__init__,app,validation}.py`; `src/testbed_utils/textutils.py`; `tests/test_textutils.py`; `tests/test_guestbook_api.py`; `pyproject.toml`; `.github/workflows/ci.yml`; `.factory/testing.md` |

## Context

Story PLAY-69 adds a pure helper function `word_count(text: str) -> int` to the guestbook package in a new module `src/guestbook/text_utils.py`, with a docstring containing a usage example and pytest tests covering the happy path, a boundary case and an error case. The function returns the count of whitespace-separated words (0 for empty or whitespace-only input) using only `str.split()`. A similar function exists at `src/testbed_utils/textutils.py:46-52`; this placement is intentional per the PRD (RK2). The planning inputs (`spec.md`, `hld.md`, `work-items.md`) sit beside this file in `docs/plans/play-68/play-69/` on the `halo/feat/play-69` branch.

## Research findings

### Change surface

| Path | Action | Why |
| --- | --- | --- |
| `src/guestbook/text_utils.py` | **create** | New module housing `word_count`. The package uses a setuptools `src/` layout (`pyproject.toml:25` `where = ["src"]`). |
| `tests/test_text_utils.py` | **create** | Pytest coverage for AC1–AC5. Follows the repo's `test_<module>.py` naming convention. |

Nothing else changes. Specifically **not** touched: `src/guestbook/__init__.py` (HLD §3 — no re-export, no change to existing modules), `pyproject.toml` (no new dependency), `.github/workflows/ci.yml`, any `testbed_utils` file, any existing test file. No `CI_FAIL` file exists at the root and none must be created.

### Existing conventions observed

**Guestbook package (`src/guestbook/`):**
- Module docstring: descriptive paragraph (`validation.py:1-4`).
- `from __future__ import annotations` as first import (`validation.py:7`, `app.py:3`).
- Type hints on every signature; return types are concrete (`str`, `int`, `dict`).
- Function docstrings use `*param*` emphasis with `>>>` examples (`validation.py:38-41`).
- Validation errors are `ValueError` with short messages, or natural Python exceptions (`validation.py:22`).

**Test files (`tests/`):**
- One `Test<Name>` class per logical group, plain `assert` statements (`test_textutils.py:4-46`).
- Import directly from the submodule (`test_textutils.py:1`).
- Error cases use `pytest.raises(ExceptionType)` (`test_guestbook_api.py`, `test_textutils.py:33`).
- No `conftest.py`, no path manipulation.

**Sibling implementation (`src/testbed_utils/textutils.py:46-52`):**
```python
def word_count(text: str) -> int:
    """Count whitespace-separated words in *text*.

    >>> word_count("the quick  brown fox")
    4
    """
    return len(text.split())
```
The guestbook version follows the same algorithm. The body is `return len(text.split())` — `str.split()` with no arguments splits on any whitespace and discards empties, which satisfies AC1–AC3.

### Toolchain

- `pyproject.toml`: `requires-python >= 3.10`, test extra `pytest>=8`, `testpaths = ["tests"]`, `addopts = "-q"`.
- `.factory/testing.md`: `test-gate: pytest`. No linter, formatter, type checker or coverage tool.
- CI (`.github/workflows/ci.yml`): job **test** = `pip install -e ".[test]"` then `pytest` on Python 3.12, ubuntu-latest; job **gate** fails iff `CI_FAIL` exists at root.

### Contracts

**Provided (new):** `word_count(text: str) -> int` importable as `from guestbook.text_utils import word_count`. No downstream consumer exists today.

**Consumed:** nothing beyond the Python standard library (`str.split`, `len`).

## Locked decisions and assumptions

### Locked decisions

| Decision | Source |
| --- | --- |
| Function signature is `word_count(text: str) -> int`. | R1, spec FR1 |
| Module path is `src/guestbook/text_utils.py`. | HLD §2 |
| No `__init__.py` re-export — import from `guestbook.text_utils`. | HLD §3 ("Avoids changing an existing module; respects G3") |
| Function returns 0 for empty and whitespace-only input. | R2, spec FR2 |
| Uses only `str.split()` from the standard library; no new dependency. | R3, spec FR3, HLD §2 |
| Docstring contains a `>>>` usage example. | R4, spec FR4 |
| Test file is `tests/test_text_utils.py`. | HLD §6 |
| No existing file in the repository is modified. | work-items.md AC8 |
| Error handling for non-string input: the coding agent decides between an explicit `TypeError` guard or natural `AttributeError` from `.split()`. | HLD §6 ("The coding agent decides") |

### Assumptions

| Assumption | Evidence | Consequence if wrong |
| --- | --- | --- |
| An explicit `TypeError` guard (`if not isinstance(text, str): raise TypeError(...)`) is preferable to a natural `AttributeError`. | AC4 says "raises `TypeError` or `AttributeError`"; an explicit guard produces a clearer message and a predictable exception type the test can assert on. The sibling `textutils.word_count` has no guard and would raise `AttributeError`; neither is wrong per the AC. | The test adjusts its `pytest.raises` target. Both are accepted by the AC. |
| The docstring example uses the exact form `>>> word_count("The quick brown fox")` / `4`, matching the sibling's style. | Sibling at `src/testbed_utils/textutils.py:49-50`; spec AC5 requires "at least one usage example showing the function called with a sample string and the expected integer result". | No impact; any correct example satisfies AC5. |

## Solution proposal

One new module of one pure function, written in the guestbook package's existing style, plus one test file. The implementation is a near-copy of the sibling `testbed_utils.textutils.word_count` with one addition: an explicit `isinstance` guard that raises `TypeError` for non-string input, giving tests a predictable exception type. The function body is `return len(text.split())` — Python's default `str.split()` splits on any whitespace and discards empties, satisfying the normal-sentence, mixed-whitespace, and empty/whitespace-only scenarios with no additional logic.

No alternative was seriously considered: the function is a one-liner by specification, the module placement and naming are fixed by the HLD, and the only design choice (explicit guard vs. natural `AttributeError`) is minor. The explicit guard is preferred because it names the problem ("expected str") rather than exposing an implementation detail (`.split()` on `None`).

Total change: ~15 lines of production code (including docstring), ~30 lines of test code, ~45 lines total — well under the 300-line cap (G3).

## Ordered implementation steps

All steps belong to work item **t1**. Order: module → tests → verify.

1. **Create `src/guestbook/text_utils.py`.**
   - Module docstring in the guestbook style (one paragraph, descriptive).
   - `from __future__ import annotations` as first import.
   - `word_count(text: str) -> int`: explicit `isinstance` guard raising `TypeError` if `text` is not a `str`; body is `return len(text.split())`.
   - Docstring with `*text*` emphasis and a `>>>` example: `word_count("The quick brown fox")` → `4`.
   - Files: `src/guestbook/text_utils.py` (new).
   - Advances: AC1 (happy path), AC2 (mixed whitespace), AC3 (boundary), AC4 (error case), AC5 (docstring).
   - Test layer: pytest (`tests/test_text_utils.py`, created in step 2).

2. **Create `tests/test_text_utils.py`.**
   - Import `from guestbook.text_utils import word_count`.
   - `TestWordCount` class with the following tests:

   | Test | Assertion | AC |
   | --- | --- | --- |
   | `test_normal_sentence` | `word_count("The quick brown fox") == 4` | AC1 |
   | `test_mixed_whitespace` | `word_count("  hello\tworld\nfoo  ") == 3` | AC2 |
   | `test_empty_string` | `word_count("") == 0` | AC3 |
   | `test_whitespace_only` | `word_count("   \t\n") == 0` | AC3 |
   | `test_non_string_raises` | `pytest.raises(TypeError)` on `word_count(None)` and `word_count(42)` | AC4 |

   - All tests are pure string-in / int-out; no network, clock, or file-system dependency (G4, AC10 from work-items.md).
   - Files: `tests/test_text_utils.py` (new).
   - Test layer: pytest (package-api layer from `.factory/testing.md`).

3. **Verify locally.**
   - Run `pip install -e ".[test]" && pytest` from the repo root.
   - Confirm all existing and new tests pass.
   - Confirm `git diff --stat` shows exactly two new files.
   - Confirm no `CI_FAIL` file at root.
   - Files: none changed.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1 | t1 | Add word_count function and tests to the guestbook package |
| 2 | t1 | Add word_count function and tests to the guestbook package |
| 3 | t1 | Add word_count function and tests to the guestbook package |

Single work item; no mapping gap.

## Verification and CI gate

From the repo root, after step 3:

```bash
pip install -e ".[test]"
pytest
pytest tests/test_text_utils.py -v
python -c "from guestbook.text_utils import word_count; print(word_count('The quick brown fox'))"
git diff --stat main
test ! -e CI_FAIL && echo "no CI_FAIL"
```

Expected:

- `pytest` — whole suite passes; existing tests (`test_textutils`, `test_dateutils`, `test_pdfutils`, `test_pdf_extract_cli`, `test_guestbook_api`, `test_hello`, `test_hello_cli`, `test_numutils`, `test_num_summary_cli`) still green.
- `pytest tests/test_text_utils.py -v` — 5 tests pass, each mapped to an AC in step 2.
- The `python -c` smoke test prints `4`.
- `git diff --stat main` shows exactly two new files (`src/guestbook/text_utils.py`, `tests/test_text_utils.py`), roughly 45 total lines, well under the 300-line cap.
- `pyproject.toml` has no diff (proves no new dependency, AC7 from work-items.md).
- No `CI_FAIL` file exists.

The repo has no linter, formatter or type checker, so `pip install -e ".[test]" && pytest` is the complete pre-merge check. CI's **test** job repeats the same on Python 3.12; the **gate** job stays green as long as `CI_FAIL` is absent. No change to `.factory/testing.md` or `.github/workflows/ci.yml` is needed.

## Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **Name collision with sibling (RK2).** `testbed_utils.textutils.word_count` has identical semantics. | Intentional per PRD. Different package, different module name (`text_utils` vs `textutils`). PR description notes the relationship and reason. |
| **Coverage gate unenforced (RK1).** Epic targets ≥90% but no `pytest-cov` is configured. | Out of scope. The five required test cases cover the function's behaviour. Flagged in the PR body. |
| **Scope lock.** | Only two new files: `src/guestbook/text_utils.py` and `tests/test_text_utils.py`. Do NOT modify `__init__.py`, `pyproject.toml`, CI config, README, any `testbed_utils` file, any existing test, or any other existing file. Do NOT create `CI_FAIL`. Do NOT add a console script or CLI entry point. |
| **Error-handling choice.** The explicit `TypeError` guard is an assumption, not a locked decision. | If the developer or reviewer prefers natural `AttributeError`, the guard is removed and the test's `pytest.raises` target changes. Both are accepted by AC4. |
| **No merge without human approval.** | The implement phase opens a PR; a human reviewer approves and merges. No skill in this run pushes, polls CI, or merges. |

## Clarification outcomes

None. All requirements are fully specified by the story, the HLD, and the work-items breakdown. No `plan-questions.json` is written.
