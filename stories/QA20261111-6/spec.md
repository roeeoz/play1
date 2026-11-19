# Feature Specification Document — Monthly expense report from a CSV ledger

## 1. Feature Overview

**What is being built.** A new, standard-library-only Python package `ledger` that reads a personal or small-team ledger kept as a UTF-8 CSV file, validates every row, and produces a deterministic monthly report — count, income, expense, net and per-category totals in a chosen base currency — usable as a library (`parse_csv` / `parse_lines` / `monthly_report`) and from the terminal (`python -m ledger report FILE --month YYYY-MM`).

**Problem.** A developer who keeps a ledger in CSV today has to open a spreadsheet to see what a month looked like. Spreadsheet arithmetic on floats and silently skipped bad rows produce a wrong total with no indication of why. The developer wants an exact (Decimal) total, a stable output, and — when the file is wrong — a pointer to the offending physical line rather than a plausible but wrong number.

**Target users / actors.**
- *Primary:* a developer keeping a personal or small-team ledger as CSV, working from the terminal.
- *Secondary:* a developer scripting against the library API or the `--json` output.

**Trace.** Requirements R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line); risks RK1, RK2. Priority Must, size M (≈5). Delivered in three dependent work items: t1 model and CSV parser → t2 monthly report → t3 command line.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals

- Parse a CSV ledger into ordered, immutable transactions, matching columns by name, and reject the first bad row with its physical line number and an exact reason (R1, R2).
- Report one calendar month: transaction count, income, expense, net, and per-category totals ordered by magnitude, optionally limited to the top N (R3).
- Convert every amount into a chosen base currency (ILS, USD, EUR) at fixed, overridable rates, with exact Decimal arithmetic and a single half-to-even rounding per figure (R4).
- Expose the report from the terminal as a fixed text layout or as lossless JSON, with distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals

- Any input format other than CSV; any output beyond the text and JSON layouts below (no charts).
- Live or fetched exchange rates; currencies beyond ILS, USD and EUR.
- Persistent configuration (config files, environment-based defaults).
- Any third-party runtime dependency.
- Changing any existing file of the repository (including `pyproject.toml`, existing packages and tests); no console-script entry point is added.
- Reporting periods other than a single calendar month; multi-month or year reports.
- Continuing past a bad row or reporting several bad rows at once.

## 3. Functional Requirements

**FR1 — Ledger input (R1).** A ledger is UTF-8 text (an optional BOM is ignored) in CSV form. The first non-empty line is the header; it must name `id`, `date`, `amount`, `currency`, `category`, `memo` in any order; extra columns are ignored. Fields are trimmed of surrounding whitespace; standard CSV quoting applies (a quoted memo may contain commas). Blank and whitespace-only lines are skipped but still count toward line numbers.

**FR2 — Transaction model (R1).** Each valid row becomes an immutable `Transaction` with `id` (str), `date` (`datetime.date`), `amount` (`Decimal`, exactly as written), `currency` (str), `category` (str), `memo` (str, may be empty). Transactions are returned in file order. A header-only file yields an empty list.

**FR3 — Entry points (R1).** `parse_lines(lines)` accepts any iterable of text lines; `parse_csv(path)` opens the file as UTF-8 with BOM tolerance and delegates to `parse_lines`, behaving identically.

**FR4 — Row validation (R2).** Parsing stops at the first invalid row and raises `LedgerError` carrying `line` (physical line number, header = 1, blank lines counted) and `reason`; its string form is `line {line}: {reason}`. The exact reasons are those listed in acceptance criteria 5–7 (bad date format, non-calendar date, non-numeric amount incl. NaN/Infinity, more than two decimals, zero amount, unknown or wrong-case currency, empty category, empty id, wrong field count, duplicate id, missing columns, missing header).

