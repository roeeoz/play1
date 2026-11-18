# Feature Specification Document: Monthly expense report from a CSV ledger (SCRUM-4)

## 1. Feature Overview
- **Summary:** a new, stdlib-only Python package `ledger` in the play1 repository. It parses a UTF-8 CSV ledger, builds a deterministic monthly report by category in a chosen base currency, and exposes the report as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- **Problem statement:** a developer who keeps a ledger as a CSV file has no quick, reliable way to see a month's income, expenses and largest categories from the terminal. Spreadsheet totals can quietly include a malformed row and come out wrong. The developer wants an exact total, or an error that points to the offending line.
- **Target users / actors:** a developer who keeps a personal or small-team ledger as a CSV file and works from the terminal. The library functions (`parse_csv`, `parse_lines`, `monthly_report`) are also a product surface for developers who script against them.

## 2. Goals & Non-Goals
### Story context
The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals
- Read a CSV ledger, matching columns by name, and reject the first bad row with its physical line number and an exact reason.
- For one month, total income, expense, net and each category in a base currency (ILS, USD or EUR) at fixed rates, with exact decimal arithmetic and a single rounding to two places, half to even.
- List categories by absolute total descending, ties by name, with an optional top-N limit.
- Offer the report from the terminal as an exact text report or as JSON with amounts as strings, using distinct exit codes: 0 for success, 2 for usage errors, 3 for data errors.

### Non-Goals
- File formats other than CSV.
- Live or fetched exchange rates, and currencies other than ILS, USD and EUR.
- Persistent configuration.
- Charts or any graphical output.
- Any third-party dependency.
- Changes to any existing file in the repository, including `CHANGELOG.md`, `pyproject.toml`, the README and existing tests.
- Reports over several months, or ranges other than a single `YYYY-MM` month.

## 3. Functional Requirements
- **FR1 — Ledger input (R1).**
  - A ledger is UTF-8 text, optionally starting with a BOM.
  - Its header row names `id`, `date`, `amount`, `currency`, `category` and `memo` in any order. Extra columns are ignored.
  - Fields are trimmed of surrounding whitespace.
  - Blank and whitespace-only lines are skipped but still count toward line numbers.
  - Standard CSV quoting is honored, so a memo may contain a comma.
  - Two entry points behave identically: one takes a file path (`parse_csv`), the other any iterable of lines (`parse_lines`).
  - Rows are returned in file order as immutable transactions with `id`, `date`, `amount` (exact Decimal, as written), `currency`, `category` and `memo` (possibly empty).
  - A file with a header and no data rows yields an empty list.
- **FR2 — Row validation (R2).**
  - Parsing stops at the first bad row. It raises a ledger data error that carries the physical line number (the header is line 1) and an exact reason, rendered as `line {line}: {reason}`.
  - The reasons are the exact strings listed in Scenarios 5–7. They cover:
    - a malformed date and an impossible calendar date
    - a non-numeric amount (including NaN and Infinity), an amount with more than 2 decimals, and a zero amount
    - an unknown currency (case-sensitive)
    - an empty category and an empty id
    - a field count that does not match the header
    - a duplicate id, which names the first line
    - missing header columns, listed in canonical order
    - a missing header (empty file)
- **FR3 — Monthly report (R3).**
  - The report takes the transactions, a month `YYYY-MM`, a base currency (default ILS), optional rates (default: the fixed module rates) and an optional `top` (default all).
  - It reports `month`, `base`, `count`, `income` (sum of positive converted amounts), `expense` (sum of negative), `net`, and `categories` as (name, total, count).
  - Categories are ordered by absolute total descending, ties by name ascending, and cut to `top` when given. The headline figures always cover the whole month.
  - A month with no transactions is a zero report, not an error.
  - The report converts to a plain dictionary, with amounts as two-decimal strings.
- **FR4 — Currency conversion and rounding (R4).**
  - Each amount is converted as `amount × RATES[currency] ÷ RATES[base]` at full precision.
  - Each figure is summed exactly, then rounded once to two places with ROUND_HALF_EVEN. Figures are rounded independently and need not add up.
  - The fixed rates are ILS 1, USD 3.70 and EUR 4.00, in ILS per unit.
