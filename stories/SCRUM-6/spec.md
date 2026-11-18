# Ticket draft: SCRUM-6, monthly expense report from a CSV ledger (intake, not ready)

**Status:** blocked on one P0 question, the CHANGELOG gate. Every other point is settled: either the story states it, or the developer told us to take the simplest reading and record it as an assumption (see "Assumptions" below).

## User story
As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

## Context: depends on the P0 answer
The story's text as written:

> The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

- **Option (a), recommended:** the last clause becomes "changes to any existing file of the repository other than one line per pull request under `## Unreleased` in `CHANGELOG.md`, which the repository's gate requires".
- **Option (b):** the sentence stays word for word, and this story waits until rule 4 of the repository gate (`PLAY-G4`) has been changed in a separate change.

## Traceability
- Traces to: R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line) · steps 1–8 · RK1, RK2.
- Priority: Must. Size: M (≈5).
- Work items: t1 → t2 → t3, built in that order.

## Acceptance criteria
Scenarios 1–25 are kept word for word as the story states them:
- **t1, parsing and validation (scenarios 1–8).**
  - `parse_csv` and `parse_lines`, and the frozen `Transaction`.
  - Header columns in any order, with fields stripped.
  - A BOM, blank lines and quoted memos are handled.
  - Errors are `LedgerError(line, reason)` with the exact reason texts, including duplicate ids and missing columns or header.
- **t2, the monthly report (scenarios 9–18).**
  - `monthly_report` and the `RATES` constant.
  - Rounding once, after summing, half to even, always to two places.
  - Categories ordered by absolute total, ties by name, with top-N.
  - The empty month and `to_dict`, and `ValueError` for caller errors.
- **t3, the command line (scenarios 19–25).**
  - Exact text and JSON output.
  - Exit codes 0, 2 and 3, and the exact stderr for data errors.
  - `--help`, and tests that drive the command through subprocess.

Under option (a) only, one criterion is added: **26.** Each pull request of the story adds exactly one line under `## Unreleased` in `CHANGELOG.md` and changes no other existing file.

## Assumptions (the developer chose the simplest reading where the story is silent)
- **A1. A row with several faults.**
  - The field-count check comes first.
  - The fields are then checked in canonical column order: `id`, `date`, `amount`, `currency`, `category`, `memo`.
  - The first fault found is reported. A duplicate id is checked after the row is otherwise valid.
- **A2. A quoted field that spans lines.** The error reports the physical line on which the row starts.
- **A3. A file with only blank or whitespace-only lines.** It is treated like the empty file: `LedgerError(1, "missing header")`.
- **A4. A duplicated column name in the header.** The story gives no error for it.
  - The simplest reading adds no new error text.
  - The STRUCTURE stage chooses which occurrence is read and records that choice.
  - The rule that columns beyond the six named ones are ignored still applies.
- **A5. The contents of `sample.csv`.** Anything the scenarios don't fix is the implementer's choice, such as each row's currency and the April row. Any fixture that satisfies scenarios 1, 9, 10, 16, 19 and 20 is acceptable.

## Notes
- In this story, "net" means income + expense. That is not the glossary's "net amount" (before tax), which covers the claims and invoice code only.
- The repository's only check is `pytest` on Python 3.12, run after an editable install. The code must also run on Python 3.10 and later.
