# Implementation plan — t1: `business_days_between` helper in `dateutils`

**Story:** US-01 · **Traces to:** R2, R9 (helper portion) · **Work item:** t1 (T1, no `dependsOn`) · **Repo:** roeeoz/play1 (971bf272-f661-4343-ba13-83764c3aec1f), default branch `main` · **Feature branch:** `halo/feat/31340705`

Inputs read: `spec.md`, `hld.md`, `work-items.md` in this folder; `src/testbed_utils/dateutils.py`, `src/testbed_utils/__init__.py`, `tests/test_dateutils.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `README.md`.

## 1. Context

testbed-utils exposes three date helpers in `src/testbed_utils/dateutils.py`: `days_between`, `is_weekend` and `humanize_delta`. The upcoming `date-span` CLI (US-02) needs a business-day count between two dates. This story adds one pure function, `business_days_between(start: date, end: date) -> int`, next to the siblings, re-exports it from the package and pins its behaviour with pytest. Nothing user-facing ships here; the CLI, `--json` mode and README belong to US-02 and US-03.

## 2. Solution proposal

### Chosen approach

One work item, one PR, three files, purely additive. The helper is a plain loop over the half-open day range that reuses the existing `is_weekend` predicate:

```python
def business_days_between(start: date, end: date) -> int:
    """Business days (Monday to Friday) between *start* and *end*.

    The earlier date is counted and the later date is excluded, so a Monday
    to the following Monday yields 5. Argument order does not matter and the
    result is never negative, unlike :func:`days_between`, which is signed.

    >>> business_days_between(date(2024, 1, 1), date(2024, 1, 8))
    5
    """
    if start > end:
        start, end = end, start
    return sum(
        1
        for offset in range((end - start).days)
        if not is_weekend(start + timedelta(days=offset))
    )
