# Feature Specification Document

## 1. Feature Overview

**Summary:** Add a new `testbed_utils/numutils.py` module providing three pure-Python functions — `mean(numbers)`, `median(numbers)` and `percentile(numbers, p)` — that let a developer summarize a list of numbers without depending on numpy.

**Problem statement:** Developers using testbed-utils currently have no in-package way to compute basic numeric summary statistics; they must either hand-write the logic or pull in a third-party library such as numpy for what is a small, common need.

**Target users:** Developers using testbed-utils directly in their own Python code (calling the functions on in-memory lists of numbers). These helpers are also the foundation the `testbed-num-summary` console script (US-02) will build on, but building that script is explicitly out of scope for this story.

---

## 2. Goals & Non-Goals

### Goals
- Provide `mean(numbers)`, `median(numbers)`, and `percentile(numbers, p)` in a new `testbed_utils/numutils.py` module.
- Each function carries a docstring with a runnable example, in the same style as `textutils.py` and `dateutils.py`.
- Each function is covered by pytest cases for its happy path, one boundary condition, and one error condition (as enumerated in the acceptance criteria below).
- Introduce no new runtime dependency; use only the Python standard library.

### Non-Goals
- Any command-line entry point or console script (that is US-02's scope).
- Any statistic beyond mean, median, and percentile (e.g., standard deviation, variance, mode) — out of scope for this epic.
- Any use of numpy or other third-party numeric libraries.
- Reading input from files, stdin, or any I/O — this story operates purely on in-memory sequences passed by the caller.

---

## 3. Functional Requirements

- **FR1 (traces R1):** `mean(numbers)` returns the arithmetic mean of a non-empty sequence of numbers.
  - Input: a non-empty sequence of numbers, e.g. `[1, 2, 3, 4]`.
  - Output: the arithmetic mean, e.g. `2.5`.
- **FR2 (traces R2):** `mean(numbers)` raises `ValueError` when given an empty sequence, with a message stating the list must not be empty.
- **FR3 (traces R3):** `median(numbers)` returns the median of a non-empty sequence of numbers — the middle value for odd-length input, the average of the two middle values for even-length input.
- **FR4 (traces R4):** `median(numbers)` raises `ValueError` when given an empty sequence, with a message stating the list must not be empty.
- **FR5 (traces R5):** `percentile(numbers, p)` returns the p-th percentile of a non-empty sequence, using linear interpolation between the two nearest ranks, for `p` in the inclusive range 0–100.
- **FR6 (traces R6):** `percentile(numbers, p)` raises `ValueError` when given an empty sequence (message states the list must not be empty) or when `p` is outside 0–100 (message states p must be between 0 and 100).
- **FR7 (traces R7):** Every public function's docstring includes a runnable example, matching the established style of `textutils.py`/`dateutils.py` (one-line summary plus a `>>>`-style example with literal expected output).
- **FR8 (traces R8):** Every public function has pytest coverage for its happy path, one boundary case, and one error case (see Acceptance Criteria).
- **FR9 (traces R13):** No new runtime dependency is introduced; the module uses only the standard library.

### Core workflow
1. A developer imports `mean`, `median`, and/or `percentile` from `testbed_utils.numutils` (and/or, depending on the open question in §8, from `testbed_utils` directly).
2. The developer calls the function(s) with an in-memory list of numbers (and, for `percentile`, a percentage value).
3. The function returns the computed statistic, or raises `ValueError` with a descriptive message if the input is invalid (empty sequence, or out-of-range `p`).

### Edge cases (from acceptance criteria)
- Single-element list for `mean`.
- Even-length list for `median` (average of two middle values).
- `percentile` called at the exact boundaries `p=0` and `p=100`.
- Empty list passed to any of the three functions.
- Out-of-range `p` (e.g., 150) passed to `percentile`.

---

## 4. User Experience & Behavior

This is a developer-facing (library/SDK) feature — the "user experience" is the calling code's experience of the API surface, not a graphical UI.

- **Key flow:** a developer writes `from testbed_utils.numutils import mean, median, percentile` (or equivalent), then calls these functions directly on Python lists already held in memory. No file I/O, network, or CLI is involved at this stage.
- **States observed:** either a numeric return value (the requested statistic) or a raised `ValueError` — there is no intermediate or async state.
- **User-facing error behavior:** invalid input (empty sequence, or `p` outside 0–100) surfaces as a Python exception (`ValueError`) with a clear, descriptive message the calling code can catch or let propagate — not a silent failure or a sentinel return value (e.g., `None`).
- **Discoverability:** each function's docstring itself doubles as a usage example (a runnable `>>>` snippet with the exact expected output), so a developer reading the source or using `help()` sees a working example immediately — this is the qualitative "discoverability" requirement (G2) named in the epic.

---

## 5. Acceptance Criteria

1. **Happy path — mean of several numbers.** Given `[1, 2, 3, 4]`, `mean(...)` returns `2.5`.
2. **Boundary — mean of a single-element list.** Given `[7]`, `mean(...)` returns `7`.
3. **Error — mean of an empty list.** Given `[]`, `mean(...)` raises `ValueError` with a message stating the list must not be empty.
4. **Happy path — median of an odd-length list.** Given `[3, 1, 2]`, `median(...)` returns `2`.
5. **Boundary — median of an even-length list.** Given `[1, 2, 3, 4]`, `median(...)` returns `2.5` (average of the two middle values).
6. **Error — median of an empty list.** Given `[]`, `median(...)` raises `ValueError` with a message stating the list must not be empty.
7. **Happy path — percentile with linear interpolation.** Given `[1, 2, 3, 4, 5]` and `p=90`, `percentile(...)` returns `4.6`.
8. **Boundary — percentile at range edges.** Given `[1, 2, 3, 4, 5]`, `percentile(..., p=0)` returns `1` and `percentile(..., p=100)` returns `5`.
9. **Error — percentile of an empty list.** Given `[]` and any valid `p`, `percentile(...)` raises `ValueError` with a message stating the list must not be empty.
10. **Error — percentile with out-of-range p.** Given `[1, 2, 3]` and `p=150`, `percentile(...)` raises `ValueError` with a message stating p must be between 0 and 100.
11. **Discoverability (G2/R7):** every public function in `numutils.py` has a docstring containing a runnable example consistent with `textutils.py`/`dateutils.py` style.
12. **Trustworthiness (G1/R8):** every public function has pytest cases covering its happy path, one boundary condition, and one error condition (scenarios 1–10 above satisfy this for all three functions).
13. **No new runtime dependency (R13):** the module and its tests add no new entry to the project's runtime dependencies.

---

## 6. Dependencies & Constraints (product-level)

- **Depends on:** nothing — this is the first story in the epic's execution plan (Wave 1).
- **Depended on by:** US-02 (`testbed-num-summary` console script), which imports and calls `mean`, `median`, and `percentile` from this module — US-02 cannot start implementation until this story merges.
- **Constraint — style consistency:** the module's docstring/example style must match the existing `textutils.py` and `dateutils.py` modules, per the product definition's stated convention.
- **Constraint — no new dependency:** must not introduce numpy or any other third-party runtime dependency (explicit non-goal, confirmed by the PO message and the epic's non-goals).
- **Constraint — test determinism (G4):** all tests must use in-memory lists only — no real stdin, network, or clock dependency (naturally satisfied since these are pure functions over in-memory sequences).
- **Compliance/security:** none — this story is pure in-memory computation with no I/O surface; path-traversal and file-handling concerns belong entirely to US-02.

---

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. The following are product-imposed constraints for STRUCTURE to satisfy, not designs:
- The module must live at `testbed_utils/numutils.py` (per the story's stated "In" scope) and use only the standard library.
- The percentile calculation must produce results consistent with linear interpolation between the two nearest ranks, matching the exact worked examples in the acceptance criteria (e.g., `p=90` on `[1,2,3,4,5]` → `4.6`; `p=0`→`1`; `p=100`→`5`).
- Exact wording of `ValueError` messages, the precise type signature accepted for `numbers` (list vs. any sequence/iterable) and for `p` (int vs. float), and whether the three functions are re-exported from `testbed_utils/__init__.py`'s `__all__` are implementation choices for STRUCTURE to resolve, informed by the open questions below and by the existing package convention (every other public helper in the package is currently re-exported from `__init__.py`).

---

## 8. Open Questions (if any remain)

- **Package-level re-export:** every existing public helper (`slugify`, `truncate`, `word_count`, `days_between`, etc.) is re-exported from `testbed_utils/__init__.py`'s `__all__`. Neither the epic brief nor this story's "In/Out" scope mentions whether `mean`, `median`, and `percentile` should be added there too. This does not block writing or testing this story's stated acceptance criteria (existing tests import directly from the submodule, e.g. `from testbed_utils.textutils import slugify`, and the new tests can do the same from `testbed_utils.numutils`), so it is not treated as a blocking gap — but it is a real, unresolved product-surface decision that affects discoverability (G2) and the public contract US-02 will build against. Recorded as an assumption below; STRUCTURE should confirm before merge.
- **Exact `ValueError` message text:** the story requires messages that state the list must not be empty / that p must be between 0 and 100, but does not pin exact wording. Treated as an implementation detail, not a product-level gap, since the substance is fully specified.
- **`p` parameter type:** all acceptance-criteria examples use integer `p` (90, 0, 100, 150); whether float `p` values (e.g., 99.5) must also be supported is unstated. Not tested by any acceptance criterion, so not blocking.
- **`numbers` parameter type:** the requirements text says "sequence" but every example uses a literal list; whether tuples/generators must also work is unstated and untested.

---

_Source: Epic — "Pure-Python number summary helpers and console script" (Draft 0.2, 2026-09-23); User Story US-01._
