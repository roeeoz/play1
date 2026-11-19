# Feature Specification — PLAY3-2: Read and validate a CSV ledger

**Epic:** Monthly ledger reports from the command line (PLAY3-1) · **Epic PRD:** https://roeeoz.atlassian.net/wiki/pages/viewpage.action?pageId=41385985 · **Repository:** roeeoz/play1, base branch `main`

> **Status: ready for STRUCTURE.** The developer accepted the proposed reason-text catalogue, value rules and header/edge-case rules as written (intake, 2026-11-19); they are requirements in section 3.

## 1. Feature Overview

- **What is built:** a new stdlib-only Python package `ledger` under `src/` that reads a UTF-8 CSV ledger (columns id, date, amount, currency, category, memo, in any header order) into transactions in file order, each with an exact decimal amount, and stops at the first row that cannot become a transaction, reporting `{line}: {reason}` with the row's physical line number.
- **Problem:** totalling a month by hand in a spreadsheet lets a malformed row hide inside a wrong total (Epic PRD, Summary and hypothesis). This story is the foundation that removes that: nothing downstream sees a row the parser did not validate.
- **Users:** a developer who keeps a CSV ledger. Downstream, the stories "Monthly report by category in a base currency" (PLAY3-3) and "python -m ledger report command line" (PLAY3-4) consume the transactions and print the error unchanged (Epic PRD, Risks, RK2).
- **Story facts:** Must, M (≈3), traces to R1, R2 · RK1, no blockers, depends on nothing; first in the epic's execution plan.

## 2. Goals & Non-Goals

### Story context

In: `src/ledger/` parsing (`parse_csv`, `parse_lines`), the `Transaction` record and `LedgerError(line, reason)`. Out: the report and the command line.

### Goals

- Every row of a valid ledger becomes a transaction, in file order, with an exact decimal amount — no floating-point money (RK1).
- The first row that cannot become a transaction stops parsing with its physical line number and one fixed reason text for its kind of error (R2), so the command line in PLAY3-4 can print it unchanged.
- Real-world CSV quirks are tolerated: a UTF-8 BOM, blank lines, quoted fields, and the six columns in any header order (R1).

### Non-Goals

- Monthly totals, currency conversion, rounding and ordering — "Monthly report by category in a base currency" (PLAY3-3).
- The `python -m ledger report` command, its exit codes and the `error: {FILE}:{line}: {reason}` line — "python -m ledger report command line" (PLAY3-4).
- Other input formats (JSON, OFX, spreadsheets) and live or configurable rates (Epic PRD, Out of scope).
- Collecting more than one error per run: parsing stops at the first bad row (R2).

## 3. Functional Requirements

- **FR1 — Input.** A UTF-8 CSV ledger whose header names id, date, amount, currency, category and memo, in any order. A leading BOM, blank lines and quoted fields (commas, quotes or line breaks inside a value) are accepted (R1). Extra header columns are ignored.
- **FR2 — Output.** One transaction per data row, in file order, with the six values; the amount is an exact decimal with at most two decimal places (R1, RK1). A header-only ledger is valid and yields no transactions.
- **FR3 — Fail fast.** Parsing stops at the first row that cannot become a transaction and reports `{line}: {reason}`, where `line` is the row's physical line number in the file and `reason` is one fixed text per kind of error (R2). No partial list of transactions is returned alongside an error.
- **FR4 — Valid values.**
  - **date:** `YYYY-MM-DD` and a real calendar date (`2026-02-30` is invalid);
  - **amount:** a plain decimal number with at most two decimal places; negative is an expense, positive is income, zero is accepted; no thousands separators or currency symbols;
  - **currency:** exactly `ILS`, `USD` or `EUR` — case-sensitive (Epic PRD, R4);
  - **empty values:** only memo may be empty; id, date, amount, currency and category must not be;
  - **spaces:** a value is taken as written, never trimmed, so `" 12.00"` is an invalid amount;
  - **id:** unique across the ledger.
- **FR5 — The reason-text catalogue.** These are the only kinds of error and their exact texts; the quoted part is the offending value or name exactly as written in the file:

