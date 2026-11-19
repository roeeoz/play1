# Feature Specification Document — Monthly expense report from a CSV ledger (DRAFT — not ready)

## 1. Feature Overview

> **Status: draft, NOT READY.** One blocking question is still open (§8, Q1): the story rules out changing any existing file, but the play1 layout gate fails any pull request that does not add a line to `CHANGELOG.md` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4, `PLAY-G4`). Everything else below is taken from the story as published.

- **What is being built:** a new stdlib-only Python package `ledger` (under `src/`, tests under `tests/`) that reads a CSV ledger, validates every row, and prints a deterministic monthly report (income, expense, net, totals per category) in a chosen base currency, through `python -m ledger report`.
- **Problem:** a developer who keeps a personal or small-team ledger as a CSV file has no way to get a monthly summary from the terminal without opening a spreadsheet. When a row is malformed, a tool must point at that row by line number instead of producing a silently wrong total.
- **Target user:** a developer who keeps a personal or small-team CSV ledger and works from the terminal. Secondary consumer: a script or another program that reads the `--json` output, or imports the package's `parse_csv` / `parse_lines` / `monthly_report` functions.
- **Delivery shape (from the story):** three dependent work items: t1 model and CSV parser (R1, R2), t2 monthly report (R3, R4), t3 command line (R5). Traces to R1–R5, steps 1–8, risks RK1, RK2. Priority Must, size M (≈5), no blockers stated.

## 2. Goals & Non-Goals
### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals

- G1 — Parse a UTF-8 CSV ledger (header by name, any column order) into validated transactions, in file order.
- G2 — Reject the first bad row with its physical line number and an exact, human-readable reason, so a wrong total is never produced.
- G3 — Total one calendar month by category in a base currency (ILS, USD or EUR, default ILS), with income, expense, net, transaction count and categories ordered by absolute total, optionally limited to the top N.
- G4 — Deterministic money: `Decimal` end to end, fixed rates, one `ROUND_HALF_EVEN` rounding per figure after summing, always two decimal places.
- G5 — A terminal command `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]` with a fixed text format, a lossless JSON format, and distinct exit codes for usage (2) and data (3) errors.

### Non-Goals

- Any file format other than CSV; live or fetched exchange rates; persistent configuration; charts.
- Any third-party dependency (the package is stdlib-only).
- Changes to any existing file of the repository — **as published; collides with the repository's CHANGELOG gate, see §8 Q1**.
- Reports spanning more than one month, date ranges, or currencies beyond ILS/USD/EUR.
- Writing or editing the ledger file.

## 3. Functional Requirements

**Parsing and validation (t1 — R1, R2)**

- FR1 — Input: a UTF-8 CSV ledger, optionally with a BOM, whose header names `id`, `date`, `amount`, `currency`, `category`, `memo` in any order; extra columns are ignored. Two entry points: `parse_csv(path)` and `parse_lines(lines)` (any iterable of lines), which behave identically.
- FR2 — Output: a list of `Transaction` values in file order — frozen, with `id` (str), `date` (`datetime.date`), `amount` (`Decimal`, exactly as written), `currency`, `category`, `memo` (str, possibly empty). Fields are trimmed; blank and whitespace-only lines are skipped; quoted fields keep embedded commas.
- FR3 — Validation, first bad row stops parsing with `LedgerError(line, reason)`; `line` is the physical line (header = 1, blank lines count); `str(error)` is `line {line}: {reason}`. Reasons are the exact texts in AC 5–7: date format, calendar date, non-number amount (incl. `NaN`/`Infinity`), more than two decimals, zero amount, unknown currency (case-sensitive), empty category, empty id, field-count mismatch, duplicate id, missing columns (canonical order), missing header.
- FR4 — A header-only file yields an empty list.

**Monthly report (t2 — R3, R4)**

- FR5 — `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` keeps only the transactions dated in `month` (`YYYY-MM`).
- FR6 — Conversion: `amount × rates[currency] ÷ rates[base]` at full precision before summing; `RATES` = ILS 1, USD 3.70, EUR 4.00 (ILS per unit); rates may be passed in.
- FR7 — Figures: `income` (sum of positives), `expense` (sum of negatives), `net`, and per category `CategoryTotal(name, total, count)`; each the exact sum quantized once to two places with `ROUND_HALF_EVEN`, independently (they need not add up).
- FR8 — Categories ordered by absolute total descending, ties by name ascending; `top` keeps the first N categories only, while the month totals and `count` still cover every transaction of the month.
- FR9 — An empty month is a zero report, not an error; `to_dict()` gives the JSON-ready form with amounts as strings.
- FR10 — Caller errors (`month` not `YYYY-MM` with month 01–12, `base` not in `rates`, `top` < 1) raise `ValueError`, never `LedgerError`.

