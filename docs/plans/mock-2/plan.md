# Implementation Plan: testbed_utils Performance Optimisations

## Context

`testbed_utils` is a pure-Python stdlib library used in Demerzel integration-test fixtures. Two functions have concrete, auditable inefficiencies: `slugify` performs an unnecessary encode→decode round-trip creating an intermediate bytes object, and `truncate` recomputes `len(text)` and `len(suffix)` on every conditional branch instead of once. The fix eliminates these redundancies with semantically equivalent rewrites and adds a benchmark test file as a verifiable regression gate.

## Approach

Work item **t1** (modify `src/testbed_utils/textutils.py`) has no dependencies and must land first. Work item **t2** (create `tests/test_performance.py`) imports the optimised functions from t1 and must follow. Both items touch only one file each. No changes to `pyproject.toml`, `ci.yml`, `__init__.py`, or any test file other than the new benchmark. The existing 24-test suite (12 in `test_textutils.py` + 12 in `test_dateutils.py`) validates correctness of t1 with zero modifications.

## Steps

### t1 — Modify `src/testbed_utils/textutils.py`

1. **Read the current file** to confirm exact line numbers and variable names for both functions before editing.

2. **Optimise `slugify` (~line 23):** Replace the encode→decode line:
   ```python
   # remove
   ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
   # insert
   ascii_text = "".join(c for c in normalized if ord(c) < 128)
   ```
   Leave `_SLUG_STRIP_RE`, `_SLUG_COLLAPSE_RE`, and all surrounding lines untouched.

3. **Optimise `truncate` (~lines 28-43):** Insert two local variable assignments at the very top of the function body (before any `ValueError` guard or conditional):
   ```python
   n = len(text)
   m = len(suffix)
   ```
   Then replace every occurrence of `len(text)` with `n` and every occurrence of `len(suffix)` with `m` within the function body. Do not alter the function signature or any other logic.

4. **Run existing tests** to confirm correctness:
   ```
   pytest tests/test_textutils.py tests/test_dateutils.py
   ```
   All 24 tests must pass before proceeding to t2.

### t2 — Create `tests/test_performance.py`

5. **Create the new file** with the following exact content:
   ```python
   import time
   from testbed_utils import slugify, truncate

   _INPUT = ("Hello, Wörld! Café 123. " * 500)[:10000]

   def test_slugify_performance():
       start = time.perf_counter()
       slugify(_INPUT)
       assert time.perf_counter() - start < 0.1

   def test_truncate_performance():
       start = time.perf_counter()
       truncate(_INPUT, max_length=5000, suffix="...")
       assert time.perf_counter() - start < 0.1
   ```

6. **Run the new benchmark tests** in isolation:
   ```
   pytest tests/test_performance.py -v
   ```
   Both functions must pass.

7. **Run the full suite** to confirm no regressions:
   ```
   pytest tests/
   ```
   All 26 tests (24 existing + 2 new) must pass.

## Verification

| Acceptance Criterion | How verified |
|---|---|
| AC1 — 24 existing tests pass | `pytest tests/test_textutils.py tests/test_dateutils.py` exits 0 after step 4 |
| AC2 — benchmark tests pass | `pytest tests/test_performance.py` exits 0 after step 6 |
| AC3 — no `CI_FAIL` at repo root | `ls CI_FAIL` must fail; no step introduces this file |
| AC4 — `pyproject.toml` unchanged | `git diff pyproject.toml` must be empty |
| AC5 — diff ≤ 40 lines | `git diff --stat` across t1 + t2: ~3 lines changed in source + ~18 lines new test file |
| AC6 — `slugify` output identical | Covered by existing `test_textutils.py` tests (including `test_strips_accents`) |
| AC7 — `truncate` output identical | Covered by existing `test_textutils.py` tests across all truncation branches |

## Risks & Open Points

- **Test count discrepancy:** The feature spec states 19 existing tests; the HLD corrects this to 24 (12 `test_textutils` + 12 `test_dateutils`). This plan targets 24. Run `pytest --collect-only` before editing to confirm the true count and update if it differs.
- **Line number drift:** The spec cites `slugify` at lines 16–25 and `truncate` at lines 28–43, but these are estimates. Step 1 (reading the file before editing) is mandatory — do not skip it.
- **`ord(c) < 128` equivalence:** NFKD decomposition converts accented characters into base ASCII codepoints plus combining codepoints (ord > 127). The generator correctly filters combining codepoints identical to the `encode('ascii','ignore')` approach. Validated by reasoning and the existing `test_strips_accents` test.
- **Benchmark flakiness:** The 0.1 s ceiling is ~20–100× the expected runtime (~1–5 ms). False failures from CI scheduling noise are extremely unlikely, but if they occur, the threshold can be raised to 0.5 s without compromising the regression-gate purpose.
