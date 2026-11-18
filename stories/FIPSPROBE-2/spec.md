# Ticket draft — Read and validate a CSV ledger (FIPSPROBE-2) — IN PROGRESS

## Story context
In: `src/ledger/` parsing (`parse_csv`, `parse_lines`), the `Transaction` record and `LedgerError(line, reason)`. Out: the report and the command line.

## User story
As a developer keeping a CSV ledger, I want every row read and validated, so that a malformed row is reported by its line number instead of hiding in a wrong total.

Traces to:
- Epic PRD *Monthly ledger reports from the command line*, functional requirements R1 and R2, and risk RK1.
- Priority: Must.
- Blocks FIPSPROBE-3 (the report) and FIPSPROBE-4 (the command line).

## Known behaviour (from the story and the epic)
- Input is a UTF-8 CSV whose header names id, date, amount, currency, category and memo, in any order.
- A BOM, blank lines and quoted fields are tolerated.
- Rows become transactions in file order, with exact decimal amounts and never floats (RK1).
- Parsing stops at the first bad row and reports `{line}: {reason}`, where:
  - the line is the row's physical line number
  - each kind of error has one fixed reason text (R2)
- FIPSPROBE-4 prints that reason unchanged (RK2).
- The package is stdlib-only.

## Reason texts fixed so far
- `amount '12.345' has more than 2 decimal places`
- `unknown currency 'usd'`
- Duplicate id: the reason must name the earlier line. The exact text is still open.

## Acceptance criteria (as given)
1. Scenario 1 — Happy path: a valid ledger. Given a ledger with a BOM, a blank line and quoted fields, When it is parsed, Then every row becomes a transaction in file order with an exact decimal amount.
2. Scenario 2 — Error: too many decimals. Given row 17 holds the amount `12.345`, When the ledger is parsed, Then parsing stops with line 17 and the reason "amount '12.345' has more than 2 decimal places".
3. Scenario 3 — Error: duplicate id. Given an id repeats on line 9 after line 4, When the ledger is parsed, Then parsing stops with line 9 and a reason naming line 4.
4. Scenario 4 — Error: unknown currency. Given a row with the currency `usd`, When the ledger is parsed, Then parsing stops at that row with the reason "unknown currency 'usd'".

## Open, blocking (P0)
- The full list of kinds of error and the exact reason text for each.
- The accepted date format.
- The amount's sign convention and format.
- How header errors are reported: line number and text; whether extra columns are allowed; whether matching is case-sensitive.
- The accepted currency set and whether it is case-sensitive.

## Open (P1)
- Line numbering for a quoted field that spans several lines. Recommendation: use the line where the row starts. The header and blank lines count toward the numbering.
- Empty file or missing header. Recommendation: a data error on line 1, `missing header`.
- A file that is not UTF-8. Recommendation: treat it as an unreadable-file error, not a data error, which matches R5's exit code 2.
- Whitespace around fields. Recommendation: trim it.

## Out of scope
- The monthly report, the command line, exchange rates, and input formats other than CSV.
