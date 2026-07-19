# Specification — Make the tool faster

# Feature Specification Document

## 1. Feature Overview

**Summary:** Reduce redundant computation in the two `testbed_utils` functions that have concrete, measurable inefficiency: `slugify` (five sequential string allocations) and `truncate` (repeated `len()` calls). Add a lightweight benchmark test so the improvement is verifiable and future regressions are caught.

**Problem statement:** Users of the `testbed_utils` library report that the tool feels slow on occasion. A code audit found no I/O, network calls, or nested loops, but identified two functions with low-risk, concrete redundancy: `slugify` performs five sequential string passes where fewer would suffice, and `truncate` recomputes `len(text)` and `len(suffix)` on every branch instead of once.

**Target users / actors:** Python developers (internal Demerzel integration-test authors) who import and call `testbed_utils` functions in test fixtures, potentially with moderately large string inputs.

---

## 2. Goals & Non-Goals

### Goals
- Reduce the number of intermediate string allocations in `slugify` by collapsing the encode→decode round-trip.
- Eliminate redundant `len()` calls in `truncate` by caching the values in local variables at function entry.
- Add one benchmark pytest test (`tests/test_performance.py`) that calls `slugify` and `truncate` with a 10 000-character input and asserts wall-clock time is under 0.1 s, giving the performance claim a verifiable artefact and preventing future regression.

### Non-Goals
- Optimising `word_count`, `days_between`, `is_weekend`, or `humanize_delta` — no measurable redundancy was found.
- Adding third-party performance libraries (e.g. `regex`, `Cython`).
- Profiling or benchmarking against production workloads — the test uses a representative synthetic input.
- Changing the public API or function signatures.
- Addressing potential slowness unrelated to these two functions.

---

## 3. Functional Requirements

**FR1 — `slugify` optimisation (`textutils.py:16-25`)**
Replace the encode→decode round-trip (`unicodedata.normalize` → `.encode('ascii', 'ignore')` → `.decode('ascii')`) with a generator expression that filters only ASCII-ordinal characters from the NFKD-normalised string, avoiding a second full string allocation. The two module-level compiled regex patterns (`_SLUG_STRIP_RE`, `_SLUG_COLLAPSE_RE`) must be retained and applied as before. The function's output must be identical for all inputs covered by the existing test suite.

**FR2 — `truncate` optimisation (`textutils.py:28-43`)**
Compute `len(text)` and `len(suffix)` exactly once each at the top of the function and store them in local variables. Replace all subsequent references to `len(text)` and `len(suffix)` within the function body with those variables. The function's output must be identical for all inputs covered by the existing test suite.

**FR3 — Benchmark test (`tests/test_performance.py`)**
Add a new pytest test file containing one test function that:
- Constructs a synthetic input string of 10 000 characters (e.g. repeated mixed-case Unicode text with spaces and punctuation).
- Calls `slugify` with that input and asserts the call completes in under 0.1 seconds.
- Calls `truncate` with that input (and a representative `max_len` and `suffix`) and asserts the call completes in under 0.1 seconds.
- Uses only the Python standard library (`time` or `timeit`) — no pytest-benchmark or other third-party timing libraries.

**FR4 — CI gate must remain green**
No file named `CI_FAIL` may exist at the repository root after the change. This file is currently absent and must not be introduced.

**FR5 — All existing tests must pass**
All 19 existing pytest tests across `tests/test_textutils.py` and `tests/test_dateutils.py` must continue to pass without modification.

---

## 4. User Experience & Behavior

This is a developer-facing library. The observable user experience is:

1. **Calling `slugify` or `truncate`** with the same arguments produces identical return values before and after the change — no behavioural difference.
2. **Running the test suite** (`pytest`) passes all 22 tests (19 existing + 3 new benchmark assertions) and reports no failures.
3. **Running CI** completes with a green `gate` job because `CI_FAIL` is absent.
4. The new `test_performance.py` file is discoverable by pytest without any additional configuration — it follows the existing naming convention.

Edge cases visible to users:
- `slugify` on an empty string returns `""` — unchanged.
- `truncate` where `len(text) <= max_len` returns `text` unmodified — unchanged.
- `truncate` where `len(suffix) >= max_len` behaviour is preserved exactly as before.

---

## 5. Acceptance Criteria

- AC1: `pytest tests/test_textutils.py tests/test_dateutils.py` exits 0 with all 19 tests passing.
- AC2: `pytest tests/test_performance.py` exits 0 with the new benchmark test(s) passing.
- AC3: No `CI_FAIL` file exists at the repository root.
- AC4: No new entries appear in `pyproject.toml` dependencies (runtime or test).
- AC5: The diff is ≤ 40 lines changed across all modified files.
- AC6: `slugify` return values are identical to the pre-change implementation for all inputs in the existing test suite.
- AC7: `truncate` return values are identical to the pre-change implementation for all inputs in the existing test suite.

---

## 6. Dependencies & Constraints (product-level)

- The package depends only on the Python standard library; this must remain true after the change.
- The CI `gate` job (`ci.yml:25-39`) blocks the PR if `CI_FAIL` exists — this is a hard constraint.
- The change must be backward-compatible: no public API surface (function names, signatures, return types) may change.
- The diff must be small and reviewable (≤ 40 lines) to stay within the scope of a targeted performance fix.

---

## 7. Technical Design (deferred to STRUCTURE)

Architecture, exact implementation of the generator expression, variable naming, test timing approach, and PR breakdown are owned by the tech lead in the STRUCTURE stage. The product constraint the implementation must respect: use only the Python standard library, keep the module-level compiled regex patterns, and do not alter public function signatures.

---

## 8. Open Questions

None blocking. The following are noted for awareness:
- Typical caller input sizes in production are unknown; the 10 000-character benchmark threshold (0.1 s) is a reasonable proxy but could be tuned if profiling data becomes available.
- If future callers invoke `slugify` or `word_count` repeatedly with the same inputs, `functools.lru_cache` could be evaluated as a follow-on — out of scope for this ticket.
