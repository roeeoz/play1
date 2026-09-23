# HLD — `business_days_between` helper (US-01)

## 1. System Overview
- **What:** one new pure function, `business_days_between`, in `src/testbed_utils/dateutils.py`, plus package re-export and pytest coverage.
- **Problem:** the upcoming `date-span` CLI (US-02) needs a tested business-day count without re-implementing weekday logic.
- **Responsibilities:** count Monday–Friday days between two dates; be order-independent; ship tested. Nothing else (no CLI, no README, no holidays, no timezones).

## 2. Architecture Overview
- **Component:** `testbed_utils.dateutils` — already the intended extension point (module docstring says canned tasks add functions here). Currently 3 helpers: `days_between`, `is_weekend`, `humanize_delta`, all taking native `date`/`timedelta`.
- **Boundary:** additive only. Existing helpers are not modified (FR5). `__init__.py` gains one import name and one `__all__` entry, keeping the existing alphabetical order.
- **External dependencies:** none. Standard library `datetime` only; no new packages.
- **Repository:** `roeeoz/play1` (971bf272-f661-4343-ba13-83764c3aec1f) — the only repo, and the one that already hosts `dateutils`.

## 3. Data Flow
- Synchronous, in-process, pure: caller passes two `date` objects → integer returned. No I/O, no state, no events.
- Future flow (US-02, out of scope here): CLI parses ISO strings with `date.fromisoformat` → passes `date` objects to this helper → prints result.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `dateutils.business_days_between` | Count Mon–Fri days in the span | two `datetime.date` → `int` | roeeoz/play1 |
| `testbed_utils.__init__` export | Expose helper at package level like siblings | — | roeeoz/play1 |
| `tests/test_dateutils.py` new test class | Pin AC1–AC5 | — | roeeoz/play1 |

## 5. Interface Contract (locked for US-02)
- **Name:** `business_days_between`, importable from both `testbed_utils.dateutils` and `testbed_utils`.
- **Parameters:** two `datetime.date` values (not ISO strings). Resolves the spec's open question in favour of sibling consistency; the CLI parses first.
- **Return:** non-negative `int`.
- **Counting convention:** half-open — the earlier date is counted, the later date is excluded. This is the only convention satisfying all five ACs (Mon→next Mon = 5; Sat→Sun = 0; Mon→Tue = 1; identical = 0). It also matches `days_between`'s magnitude (7 calendar days for Mon→Mon), so US-02 will report 7 whole days / 5 business days for the same pair.
- **Order:** arguments may be given in either order; the result is identical. Must be stated in the docstring.

## 6. Key Technical Decisions
- **`date` objects, not strings** — matches `days_between`/`is_weekend`; parsing is the CLI's job. Alternative (accept ISO strings) rejected: would make this helper the odd one out and duplicate parsing the CLI must do anyway for error reporting.
- **Order-normalising, unsigned result** — required by AC5. Note: `days_between` is *signed* (docstring: "negative if end precedes start"; existing test asserts -7), so the spec's claim that this "matches" `days_between` is incorrect. The helper normalises order itself; `days_between` is left unchanged (FR5).
- **Half-open span** — fixed by the ACs, named explicitly so US-02/US-03 quote the right numbers.
- **Algorithm** — left to the implementer (simple day loop reusing `is_weekend`, or O(1) whole-weeks-plus-remainder). Spans are small; correctness against AC1–AC5 is what matters.
- **Package re-export** — yes, matching the established convention in `__init__.py`.
- **No version bump** — nothing in the repo establishes a bump convention for additive helpers; leave `0.1.0`.

## 7. Risks & Constraints
- **Convention slip:** an inclusive count passes only AC2. Mitigated by tests pinning all five ACs.
- **Contract lock-in:** name, `date` parameters, int return and half-open convention become US-02's dependency once merged.
- **Doctests not executed:** pytest is not run with `--doctest-modules`, so any `>>>` example in the docstring must be hand-verified.
- **`datetime` inputs:** `datetime` is a `date` subclass; mixed `date`/`datetime` arithmetic can raise. Siblings do not guard against this; this helper does not either.
- **Toolchain:** pytest only (`pytest>=8`, `testpaths=["tests"]`, `-q`); no linter/formatter configured. CI runs `pip install -e ".[test]" && pytest` on Python 3.12. Baseline: 38 passing.
