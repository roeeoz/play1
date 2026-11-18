# Feature Specification Document — Read and validate a CSV ledger (FIPSPROBE-2)

## 1. Feature Overview

**What is being built.** A new stdlib-only Python package `ledger` under `src/`. It reads a UTF-8 CSV ledger and validates every row. It returns the rows as transactions in file order, with exact decimal amounts. It stops at the first malformed row and reports that row's physical line number with one fixed reason text.

**Problem.** A month's total is usually added up by hand. A malformed row can hide inside a wrong total. A row that is silently skipped or mis-parsed makes the total untrustworthy. This is the problem the epic *Monthly ledger reports from the command line* exists to remove (Epic PRD, Summary and hypothesis; risk RK1).

**Target users.** Developers who keep a CSV ledger. Downstream, the two sibling stories consume this one:
- FIPSPROBE-3 (the monthly report) uses the transactions.
- FIPSPROBE-4 (the command line) prints the error line and reason unchanged (Epic PRD, risk RK2).

## 2. Goals & Non-Goals

### Story context
In: `src/ledger/` parsing (`parse_csv`, `parse_lines`), the `Transaction` record and `LedgerError(line, reason)`. Out: the report and the command line.

### Goals
- Read a UTF-8 CSV ledger whose header names id, date, amount, currency, category and memo in any order. Tolerate a BOM, blank lines and quoted fields (Epic PRD, R1).
- Turn every data row into a transaction, in file order, with an exact decimal amount. No floating point is used at any point (RK1).
- Stop at the first row that cannot become a transaction. Report it as `{line}: {reason}`, using the row's physical line number and one fixed reason text per kind of error (R2).
- Fix the reason texts as a contract that FIPSPROBE-4 prints unchanged (RK2).
- Fix the sign convention (negative means expense, positive means income) that FIPSPROBE-3 relies on.

### Non-Goals
- The monthly report, totals, currency conversion, rates and rounding (FIPSPROBE-3).
- The `python -m ledger` command line, its output format and exit codes (FIPSPROBE-4).
- Input formats other than CSV (JSON, OFX, spreadsheets). The Epic PRD puts these in a later phase.
- Collecting several errors in one pass. Parsing stops at the first one.
- Live or configurable exchange rates, and any user interface.

## 3. Functional Requirements

**FR1 — Input.**
- The ledger is UTF-8 text, with or without a leading BOM.
- It can be read from a file (`parse_csv`) or from lines of text that are already in hand (`parse_lines`). Both give identical results and identical errors for the same content.

**FR2 — Header.**
- The first non-blank line is the header. It must name the six columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order.
- Names match exactly and case-sensitively, after trimming surrounding whitespace.
- Extra columns are allowed and ignored.
- Header problems are reported on line 1:
  - an empty file, or a file with only blank lines: `missing header`
  - a required column that is absent: `missing column '{name}'`, e.g. `missing column 'memo'`
  - a required column named more than once: `duplicate column '{name}'`, e.g. `duplicate column 'id'`

**FR3 — Rows.**
- Each later non-blank record is one transaction, in file order.
- Blank lines are skipped and are never errors.
- Quoted fields follow standard CSV quoting. A quoted field may contain commas, doubled quotes and line breaks.
- Surrounding whitespace is trimmed from every field before it is validated.

**FR4 — Line numbers.**
- The reported line is the physical line in the file where the offending record starts, counting from 1.
- The header and every blank line count.
- A record whose quoted field spans several lines is reported at its first line.

**FR5 — Field rules.**
- **Field count.** A row must have exactly as many fields as the header.
- **id.** It must be non-empty. It must not repeat an id seen on an earlier row.
- **date.** Only ISO `YYYY-MM-DD` that is a real calendar date. For example, `2026-02-30` and `2026-13-01` are rejected.
- **amount.**
  - A decimal number with an optional leading `-` or `+` and 0, 1 or 2 decimal places.
  - Thousands separators are not allowed.
  - Negative means expense and positive means income.
  - Zero is allowed.
  - The value is kept exactly as written. It is never rounded.