**FR5 — Monthly report (R3).** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` selects the transactions dated in `month` (`YYYY-MM`) and returns a report with `month`, `base`, `count`, `income` (sum of positive converted amounts), `expense` (sum of negative converted amounts), `net`, and `categories` — a list of `CategoryTotal(name, total, count)` ordered by absolute total descending, ties by name ascending, truncated to `top` when given. Totals and count cover all of the month's transactions regardless of `top`. An empty month is a zero report. `report.to_dict()` gives the JSON-ready form with amounts as strings.

**FR6 — Conversion and rounding (R4).** `RATES` maps ILS → 1, USD → 3.70, EUR → 4.00 (ILS per unit). Each amount is converted as `amount × rates[currency] ÷ rates[base]` at full Decimal precision; each figure is summed exactly and quantized once to two places with `ROUND_HALF_EVEN`, independently, always showing two decimals. Rates are a caller-supplied parameter.

**FR7 — Caller errors (R3).** An invalid `month`, a `base` not in `rates`, or `top < 1` raises `ValueError`, never `LedgerError`.

**FR8 — Command line (R5).** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]` prints the text report (or JSON with `--json`) and exits 0. Usage errors (missing subcommand or `--month`, invalid month, `--top` < 1, unknown base, unreadable FILE) exit 2 with nothing on stdout and a message on stderr. A data error exits 3 with nothing on stdout and stderr exactly `error: {FILE}:{line}: {reason}`. `--help` documents the options.

## 4. User Experience & Behavior

**Flow 1 — See a month.** The developer runs `python -m ledger report ledger.csv --month 2026-03`. They see thirteen lines (for six categories): `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, `categories:`, then one line per category indented two spaces as `  name: total (count)`. All amounts show exactly two decimals; expenses carry a leading minus. Output is byte-for-byte deterministic for the same input.

**Flow 2 — Another currency / short list.** Adding `--base USD` restates every figure in USD; `--top N` shortens only the category list.

**Flow 3 — Scripting.** `--json` prints one JSON object (`month`, `base`, `count`, `income`, `expense`, `net`, `categories[{name,total,count}]`) with all amounts as strings so no precision is lost.

**Flow 4 — Empty month.** A month with no transactions is not an error: figures read `0.00` and the category line reads `categories: none`.

**Flow 5 — Bad file.** The developer sees a single stderr line `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`, nothing on stdout, exit code 3 — enough to open the file at that line and fix it.

**Flow 6 — Wrong command.** A malformed command line gives a usage message on stderr, nothing on stdout, exit code 2; `--help` exits 0 and documents `--month`.

**Observable states.** success (0, report on stdout, empty stderr) · usage error (2) · data error (3). stdout and stderr are never mixed: on error stdout is empty.

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

- **Repository fit (checked against `roeeoz/play1@main`, 0fe2628).** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets `testpaths = ["tests"]`; neither `src/ledger/` nor `tests/test_ledger_*.py` nor `tests/fixtures/ledger/` exists yet. The pre-conditions hold, and a new package under `src/` is picked up without editing `pyproject.toml`, so the "no change to existing files" boundary is achievable.
- **Gates every PR must pass.** `.factory/testing.md` / `.github/workflows/ci.yml`: `pip install -e ".[test]"` then `pytest` on Python 3.12 (with the `gate` job green, i.e. no `CI_FAIL` file). The `repo-gate` skill (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): Python source under `src/`, tests under `tests/`, no file over 200 KB, new shell scripts executable with a shebang. The story's layout satisfies all of them; no exemption is needed.
- **Python ≥ 3.10** (`requires-python` in `pyproject.toml`); standard library only.
- **Delivery order:** t1 (model + parser) → t2 (report) → t3 (command line); each depends on the previous one. No other story blocks this one.
- **Merge:** a person merges the PR after review; "done" means the PR's required checks are green.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, how the CSV reader tracks physical line numbers, the argument-parsing mechanism and how unreadable files map to exit code 2, Decimal context settings, and the exact contents of the fixture files (`sample.csv`, `bom_blank.csv`, `empty.csv`, `bad_amount.csv`) — which must reproduce the totals fixed in criteria 9–10, 16, 19–20 — are for STRUCTURE. Product-imposed constraints: stdlib only, `decimal.Decimal` end to end, deterministic output, CLI tests via `subprocess` on the installed package.

## 8. Open Questions

None blocking. Non-blocking notes for STRUCTURE (behaviour the criteria do not pin, to be chosen and disclosed, not to be invented as new product behaviour):

- Amount spellings the criteria do not name — a leading `+`, exponent notation (`1e3`), negative zero (`-0.00`, which must at least fall under "amount must not be zero"), thousands separators — accept or reject consistently with the stated reasons.
- The repository's contextual glossary skill (claims/invoices) defines "net amount" as before-tax; it applies to invoice code, not to this ledger, so the story's `net` (= income + expense) stands.
