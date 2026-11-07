# Feature Specification Document (DRAFT, not ready: P0 on CHANGELOG scope is open)

## 1. Feature Overview
- **What:** A new stdlib-only Python package `ledger` in roeeoz/play1. It provides `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`, which totals one month of a CSV ledger by category in a base currency.
- **Problem:** A developer who keeps a ledger as a CSV file wants a deterministic monthly summary (income, expenses, net, largest categories) from the terminal, without a spreadsheet. A bad row should be pointed to by its line number, never folded silently into a wrong total.
- **Actor:** A developer who keeps a personal or small-team ledger as a CSV file.

## 2. Goals & Non-Goals
### Story context
The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

> PENDING P0: under option (a), the last sentence becomes "…changes to any existing file of the repository, except one line describing the change under `## Unreleased` in `CHANGELOG.md`."

### Goals
- Parse a CSV ledger into validated transactions. Stop at the first bad row and report its physical line number and an exact reason.
- Build a monthly report in a chosen base currency. Round once, after summing. Order categories by absolute total and support an optional top-N.
- Provide a CLI with text and JSON output and distinct exit codes: 0 for success, 2 for usage errors, 3 for data errors.

### Non-Goals
- Other file formats, live exchange rates, persistent configuration, charts, third-party dependencies, and changes to existing repository files (subject to the P0 decision).

## 3. Functional Requirements
- **FR1 (R1, t1) CSV parsing:** `parse_lines(lines)` and `parse_csv(path)` return frozen `Transaction(id, date, amount, currency, category, memo)` values in file order. Columns are matched by header name, fields are trimmed, and extra columns are ignored. A BOM, blank lines and whitespace-only lines are ignored. Quoted memos keep their commas. A header with no data rows gives an empty list.
- **FR2 (R2, t1) Row validation:** The first bad row raises `LedgerError(line, reason)`, where `str()` is `line {line}: {reason}`. The exact reasons are listed in Scenarios 5–7.
- **FR3 (R3, t2) Monthly report:** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` gives the month, base, count, income, expense, net, and categories. Categories are ordered by absolute total descending, with ties broken by name ascending. An empty month gives a zero report. `to_dict()` returns amounts as strings.
- **FR4 (R4, t2) Conversion and rounding:** Each amount is converted as `amount × rates[currency] ÷ rates[base]` at full precision. Each figure is summed exactly, then quantized once to two places with `ROUND_HALF_EVEN`. Invalid month, base or top raises `ValueError`.
- **FR5 (R5, t3) CLI:** Text and JSON output are byte-exact as in Scenarios 19–21. Usage errors exit 2 and data errors exit 3. Errors print nothing on stdout and a message on stderr.

## 4. User Experience & Behavior
- The text report has exactly the layout in Scenario 19: seven header lines, then category lines indented by two spaces. An empty month shows `categories: none`.
- JSON output is a single object with amounts as strings (Scenario 20).
- A data error appears on stderr exactly as `error: {FILE}:{line}: {reason}`, where FILE is the path as typed (Scenario 23).
- `--help` documents `--month`.

## 5. Acceptance Criteria
(Scenarios 1–25 from the story, carried over word for word. This list will be finalized once the P0 is answered. If option (a) is chosen, one criterion is added: the pull request adds one line describing the change under `## Unreleased` in `CHANGELOG.md` and changes no other existing file.)

## 6. Dependencies & Constraints
- roeeoz/play1, base branch `main`. Python 3.10 or newer. CI runs `pip install -e ".[test]"` and then `pytest` on 3.12.
- The repo gate requires source under `src/`, tests under `tests/`, no file over 200 KB, and a CHANGELOG entry (PLAY-G4, which is the open P0).
- Work items are ordered t1 → t2 → t3.

## 7. Technical Design
Deferred to STRUCTURE.

## 8. Open Questions
- P0: the conflict between the scope rule and the CHANGELOG gate.
- P1: the field count N when the header has extra columns, the line number reported for a multi-line quoted row, and the message for a duplicate header column.
