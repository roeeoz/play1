# Implementation plan — t1: `business_days_between` helper in `dateutils`

**Story:** US-01 · **Traces to:** R2, R9 (helper portion) · **Repo:** roeeoz/play1 (971bf272-f661-4343-ba13-83764c3aec1f), default branch `main` · **Tier:** T1

## 1. Context

testbed-utils exposes three date helpers in `src/testbed_utils/dateutils.py`: `days_between`, `is_weekend` and `humanize_delta`. The upcoming `date-span` CLI (US-02) needs a business-day count between two dates, so this story adds one pure function, `business_days_between(start: date, end: date) -> int`, next to them, re-exports it from the package, and pins its behaviour with pytest. Nothing user-facing ships here; the CLI, `--json` mode and README belong to US-02 and US-03.

## 2. Approach

One work item, one PR, three files. The change is additive: the three existing helpers and their tests stay byte-for-byte unchanged. The helper reuses `is_weekend` for the weekday test and follows the sibling convention of taking native `datetime.date` objects, leaving ISO parsing to the CLI.

Contract locked by the HLD, which US-02 will build against once merged:

| Aspect | Decision |
| --- | --- |
| Signature | `business_days_between(start: date, end: date) -> int` |
| Import paths | `testbed_utils.dateutils` and `testbed_utils` |
| Counting | Half-open: the earlier date is counted, the later date excluded |
| Order | Either order accepted, result identical, never negative |
| Dependencies | Standard library only; no version bump |

No shared decision log, changelog or contract table exists in this repo, so no feature-scoped identifiers are needed. No dependency graph constraints: t1 has no `dependsOn`.

## 3. Steps

All steps belong to work item **t1**.

1. **Branch and baseline.** Create a feature branch from `main`. Run `pip install -e ".[test]"` and `pytest`; expect 38 passed. Confirm no `CI_FAIL` file exists at the repo root, since the CI `gate` job fails on its presence.

2. **Add the helper** in `src/testbed_utils/dateutils.py`, placed after `is_weekend` and before `humanize_delta`.
   - Signature: `def business_days_between(start: date, end: date) -> int:`. The module already imports `date` and `timedelta` and uses `from __future__ import annotations`; no new imports.
   - Normalise order first: if `start > end`, swap them.
   - Count half-open: iterate `(end - start).days` days from the earlier date, adding one for each day where `is_weekend(day)` is false. Spans are small, so a plain loop is fine and reuses the sibling helper.
   - Docstring states three things: only Monday to Friday are counted; the earlier date is counted and the later date excluded; argument order does not matter and the result is never negative, unlike `days_between`, which is signed.
   - If the docstring includes a `>>>` example, use `date(2024, 1, 1)` to `date(2024, 1, 8)` returning `5` and hand-check it, because pytest is not configured to collect doctests.

3. **Export at package level** in `src/testbed_utils/__init__.py`. Add `business_days_between` to the existing one-line dateutils import and insert it into `__all__` immediately before `"days_between"`, keeping the list alphabetical. Leave the version at `0.1.0`.

4. **Add tests** in `tests/test_dateutils.py`. Extend the import line with `business_days_between` and add a `TestBusinessDaysBetween` class after `TestIsWeekend`, matching the existing style: one class per function, plain asserts, `date(...)` literals, no fixtures. Five tests:

   | Test | Start | End | Expected |
   | --- | --- | --- | --- |
   | `test_full_business_week` | 2024-01-01 (Mon) | 2024-01-08 (Mon) | 5 |
   | `test_weekend_only_span` | 2024-01-06 (Sat) | 2024-01-07 (Sun) | 0 |
   | `test_single_business_day` | 2024-01-01 (Mon) | 2024-01-02 (Tue) | 1 |
   | `test_identical_dates` | 2024-01-03 | 2024-01-03 | 0 |
   | `test_reversed_order_matches_forward` | 2024-01-08 | 2024-01-01 | 5, and equal to the forward call |

5. **Verify locally** (see §4), then check the diff touches exactly three files.

6. **Open the PR** against `main`, titled in the house style `WI-<id>-1: Add business_days_between helper to dateutils with package export and tests`. The body traces to US-01 and R2/R9, lists the five pinned values, and names the half-open convention and order-independence as the contract US-02 consumes. Wait for the CI `test` and `gate` jobs, then hand off to the human approval gate. Do not merge.

## 4. Verification

- **Unit tests (step 4):** the five new tests map one-to-one onto AC1 to AC5. AC6 is satisfied by them running under the project's `pytest` invocation.
- **Full suite:**

  ```bash
  pip install -e ".[test]"
  pytest
  ```

  Expected: 43 passed, zero failures, existing 38 untouched.
- **Package export:**

  ```bash
  python -c "from testbed_utils import business_days_between; print(business_days_between(__import__('datetime').date(2024,1,1), __import__('datetime').date(2024,1,8)))"
  ```

  Expected output: `5`.
- **Scope boundary (AC7):** `git diff --stat main` lists only `src/testbed_utils/dateutils.py`, `src/testbed_utils/__init__.py` and `tests/test_dateutils.py`. No changes to `pyproject.toml`, README, CI or `pdfutils`.
- **Unchanged siblings (FR5):** `git diff main -- src/testbed_utils/dateutils.py` shows only added lines; `days_between`, `is_weekend`, `humanize_delta` and their tests are untouched.
- **CI:** the `test` job (Python 3.12, `pip install -e ".[test]" && pytest`) and the `gate` job both pass on the PR.

## 5. Risks & open points

- **Inclusive-count slip.** Counting both endpoints returns 6, 2 and 1 for AC1 to AC3. Closed by the pinned tests; a reviewer should check the loop bound is `(end - start).days`, not `+ 1`.
- **Signed-versus-unsigned mismatch.** The story's blocker text says the helper "matches `days_between`", but `days_between` is signed and an existing test asserts `-7` for reversed input. The HLD resolves this: the new helper is unsigned and order-independent, and `days_between` is left alone. The docstring must say so to avoid surprising US-02.
- **Q1 still formally open.** The working assumption (accept either order, return an unsigned count) is implemented here. If the PO later rules that reversed input must be rejected, the change is a one-line guard in this helper plus a test, but it would be a breaking change for US-02 once shipped.
- **`__all__` placement.** Cosmetic, but the work item asks for alphabetical order; `business_days_between` sorts before `days_between`.
- **Doctest drift.** Doctests are never collected, so any `>>>` example is documentation only and must be hand-checked.
- **`datetime` inputs.** `datetime` subclasses `date`; mixing the two in subtraction raises. The siblings do not guard against this, and neither does this helper. Not a regression.
- **Algorithm latitude.** The HLD allows a loop or an O(1) formula. The loop is chosen for readability and reuse of `is_weekend`; performance is irrelevant at CLI span sizes.
