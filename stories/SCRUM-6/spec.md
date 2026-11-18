# Ticket draft: SCRUM-6, monthly expense report from a CSV ledger (intake, not ready)

**Status:** blocked on one P0 question (the CHANGELOG gate). Everything else in the story is unchanged and is listed below for review.

## User story
As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

## Context: proposed change, pending the P0 answer
The story's text as written, with the last sentence amended under option (a):

> The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository **other than one line per pull request under `## Unreleased` in `CHANGELOG.md`, which the repository's gate requires**.

Under option (b), the original sentence stays word for word, and the work waits until rule 4 of the repository gate is changed.

## Traceability
R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line) · steps 1–8 · RK1, RK2. Priority: Must. Size: M (≈5). Work items t1 → t2 → t3, built in that order.

## Acceptance criteria
Scenarios 1–25 are kept word for word as the story states them:
- **t1, parsing and validation (scenarios 1–8):** `parse_csv` and `parse_lines`, the frozen `Transaction`, BOM and blank-line handling, and `LedgerError(line, reason)` with the exact reason texts.
- **t2, the monthly report (scenarios 9–18):** `monthly_report`, the `RATES` constant, rounding once with half-to-even, ordering by absolute total with ties by name, top-N, the empty month and `to_dict`, and `ValueError` for caller errors.
- **t3, the command line (scenarios 19–25):** exact text and JSON output, exit codes 0, 2 and 3, the exact stderr for data errors, `--help`, and subprocess-driven tests.

Proposed addition under option (a): **26.** Each pull request of the story adds exactly one line under `## Unreleased` in `CHANGELOG.md` and changes no other existing file.

## Points left to the design stage unless the developer answers them (P1)
- The check order when a row has several faults.
- The line number reported for a quoted memo that spans several lines.
- A file with only blank or whitespace lines.
- A duplicated column name in the header.

## Notes
- The contents of `sample.csv` beyond the totals the scenarios fix (each row's currency, the April row) are for the implementer to choose. Any fixture that meets scenarios 1, 9, 10, 16, 19 and 20 is acceptable.
- In this story, "net" means income + expense. That is not the glossary's "net amount" (before tax), which covers the claims and invoice code only.
- The repository's only check is `pytest` on Python 3.12, run after an editable install. The code must also run on Python 3.10 and later.
