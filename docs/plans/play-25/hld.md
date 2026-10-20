# HLD — US-01 Pure-Python number summary helpers (numutils)

## 1. System Overview
- **What:** a new `numutils` module inside the existing `testbed_utils` package exposing three pure functions: `mean(numbers)`, `median(numbers)`, `percentile(numbers, p)`.
- **Problem:** the package has text and date helpers but no in-package numeric summaries; users otherwise hand-roll them or pull in numpy.
- **Responsibilities:** compute the three statistics over in-memory sequences; reject empty input and out-of-range `p` with descriptive `ValueError`s; document each function with a runnable `>>>` example; ship three-case pytest coverage per function.
- **Explicitly not here:** any CLI, file/stdin reading, path validation, other statistics (all US-02 or out of epic scope).

## 2. Architecture Overview
- **Repository:** `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`), the only repo in scope.
- **Package layout:** setuptools `src/` layout (`pyproject.toml` `where = ["src"]`). The new module therefore lives at `src/testbed_utils/numutils.py`, alongside `textutils.py`, `dateutils.py`, `pdfutils.py`. The spec's bare `testbed_utils/numutils.py` is read as this path; following it literally would create an uninstalled second package.
- **Public surface:** `testbed_utils.numutils` (submodule) plus re-export of the three names from `testbed_utils/__init__.py` `__all__`, matching the convention every other public helper follows and README Task B's instruction to export new helpers from `__init__.py`.
- **External dependencies:** Python standard library only. `requires-python >= 3.10`; CI runs 3.12. No new runtime or test dependency.

## 3. Data Flow Design
- Caller passes an in-memory sequence of ints/floats (and, for percentile, a `p` in 0–100) → function validates → computes synchronously → returns a number or raises `ValueError`.
- Fully synchronous, stateless, no I/O, no events.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| `src/testbed_utils/numutils.py` (new) | mean, median, percentile with validation and docstring examples | sequence of numbers (+ `p`) → number, or `ValueError` | roeeoz/play1 |
| `tests/test_numutils.py` (new) | pytest coverage for scenarios 1–10; verifies docstring examples are literally correct | in-memory lists only | roeeoz/play1 |
| `src/testbed_utils/__init__.py` (edit) | import + `__all__` entries for the three helpers; package docstring mentions numbers | — | roeeoz/play1 |

## 5. Interface Contracts
- **For US-02 (downstream consumer):** `mean`, `median`, `percentile` importable from both `testbed_utils.numutils` and `testbed_utils`. Behavioural contract is the ten acceptance scenarios; `percentile` uses linear interpolation between nearest ranks (numpy's default "linear" method), which also yields US-02's expected p90 values (`[10,20,30]` → 28, `[42]` → 42).
- **Error contract:** `ValueError` only; empty-input message states the list must not be empty; out-of-range `p` message states p must be between 0 and 100. No custom exception classes (none exist in the package).
- **Numeric type:** results compare equal (`==`) to the spec's expected values. Whether integer-valued results come back as `int` or `float` is the implementer's choice; output formatting (e.g. printing `3` rather than `3.0`) is owned by US-02.

## 6. Key Technical Decisions
- **Hand-rolled formulas over `statistics` module delegation.** `statistics.mean([])` raises `StatisticsError` with a message that does not satisfy the spec's wording, and `statistics.quantiles` takes cut-point counts rather than an arbitrary `p` and fails on <2 points on 3.10/3.11. Explicit empty-check plus simple arithmetic over a sorted list is portable across 3.10–3.14 and matches every worked example.
- **Re-export from package root.** Follows the existing `__init__.py` convention and README Task B; pins the import surface US-02 will code against.
- **Accept any iterable, materialize once.** Spec says "sequence"; converting to a list up front accepts tuples/generators at no cost.
- **Docstring examples verified by tests, not CI config.** CI does not run doctests and `pyproject.toml` is out of this story's lane, so the test file itself checks the examples produce their shown output.

## 7. Risks & Constraints
- **Path slip in the spec** (`testbed_utils/` vs `src/testbed_utils/`): resolved by this design; ticket cites the `src/` path.
- **Float exactness:** the five verified cases (`4.6`, `1.0`, `5.0`, `28.0`, `42.0`) are exact; any extra test values must be verified or use `pytest.approx`.
- **Coverage target unenforced:** the epic's ≥90% goal has no `pytest-cov` gate in the repo; adding one is out of scope and is flagged, not done.
- **No lint/format tooling in repo:** the only pre-PR check is `pip install -e ".[test]" && pytest`.
- **Size:** ~60–80 source lines + ~60–80 test lines, well under the 300-line cap.