- **currency.** Exactly one of `ILS`, `USD` or `EUR`, uppercase only. The epic's fixed rates cover these three.
- **category.** It must be non-empty.
- **memo.** It may be empty.

**FR6 — Error kinds and their fixed reason texts.**

Each of the eight kinds of error has exactly one reason text. In the texts below, `{value}` is the field's trimmed value.

| Kind | Reason text | Example |
| --- | --- | --- |
| Wrong number of fields | `row has {n} fields, expected {m}` | `row has 5 fields, expected 6` |
| Empty id | `empty id` | `empty id` |
| Duplicate id | `duplicate id '{value}' (first seen on line {line})` | `duplicate id 'T-7' (first seen on line 4)` |
| Bad date | `invalid date '{value}'` | `invalid date '2026-13-01'` |
| Non-numeric amount | `amount '{value}' is not a number` | `amount 'abc' is not a number` |
| Too many decimal places | `amount '{value}' has more than 2 decimal places` | `amount '12.345' has more than 2 decimal places` |
| Unknown currency | `unknown currency '{value}'` | `unknown currency 'usd'` |
| Empty category | `empty category` | `empty category` |

The three header texts in FR2 complete the set.

**FR7 — Error report.**
- Parsing stops at the first error.
- The error carries the line number and the reason as separate values. Its text form is `{line}: {reason}`, e.g. `17: amount '12.345' has more than 2 decimal places`.
- No transactions are returned when an error occurs.

**FR8 — Unreadable input.**
- A file that cannot be opened, or that is not valid UTF-8, is an unreadable-file problem, not a data error. It is not reported as `{line}: {reason}`.
- This keeps it apart from data errors, so FIPSPROBE-4 can give it exit code 2 rather than 3 (Epic PRD, R5).

**FR9 — Transaction.**
- Each transaction holds:
  - the id
  - the date as a calendar date
  - the amount as an exact decimal
  - the currency code
  - the category
  - the memo
- All text values are trimmed. Extra columns are not kept.

## 4. User Experience & Behavior

