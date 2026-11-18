# Feature Specification Document — Monthly expense report from a CSV ledger

## 1. Feature Overview

**Summary.** A new, standard-library-only Python package `ledger` that reads a CSV ledger, validates every row, and prints a one-month report — income, expense, net and per-category totals — in a chosen base currency, from the terminal: `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has no quick, deterministic way to see a month's totals without opening a spreadsheet, and a malformed row silently produces a wrong total instead of being pointed at.

**Target users / actors.** A developer who keeps a personal or small-team ledger as a CSV file and wants a monthly summary from the terminal (persona from the story). Secondary consumer: scripts reading the `--json` output, and Python callers of the library functions (`parse_csv`, `parse_lines`, `monthly_report`).

**User story.** As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

Priority: Must · Size: M (≈5) · Traces to: R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line) · steps 1–8 · RK1, RK2 · Blockers: none.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals

- G1 — Parse a UTF-8 CSV ledger into ordered, immutable transactions, matching columns by header name (R1).
- G2 — Reject the first invalid row with its physical line number and an exact, human-readable reason, so no wrong total is ever produced (R2).
- G3 — Build a deterministic one-month report: count, income, expense, net and per-category totals ordered by size, optionally limited to the top N (R3).
- G4 — Express every figure in a chosen base currency (ILS, USD or EUR) at fixed rates, with exact decimal arithmetic and one half-to-even rounding per figure after summing (R4).
- G5 — Expose it all as `python -m ledger report`, with a text and a JSON output and distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals

- Other file formats (anything but CSV).
- Live or fetched exchange rates; rates other than the fixed table (except as a library parameter, Scenario 17).
- Persistent configuration (config files, saved defaults).
- Charts or any graphical output.
- Any third-party dependency for the `ledger` package.
- Changes to any existing file of the repository (including `pyproject.toml`, existing tests, fixtures, CI).
- Reports over more than one month, date ranges, or currencies beyond ILS, USD and EUR.

## 3. Functional Requirements

### Work item t1 — model and CSV parsing (R1, R2)

- **FR1 — Transaction.** A frozen dataclass `Transaction` with `id` (str), `date` (`datetime.date`), `amount` (`Decimal`, exactly the text's value), `currency` (str), `category` (str), `memo` (str, possibly empty).
- **FR2 — Two entry points.** `parse_lines(lines)` accepts any iterable of text lines; `parse_csv(path)` opens the file with encoding `utf-8-sig` and `newline=""` and delegates to `parse_lines`. Both return a list of transactions in file order.
- **FR3 — Header.** The first line is the header. Columns are matched by name in any order; columns beyond the six named ones are ignored. Missing columns → `LedgerError(1, "missing column(s): …")` listing the missing names in canonical order `id, date, amount, currency, category, memo`; an empty file → `LedgerError(1, "missing header")`. A header-only file returns `[]`.
- **FR4 — Tolerances.** A UTF-8 BOM and blank or whitespace-only lines are ignored (but still counted as physical lines). Fields are trimmed of surrounding spaces. Standard CSV quoting is honoured (a quoted memo may contain a comma).
- **FR5 — Row validation.** Parsing stops at the first bad row, raising `LedgerError` with `line` (physical line number; header = 1; blank lines count) and `reason`; `str(error)` is `line {line}: {reason}`. Reasons are exactly those listed in Scenario 5 and Scenario 6 (date format, calendar date, non-numeric amount including `NaN`/`Infinity`, more than two decimal places, zero amount, unknown currency compared case-sensitively, empty category, empty id, field-count mismatch, duplicate id).

### Work item t2 — monthly report (R3, R4)

- **FR6 — `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.** Selects the transactions dated in `month` (`YYYY-MM`) and returns a report with `month`, `base`, `count`, `income`, `expense`, `net` and `categories` (list of `CategoryTotal(name, total, count)`).
- **FR7 — Conversion.** Each amount is converted as `amount × RATES[currency] ÷ RATES[base]` at full Decimal precision before summing. `RATES` is a module constant: `ILS` → `Decimal("1")`, `USD` → `Decimal("3.70")`, `EUR` → `Decimal("4.00")`. Rates may be passed as a parameter.
- **FR8 — Rounding.** Every figure (`income`, `expense`, `net`, each category total) is the exact sum quantized once to two places with `ROUND_HALF_EVEN`, independently of the others; figures always carry two decimal places.
- **FR9 — Ordering and top-N.** Categories are ordered by absolute total descending, ties by name ascending. `top=N` keeps the first N categories only; totals and count always cover all the month's transactions. `top=None` keeps all.
- **FR10 — Empty month.** A month with no transactions yields a zero report (count 0, figures `0.00`, no categories).
- **FR11 — Serialization.** `report.to_dict()` returns `month`, `base`, `count`, `income`, `expense`, `net`, `categories` with amounts as strings (two places) and categories as objects `{name, total, count}`.
- **FR12 — Caller errors.** Invalid `month`, a `base` not in `rates`, or `top < 1` raise `ValueError`, never `LedgerError`.

