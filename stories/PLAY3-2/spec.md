# Feature Specification — PLAY3-2: Read and validate a CSV ledger (draft, not ready)

**Epic:** Monthly ledger reports from the command line (PLAY3-1) · **Epic PRD:** https://roeeoz.atlassian.net/wiki/pages/viewpage.action?pageId=41385985 · **Repository:** roeeoz/play1, base branch `main`

> **Status: draft.** The intake is not ready. The open points in section 8 decide what the parser accepts and the exact reason text the developer sees for each kind of bad row; the epic's requirement "one fixed reason text per kind of error" (Epic PRD, Functional requirements, R2) fixes only three of them today.

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

Settled by the story and the epic:

- **FR1 — Input.** A UTF-8 CSV ledger whose header names id, date, amount, currency, category and memo, in any order. A leading BOM, blank lines and quoted fields (commas or quotes inside a value) are accepted (R1).
- **FR2 — Output.** One transaction per data row, in file order, with the six values; the amount is an exact decimal with at most two decimal places (R1, RK1).
- **FR3 — Fail fast.** Parsing stops at the first row that cannot become a transaction and reports `{line}: {reason}`, where `line` is the row's physical line number in the file and `reason` is one fixed text per kind of error (R2).
- **FR4 — Known reason texts.**
  - more than two decimals: `amount '12.345' has more than 2 decimal places` (story criterion 2);
  - unknown currency: `unknown currency 'usd'` (story criterion 4) — so currency codes are case-sensitive, and the known set is ILS, USD, EUR (Epic PRD, R4);
  - duplicate id: a reason that names the line of the first occurrence (story criterion 3) — exact wording **not yet fixed** (Q1).
- **FR5 — Two entry points.** The same rules apply whether the ledger comes from a file (`parse_csv`) or from lines already in memory (`parse_lines`) (story context).

Proposed, awaiting the developer's confirmation (Q1–Q3 in section 8) — not yet requirements:

| Kind of error | Proposed reason text | Line reported |
| --- | --- | --- |
| Empty file (no header) | `missing header` | 1 |
| Header lacks a required column | `missing column 'date'` (first missing, in the order id, date, amount, currency, category, memo) | header line |
| Header names a column twice | `duplicate column 'amount'` | header line |
| Row has a different number of fields than the header | `expected 6 fields, got 5` | the row |
| Empty id, date, amount, currency or category | `missing id` (field name) | the row |
| Date not a real calendar date in `YYYY-MM-DD` | `invalid date '2026-02-30'` | the row |
| Amount not a plain decimal number | `invalid amount '1,200.00'` | the row |
| Amount with more than two decimals | `amount '12.345' has more than 2 decimal places` | the row |
| Currency not exactly ILS, USD or EUR | `unknown currency 'usd'` | the row |
| Id already used | `duplicate id 'T-7' (first seen on line 4)` | the row |

Proposed value rules: a negative amount is an expense and a positive one income (needed by PLAY3-3's income/expense split); zero is accepted; no thousands separators or currency symbols; memo may be empty; extra header columns are ignored; surrounding spaces in a value are kept as-is (so `" 12.00"` is an invalid amount); a header-only ledger is valid and yields no transactions; for a quoted value spanning several lines, the reported line is the line where the row starts.

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

## 6. Dependencies & Constraints (product-level)

- **Repository (met):** play1 discovers packages under `src/` (`pyproject.toml`, `[tool.setuptools.packages.find] where = ["src"]`) and runs pytest from `tests/` (`testpaths = ["tests"]`), the epic's one dependency.
- **Gates every PR meets:** the `test` job in `.github/workflows/ci.yml` (`pip install -e ".[test]"` then `pytest`, Python 3.12) is the declared test gate (`.factory/testing.md`); the play1 layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) requires Python source under `src/`, tests under `tests/`, and no file over 200 KB. The story collides with none of them.
- **Stdlib only:** the `ledger` package uses no third-party library (Epic PRD, Summary).
- **Consumers:** PLAY3-3 and PLAY3-4 are blocked by this story and depend on the reason texts staying fixed (RK2).

## 7. Technical Design (deferred to STRUCTURE)

The module layout, the exact signatures of `parse_csv` / `parse_lines`, the fields of `Transaction`, the type of `date`, and how `LedgerError` carries `line` and `reason` are for the STRUCTURE stage. Product constraints it must honour: exact decimals end to end, physical line numbers, the reason texts in section 3 unchanged, and an unreadable file kept distinct from a data error (PLAY3-4 exits 2 for one and 3 for the other, Epic PRD R5).

## 8. Open Questions

- **Q1 (blocking) — the reason-text catalogue.** R2 requires one fixed reason per kind of error, and PLAY3-4 prints it verbatim, but the story fixes only two texts and leaves the duplicate-id text open. Are the kinds of error and texts in section 3's proposed table the full catalogue? *Recommendation:* adopt the table as written.
- **Q2 (blocking) — what a valid value is.** Date format (`YYYY-MM-DD`, real calendar date), amount format (sign means income/expense, zero allowed, no thousands separators), and which fields may be empty (memo only). *Recommendation:* the proposed value rules in section 3.
- **Q3 (blocking) — header and edge cases.** Extra header columns (ignored), a duplicated header column (error), an empty file (error `missing header`), a header-only file (valid, no transactions), spaces around values (kept, so they fail validation), and the line reported for a multi-line quoted row (where it starts). *Recommendation:* as proposed in section 3.
