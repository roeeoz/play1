# Implementation plan — US-01 Pure-Python number summary helpers (numutils)

| Field | Value |
| --- | --- |
| Work item | t1 — Add numutils module (mean, median, percentile) with tests and package re-export |
| Repo | `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`) — checkout at `/workspace` |
| Tier | T1 (single work item, no dependencies) |
| Traces | R1–R8, R13 · spec AC1–AC13 · HLD §2, §5, §6 |
| Inputs read | `docs/plans/play-24/play-25/spec.md`, `hld.md`, `work-items.md`; `src/testbed_utils/{__init__,textutils,dateutils}.py`; `tests/test_textutils.py`, `tests/test_dateutils.py`; `pyproject.toml`; `README.md`; `.github/workflows/ci.yml` |

## 1. Context

testbed-utils ships text, date and PDF helpers but nothing numeric. A developer wanting a
quick mean, median or percentile hand-rolls it or pulls in numpy. This story adds a
`numutils` module with those three pure functions, each with a runnable docstring example and
three-case pytest coverage, using only the standard library. US-02's `testbed-num-summary`
console script will import these helpers later; the script itself is out of scope here.

## 2. Research findings

### 2.1 Change surface

| Path | Action | Why |
| --- | --- | --- |
| `src/testbed_utils/numutils.py` | **create** | The module. The package uses a setuptools `src/` layout (`[tool.setuptools.packages.find] where = ["src"]`), so the spec's bare `testbed_utils/numutils.py` resolves to this path. Creating it at the repo root would produce an uninstalled second package. |
| `src/testbed_utils/__init__.py` | **edit** (3 lines + 1 docstring word) | Import the three names and add them to `__all__`. Every existing public helper is re-exported here; README Task B tells implementers to export new helpers from `__init__.py`. |
| `tests/test_numutils.py` | **create** | Pytest coverage for scenarios 1–10, the two US-02 downstream values, the root re-export, and a doctest run of the module. |