```

The module already imports `date` and `timedelta` and uses `from __future__ import annotations`, so no new imports are needed. The three existing helpers and their tests stay byte-for-byte unchanged.

### Key design decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Parameter type | Two `datetime.date` objects, not ISO strings | Matches `days_between` and `is_weekend`; ISO parsing and its error reporting belong to the CLI (US-02). Resolves the spec's open question per the HLD. |
| Counting convention | Half-open: earlier date counted, later date excluded | The only convention satisfying all five ACs (Mon to next Mon = 5, Sat to Sun = 0, Mon to Tue = 1, identical = 0). Also matches the magnitude of `days_between` so US-02 reports 7 whole days and 5 business days for the same pair. |
| Argument order | Normalise by swapping when `start > end`; result is unsigned | Required by AC5. Deliberately differs from `days_between`, which is signed (existing test asserts `-7`); the docstring must say so. |
| Algorithm | Day loop reusing `is_weekend` | Readable, reuses the sibling helper, and spans at CLI scale are tiny. The HLD allows an O(1) formula, but it adds off-by-one surface for no benefit here. |
| Package export | Add to the `__init__.py` import line and to `__all__` before `"days_between"` | Follows the existing convention; `__all__` is alphabetical and `business_days_between` sorts first. |
| Versioning and dependencies | No version bump, standard library only | Nothing in the repo establishes a bump convention for additive helpers; the epic forbids new dependencies. |
| Placement in module | After `is_weekend`, before `humanize_delta` | Keeps the predicate it depends on defined above it and groups the two span helpers near each other. |

### Contract locked for US-02

| Aspect | Value |
| --- | --- |
| Name | `business_days_between` |
| Import paths | `testbed_utils.dateutils` and `testbed_utils` |
| Signature | `(start: date, end: date) -> int` |
| Return | Non-negative `int`; 0 for identical dates |
| Order | Either order accepted; identical result |

## 3. Research findings

### Change surface

| File | Change | Nature |
| --- | --- | --- |
| `src/testbed_utils/dateutils.py` | New function between `is_weekend` (line 21) and `humanize_delta` (line 26) | Additive only |
| `src/testbed_utils/__init__.py` | Extend the dateutils import on line 8; add one `__all__` entry | Additive only |
| `tests/test_dateutils.py` | Extend the import on line 3; add `TestBusinessDaysBetween` after `TestIsWeekend` | Additive only |

Not touched: `pyproject.toml` (no console script yet), `README.md`, `.github/workflows/ci.yml`, `pdfutils.py`, `textutils.py`, other test files.

### Existing conventions observed

- Helpers take native `date` / `timedelta` values and are documented with a one-line summary plus optional `>>>` examples.
- `__init__.py` uses a single alphabetical import per module and an alphabetical `__all__`.
- Tests use one class per function, plain `assert`, `date(...)` literals, no fixtures or parametrize.
- pytest config: `testpaths=["tests"]`, `addopts="-q"`. Doctests are not collected, so `>>>` examples are documentation only.
- CI: `test` job runs `pip install -e ".[test]"` then `pytest` on Python 3.12; `gate` job fails only if a `CI_FAIL` file exists at the repo root. No `CI_FAIL` file exists on the branch. No linter or formatter is configured.
- Baseline: 38 tests (`test_dateutils.py` 12, `test_textutils.py` 12, `test_pdf_extract_cli.py` 9, `test_pdfutils.py` 5).

### Resolved unknowns

| Unknown (from spec §8 / HLD §7) | Resolution |
| --- | --- |
| `date` vs ISO string parameters | `date` objects, per HLD §5. |
| Package-level re-export | Yes, per HLD §6. |
| Algorithm | Day loop reusing `is_weekend`; see §2. |
| "Matches `days_between`" wording in the story blocker | `days_between` is signed; the new helper is unsigned and order-independent. `days_between` is left unchanged (FR5). |
| AC arithmetic | Hand-verified: 2024-01-01 and 2024-01-08 are Mondays, 2024-01-06 is a Saturday; the half-open, order-normalised count returns 5, 0, 1, 0 and 5 for AC1 to AC5. |
| Q1 (reject reversed input?) | Still formally open with the PO, but the spec's AC5 and the HLD lock the working assumption: accept either order, return the unsigned count. No developer question is needed for this story. |

## 4. Implementation tasks (ordered)

All tasks belong to work item **t1**.

| # | Task | File | Satisfies |
| --- | --- | --- | --- |
| 1 | Baseline: `pip install -e ".[test]"` and `pytest`; expect 38 passed. Confirm no `CI_FAIL` at the repo root. | — | Pre-condition |
| 2 | Add `business_days_between` after `is_weekend` with the docstring and body from §2. Loop bound is `(end - start).days`, not `+ 1`. | `src/testbed_utils/dateutils.py` | AC1–AC5, FR1–FR5 |
| 3 | Add `business_days_between` to the dateutils import and insert `"business_days_between"` in `__all__` immediately before `"days_between"`. Leave `__version__` at `0.1.0`. | `src/testbed_utils/__init__.py` | Work-item AC "importable from both paths" |
| 4 | Extend the import line and add `TestBusinessDaysBetween` after `TestIsWeekend` with the five tests in §5. | `tests/test_dateutils.py` | AC6, FR6 |
| 5 | Run the test gate (§6). Check `git diff --stat main` lists exactly the three files above. | — | AC7 |
| 6 | Open the PR against `main` (platform-assigned `WI-<id>-1:` prefix, title "Add business_days_between helper to dateutils with package export and tests"). Body traces to US-01, R2 and R9, lists the five pinned values, and names the half-open convention and order-independence as the contract US-02 consumes. Wait for `test` and `gate`, then hand off to the human approval gate. Do not merge. | — | Delivery |

## 5. Tests to add

New class `TestBusinessDaysBetween` in `tests/test_dateutils.py`, existing style:

| Test | Start | End | Expected | AC |
| --- | --- | --- | --- | --- |
| `test_full_business_week` | `date(2024, 1, 1)` (Mon) | `date(2024, 1, 8)` (Mon) | `5` | AC1 |
| `test_weekend_only_span` | `date(2024, 1, 6)` (Sat) | `date(2024, 1, 7)` (Sun) | `0` | AC2 |
| `test_single_business_day` | `date(2024, 1, 1)` (Mon) | `date(2024, 1, 2)` (Tue) | `1` | AC3 |
| `test_identical_dates` | `date(2024, 1, 3)` | `date(2024, 1, 3)` | `0` | AC4 |
| `test_reversed_order_matches_forward` | `date(2024, 1, 8)` | `date(2024, 1, 1)` | `5`, and `== business_days_between(date(2024, 1, 1), date(2024, 1, 8))` | AC5 |

Existing test layers: unit tests only; this repo has no integration or CLI test for dateutils and none is needed here. The existing `TestDaysBetween`, `TestIsWeekend` and `TestHumanizeDelta` classes stay untouched.

## 6. Test gate

```bash
pip install -e ".[test]"
pytest
```

Must show:

- 43 passed, 0 failed (38 baseline plus 5 new).
- Package export check prints `5`:

  ```bash
  python -c "from datetime import date; from testbed_utils import business_days_between; print(business_days_between(date(2024, 1, 1), date(2024, 1, 8)))"
  ```

- `git diff --stat main` lists only `src/testbed_utils/dateutils.py`, `src/testbed_utils/__init__.py`, `tests/test_dateutils.py`.
- `git diff main -- src/testbed_utils/dateutils.py` shows only added lines; `days_between`, `is_weekend` and `humanize_delta` are unchanged (FR5).
- CI `test` and `gate` jobs green on the PR.

No linter or formatter is configured in this repo, so there is no lint step in the gate.

## 7. Risks and scope guards

| Risk | Guard |
| --- | --- |
| Inclusive-count slip (both endpoints counted) returns 6, 2 and 1 for AC1 to AC3. | Pinned tests; reviewer checks the loop bound is `(end - start).days`. |
| Signed-versus-unsigned confusion with `days_between`. | Docstring states order-independence and the non-negative result explicitly; `days_between` and its `-7` test are not touched. |
| Q1 later resolved as "reject reversed input". | Would be a one-line guard plus a test, but a breaking change for US-02 once shipped. Flagged in the PR body; not implemented here. |
| Doctest drift. | The `>>>` example is hand-verified (returns 5); doctests are never collected. |
| `datetime` passed instead of `date`. | Siblings do not guard against this and neither does this helper; not a regression. |
| Scope creep into US-02 or US-03. | No `pyproject.toml`, README, CLI, or `--json` changes. The diff is limited to the three files in §3. |
| `__all__` ordering. | `business_days_between` goes before `days_between` to keep the list alphabetical. |
