# Feature Specification Document: Monthly expense report from a CSV ledger

## 1. Feature Overview
- **What is being built:** a new, stdlib-only Python package called `ledger`, run from the terminal as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
  - It reads a CSV ledger.
  - It totals one month by category in a base currency.
  - It reports the month's income, expense, net and largest categories.
  - It is delivered in three dependent work items: t1 (model and CSV parser), t2 (monthly report) and t3 (command line).
- **Problem:** a developer who keeps a ledger as a CSV file has no quick, deterministic monthly summary without opening a spreadsheet. A bad row should be pointed at by its line number, not silently produce a wrong total.
- **Target user:** a developer who keeps a personal or small-team ledger as a CSV file and works from the terminal.

## 2. Goals & Non-Goals
### Story context
The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals
- Parse a UTF-8 CSV ledger into typed transactions.
  - Columns are matched by name, in any order.
  - Fields are stripped of surrounding spaces.
  - A BOM and blank lines are tolerated.
- Reject the first bad row with a precise, line-numbered reason, so the user never gets a wrong total.
- Produce a deterministic monthly report:
  - the month's transaction count, income, expense and net;
  - per-category totals in the chosen base currency, ordered by absolute total;
  - an optional top-N limit on the categories shown.
- Convert currencies at fixed rates, with exact Decimal arithmetic and a single half-to-even rounding of each figure after summing.
- Offer a command line with a text output and a JSON output, and distinct exit codes:
  - 0 for success;
  - 2 for a usage error;
  - 3 for a data error.

### Non-Goals
- Other file formats.
- Live or fetched exchange rates.
- Persistent configuration.
- Charts.
- Any third-party dependency.
- Changes to any existing file of the repository, including `pyproject.toml`. As a result there is no console script: `python -m ledger` is the only entry point.
- Glossary terms from the claims/invoice domain. They don't apply to this ledger.

## 3. Functional Requirements
### FR1: Transaction model (t1, R1)
A transaction is an immutable value with these fields:
- `id`: text.
- `date`: a calendar date.
- `amount`: an exact decimal that keeps the text's value, so `12000.00` stays `12000.00`.
- `currency`: text.
- `category`: text.
- `memo`: text, possibly empty.

### FR2: CSV parsing (t1, R1)
- Two entry points with identical behaviour:
  - `parse_lines(lines)` takes any iterable of lines.
  - `parse_csv(path)` opens the file as `utf-8-sig` with `newline=""` and delegates to `parse_lines`.
- Header handling:
  - Columns are matched by name, in any order.
  - Columns beyond the six named ones are ignored.
  - All fields are stripped.
- Tolerated input:
  - A UTF-8 BOM.
  - Blank and whitespace-only lines.
  - Quoted memos, including memos that contain commas.
  - An empty memo.
- A file with a header and no rows yields an empty list.

### FR3: Row validation (t1, R2)
- The first bad row stops parsing and raises `LedgerError(line, reason)`.
  - `line` is the physical line number: the header is line 1, and blank lines count.
  - `str(error)` is `line {line}: {reason}`.
- Each problem has an exact reason string:
  - bad date format;
  - a date that isn't a calendar date;
  - a non-numeric amount, including NaN and Infinity;
  - an amount with more than two decimal places;
  - a zero amount;
  - an unknown currency (compared case-sensitively);
  - an empty category;
  - an empty id;
  - a field-count mismatch;
  - a duplicate id;
  - missing columns;
  - a missing header.
- Section 5 gives each string verbatim.

### FR4: Monthly report (t2, R3)
- Call: `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.
- Only transactions dated in `month` count.
- The report holds `month`, `base`, `count`, `income`, `expense`, `net` and `categories`.
  - `categories` is a list of `CategoryTotal(name, total, count)`.
  - It is ordered by absolute total descending, with ties broken by name ascending.
- `top` limits only the categories list. The totals and the count always cover every transaction in the month.
- An empty month is a zero report.
- `to_dict()` gives a JSON-ready mapping in which amounts are strings.

### FR5: Currency conversion and rounding (t2, R4)
- `RATES` is ILS 1, USD 3.70, EUR 4.00, in ILS per unit.
- Each amount is converted as `amount × RATES[currency] ÷ RATES[base]` at full precision before summing.
- Every figure is quantized independently to two places with `ROUND_HALF_EVEN`, once, after summing. The figures are not forced to add up.
- Rates can be passed in as a parameter.

### FR6: Argument validation (t2)
`ValueError` is raised for:
- a malformed month;
- a `base` that isn't one of the rates' currencies;
- `top < 1`.

These are caller errors, never `LedgerError`.

### FR7: Command line (t3, R5)
- Command: `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- Defaults: `--base` is ILS. `--top` takes an integer of at least 1.
- Outputs: a 13-line text report, or a JSON object with `--json`. An empty month shows `categories: none`.
- Exit codes:
  - 0 for success;
  - 2 for a usage error (nothing on stdout, a message on stderr);
  - 3 for a data error (nothing on stdout; stderr is exactly `error: {FILE}:{line}: {reason}`).