- **Happy path.** The developer points the parser at a ledger. Every row comes back as a transaction, in the order it appears in the file. BOMs, blank lines and quoted fields make no visible difference.
- **Error path.** The developer sees exactly one error: the physical line number and one fixed reason text, as `{line}: {reason}`. Because the texts are fixed, a script or test can match them exactly. FIPSPROBE-4 will show them as `error: {FILE}:{line}: {reason}`.
- **States.** A parse has one of three outcomes:
  - all rows valid: transactions returned
  - a data error at a line: one error, no transactions
  - an unreadable file: a file-level problem, not a line error

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: a valid ledger. Given a ledger with a BOM, a blank line and quoted fields, When it is parsed, Then every row becomes a transaction in file order with an exact decimal amount.
2. Scenario 2 — Error: too many decimals. Given row 17 holds the amount `12.345`, When the ledger is parsed, Then parsing stops with line 17 and the reason "amount '12.345' has more than 2 decimal places".
3. Scenario 3 — Error: duplicate id. Given an id repeats on line 9 after line 4, When the ledger is parsed, Then parsing stops with line 9 and a reason naming line 4.
4. Scenario 4 — Error: unknown currency. Given a row with the currency `usd`, When the ledger is parsed, Then parsing stops at that row with the reason "unknown currency 'usd'".
5. Given the id `T-7` first appears on line 4 and repeats on line 9, When the ledger is parsed, Then the reason is exactly "duplicate id 'T-7' (first seen on line 4)".
6. Given a header whose six required columns are in a non-standard order and which has one extra column, When the ledger is parsed, Then every row parses correctly and the extra column is ignored.
7. Given a header without `memo`, When the ledger is parsed, Then parsing stops with line 1 and the reason "missing column 'memo'". Given a header naming `id` twice, Then it stops with line 1 and the reason "duplicate column 'id'". Given a header naming `Memo` instead of `memo`, Then it stops with line 1 and the reason "missing column 'memo'".
8. Given an empty file or a file of only blank lines, When it is parsed, Then parsing stops with line 1 and the reason "missing header".
9. Given a row with five fields under a six-column header, When the ledger is parsed, Then parsing stops at that row with the reason "row has 5 fields, expected 6".
10. Given a row with an empty or whitespace-only id, When the ledger is parsed, Then parsing stops at that row with the reason "empty id".
11. Given a row with the date `2026-13-01`, `2026-02-30` or `01/03/2026`, When the ledger is parsed, Then parsing stops at that row with the reason "invalid date '{value}'" naming that date.
12. Given a row with the amount `abc` or `1,000.00`, When the ledger is parsed, Then parsing stops at that row with the reason "amount '{value}' is not a number" naming that amount.
13. Given rows with the amounts `-12.50`, `+3`, `0` and `7.5`, When the ledger is parsed, Then each is accepted and kept as the exact decimal written, and the negative amount is the expense.
14. Given a row with an empty category, When the ledger is parsed, Then parsing stops at that row with the reason "empty category".
15. Given a row with an empty memo, When the ledger is parsed, Then the row becomes a transaction with an empty memo.
16. Given a row with each of the currencies `ILS`, `USD` and `EUR`, When the ledger is parsed, Then all are accepted. Given `Eur`, Then parsing stops with the reason "unknown currency 'Eur'".
17. Given fields with spaces around them, e.g. ` USD `, When the ledger is parsed, Then the values are trimmed before validation and in the transaction.
18. Given a header, two blank lines and a malformed first data row, When the ledger is parsed, Then the reported line is 4. Given a malformed row whose quoted memo spans lines 5–6, Then the reported line is 5.
19. Given any data error, Then the error exposes its line number and its reason separately, and its text is exactly `{line}: {reason}`.
20. Given a file that is not valid UTF-8, When it is parsed, Then it fails as an unreadable file and not as a `{line}: {reason}` data error.
21. Given the same ledger content, When it is read with `parse_csv` from a file and with `parse_lines` from its lines, Then both give the same transactions, or the same line and reason.

## 6. Dependencies & Constraints (product-level)

- **FIPSPROBE-3** depends on this story for the transaction, the sign convention and a date it can filter by month.
- **FIPSPROBE-4** depends on this story for the line, the reason, the reason texts and the split between unreadable files and data errors.
- **The reason texts in FR2 and FR6 are a contract.** FIPSPROBE-4 prints them unchanged (RK2), so changing them later is a change to that story's behaviour.
- **Stdlib only.** No new dependencies.
- **Repository conventions:**
  - The package lives under `src/` and is found by the existing manifest.
  - Tests live in `tests/` and import the installed package.
  - Each ticket adds a line under `## Unreleased` in `CHANGELOG.md`.

## 7. Technical Design (deferred to STRUCTURE)

STRUCTURE settles the following:
- The exact signatures of `parse_csv` (a path or a file object) and `parse_lines` (an iterable of strings).
- The shape of `Transaction`.
- How the unreadable-file problem is surfaced.
- The internal validation layout. The repository keeps rules in pure functions.

Two constraints come from the product:
- Amounts are never floats.
- `LedgerError` carries `line` and `reason` and renders as `{line}: {reason}`.

## 8. Open Questions

None of these blocks the work. Each has a recommended default for STRUCTURE.

- **A row with several problems.** Which reason is reported? Recommended: check in a fixed order and report the first failure. The order is field count, id (empty, then duplicate), date, amount (not a number, then decimal places), currency, category. Any fixed order meets R2. The chosen order should be written down.
- **Edge amount forms.** Are `12.`, `.5` and exponent forms such as `1e3` accepted? Recommended: reject all three as "amount '{value}' is not a number". The accepted format is "signed digits with 0–2 decimal places", and none of these is written that way.
- **Duplicate ids.** Recommended: compare the trimmed ids exactly, case-sensitively, so `T-7` and `t-7` are different ids.