- **FR5 — Caller errors.** A bad month, a base that is not in the rates, or a `top` below 1 is a caller error (`ValueError`), kept distinct from ledger data errors.
- **FR6 — Command line (R5).**
  - The command is `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
  - Text output is exactly the line layout of Scenario 19, or `categories: none` for an empty month.
  - JSON output is the report dictionary.
  - On usage errors (Scenario 22), including a FILE that cannot be opened, the command exits 2 with nothing on stdout and a message on stderr.
  - On a data error it exits 3 with nothing on stdout, and stderr is exactly `error: {FILE}:{line}: {reason}` plus a newline, with FILE as typed.
  - `--help` documents `--month` and exits 0.
- **Edge cases covered:** the BOM, blank lines, quoted memos, header-only files, empty files, reordered and extra columns, duplicate ids across blank lines, top-N larger than the number of categories, ties, empty months, out-of-month rows and caller-supplied rates.

## 4. User Experience & Behavior
- **Primary flow:**
  1. The developer runs `python -m ledger report ledger.csv --month 2026-03`.
  2. A 13-line plain-text report appears: `month`, `base`, `transactions`, `income`, `expense`, `net`, then `categories:` and one two-space-indented `name: total (count)` line per category.
  3. The command exits 0 with nothing on stderr.
- **JSON flow:** adding `--json` prints one JSON object whose amounts are strings with two decimals, so it is safe for scripts.
- **Base and top:**
  - `--base USD` or `--base EUR` restates every figure in that currency.
  - `--top N` shows only the N largest categories. The headline figures are unchanged.
- **Empty month:** the report shows zeros (`0.00`) and `categories: none`, and exits 0.
- **Bad data:**
  - Nothing appears on stdout.
  - stderr shows `error: <FILE as typed>:<line>: <reason>`, for example `error: tests/fixtures/ledger/bad_amount.csv:3: amount '-2.505' has more than 2 decimal places`.
  - The command exits 3.
  - No partial or wrong total is ever printed.
- **Misuse:**
  - The cases are: no subcommand, a missing or invalid `--month`, `--top 0`, an unsupported `--base`, or a FILE that cannot be opened.
  - Nothing appears on stdout, a message appears on stderr, and the command exits 2.
- **Output qualities:**
  - Output is deterministic: the same input always gives byte-identical output.
  - Every amount has exactly two decimal places.
  - No floats appear anywhere in the output.

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
- **Traces to:** R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line), steps 1–8, and risks RK1 and RK2. Priority: Must. Size: M (≈5). Blockers: none.
- **Work items:** three dependent items, delivered in order. Each builds on the previous one.
  - t1: model and parser
  - t2: monthly report
  - t3: command line
- **Repository:** play1, target branch `main`.
  - The pre-conditions are confirmed: the manifest discovers packages under `src/`, pytest's `testpaths` is `tests`, and the test gate installs the package in editable mode and then runs `pytest`.
  - No `src/ledger/` or `tests/test_ledger_*.py` exists yet.
- **Python versions:** the package must work on the repository's supported Python, `>=3.10`. CI runs 3.12.
- **No new dependencies.** Only the standard library is used.
- **Existing files stay untouched.** The change adds files only under `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`. The story folder is written by the platform.
- **Exchange rates are fixed product constants** and are never fetched.
- **Merging:** a person reviews and merges the pull request after its required checks are green. The factory never merges.

## 7. Technical Design (deferred to STRUCTURE)
The tech lead decides the following in STRUCTURE:
- the module layout inside `ledger`
- the shape of the `Transaction`, `CategoryTotal` and report types beyond the names and fields the criteria fix
- how the command line is built, beyond the observable behavior
- fixture contents beyond those the criteria describe
- test organization per work item

The product imposes these constraints:
- Decimal end to end, with no floats.
- A single rounding step, ROUND_HALF_EVEN.
- Exact stderr and stdout text.
- Exit codes 0, 2 and 3.
- CLI tests through a subprocess against the installed package.
- Python 3.10-compatible standard library only.

## 8. Open Questions (if any remain)
None of these block the work. Each has a working assumption, listed in order of importance.
1. **CHANGELOG.** Earlier stories in this repo added a `CHANGELOG.md` line, but this story forbids changes to existing files. *Working assumption:* leave `CHANGELOG.md` untouched. Changing that would require changing the story's scope.
2. **Field-count message when the header has more than six columns.** *Working assumption:* "expected N" is the header's column count. That gives exactly `expected 6 fields, got 5` for a six-column header.
3. **Line reported for a row whose quoted memo spans several physical lines.** *Working assumption:* the line where the row starts.
4. **A ledger file that is not valid UTF-8.** *Working assumption:* a data error (exit 3), not a usage error.
5. **A header with a duplicated column name, and an id or category made only of whitespace.** *Working assumption:*
   - A whitespace-only id or category is empty after trimming, so it reports `empty id` or `empty category`.
   - A duplicated header column is left to STRUCTURE, as a header data error on line 1.
