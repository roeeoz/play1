# Feature Specification Document — Monthly expense report from a CSV ledger (SCRUM-12)

> Status: specification (intake READY_FOR_SPEC). The developer ruled that the story text and its acceptance criteria are the whole requirement, and that where they are silent the simplest reading applies and is recorded as an assumption (§8).

## 1. Feature Overview

**What is being built.** A new, standard-library-only Python package `ledger` (under `src/`, tests under `tests/`) that reads a CSV ledger, validates every row, and produces a monthly report — income, expense, net, transaction count and per-category totals — in a chosen base currency, available both as a Python API and as the command `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has to open a spreadsheet to see a month's totals, and a malformed row silently produces a wrong total. They want a deterministic summary from the terminal, and a bad row pointed at by its line number instead of a wrong figure.

**Target users / actors.** A developer keeping a personal or small-team CSV ledger, working from the terminal (and, for the API, from Python code).

**Delivery shape (from the story).** Three dependent work items: t1 — the model and CSV parser (R1, R2); t2 — the monthly report (R3, R4); t3 — the command line (R5). Traces to R1–R5, steps 1–8, risks RK1, RK2. Priority Must, size M (≈5).

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository other than the one `CHANGELOG.md` line under `## Unreleased` that the repository's pull-request gate requires.

### Goals

- Parse a UTF-8 CSV ledger (header-named columns in any order) into typed, immutable transactions, in file order.
- Reject the first invalid row with its physical line number and an exact, human-readable reason — never produce a total from bad data.
- Total one calendar month by category in a base currency (ILS, USD or EUR) using fixed rates and exact decimal arithmetic, rounded once with half-to-even.
- Expose the report from the terminal as a fixed text layout or as JSON, with distinct exit codes for success (0), usage errors (2) and data errors (3).

### Non-Goals

- Other file formats (anything but CSV).
- Live or fetched exchange rates.
- Persistent configuration.
- Charts or any graphical output.
- Any third-party dependency (runtime or for the package itself).
- Changes to any existing file of the repository, with one exception: a single line describing the new `ledger` command added under `## Unreleased` in `CHANGELOG.md`, which the repository's pull-request gate requires (assumption A1, §8).

## 3. Functional Requirements

**FR1 — Ledger input (R1).** Input is a UTF-8 CSV file (an optional UTF-8 BOM is ignored) whose first non-empty content is a header naming `id`, `date`, `amount`, `currency`, `category`, `memo` in any order; extra columns are ignored. Blank and whitespace-only lines are skipped but still count toward line numbers (header = line 1). Fields are trimmed; quoted fields keep embedded commas. Two entry points behave identically: `parse_csv(path)` (opens with `utf-8-sig`, `newline=""`) and `parse_lines(lines)` (any iterable of lines).

**FR2 — Transaction (R1).** Each valid row becomes a frozen `Transaction(id: str, date: datetime.date, amount: Decimal, currency: str, category: str, memo: str)`; the amount keeps the text's exact value (`12000.00` → `Decimal("12000.00")`); memo may be `""`. Output is a list in file order; header-only input yields `[]`.

**FR3 — Row validation (R2).** Parsing stops at the first bad row and raises `LedgerError(line, reason)`, `str()` = `line {line}: {reason}`, with the exact reasons listed in criteria 5–7 (bad date format, non-calendar date, non-number incl. NaN/Infinity, >2 decimals, zero, unknown currency — case-sensitive, empty category, empty id, wrong field count, duplicate id with first line, missing columns in canonical order, missing header).

**FR4 — Monthly report (R3).** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` keeps only transactions in `month` (`YYYY-MM`, month 01–12), and returns `month`, `base`, `count`, `income` (sum of positives), `expense` (sum of negatives), `net`, and `categories` — `CategoryTotal(name, total, count)` ordered by absolute total descending, ties by name ascending, truncated to `top` when given (totals and count always cover the whole month). `to_dict()` renders amounts as two-place strings.

**FR5 — Conversion and rounding (R4).** `RATES = {ILS: 1, USD: 3.70, EUR: 4.00}` (Decimal, ILS per unit). Each amount converts as `amount × RATES[currency] ÷ RATES[base]` at full precision; each figure is the exact sum quantized once to two places with `ROUND_HALF_EVEN`, independently (figures need not add up). Rates are a parameter.

**FR6 — Caller errors (R3).** Invalid `month`, a `base` not in `rates`, or `top < 1` raise `ValueError`, never `LedgerError`.

**FR7 — Command line (R5).** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR (default ILS)] [--top N≥1] [--json]`. Exit 0 with the report on stdout and nothing on stderr; exit 2 with nothing on stdout and a message on stderr for usage errors (no subcommand, missing/invalid `--month`, `--top 0`, unknown `--base`, unopenable FILE); exit 3 with nothing on stdout and `error: {FILE}:{line}: {reason}` on stderr for a ledger data error. `--help` exits 0 and documents `--month`.