**Command line (t3 — R5)**

- FR11 — `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`; `--base` defaults to ILS; `--top` is an integer ≥ 1.
- FR12 — Success: exit 0, report on stdout (text format of AC 19/21, or JSON of AC 20), nothing on stderr.
- FR13 — Usage errors (no subcommand, missing `--month`, invalid `--month`/`--top`/`--base`, a FILE that cannot be opened): exit 2, nothing on stdout, a message on stderr.
- FR14 — Data errors (a `LedgerError`): exit 3, nothing on stdout, stderr exactly `error: {FILE}:{line}: {reason}` + newline, FILE as given.
- FR15 — `python -m ledger report --help` exits 0 and documents `--month`.

## 4. User Experience & Behavior

- **Main flow:** the developer runs `python -m ledger report ledger.csv --month 2026-03` and reads thirteen-or-so plain lines: `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, `categories:`, then one two-space-indented `name: total (count)` line per category in report order. An empty month prints `categories: none` and zero figures.
- **Machine flow:** adding `--json` prints one JSON object with `month`, `base`, `count`, `income`, `expense`, `net`, `categories` (`name`, `total`, `count`); amounts are strings so no precision is lost.
- **Bad data:** the user sees exactly one line on stderr, `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`, exit code 3, and no partial report on stdout.
- **Bad usage:** a message on stderr, exit code 2, nothing on stdout.
- **Look and feel:** plain text, no colour, no tables, no charts; every amount always shows exactly two decimal places (`5.00`, `-2.00`). Output is deterministic: the same file and arguments always print the same bytes.

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

- **Target repository rules (play1, base branch `main`):**
  - Layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): Python source under `src/`, tests under `tests/` (the story complies); no file over 200 KB (fixtures are tiny); **rule 4 / `PLAY-G4` — every pull request must add a line under `## Unreleased` in `CHANGELOG.md`, otherwise a blocker.** The story's "no changes to any existing file" collides with this rule — see §8 Q1.
  - Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`): `pip install -e ".[test]"` then `pytest` on Python 3.12; no `conftest.py`, no `sys.path` manipulation. The story's AC 25 and its pre-conditions match this.
  - `pyproject.toml` already discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets `testpaths = ["tests"]`, so `python -m ledger` needs no manifest change; `src/ledger/` and `tests/test_ledger_*.py` do not exist yet (verified on `main` at `b7b5d0a`).
- **Product constraints:** stdlib only; fixed exchange rates, never fetched; `Decimal` money with one `ROUND_HALF_EVEN` rounding per figure.
- **Sibling stories / epic:** the epic PRD, backlog and Confluence research referenced by the publication note were not supplied to this turn; this spec relies on the story text alone (R1–R5, steps 1–8, RK1, RK2 are cited but not restated).

## 7. Technical Design (deferred to STRUCTURE)

Module layout, the CLI parser, how usage errors map to exit 2, the fixture contents that reproduce the AC 9/10/16/20 figures (e.g. freelance as 250.00 USD, consistent with 925.00 ILS), and the PR breakdown into t1/t2/t3 belong to STRUCTURE. Constraints the product imposes: exact error texts and output lines as in §5; the CLI tested only through `[sys.executable, "-m", "ledger", ...]`.

## 8. Open Questions

- **Q1 (P0, blocking) — CHANGELOG vs. "no changes to any existing file".** The play1 layout gate fails any PR that does not add a line under `## Unreleased` in `CHANGELOG.md` (rule 4, `PLAY-G4`); the story puts "changes to any existing file of the repository" out of scope. No exemption from the gate is possible. Options: (a) narrow the exclusion to "no changes to any existing file except one added line under `## Unreleased` in `CHANGELOG.md` describing the `ledger` package"; (b) keep the exclusion and change the gate rule in the repository first, in a separate change. *Recommendation: (a)* — it is the only option this story can deliver green on its own, and every earlier story in the repo (PLAY-156/172/175) did exactly this.
- **Q2 (P1) — non-UTF-8 file.** A FILE that opens but is not valid UTF-8 is not covered by AC 22 or 23. *Recommendation:* treat it as a file that cannot be read — exit 2, nothing on stdout, a message on stderr — since no line-level reason can be given; answer "exit 3 with a line number" if you prefer it reported as a data error.
- **Q3 (P2) — duplicate column names in the header** (e.g. two `amount` columns) are not specified; left to STRUCTURE unless you want a defined error.
