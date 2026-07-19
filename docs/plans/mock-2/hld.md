# High-level design — Make the tool faster

# High-Level Design: testbed_utils Performance Optimisations

## 1. System Overview

**What is being built:** Two targeted micro-optimisations to the `testbed_utils` pure-Python library — one in `slugify` and one in `truncate` — plus a lightweight benchmark test file that acts as a measurable regression gate. No new abstractions, no API changes, no new dependencies.

**Problem:** `slugify` allocates unnecessary intermediate objects via an encode→decode round-trip; `truncate` calls `len()` redundantly on every conditional branch. Both are concrete, auditable inefficiencies for callers passing large string inputs.

**Key responsibilities:**
- Replace the `encode('ascii','ignore').decode('ascii')` pair in `slugify` with `"".join(c for c in normalized if ord(c) < 128)`, eliminating the intermediate bytes object.
- Cache `len(text)` and `len(suffix)` as local variables `n` and `m` at the top of `truncate`, replacing all subsequent `len()` calls within the function body.
- Add `tests/test_performance.py` with two benchmark test functions (`test_slugify_performance`, `test_truncate_performance`) that assert each call completes in < 0.1 s on a deterministic 10 000-character synthetic Unicode input.

---

## 2. Architecture Overview

The library is a pure-Python stdlib package. All changes are confined to one existing source module and one new test module. No cross-module or cross-service boundaries are touched.

```
play1/
  src/testbed_utils/
    textutils.py        ← MODIFIED  (slugify line ~23, truncate lines ~36-43)
    dateutils.py        (unchanged)
    __init__.py         (unchanged)
  tests/
    test_textutils.py   (unchanged — 12 tests)
    test_dateutils.py   (unchanged — 12 tests)
    test_performance.py ← NEW        (2 benchmark tests)
  pyproject.toml        (unchanged)
  .github/workflows/ci.yml  (unchanged — auto-discovers new test via testpaths)
```

---

## 3. Data Flow Design

Both optimisations are pure synchronous string transformations with no I/O, no state mutation, and no events.

**slugify — before:** text → NFKD normalise → bytes (encode) → str (decode) → regex strip → lower → regex collapse → slug  
**slugify — after:** text → NFKD normalise → generator filter (ord < 128) → join → regex strip → lower → regex collapse → slug

**truncate — before:** text → `len(text)` per branch → `len(suffix)` twice → result  
**truncate — after:** text → `n = len(text)`, `m = len(suffix)` once → branch on n, m → result

Return values are semantically identical in both cases.

---

## 4. Component Breakdown

| Component | Responsibility | Inputs | Outputs | Repo |
|---|---|---|---|---|
| `src/testbed_utils/textutils.py` | String utility functions | Python `str` | Python `str` | play1 |
| `tests/test_performance.py` | Benchmark regression gate | 10 000-char synthetic string | pytest pass/fail | play1 |

---

## 5. Interface Contracts

No interface changes. Public signatures remain identical:
- `slugify(text: str) -> str`
- `truncate(text: str, max_length: int, suffix: str = "...") -> str`

Existing callers require no updates.

---

## 6. Key Technical Decisions

| Decision | Choice | Rationale |
|---|---|---|
| ASCII filter method | `"".join(c for c in normalized if ord(c) < 128)` | Semantically identical to `encode/decode`; avoids bytes allocation. NFKD combining chars have ord > 127 so are filtered correctly. |
| len() caching position | Before the `ValueError` guard | Cleanest — all locals defined at function entry; `len()` never raises |
| Timing method | `time.perf_counter()` | Sub-microsecond wall-clock resolution; stdlib only; lower OS-scheduling noise than `time.time()` |
| Benchmark structure | Two separate test functions | Each independently reportable in pytest; cleaner failure isolation |
| Synthetic input | `("Hello, Wörld! Café 123. " * 500)[:10000]` | Deterministic, contains Unicode and punctuation, exercises NFKD decomposition path |
| Benchmark `max_length` | 5000 with suffix `"..."` | Exercises the active truncation branch (not the early-return branch) |

---

## 7. Risks & Constraints

- **Correctness (low):** `ord(c) < 128` is semantically identical to `encode('ascii','ignore')`. NFKD decomposes accented chars into base ASCII + combining codepoints (ord > 127); combining chars are filtered. Confirmed by reasoning and existing `test_strips_accents`. Control characters 0x00–0x1F (ord < 32) are preserved by both approaches.
- **Benchmark flakiness (very low):** 0.1 s ceiling is ~20–100× the expected runtime (~1–5 ms). False CI failures are extremely unlikely.
- **Diff budget:** Two source edits ~3 lines each, new test file ~20 lines. Total well within AC5's 40-line limit.
- **CI gate:** No `CI_FAIL` file introduced; existing gate remains green.
- **Test count discrepancy:** Spec cites 19 existing tests; actual count is 24 (12 textutils + 12 dateutils). This is a spec error — all 24 must pass.
