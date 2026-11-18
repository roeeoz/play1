# Feature Specification Document — SCRUM-19: Monthly expense report from a CSV ledger

> Status: in-progress intake draft (NOT_READY — one blocking question open, see §8).

## 1. Feature Overview

**What is being built.** A new, standard-library-only Python package `ledger` (under `src/`, tests under `tests/`) that reads a CSV ledger and prints a monthly report from the terminal: `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`. The report shows, for one month and in one base currency, the transaction count, income, expense, net, and the per-category totals ordered by size.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has no quick, deterministic way to get a month's summary without opening a spreadsheet, and a malformed row silently produces a wrong total instead of being pointed out.

**Target user.** A developer who keeps a personal or small-team ledger as a CSV file and works from the terminal.

**User story.** As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

Traces to: R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line) · steps 1–8 · RK1, RK2. Priority: Must. Size: M (≈5). Delivered as three dependent work items: t1 model and CSV parsing → t2 monthly report → t3 command line.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

> ⚠️ Pending the answer to Q1 (§8): the last exclusion — "changes to any existing file of the repository" — collides with the repository's pull-request gate, which requires a `CHANGELOG.md` entry. Recommended resolution: amend it to "changes to any existing file of the repository other than one line under `## Unreleased` in `CHANGELOG.md`". The paragraph above is copied unchanged until the developer decides.

### Goals

- Parse a UTF-8 CSV ledger into ordered, validated transactions, rejecting the first bad row with its physical line number and an exact reason (R1, R2).
- Produce a deterministic monthly report in a chosen base currency: count, income, expense, net and category totals ordered by absolute size, optionally limited to the top N (R3).
- Convert currencies at fixed, parameterisable rates and round each figure exactly once, after summing, half to even, with two decimal places always (R4).
- Expose the report through `python -m ledger report`, as human-readable text or JSON, with distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals

- Other input formats (anything but CSV) and other output formats beyond the text and JSON report.
- Live or fetched exchange rates; currencies other than ILS, USD, EUR.
- Persistent configuration (config files, saved defaults).
- Charts or any visual output.
- Any third-party dependency (runtime or for the package itself).
- Changes to existing files of the repository (scope of this exclusion pending Q1).
- Multi-month ranges, budgets, editing or writing the ledger.

## 3. Functional Requirements

**FR1 — Ledger input (R1).** A ledger is a UTF-8 CSV file (a leading BOM is tolerated) whose first line is a header naming `id`, `date`, `amount`, `currency`, `category`, `memo` in any order; extra columns are ignored; columns are matched by name. Blank and whitespace-only lines are skipped but still count toward line numbers. Field values are trimmed. Quoted fields (e.g. a memo containing a comma) are honoured. A header with no data rows yields no transactions and no error.

