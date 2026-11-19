# Feature Specification Document — Monthly expense report from a CSV ledger (DRAFT, not ready)

> Status: NOT_READY — one blocking question (Open Question Q1): the story's
> "no changes to any existing file" boundary collides with the play1 pull-request
> gate, which requires a `CHANGELOG.md` entry. Everything else below is taken from
> the published story and is settled.

## 1. Feature Overview

- **What is built:** a new stdlib-only Python package `ledger` (under `src/`, tests
  under `tests/`) that parses a CSV ledger, builds a monthly report by category in a
  chosen base currency, and exposes it as `python -m ledger report`.
- **Problem:** a developer keeping a ledger as a CSV file has no deterministic,
  terminal-only way to see a month's income, expenses and largest categories; a
  spreadsheet is heavy, and a silently malformed row produces a wrong total.
- **Target user:** a developer who keeps a personal or small-team ledger as a CSV
  file and wants a monthly summary from the terminal.

## 2. Goals & Non-Goals
### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals
- Parse a UTF-8 CSV ledger into ordered, validated transactions (R1, R2).
- Reject a bad row with its physical line number and an exact reason, never a wrong total (R2).
- Total one month by category in ILS, USD or EUR at fixed rates, rounding once after summing, half to even (R3, R4).
- Offer the report from the terminal as text or JSON, with documented exit codes 0 / 2 / 3 (R5).

### Non-Goals
- Other file formats; live or fetched exchange rates; persistent configuration; charts.
- Any third-party dependency.
- Changes to any existing file of the repository (see Q1 — collides with the PR gate).

## 3. Functional Requirements

- **FR1 — Parsing (R1, t1).** `parse_lines(lines)` takes any iterable of text lines; `parse_csv(path)` opens the file as `utf-8-sig` with `newline=""` and delegates. Output: a list of frozen `Transaction(id, date, amount, currency, category, memo)` in file order. Columns are matched by header name in any order; extra columns are ignored; fields are trimmed; BOM and blank/whitespace-only lines are ignored; quoted fields keep commas; a header-only file yields `[]`.
- **FR2 — Validation (R2, t1).** The first bad row raises `LedgerError(line, reason)`, `str()` = `line {line}: {reason}`, `line` = physical line (header = 1, blank lines count). Exact reasons as listed in criteria 5–7 (date format, calendar date, non-number incl. NaN/Infinity, > 2 decimals, zero, unknown currency case-sensitive, empty category, empty id, field count, duplicate id with first line, missing columns in canonical order, missing header).
- **FR3 — Monthly report (R3, t2).** `monthly_report(transactions, month, base="ILS", rates=RATES, top=None)` keeps only the month's transactions and returns `month`, `base`, `count`, `income`, `expense`, `net` and `categories` (`CategoryTotal(name, total, count)`), ordered by absolute total descending, ties by name ascending; `top` truncates categories only; `to_dict()` renders amounts as strings.
- **FR4 — Conversion and rounding (R4, t2).** `amount × rates[currency] ÷ rates[base]` at full precision, summed, then each figure quantized independently to two places with `ROUND_HALF_EVEN`; always two places. `RATES` = ILS 1, USD 3.70, EUR 4.00; `rates` is a parameter.
- **FR5 — Argument errors (t2).** Bad `month` (not `YYYY-MM` with 01–12), `base` not in `rates`, `top` < 1 → `ValueError`, never `LedgerError`.
- **FR6 — Command line (R5, t3).** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N≥1] [--json]`. Exit 0 with the report on stdout; exit 2 for usage errors and an unopenable FILE (nothing on stdout); exit 3 for a data error with stderr exactly `error: {FILE}:{line}: {reason}`.
- **Edge cases:** empty month → zero report (`categories: none` in text); only the month's rows count; rounding never forced to add up.

## 4. User Experience & Behavior

- **Flow:** the developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a fixed 7-line summary followed by one indented line per category (`  name: total (count)`), or the same data as one JSON object with `--json`.
- **Output format (checkable):** labels `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, `categories:`; amounts always two decimal places; an empty month prints `categories: none`. JSON amounts are strings so no precision is lost.
- **Errors the user sees:** usage problems → argparse-style message on stderr, exit 2; a bad ledger row → `error: <FILE as typed>:<line>: <reason>`, exit 3; stdout stays empty on any error.
- **Determinism:** the same file and arguments always give byte-identical output; no network access.
- `--help` documents `--month`.

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

- **Repository pre-conditions (verified):** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets `testpaths = ["tests"]`; CI (`.github/workflows/ci.yml`, job `test`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12; no `src/ledger/` and no `tests/test_ledger_*.py` exist. A new package under `src/` is picked up without editing `pyproject.toml`.
- **PR gate (`.factory/plugins/claims-dev/skills/repo-gate`):** Python under `src/`, tests under `tests/`, no file > 200 KB, and **rule 4 / PLAY-G4: the PR must add a line under `## Unreleased` in `CHANGELOG.md`** — an existing file. This collides with the story's "no changes to any existing file" (Q1).
- **Test gate (`.factory/testing.md`):** tests import only through the installed package — no `conftest.py`, no `sys.path` manipulation (matches criterion 25).
- Stdlib only; no network; fixed rates.
- The repository's claims glossary (invoice, credit note, billing period) applies to invoice/claims code and is not taken to rename this ledger's terms.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, class shapes beyond those the criteria name, how argparse maps errors to exit 2, and the split into the three work items (t1 → t2 → t3) are for STRUCTURE.

## 8. Open Questions

- **Q1 (P0, blocking) — CHANGELOG vs. "no changes to any existing file".** The play1 PR gate rule PLAY-G4 fails any pull request that does not add a line under `## Unreleased` in `CHANGELOG.md`, and that file already exists. Options: (a) narrow the story's boundary to "no changes to any existing file except one line under `## Unreleased` in `CHANGELOG.md`", and add a scope-boundary criterion: the PR touches no other existing file and the existing pytest suite still passes unchanged; (b) keep the boundary and change the gate rule in the repository first, in a separate change. Recommendation: (a) — it is the only option this story can deliver on its own, and the CHANGELOG line is documentation, not a behaviour change; the added criterion also gives the story the regression/scope-boundary scenario the Definition of Ready asks for.
- **Q2 (P2) — Size label.** The story reads "M (≈5)"; on the story template's scale M is ≈3 points and L is ≈5. Working assumption: L (≈5 points); it does not change the scope.