| Kind of error | Reason text | Line reported |
| --- | --- | --- |
| Empty file (no header) | `missing header` | 1 |
| Header lacks a required column | `missing column 'date'` (the first missing, in the order id, date, amount, currency, category, memo) | header line |
| Header names a column twice | `duplicate column 'amount'` | header line |
| Row has a different number of fields than the header | `expected 6 fields, got 5` (the header's field count, then the row's) | the row |
| Empty id, date, amount, currency or category | `missing id` (the field's name; the first empty one, in the order id, date, amount, currency, category) | the row |
| Date not a real calendar date in `YYYY-MM-DD` | `invalid date '2026-02-30'` | the row |
| Amount not a plain decimal number | `invalid amount '1,200.00'` | the row |
| Amount with more than two decimals | `amount '12.345' has more than 2 decimal places` | the row |
| Currency not exactly ILS, USD or EUR | `unknown currency 'usd'` | the row |
| Id already used | `duplicate id 'T-7' (first seen on line 4)` | the row |

- **FR6 — Line numbers.** The line is the physical line in the file, counting the header, blank lines and the BOM-carrying first line as an editor does; for a row whose quoted value spans several lines, it is the line where the row starts.
- **FR7 — Two entry points.** The same rules and texts apply whether the ledger comes from a file (`parse_csv`) or from lines already in memory (`parse_lines`) (story context).

## 4. User Experience & Behavior

- **Who sees it:** a developer, through a Python call in this story and, after PLAY3-4, through `error: {FILE}:{line}: {reason}` on standard error. The reason text written here is therefore the exact text the developer reads in the terminal (RK2).
- **Flow:** the developer points the parser at a ledger → either gets every transaction back in file order, or gets one error naming one line and one reason, fixes that row, and runs again.
- **What a good error looks like:** it quotes the offending value as written in the file (`'12.345'`, `'usd'`) and names the line the developer opens in an editor — the physical line, counting the header, blank lines and BOM-carrying first line like any editor does.
- **What never happens:** a malformed row silently skipped, a partial list of transactions returned alongside an error, or an amount carried as a float.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: a valid ledger. Given a ledger with a BOM, a blank line and quoted fields, When it is parsed, Then every row becomes a transaction in file order with an exact decimal amount.
2. Scenario 2 — Error: too many decimals. Given row 17 holds the amount `12.345`, When the ledger is parsed, Then parsing stops with line 17 and the reason "amount '12.345' has more than 2 decimal places".
3. Scenario 3 — Error: duplicate id. Given an id repeats on line 9 after line 4, When the ledger is parsed, Then parsing stops with line 9 and a reason naming line 4.
4. Scenario 4 — Error: unknown currency. Given a row with the currency `usd`, When the ledger is parsed, Then parsing stops at that row with the reason "unknown currency 'usd'".
5. Scenario 5 — Error: duplicate id text. Given the id `T-7` on line 4 and again on line 9, When the ledger is parsed, Then parsing stops with line 9 and the reason "duplicate id 'T-7' (first seen on line 4)".
6. Scenario 6 — Error: header. Given an empty file, a header without `date`, or a header naming `amount` twice, When the ledger is parsed, Then parsing stops with, respectively, line 1 and "missing header", the header line and "missing column 'date'", or the header line and "duplicate column 'amount'".
7. Scenario 7 — Error: row values. Given a row with 5 fields under a 6-column header, an empty id, the date `2026-02-30`, or the amount `1,200.00`, When the ledger is parsed, Then parsing stops at that row with, respectively, "expected 6 fields, got 5", "missing id", "invalid date '2026-02-30'" or "invalid amount '1,200.00'".
8. Scenario 8 — Boundary: accepted values. Given a header with an extra column, rows with a negative, a positive and a zero amount, and a row with an empty memo, When the ledger is parsed, Then every row becomes a transaction with its amount's sign kept and the extra column ignored.
9. Scenario 9 — Boundary: header only. Given a ledger holding only its header, When it is parsed, Then it yields no transactions and no error.
10. Scenario 10 — Boundary: untrimmed value. Given a row whose amount is `" 12.00"`, When the ledger is parsed, Then parsing stops at that row with the reason "invalid amount ' 12.00'".
11. Scenario 11 — Boundary: multi-line row. Given a row starting on line 5 whose quoted memo spans lines 5–6 and which holds an invalid amount, When the ledger is parsed, Then parsing stops with line 5.

## 6. Dependencies & Constraints (product-level)

- **Repository (met):** play1 discovers packages under `src/` (`pyproject.toml`, `[tool.setuptools.packages.find] where = ["src"]`) and runs pytest from `tests/` (`testpaths = ["tests"]`), the epic's one dependency.
- **Gates every PR meets:** the `test` job in `.github/workflows/ci.yml` (`pip install -e ".[test]"` then `pytest`, Python 3.12) is the declared test gate (`.factory/testing.md`); the play1 layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) requires Python source under `src/`, tests under `tests/`, and no file over 200 KB. The story collides with none of them.
- **Stdlib only:** the `ledger` package uses no third-party library (Epic PRD, Summary).
- **Consumers:** PLAY3-3 and PLAY3-4 are blocked by this story and depend on the reason texts staying fixed (RK2).

## 7. Technical Design (deferred to STRUCTURE)

The module layout, the exact signatures of `parse_csv` / `parse_lines`, the fields of `Transaction`, the type of `date`, and how `LedgerError` carries `line` and `reason` are for the STRUCTURE stage. Product constraints it must honour: exact decimals end to end, physical line numbers, the reason texts in section 3 unchanged, and an unreadable file kept distinct from a data error (PLAY3-4 exits 2 for one and 3 for the other, Epic PRD R5).

## 8. Open Questions

No blocking question remains: the reason-text catalogue, the value rules and the header/edge-case rules were accepted by the developer as proposed.

- **Assumption — which error a row with several faults reports.** When one row breaks more than one rule, the report names one of them. The spec fixes the order only for empty fields (id, date, amount, currency, category) and for missing header columns; the order among the other checks (field count, date, amount, decimals, currency, duplicate id) is left to STRUCTURE, provided it is fixed and documented. Risk: low — the developer still gets the right line, and fixing the row surfaces the next fault.