### Work item t3 — command line (R5)

- **FR13 — Command.** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`; `--base` defaults to ILS; `--top` accepts integers ≥ 1; `--help` documents `--month`.
- **FR14 — Text output** (default): exactly the lines shown in Scenario 19 and Scenario 21 (`categories: none` for an empty month).
- **FR15 — JSON output** (`--json`): the `to_dict()` object, amounts as strings.
- **FR16 — Exit codes.** 0 on success (nothing on stderr); 2 on usage errors, including a FILE that cannot be opened (nothing on stdout, a message on stderr); 3 on a data error (nothing on stdout, stderr exactly `error: {FILE}:{line}: {reason}` and a newline, FILE as given).

## 4. User Experience & Behavior

**Key flow.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a plain-text summary: month, base, transaction count, income, expense, net, then categories largest first, each indented two spaces as `name: total (count)`. Adding `--base USD` re-expresses every figure in USD; `--top N` shortens the category list; `--json` gives a machine-readable object with amounts as strings.

**States.** Success (exit 0, report on stdout, stderr empty) · usage error (exit 2, stdout empty, message on stderr) · data error (exit 3, stdout empty, one line `error: FILE:LINE: reason` on stderr). Output is fully deterministic: the same file and arguments always print the same bytes.

**Output format qualities.** Every amount always shows exactly two decimal places (`5.00`, `-2.00`, `0.00`); expenses keep their minus sign; an empty month prints `categories: none`; JSON amounts are strings so no precision is lost.

**Error messages the user sees** (data errors, prefixed `error: FILE:LINE: `): `date '2026-3-1' is not YYYY-MM-DD`, `date '2026-02-30' is not a calendar date`, `amount 'abc' is not a number`, `amount '1.505' has more than 2 decimal places`, `amount must not be zero`, `unknown currency 'usd'`, `empty category`, `empty id`, `expected 6 fields, got 5`, `duplicate id 't1' (first seen on line 2)`, `missing column(s): …`, `missing header`. Line numbers are physical lines of the file as the user sees it in an editor (header = 1, blank lines counted).

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

- **Repository preconditions — verified on `main` at `b7b5d0a`.** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest `testpaths = ["tests"]`; the CI gate `.github/workflows/ci.yml` runs `pip install -e ".[test]"` then `pytest` on Python 3.12; `src/` holds only `guestbook` and `testbed_utils`, and no `src/ledger/`, `tests/test_ledger_*.py` or `tests/fixtures/ledger/` exist yet. A new package under `src/` is therefore picked up without editing any existing file.
- **No existing file changes.** The package, its tests and the fixtures under `tests/fixtures/ledger/` are all new files.
- **Stdlib only** for the `ledger` package (the repository's existing dependencies `pypdf` and `flask` are unrelated and untouched).
- **Fixed rates**, never fetched: ILS 1, USD 3.70, EUR 4.00 (ILS per unit).
- **Delivery order.** t1 (parsing) → t2 (report, uses t1's `Transaction`) → t3 (CLI, uses both). The sample fixture's rows must reproduce every figure Scenarios 9, 10, 13, 16, 19 and 20 state; the story fixes the totals, not the individual rows, so the fixture's currencies are chosen to match them (e.g. a freelance row of 250.00 USD gives 925.00 ILS and 250.00 USD).

## 7. Technical Design (deferred to STRUCTURE)

Module layout inside `src/ledger/`, the CSV reading strategy (how physical line numbers are tracked through quoted fields), argument parsing, mapping exceptions to exit codes, and the test organisation are for the STRUCTURE stage. Product constraints it must honour: the public names `Transaction`, `LedgerError(line, reason)`, `parse_lines`, `parse_csv`, `monthly_report`, `CategoryTotal`, `RATES`, `report.to_dict()`; `Decimal` end to end; the exact messages, output lines and exit codes in §5; and CLI tests that go through `[sys.executable, "-m", "ledger", ...]`.

## 8. Open Questions

None blocking. Residual points left to STRUCTURE, recorded as assumptions rather than requirements:

- **A1 — Undecodable or unreadable content.** The story does not say what happens to a file that is not valid UTF-8. Assumption: it is reported like any other problem the user must fix, without a traceback; the exact message and exit code (2 or 3) are STRUCTURE's call. Risk: low — not in any criterion.
- **A2 — Header-level errors on the CLI.** `missing header` / `missing column(s)` are `LedgerError`s; by Scenario 23's rule they print `error: FILE:1: …` and exit 3. Assumption only; not separately criterion-tested.
- **A3 — Field-count message with extra columns.** Scenario 5's `expected 6 fields, got 5` is the six-column case; with extra header columns the expected count is assumed to be the header's own field count.
