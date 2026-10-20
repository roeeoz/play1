# Implementation Plan: Add `greet(name)` to `testbed_utils`

## Context

`testbed_utils` is a small fixture package used by CI and developer-tooling tests. It currently has no canonical trivial callable; `greet(name)` is added as that canonical "hello world" function so end-to-end tooling tests have a self-contained symbol to exercise. The change is purely additive and touches exactly three files.

## Approach

The function body already exists in `textutils.py` (present in the working tree). The two remaining gaps are wiring `greet` into the package's public API (`__init__.py`) and covering it with a pytest test (`tests/test_textutils.py`). Both edits are independent of each other and can be made in any order, but the test must be written last so the import it relies on is confirmed correct first.

## Steps

1. **Verify `textutils.py` (t1 — `src/testbed_utils/textutils.py`)**  
   Confirm the function body is present and matches the spec exactly:  
   ```python
   def greet(name: str) -> str:
       return f"Hello, {name}!"
   ```  
   No edit needed if already correct; otherwise append after `word_count`.

2. **Export `greet` from the package (t1 — `src/testbed_utils/__init__.py`)**  
   - Extend the `textutils` import line:  
     ```python
     from testbed_utils.textutils import greet, slugify, truncate, word_count
     ```  
   - Insert `"greet"` into `__all__` alphabetically between `"days_between"` and `"humanize_delta"`:  
     ```python
     __all__ = [
         "days_between",
         "greet",
         "humanize_delta",
         "is_weekend",
         "slugify",
         "truncate",
         "word_count",
     ]
     ```

3. **Add the pytest test (t1 — `tests/test_textutils.py`)**  
   - Update the top-of-file import to include `greet`:  
     ```python
     from testbed_utils import greet, slugify, truncate, word_count
     ```  
   - Append `TestGreet` after `TestWordCount`:  
     ```python
     class TestGreet:
         def test_returns_greeting(self):
             assert greet("Roee") == "Hello, Roee!"
     ```

## Verification

- After Step 2: `python -c "from testbed_utils import greet; print(greet('Roee'))"` must print `Hello, Roee!`.
- After Step 3: `pytest tests/test_textutils.py` must show `TestGreet::test_returns_greeting` passing with no pre-existing failures.
- Final: run the full `pytest` suite and confirm zero new failures. Confirm no `CI_FAIL` file exists at the repo root.

**Acceptance criteria mapping:**
| AC | Verified by |
|---|---|
| AC1 `greet("Roee") == "Hello, Roee!"` | `TestGreet::test_returns_greeting` |
| AC2 pytest test passes | `pytest` green |
| AC3 no new failures | full suite run |
| AC4 `from testbed_utils import greet` succeeds | Step 2 smoke-check |

## Risks & Open Points

- **`textutils.py` already modified**: the working tree already contains the `greet` function. Step 1 is a verification rather than a write; if the body differs from spec (wrong format string, missing type annotations), it must be corrected before proceeding.
- **`__all__` ordering**: `"greet"` must land between `"days_between"` and `"humanize_delta"`; misplacing it would violate the existing alphabetical convention (not a runtime error, but a style regression).
- **No other risks**: the change is additive; no existing code path, import, or test is modified.