**FR2 — Transaction values (R1).** Each row becomes an immutable transaction with `id` (text), `date` (calendar date), `amount` (exact decimal, preserving the text's value, e.g. `12000.00`), `currency` (text), `category` (text), `memo` (text, possibly empty), returned in file order. Ledger text can be parsed from a file path or from any iterable of lines, with identical results.

**FR3 — Row validation (R2).** Parsing stops at the first bad row and reports its physical line number (header = line 1, blank lines count) and an exact reason, displayed as `line {line}: {reason}`. Reasons are fixed texts for: malformed date, non-calendar date, non-numeric amount (including `NaN`/`Infinity`), more than two decimal places, zero amount, unknown currency (case-sensitive), empty category, empty id, wrong field count, duplicate id (naming the first line it was seen on), missing header columns (listed in canonical order), and missing header (empty file). Exact texts are in §5, criteria 5–7.

**FR4 — Monthly report (R3).** Given transactions, a month `YYYY-MM` (month 01–12), a base currency (default ILS) and an optional top-N (≥1, default all): only transactions dated in that month count; the report states `month`, `base`, `count`, `income` (sum of positive), `expense` (sum of negative), `net`, and `categories` — each with name, total and count — ordered by absolute total descending, ties by name ascending. Top-N truncates only the category list; the other figures always cover the whole month. An empty month is a zero report, not an error. The report has a dictionary form with amounts as two-place strings.

**FR5 — Conversion and rounding (R4).** Each amount is converted as `amount × rate[currency] ÷ rate[base]` at full precision, with default rates ILS 1, USD 3.70, EUR 4.00 (ILS per unit), overridable by the caller. Each figure is the exact sum rounded once to two places with half-to-even; figures are rounded independently and are not forced to add up. Every figure always shows two decimal places.

**FR6 — Caller errors (R3).** An invalid month, a base not among the rates, or a top below 1 is a caller error, distinct from a ledger data error.

**FR7 — Command line (R5).** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`, with `--help`. Outputs: a fixed-format text report (default) or a JSON object (`--json`) with amounts as strings. Exit 0 on success with an empty stderr; exit 2 with nothing on stdout and a message on stderr for usage errors (no subcommand, missing/invalid `--month`, `--top` < 1, unsupported `--base`, unopenable FILE); exit 3 with nothing on stdout and `error: {FILE}:{line}: {reason}` on stderr for ledger data errors.

**FR8 — Tests and fixtures.** Fixtures live under `tests/fixtures/ledger/` (`sample.csv`, `bom_blank.csv`, `empty.csv`, `bad_amount.csv`); tests are `tests/test_ledger_*.py`; the command-line tests run the real installed entry point via `subprocess` with `sys.executable -m ledger`, without `sys.path` manipulation.

## 4. User Experience & Behavior

**Primary flow.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a thirteen-line-style plain-text report on stdout:

```
month: 2026-03
base: ILS
transactions: 7
income: 12925.00
expense: -3025.50
net: 9899.50
categories:
  salary: 12000.00 (1)
  rent: -1500.00 (1)
  ...
```

One `key: value` line per figure, then `categories:` and one line per category indented by two spaces as `name: total (count)`, in report order. An empty month prints `categories: none` instead of the category block.

**Machine-readable flow.** With `--json`, stdout is a single JSON object with keys `month`, `base`, `count`, `income`, `expense`, `net`, `categories` (list of `{name, total, count}`); all amounts are strings with two decimals so no precision is lost.

**Options.** `--base` (ILS, USD or EUR; default ILS) changes the reporting currency; `--top N` (integer ≥ 1) shows only the N largest categories while the totals still cover the whole month.

**Error experience.**
- A bad ledger row: nothing on stdout; stderr is exactly `error: {FILE}:{line}: {reason}` (FILE as typed by the user) and exit code 3 — the user can jump straight to the line.
- A wrong command line or unopenable file: nothing on stdout, a usage message on stderr, exit code 2.
- Success: exit 0, stderr empty.

**Qualities.** Output is deterministic: the same file and arguments always produce byte-identical output. Two decimal places always. No colour, no charts.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: a valid file parses in order. Given `tests/fixtures/ledger/sample.csv` holds the header and nine valid rows (seven dated 2026-03, one 2026-02-27, one 2026-04-01; ids `t001`…`t009`), When `parse_csv(path)` is called, Then it returns nine `Transaction` values in file order, each a frozen dataclass with `id` (str), `date` (`datetime.date`), `amount` (`Decimal`, exactly the text's value, so `12000.00` stays `Decimal("12000.00")`), `currency` (str), `category` (str) and `memo` (str, possibly empty).
2. Scenario 2 — Happy path: header order is free and fields are stripped. Given a header `memo,category,currency,amount,date,id` and a row whose fields carry surrounding spaces, When the text is parsed, Then the transaction holds the trimmed values and the columns are matched by name, not by position. Columns beyond the six named ones are ignored.
3. Scenario 3 — Boundary: BOM, blank lines and a quoted memo. Given `tests/fixtures/ledger/bom_blank.csv` starts with a UTF-8 BOM, has blank and whitespace-only lines between rows, an empty memo on one row and a memo quoted because it contains a comma on another, When parsed, Then two transactions are returned, the BOM and the blank lines are ignored, the empty memo is `""` and the quoted memo keeps its comma.
4. Scenario 4 — Boundary: header only. Given a file with the header row and no data rows, When parsed, Then an empty list is returned and no error is raised.
5. Scenario 5 — Error: a bad row raises `LedgerError(line, reason)`. Given a row that cannot become a transaction, When parsed, Then `LedgerError` is raised carrying `line` (the physical line number in the file: the header is line 1 and blank lines count) and `reason`, with `str(error)` equal to `line {line}: {reason}`, and the reason for each case is exactly: a date not matching `YYYY-MM-DD` → `date '2026-3-1' is not YYYY-MM-DD`; a well-formed date that is not a calendar date → `date '2026-02-30' is not a calendar date`; an amount that is not a decimal number, including `NaN` and `Infinity` → `amount 'abc' is not a number`; an amount with more than two decimal places → `amount '1.505' has more than 2 decimal places`; a zero amount → `amount must not be zero`; a currency outside ILS/USD/EUR, compared case-sensitively → `unknown currency 'usd'`; an empty category → `empty category`; an empty id → `empty id`; a row whose field count differs from the header's → `expected 6 fields, got 5`. Parsing stops at the first bad row.
6. Scenario 6 — Error: duplicate id. Given two rows share an id, with a blank line between them, When parsed, Then the error names the second row's line and reads `duplicate id 't1' (first seen on line 2)`.
7. Scenario 7 — Error: header problems. Given a header lacking required columns, When parsed, Then `LedgerError(1, "missing column(s): currency, category, memo")` lists the missing names in the canonical order `id, date, amount, currency, category, memo`; Given an empty file (`tests/fixtures/ledger/empty.csv`, zero bytes), When parsed, Then `LedgerError(1, "missing header")`.
8. Scenario 8 — Edge: two entry points. Given ledger text as any iterable of lines (for example an `io.StringIO`), When `parse_lines(lines)` is called, Then it behaves exactly as `parse_csv` does on a file; `parse_csv(path)` opens the path with encoding `utf-8-sig` and `newline=""` and delegates to `parse_lines`.
9. Scenario 9 — Happy path: March of the sample in ILS. Given the nine sample transactions, When `monthly_report(transactions, "2026-03")` is called, Then the report has `month` `2026-03`, `base` `ILS`, `count` 7, `income` `Decimal("12925.00")`, `expense` `Decimal("-3025.50")`, `net` `Decimal("9899.50")`, and `categories` is the list of `CategoryTotal(name, total, count)` ordered by absolute total descending: salary 12000.00 (1), rent -1500.00 (1), freelance 925.00 (1), groceries -760.50 (2), software -444.00 (1), travel -321.00 (1).
10. Scenario 10 — Happy path: another base currency. Given the sample, When the report is built with `base="USD"`, Then every amount is converted as `amount × RATES[currency] ÷ RATES[base]` at full Decimal precision before summing, so salary totals `3243.24` and freelance `250.00`, and the report's `base` reads `USD`. `RATES` is a module constant mapping `ILS` → `Decimal("1")`, `USD` → `Decimal("3.70")`, `EUR` → `Decimal("4.00")`.
11. Scenario 11 — Boundary: rounding happens once, after summing, half to even. Given one transaction of 0.05 ILS, When reported in base EUR, Then `income` is `0.01` (the exact 0.0125 rounded once); Given three such transactions, Then `income` is `0.04` (the exact sum 0.0375 rounded once), not `0.03` (three individually rounded cents). Every figure (`income`, `expense`, `net`, each category total) is the exact sum quantized to two places with `ROUND_HALF_EVEN`, independently of the others, so the report does not force them to add up.
12. Scenario 12 — Boundary: two places always. Given transactions of 5 ILS and -2 ILS, When reported, Then `str(income)` is `5.00`, `str(expense)` is `-2.00` and `str(net)` is `3.00`.
13. Scenario 13 — Happy path: top-N. Given the sample, When the report is built with `top=2`, Then `categories` is salary then rent only, while `income`, `expense`, `net` and `count` still cover all seven transactions; a `top` larger than the number of categories keeps them all; `top=None` (the default) keeps them all.
14. Scenario 14 — Edge: ties. Given two categories with equal absolute totals, When reported, Then they are ordered by category name ascending.
15. Scenario 15 — Edge: empty month is a zero report. Given the sample, When the report is built for `2026-05`, Then `count` is 0, `income`, `expense` and `net` are `Decimal("0.00")`, `categories` is empty, and `report.to_dict()` is `{"month": "2026-05", "base": "ILS", "count": 0, "income": "0.00", "expense": "0.00", "net": "0.00", "categories": []}`.
16. Scenario 16 — Edge: only the month's transactions count. Given the sample, When the report is built for `2026-02`, Then `categories` is exactly groceries -99.99 (1).
17. Scenario 17 — Edge: rates are a parameter. Given `rates={"ILS": 1, "USD": 2, "EUR": 4}` as Decimals, When a 10 USD transaction is reported in ILS, Then `income` is `20.00`.
18. Scenario 18 — Error: arguments. When `month` is not `YYYY-MM` with a month of 01–12 (`2026-3`, `2026-13`, `2026-00`, `March 2026`, `202603`, the empty string), Then `ValueError` is raised; when `base` is not a key of `rates`, Then `ValueError`; when `top` is less than 1, Then `ValueError`. These are caller errors, never `LedgerError`.
19. Scenario 19 — Happy path: text report. When `python -m ledger report tests/fixtures/ledger/sample.csv --month 2026-03` runs, Then it exits 0 with nothing on stderr and stdout is exactly these thirteen lines: `month: 2026-03`, `base: ILS`, `transactions: 7`, `income: 12925.00`, `expense: -3025.50`, `net: 9899.50`, `categories:`, then one line per category, indented by two spaces, in report order: `  salary: 12000.00 (1)`, `  rent: -1500.00 (1)`, `  freelance: 925.00 (1)`, `  groceries: -760.50 (2)`, `  software: -444.00 (1)`, `  travel: -321.00 (1)`.
20. Scenario 20 — Happy path: JSON with base and top. When the same command runs with `--base USD --top 1 --json`, Then it exits 0 and stdout parses as the JSON object `{"month": "2026-03", "base": "USD", "count": 7, "income": "3493.24", "expense": "-817.70", "net": "2675.54", "categories": [{"name": "salary", "total": "3243.24", "count": 1}]}` — amounts are strings, so no precision is lost.
21. Scenario 21 — Edge: empty month on the command line. When the command runs with `--month 2026-05`, Then it exits 0 and stdout ends with the lines `income: 0.00`, `expense: 0.00`, `net: 0.00`, `categories: none`.
22. Scenario 22 — Error: usage. When the command line is wrong — no subcommand; `--month` missing; `--month 2026-13`; `--top 0`; `--base GBP`; a FILE that cannot be opened — Then the process exits 2, prints nothing on stdout and a message on stderr. `--base` accepts exactly ILS, USD and EUR and defaults to ILS; `--top` accepts integers of at least 1.
23. Scenario 23 — Error: data. When the FILE has a bad row (`tests/fixtures/ledger/bad_amount.csv`, whose third line carries the amount `-2.505`), Then the process exits 3, prints nothing on stdout and stderr is exactly `error: {FILE}:3: amount '-2.505' has more than 2 decimal places` followed by a newline, FILE being the path as given on the command line.
24. Scenario 24 — Happy path: help. When `python -m ledger report --help` runs, Then it exits 0 and stdout documents `--month`.
25. Scenario 25 — Edge: the tests run the real entry point. Given `tests/test_ledger_cli.py`, When it drives the command, Then it does so through `subprocess` with `[sys.executable, "-m", "ledger", ...]`, relying on the installed package and on no `sys.path` manipulation.

## 6. Dependencies & Constraints (product-level)

- **Repository pre-conditions (verified in the checkout).** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest `testpaths = ["tests"]`; the test gate (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12. No `src/ledger/`, no `tests/test_ledger_*.py` and no `tests/fixtures/ledger/` exist yet. A new `src/ledger/` package is therefore picked up by the existing manifest with no edit to `pyproject.toml`.
- **Repository layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`)**, run on every pull request: Python source under `src/`, tests under `tests/` (met by the story); no file over 200 KB (met); and **rule 4 — the pull request must add a line under `## Unreleased` in `CHANGELOG.md`, otherwise a `PLAY-G4` blocker**. `CHANGELOG.md` already exists, so this rule collides with the story's exclusion of "changes to any existing file of the repository" — see Q1.
- **Stdlib only.** No third-party dependency may be added; the package must not rely on the repository's existing runtime dependencies (`pypdf`, `flask`).
- **Determinism.** Fixed exchange rates, never fetched; identical input gives identical output.
- **Build order.** t1 (parsing) → t2 (report) → t3 (command line); each depends on the previous.
- The `claims-dev` glossary and reviewer target invoices/claims code; the ledger is not invoices code, so their naming rules are not imposed by this story.

