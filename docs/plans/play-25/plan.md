# Implementation plan — US-01 Pure-Python number summary helpers (numutils)

Work item: **t1** · Repo: `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`) · Traces: R1–R8, R13

## 1. Context

testbed-utils ships text, date and PDF helpers but nothing for numbers, so a developer who wants a quick mean, median or percentile either hand-rolls it or pulls in numpy. This story adds a `numutils` module with those three pure functions, each with a runnable docstring example and three-case pytest coverage, using only the standard library. It is the foundation that US-02's `testbed-num-summary` console script will import; the script itself is out of scope here.

## 2. Approach

A single work item, three files, no sequencing across stories. The package uses a setuptools `src/` layout, so the module lives at `src/testbed_utils/numutils.py` (the spec's bare `testbed_utils/numutils.py` would create an uninstalled second package). The module copies the existing `textutils.py` / `dateutils.py` style: module docstring, `from __future__ import annotations`, one-line summary with `*param*` emphasis, `>>>` example with literal output, plain `ValueError` messages. Tests copy the `tests/test_textutils.py` layout: one `Test<Function>` class per function, plain asserts, `pytest.raises(ValueError, match=...)`. The three names are re-exported from `testbed_utils/__init__.py` to match every other public helper and README Task B.

Formulas are hand-rolled rather than delegated to `statistics`, because `statistics.mean([])` raises `StatisticsError` with the wrong wording and `statistics.quantiles` does not take an arbitrary `p` and fails on fewer than two points on 3.10/3.11. Order of work: module, init edit, tests, verify, PR.

## 3. Steps

1. **Clone and branch (t1).** Clone `https://github.com/roeeoz/play1` into the workspace and create `feat/us-01-numutils` from `main`. Confirm there is no `CI_FAIL` file at the root and do not create one.

2. **Create `src/testbed_utils/numutils.py` (t1).** Implement exactly this contract:

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

   Implementer notes:
   - Check emptiness before the `p` range so `percentile([], 50)` reports the empty-list message (scenario 9).
   - Docstring outputs are literal reprs. Integer-valued float results print as `7.0`, so only use the four verified examples above.
   - Materialize the iterable once; never iterate the argument twice.

3. **Edit `src/testbed_utils/__init__.py` (t1).**
   - Add `from testbed_utils.numutils import mean, median, percentile` between the dateutils and pdfutils imports.
   - Insert `"mean"`, `"median"`, `"percentile"` into `__all__`, keeping alphabetical order.
   - Change "text/date utility library" to "text/date/number utility library" in the package docstring. Do not touch `__version__`.

4. **Create `tests/test_numutils.py` (t1).** Import from `testbed_utils.numutils`, one class per function, plain asserts, `pytest.raises(ValueError, match=...)` for messages. Cases:

   | Class | Case | Assertion |
   | --- | --- | --- |
   | `TestMean` | happy (S1) | `mean([1, 2, 3, 4]) == 2.5` |
   | `TestMean` | boundary (S2) | `mean([7]) == 7` |
   | `TestMean` | error (S3) | `mean([])` raises, `match="must not be empty"` |
   | `TestMedian` | happy (S4) | `median([3, 1, 2]) == 2` |
   | `TestMedian` | boundary (S5) | `median([1, 2, 3, 4]) == 2.5` |
   | `TestMedian` | error (S6) | `median([])` raises, `match="must not be empty"` |
   | `TestPercentile` | happy (S7) | `percentile([1, 2, 3, 4, 5], 90) == 4.6` |
   | `TestPercentile` | boundary (S8) | `p=0` gives `1`, `p=100` gives `5` |
   | `TestPercentile` | downstream (US-02) | `percentile([10, 20, 30], 90) == 28`; `percentile([42], 90) == 42` |
   | `TestPercentile` | error (S9) | `percentile([], 50)` raises, `match="must not be empty"` |
   | `TestPercentile` | error (S10) | `percentile([1, 2, 3], 150)` raises, `match="between 0 and 100"` |
   | `TestPackageExports` | re-export | `from testbed_utils import mean, median, percentile` works; each name is in `testbed_utils.__all__` |
   | `TestDocstringExamples` | doctest | `doctest.testmod(numutils).failed == 0` |

   The doctest case is what proves the docstring examples are literally correct, using only the standard library and without touching CI config.

5. **Verify locally (t1).** From the repo root:

   ```bash
   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[test]"
   pytest
   python -c "from testbed_utils import mean, median, percentile; print(percentile([1,2,3,4,5], 90))"
   git diff --stat main
   git status --short
   ```

   Expected: full suite passes, the print shows `4.6`, the diff touches exactly three files and stays well under 300 changed lines, `pyproject.toml` shows no diff, no `CI_FAIL` file exists. The repo has no linter or formatter, so install plus pytest is the whole pre-PR check.

6. **Commit and open the PR (t1).** One commit: "Add numutils module with mean, median and percentile (US-01)". PR body references work item t1, story US-01, requirements R1–R8 and R13, lists the three touched files, pastes the pytest summary, and notes the unenforced coverage gate (see §5). End the commit message and PR body with the session's attribution lines. Do not merge; the human approval gate decides.

## 4. Verification

- **Step 2/4:** scenarios 1–10 map one-to-one onto the `TestMean`, `TestMedian` and `TestPercentile` cases above, giving each function its happy, boundary and error case (R8, AC12). The two downstream values (`28`, `42`) pin the contract US-02 depends on.
- **Step 3/4:** `TestPackageExports` proves the root import and `__all__` entries.
- **Step 4:** `TestDocstringExamples` proves every `>>>` example produces its shown output (R7, AC11).
- **Step 5:** the existing suite still passes; `pyproject.toml` unchanged proves R13 / AC13.
- **Final acceptance:** run `pytest tests/test_numutils.py -v` and tick each scenario against its named test; run the `python -c` import check as the end-to-end smoke test of the installed package.

All tests use in-memory lists only; no stdin, files, clock or network (G4).

## 5. Risks & open points

- **Path slip in the spec.** The spec says `testbed_utils/numutils.py`; the repo's `src/` layout means `src/testbed_utils/numutils.py`. Resolved here and in the HLD; the reviewer should confirm the file lands under `src/`.
- **Coverage gate is unenforced.** The epic targets ≥90% but the repo has no `pytest-cov`. Adding one touches `pyproject.toml`, which is outside this story. Flagged in the PR body, not fixed.
- **Float exactness.** The nine worked values (`2.5`, `7`, `2`, `2.5`, `4.6`, `1`, `5`, `28`, `42`) are verified exact under `==`. Any further numeric test values must be checked or use `pytest.approx`.
- **Return type.** Integer-valued results may come back as `float` (e.g. `7.0`). All acceptance checks use `==`, which passes. Display formatting (`3` vs `3.0`) is owned by US-02.
- **Open questions closed at no cost.** `p` accepts int or float; `numbers` accepts any iterable because it is materialized once. Root re-export follows the package convention and README Task B.
- **Python version.** Local Python may be newer than CI's 3.12; nothing in the module is version-specific, so this is acceptable.
- **Scope lock.** Only three files change. No `pyproject.toml`, CI, README, CLI, file reading or extra statistics.