**Edge cases covered:** BOM; blank lines; quoted memo; empty memo; header only; empty file; extra columns; empty month (zero report); out-of-month transactions excluded; ties; `top` larger than the category count; rounding of sub-cent conversions.

## 4. User Experience & Behavior

**Flow 1 — text report.** The developer runs `python -m ledger report ledger.csv --month 2026-03`. They see exactly: `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, `categories:` lines, then one line per category indented two spaces as `  name: total (count)`, in report order. Every amount always shows two decimal places (`5.00`, `-2.00`). An empty month prints `categories: none` with zero figures `0.00`.

**Flow 2 — JSON report.** Adding `--json` prints one JSON object (`month`, `base`, `count`, `income`, `expense`, `net`, `categories[{name,total,count}]`) with amounts as strings so no precision is lost — suitable for piping to other tools.

**Flow 3 — bad data.** If the file has an invalid row, nothing is printed on stdout; stderr shows one line `error: {FILE}:{line}: {reason}` (FILE as typed by the user, line the physical line in the file), and the exit code is 3. The developer can jump straight to the line.

**Flow 4 — usage mistakes.** A wrong command line (missing subcommand or `--month`, an invalid month, `--top 0`, unknown base, unopenable file) prints a message on stderr, nothing on stdout, and exits 2.

**Qualities.** Deterministic: the same file and arguments always produce byte-identical output. Terminal-only, plain text; no colours, charts or interactive prompts.

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

- **Repository fit (verified).** `pyproject.toml` discovers packages with `[tool.setuptools.packages.find] where = ["src"]` and sets pytest `testpaths = ["tests"]`; CI (`.github/workflows/ci.yml`, job `test`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12. A new `src/ledger/` is therefore found and installed without touching the manifest, and `python -m ledger` works from the installed package. No `src/ledger/` or `tests/test_ledger_*.py` exists yet; `tests/fixtures/` exists (other fixtures), `tests/fixtures/ledger/` does not.
- **Repository gate — changelog line.** The play1 layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4, id `PLAY-G4`) blocks any pull request whose diff does not add a line under `## Unreleased` in `CHANGELOG.md`. The gate cannot be waived per story, so the scope admits exactly that one added line (assumption A1, §8); no other existing file changes.
- **Gate rules met by design:** Python under `src/`, tests under `tests/` (rule 1); fixtures well under 200 KB (rule 3); no shell scripts (rule 2).
- **Stdlib only:** no new runtime or test dependency (pytest is already the test extra).
- **Fixed rates:** ILS 1, USD 3.70, EUR 4.00 — never fetched.
- **Merge:** a person merges the pull request after review; "done" is the pull request with its required checks green.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, how the CSV reader tracks physical line numbers through quoted fields, the CLI argument parser and its error mapping to exit codes, and test organisation across `tests/test_ledger_*.py` are for STRUCTURE. Product-imposed constraints: `Decimal` end to end; `parse_csv` opens with `utf-8-sig` and `newline=""`; CLI tests via `subprocess` with `sys.executable -m ledger`, no `sys.path` manipulation; sample fixture content must reproduce the exact totals of criteria 9, 10, 16, 19 and 20 (the story fixes the totals, not every row — e.g. the 2026-04-01 row's values are the fixture author's choice).

## 8. Open Questions (if any remain)

No blocking question remains. Per the developer's ruling, the points the story leaves silent are settled by the simplest reading and recorded here as assumptions, each with its risk:

- **A1 — `CHANGELOG.md` line (scope).** The story rules out changing any existing file, but the repository's gate (PLAY-G4) requires each pull request to add a line under `## Unreleased` in `CHANGELOG.md`, and the gate cannot be waived. Assumed: the exclusion admits exactly that one added line and nothing else. *Risk:* if the "no existing file" rule must hold literally, the gate rule has to be changed in the repository first, in a separate change, before this story's PR can pass.
- **A2 — field-count message with extra columns.** Criterion 5's example `expected 6 fields, got 5` reflects a six-column header; criterion 2 allows extra columns. Assumed: the expected count is the header's own field count (e.g. `expected 7 fields, got 6` for a seven-column header). *Risk:* low — the six-column example stays exact either way.
- **A3 — undecodable file on the CLI.** A FILE that opens but is not valid UTF-8 is not covered by criteria 22–23. Assumed: treated like a file that cannot be opened — exit 2, nothing on stdout, a message on stderr. *Risk:* low — no criterion's output changes.
- **Epic sources.** The epic's PRD, backlog and Confluence research were not supplied to this intake; per the developer, the story text and its criteria are the whole requirement (R1–R5, RK1, RK2 are cited from the story, not re-read).