Nothing else changes. Specifically **not** touched: `pyproject.toml` (R13 — no dependency
change, and `pyproject.toml` is outside this story's lane), `.github/workflows/ci.yml`,
`README.md`, `textutils.py`, `dateutils.py`, `pdfutils.py`, existing tests, `__version__`.
No `CI_FAIL` file exists at the root today and none must be created.

### 2.2 Existing conventions to copy

Observed in `textutils.py` / `dateutils.py`:

- Module docstring: one-line title, blank line, "Deliberately simple and genuinely extendable —" sentence.
- `from __future__ import annotations` as the first import.
- Module-level private constants prefixed `_` (e.g. `_SLUG_STRIP_RE`).
- Function docstrings: one-line summary with `*param*` emphasis, optional detail paragraph, then a `>>>` example with the literal repr on the next line.
- Validation errors are plain `ValueError` with a short lowercase message (`"max_length must be non-negative"`). No custom exception classes exist in the package.
- Type hints on every signature; return types are concrete (`str`, `int`, `bool`).

Observed in `tests/test_textutils.py` / `tests/test_dateutils.py`:

- Import directly from the submodule (`from testbed_utils.textutils import slugify, ...`).
- One `Test<FunctionName>` class per function, plain `assert` statements, no fixtures.
- Error cases use `with pytest.raises(ValueError):`. The existing tests do not check messages; this story adds `match=` because the ACs require message substance.
- No `conftest.py`, no fixtures directory use for unit tests (fixtures dir holds PDFs for pdfutils only).

### 2.3 Toolchain

- `pyproject.toml`: `requires-python >= 3.10`, runtime dep `pypdf` only, test extra `pytest>=8`, `testpaths = ["tests"]`, `addopts = "-q"`.
- CI (`ci.yml`): job **test** = `pip install -e ".[test]"` then `pytest` on Python 3.12; job **gate** fails iff `CI_FAIL` exists at root.
- No linter, formatter, type checker, coverage tool, or doctest run is configured anywhere. Install plus pytest is the whole gate.
- Local Python is 3.14; nothing planned is version-specific (no `match`, no 3.11+ stdlib APIs).

### 2.4 Contracts

**Provided to US-02 (downstream):**

| Name | Signature | Behaviour |
| --- | --- | --- |
| `mean` | `mean(numbers: Iterable[float]) -> float` | `sum / len`; `ValueError("numbers must not be empty")` on empty input |
| `median` | `median(numbers: Iterable[float]) -> float` | middle element of sorted data, or mean of the two middle elements; same empty error |
| `percentile` | `percentile(numbers: Iterable[float], p: float) -> float` | linear interpolation between nearest ranks at `rank = (n-1)·p/100`; empty error checked first, then `ValueError("p must be between 0 and 100")` |

Importable from both `testbed_utils.numutils` and `testbed_utils`. Only `ValueError` is raised.

**Consumed:** nothing beyond the Python standard library (`collections.abc.Iterable` for the hint; `sorted`, `sum`, `len`, `int`, `min` builtins). The test file additionally uses stdlib `doctest`.

### 2.5 Resolved unknowns

| Open question (spec §8) | Resolution | Basis |
| --- | --- | --- |
| Re-export from package root? | **Yes.** Add to `__init__.py` imports and `__all__`. | Every other public helper does; README Task B says to; HLD §2 and §6 decide it. |
| Exact `ValueError` wording | `"numbers must not be empty"` and `"p must be between 0 and 100"`. Tests match on the substrings `must not be empty` and `between 0 and 100`. | Spec pins substance only; these mirror the existing terse lowercase style. |
| `p` type | Accept `int` or `float`; `0 <= p <= 100` works for both. | No cost; `percentile([1,2,3,4,5], 99.5)` → `4.98` verified. |
| `numbers` type | Accept any iterable; materialize once with `list()` / `sorted()`. | Tuples and generators then work; the argument is never iterated twice. |
| Module path | `src/testbed_utils/numutils.py`. | `src/` layout in `pyproject.toml`; HLD §7. |
| Formula choice | Hand-rolled, not `statistics` module. | `statistics.mean([])` raises `StatisticsError` with the wrong wording; `statistics.quantiles` takes cut counts not `p`, and fails on <2 points on 3.10/3.11. |
| Docstring correctness proof | A test calls `doctest.testmod(numutils)` and asserts zero failures. | CI has no doctest run and `pyproject.toml` is off-limits; this uses stdlib only. |

### 2.6 Numeric verification (done during research, Python 3.14)

All expected values were checked against the formulas in §3 and are exact under `==`:

| Call | Result (repr) |
| --- | --- |
| `mean([1, 2, 3, 4])` | `2.5` |
| `mean([7])` | `7.0` |
| `median([3, 1, 2])` | `2` (raw element, int) |
| `median([1, 2, 3, 4])` | `2.5` |
| `percentile([1, 2, 3, 4, 5], 90)` | `4.6` |
| `percentile([1, 2, 3, 4, 5], 0)` / `100` | `1.0` / `5.0` |
| `percentile([10, 20, 30], 90)` | `28.0` |
| `percentile([42], 90)` | `42.0` |

Consequence for docstrings: integer-valued *float* results repr as `7.0`, so only the four
examples in §3 (`2.5`, `2`, `2.5`, `4.6`) are safe to show verbatim.

## 3. Solution proposal

**Approach.** One new module of three pure functions, written in the exact style of
`textutils.py`, plus a three-line re-export edit and one test file. No design beyond copying
the neighbouring modules is needed.

**Key design decisions.**

1. **Hand-rolled formulas over `statistics`.** Guarantees the spec's error wording and an
   arbitrary-`p` percentile on every supported Python (3.10–3.14). See §2.5.
2. **Validation order in `percentile`: emptiness first, then `p` range.** Scenario 9 says
   `percentile([], p)` for any *valid* `p` must report the empty message; checking emptiness
   first also makes `percentile([], 150)` deterministic (empty message wins).
3. **Materialize once.** `list(numbers)` / `sorted(numbers)` at the top of each function so
   any iterable is accepted and never iterated twice.
4. **Linear interpolation between nearest ranks** (numpy's default `"linear"` method):
   `rank = (n - 1) * p / 100`, `lower = int(rank)`, `upper = min(lower + 1, n - 1)`,
   result `data[lower] + (data[upper] - data[lower]) * (rank - lower)`. The `min` clamps
   `p = 100` so `upper` never indexes past the end. Verified against all eight worked values.
5. **Return type not coerced.** `median` on odd length returns the raw element (may be
   `int`); `mean`/`percentile` return `float`. All ACs use `==`, which passes. Display
   formatting (`3` vs `3.0`) is US-02's concern.
6. **Docstring examples proven by a doctest-based test**, not by CI changes.
7. **Root re-export** for `mean`, `median`, `percentile`, keeping `__all__` alphabetical.

**Target module (contract for the implementer):**

```python
"""Small numeric summary helpers.

Deliberately simple and genuinely extendable — pure Python, no numpy.
"""

from __future__ import annotations

from collections.abc import Iterable

_EMPTY_MSG = "numbers must not be empty"
_RANGE_MSG = "p must be between 0 and 100"


def mean(numbers: Iterable[float]) -> float:
    """Arithmetic mean of *numbers*.

    >>> mean([1, 2, 3, 4])
    2.5
    """
    data = list(numbers)
    if not data:
        raise ValueError(_EMPTY_MSG)
    return sum(data) / len(data)


def median(numbers: Iterable[float]) -> float:
    """Median of *numbers*: the middle value, or the mean of the two middle values.

    >>> median([3, 1, 2])
    2
    >>> median([1, 2, 3, 4])
    2.5
    """
    data = sorted(numbers)
    if not data:
        raise ValueError(_EMPTY_MSG)
    mid = len(data) // 2
    if len(data) % 2:
        return data[mid]
    return (data[mid - 1] + data[mid]) / 2


def percentile(numbers: Iterable[float], p: float) -> float:
    """The *p*-th percentile of *numbers*, linearly interpolated between nearest ranks.

    *p* must be in the inclusive range 0 to 100.

    >>> percentile([1, 2, 3, 4, 5], 90)
    4.6
    """
    data = sorted(numbers)
    if not data:
        raise ValueError(_EMPTY_MSG)
    if not 0 <= p <= 100:
        raise ValueError(_RANGE_MSG)
    rank = (len(data) - 1) * p / 100
    lower = int(rank)
    upper = min(lower + 1, len(data) - 1)
    return data[lower] + (data[upper] - data[lower]) * (rank - lower)
```

**Target `__init__.py` after edit:**

```python
"""testbed_utils — a tiny, deliberately extendable text/date/number utility library.
...
"""

from testbed_utils.dateutils import days_between, humanize_delta, is_weekend
from testbed_utils.numutils import mean, median, percentile
from testbed_utils.pdfutils import extract_fields
from testbed_utils.textutils import slugify, truncate, word_count

__all__ = [
    "days_between",
    "extract_fields",
    "humanize_delta",
    "is_weekend",
    "mean",
    "median",
    "percentile",
    "slugify",
    "truncate",
    "word_count",
]
```

## 4. Ordered implementation tasks

All tasks belong to work item **t1**. Order: module → init → tests → verify → PR.

| # | Task | Files | Satisfies |
| --- | --- | --- | --- |
| 1 | Branch from `main` (e.g. `feat/us-01-numutils`). Confirm no `CI_FAIL` at root; never create one. | — | scope guard |
| 2 | Create `src/testbed_utils/numutils.py` exactly per §3. | `src/testbed_utils/numutils.py` | AC1–AC10 (R1–R6), AC11 (R7), AC13 (R13) |
| 3 | Edit `src/testbed_utils/__init__.py`: add the `numutils` import line between `dateutils` and `pdfutils`; insert `"mean"`, `"median"`, `"percentile"` into `__all__` alphabetically; change "text/date utility library" → "text/date/number utility library". Leave `__version__` alone. | `src/testbed_utils/__init__.py` | HLD §2 public surface; spec §8 re-export decision |
| 4 | Create `tests/test_numutils.py` per the case table in §5. Import from `testbed_utils.numutils`; one `Test<Function>` class per function; plain asserts; `pytest.raises(ValueError, match=...)`; a `TestPackageExports` class; a `TestDocstringExamples` class using `doctest.testmod`. | `tests/test_numutils.py` | AC1–AC12 (R8, R7) |
| 5 | Verify locally per §6. | — | test gate |
| 6 | One commit, "Add numutils module with mean, median and percentile (US-01)". Open a PR against `main` whose body cites work item t1, US-01, R1–R8/R13, lists the three touched files, pastes the pytest summary line, and notes the unenforced coverage gate (§7). Do not merge. End commit and PR body with the session's attribution lines. | — | traceability |

## 5. Test plan (layer: pytest unit tests, `tests/`)

Only in-memory lists are used. No files, stdin, clock or network (G4).

| Class | Test | Assertion | AC |
| --- | --- | --- | --- |
| `TestMean` | `test_several_numbers` | `mean([1, 2, 3, 4]) == 2.5` | AC1 (happy) |
| `TestMean` | `test_single_element` | `mean([7]) == 7` | AC2 (boundary) |
| `TestMean` | `test_empty_raises` | `pytest.raises(ValueError, match="must not be empty")` on `mean([])` | AC3 (error) |
| `TestMedian` | `test_odd_length` | `median([3, 1, 2]) == 2` | AC4 (happy) |
| `TestMedian` | `test_even_length_averages_middle` | `median([1, 2, 3, 4]) == 2.5` | AC5 (boundary) |
| `TestMedian` | `test_empty_raises` | `match="must not be empty"` on `median([])` | AC6 (error) |
| `TestPercentile` | `test_linear_interpolation` | `percentile([1, 2, 3, 4, 5], 90) == 4.6` | AC7 (happy) |
| `TestPercentile` | `test_range_edges` | `p=0` → `1`, `p=100` → `5` | AC8 (boundary) |
| `TestPercentile` | `test_downstream_values` | `percentile([10, 20, 30], 90) == 28`; `percentile([42], 90) == 42` | HLD §5 (US-02 contract) |
| `TestPercentile` | `test_empty_raises` | `match="must not be empty"` on `percentile([], 50)` | AC9 (error) |
| `TestPercentile` | `test_out_of_range_p_raises` | `match="between 0 and 100"` on `percentile([1, 2, 3], 150)` | AC10 (error) |
| `TestPackageExports` | `test_root_import_and_all` | `from testbed_utils import mean, median, percentile` succeeds; each name `in testbed_utils.__all__` | HLD §2 |
| `TestDocstringExamples` | `test_doctests_pass` | `doctest.testmod(testbed_utils.numutils).failed == 0` | AC11 (R7) |

Every function has ≥1 happy, ≥1 boundary and ≥1 error case → AC12 (R8).

## 6. Test gate — what it must show

Run from the repo root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
pytest
pytest tests/test_numutils.py -v
python -c "from testbed_utils import mean, median, percentile; print(percentile([1,2,3,4,5], 90))"
git diff --stat main
git status --short
test ! -e CI_FAIL && echo "no CI_FAIL"
```

Expected:

- `pytest` — whole suite passes; existing `test_textutils`, `test_dateutils`, `test_pdfutils`, `test_pdf_extract_cli` still green.
- `pytest tests/test_numutils.py -v` — 13 tests pass, each AC ticked against its named test in §5.
- The `python -c` smoke test prints `4.6`.
- `git diff --stat main` shows exactly three files (`src/testbed_utils/numutils.py`, `src/testbed_utils/__init__.py`, `tests/test_numutils.py`), roughly 60–80 source lines and 60–80 test lines, well under the 300-changed-line cap.
- `pyproject.toml` has no diff (proves AC13/R13).
- No `CI_FAIL` file exists.

The repo has no linter or formatter, so install + pytest is the complete pre-PR check. CI's
**test** job repeats the same two commands on Python 3.12; the **gate** job stays green as
long as `CI_FAIL` is absent.

## 7. Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **Path slip.** Spec says `testbed_utils/numutils.py`; the repo's `src/` layout means `src/testbed_utils/numutils.py`. | Resolved here and in HLD §7. Reviewer confirms the file lands under `src/`. |
| **Docstring repr mismatch.** `mean([7])` reprs as `7.0`; showing `7` in a docstring would fail the doctest. | Only the four verified examples in §3 appear in docstrings; the doctest test enforces this. |
| **Float exactness.** Any test value beyond the nine verified ones might not be exact under `==`. | Stick to the table in §2.6; if more values are added, verify first or use `pytest.approx`. |
| **`percentile` at `p=100` indexing past the end.** | `upper = min(lower + 1, n - 1)` clamps; `rank - lower == 0` so the interpolation term is zero. Covered by AC8. |
| **Validation order.** Checking `p` before emptiness would break AC9's "any valid p" wording for invalid `p`. | Emptiness is checked first, by contract in §3. |
| **Coverage gate unenforced.** Epic targets ≥90% but there is no `pytest-cov` in the repo; adding one edits `pyproject.toml`. | Out of scope. Flagged in the PR body, not fixed. |
| **Python version drift.** Local 3.14 vs CI 3.12 vs floor 3.10. | No version-specific syntax or stdlib API is used. |
| **Scope lock.** | Only the three files in §2.1 change. No `pyproject.toml`, CI, README, CLI, file/stdin reading, path validation, extra statistics, or `__version__` bump. No `CI_FAIL`. No merge without the human approval gate. |
| **Downstream contract.** US-02 depends on the p90 values 28 and 42 and on root-level import. | Both pinned by `test_downstream_values` and `test_root_import_and_all`. |

## 8. Open points for the developer

None blocking. The spec's four §8 questions are all closed at no cost in §2.5, following the
HLD. No `plan-questions.json` is written.