- `--help` documents `--month`.

## 4. User Experience & Behavior
- **Main flow:**
  1. The user runs `python -m ledger report ledger.csv --month 2026-03`.
  2. They read the month, base, transaction count, income, expense, net, and a `categories:` block.
  3. In that block, each category is one line indented by two spaces, in the form `name: total (count)`.
- **Variants:**
  - `--base` changes the currency.
  - `--top N` shortens the category list.
  - `--json` emits a machine-readable object with amounts as strings, so no precision is lost.
- **Output format:**
  - Every amount always shows two decimal places, for example `5.00`, `-2.00` and `0.00`.
  - The output is deterministic: the same input always gives byte-identical output.
- **Errors the user sees:**
  - A bad row shows `error: {FILE}:{line}: {reason}` on stderr and exits 3. FILE is shown exactly as typed.
  - A wrong command line shows a usage message on stderr and exits 2.
  - In both cases nothing is printed on stdout.

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
- **Repository fit:** the target repository is `play1`, a Python src-layout project tested with pytest. Work is based on `main` (`b7b5d0a`).
  - The manifest already discovers packages under `src/`, and `testpaths` is `tests/`.
  - The test gate installs the package in editable mode (`pip install -e ".[test]"`) and then runs `pytest` on Python 3.12.
  - No `src/ledger/` package and no `tests/test_ledger_*.py` exist yet.
- **Files the story may add:** only `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`. It may not add a `conftest.py`, a `.gitattributes` or a console script, and may not edit `pyproject.toml`.
- **Dependencies:** none beyond the standard library. The project's existing dependencies are untouched.
- **Build order:** t1 comes first, then t2 (it builds on t1), then t3 (it builds on t2). Each work item's pull request must keep `pytest` green on its own.
- **Repository gate rule `PLAY-G4`:** it requires every pull request to add a line under `## Unreleased` in `CHANGELOG.md`, which collides with "no changes to any existing file". See section 8.
- **Merging:** a person merges each pull request after review. "Done" for each work item means its required checks are green.

## 7. Technical Design (deferred to STRUCTURE)
STRUCTURE owns the design: module layout, how the report and the command line are organised internally, the fixture contents, and how the error strings are produced. The product imposes these constraints:
- Money is Decimal end to end, with one `ROUND_HALF_EVEN` quantize per figure.
- The error strings and the stdout/stderr outputs are byte-exact, as in section 5.
- The command-line tests run the real `python -m ledger` in a subprocess.

## 8. Open Questions (if any remain)
- **Delivery risk: the CHANGELOG conflict with `PLAY-G4` is unresolved.** The story keeps "no changes to any existing file", per the developer's direction that the story text is the whole requirement. Every work item's pull request will therefore receive the `PLAY-G4` blocker. No waiver is available. The ways out are:
  - **(a)** Amend this story's scope so each pull request adds exactly one line under `## Unreleased` in `CHANGELOG.md`. This is recommended: it is the smallest change, and it matches every earlier story in the repository.
  - **(b)** Change `PLAY-G4` in the repository first, as a separate change.
- **Assumption: a quoted memo spanning several lines.** An error on such a row reports the line where the row starts, which is the simplest reading of "physical line number".
- **Assumption: a file that opens but can't be read as CSV.** If FILE isn't valid UTF-8 or has broken CSV quoting, it is treated as a data error: exit 3 with an `error: {FILE}:{line}: {reason}` message. Scenario 22's "cannot be opened" (exit 2) covers only a file that can't be opened at all.
- **Assumption: the contents of `sample.csv`.** Any nine rows matching Scenario 1's counts, dates and ids that reproduce the figures of Scenarios 9, 10, 13, 16, 19 and 20 are acceptable.
- **Left to STRUCTURE, within the exact strings of Scenario 5:**
  - whether `1.500` counts as having more than two decimal places;
  - whether a leading `+` or exponent notation is accepted;
  - which expected count the field-count message reports when the header has extra columns.