## 7. Technical Design (deferred to STRUCTURE)

Module layout inside `src/ledger/`, the argument-parsing mechanism, how line numbers are tracked through the CSV reader, and the PR-level breakdown are for the STRUCTURE stage. Product-imposed constraints it must honour: stdlib only; `Decimal` end to end with one `ROUND_HALF_EVEN` rounding per figure; the public names `parse_csv`, `parse_lines`, `Transaction`, `LedgerError`, `monthly_report`, `CategoryTotal`, `RATES` and `to_dict()` named in §5; `python -m ledger` as the entry point; exit codes 0 / 2 / 3.

## 8. Open Questions

**Q1 (P0, blocking) — CHANGELOG entry vs. "no changes to any existing file".** The repository's layout gate requires every pull request to add a line under `## Unreleased` in `CHANGELOG.md` (a `PLAY-G4` blocker otherwise), but the story puts "changes to any existing file of the repository" out of scope, and `CHANGELOG.md` already exists. The gate cannot be waived. Options: (a) narrow the exclusion to "changes to any existing file of the repository other than one line under `## Unreleased` in `CHANGELOG.md`"; (b) keep the exclusion and change the gate rule in the repository first, in a separate change. *Recommendation:* (a) — it is a one-line addition every earlier story in this repository has made (PLAY-114/156/172/175), and (b) would block this story on a change outside it. *Working assumption until answered:* (a).

**Q2 (P1) — A FILE that is not valid UTF-8.** The story says what happens when FILE cannot be opened (exit 2) and when a row is bad (exit 3), but not when the bytes are not UTF-8. Options: (a) treat it like an unreadable file — exit 2, nothing on stdout, a message on stderr; (b) treat it as a data error — exit 3 with `error: {FILE}:{line}: ...`. *Recommendation:* (a): the file cannot be read as a ledger at all, and no line number would be reliable. *Working assumption:* (a).

**Q3 (P2) — Field-count message with extra columns.** Criterion 5's example `expected 6 fields, got 5` assumes a six-column header; criterion 2 allows extra columns. *Working assumption:* the expected number is the header's column count (e.g. `expected 7 fields, got 6` for a seven-column header).
