# Feature Specification Document — Monthly expense report from a CSV ledger

## 1. Feature Overview

**What is being built.** A new, stdlib-only Python package `ledger` (under `src/`, tests under `tests/`) that reads a CSV ledger, validates every row, and totals one calendar month by category in a chosen base currency, reachable both as a library (`parse_csv` / `parse_lines`, `monthly_report`) and from the terminal as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has no quick, deterministic way to see a month's income, expenses and largest categories without opening a spreadsheet — and a spreadsheet silently produces a wrong total when a row is malformed.

**User story.** As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

**Target users / actors.** A developer working in a terminal who owns a personal or small-team CSV ledger (persona from the story). Secondary: code that imports `ledger` as a library.

**Traceability.** Requirements R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line); epic steps 1–8; risks RK1, RK2. Priority **Must**, size **M (≈5)**, blockers: none. Delivered as three dependent work items: t1 model and CSV parser → t2 monthly report → t3 command line.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals

- G1 — Parse a UTF-8 CSV ledger into ordered, immutable transactions, matching columns by header name (R1).
- G2 — Reject a bad ledger loudly: the first bad row (or header problem) is reported with its physical line number and an exact, human-readable reason, never turned into a wrong total (R2, RK1/RK2).
- G3 — Produce a deterministic monthly report — count, income, expense, net and per-category totals ordered by size — in a base currency of ILS, USD or EUR (R3, R4).
- G4 — Exact money: `Decimal` throughout, conversion at full precision, rounding once per figure after summing, half to even, always two places (R4).
- G5 — A terminal command with a fixed text format and a lossless JSON format, and distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals

- Other file formats (Excel, JSON input, OFX, …).
- Live or fetched exchange rates; rates other than the fixed table (except as a library parameter, Scenario 17).
- Persistent configuration (config files, environment defaults).
- Charts or any graphical output.
- Any third-party dependency — the package uses the standard library only.
- Changes to any existing file of the repository (including `pyproject.toml`, `README.md`, CI workflows); everything is new files.
- Reports over ranges other than one calendar month, multi-file ledgers, editing or writing ledgers.
- Reporting more than the first bad row (parsing stops at the first error).

## 3. Functional Requirements

### Parsing and validation (t1 — R1, R2)

- **FR1 — Input.** A ledger is UTF-8 text (an optional BOM is ignored) whose first non-empty line is a header naming at least `id, date, amount, currency, category, memo` in any order; extra columns are ignored. Two entry points: `parse_lines(lines)` takes any iterable of lines; `parse_csv(path)` opens the file with encoding `utf-8-sig` and `newline=""` and delegates to `parse_lines`, behaving identically.
- **FR2 — Output.** A list of `Transaction` frozen dataclasses in file order, with `id: str`, `date: datetime.date`, `amount: Decimal` (exactly the text's value, e.g. `Decimal("12000.00")`), `currency: str`, `category: str`, `memo: str` (possibly `""`). Every field is stripped of surrounding whitespace. Quoted fields follow CSV quoting (a memo may contain a comma). Blank and whitespace-only lines are skipped but still counted for line numbers. A header with no rows returns `[]`.
- **FR3 — Validation rules and exact reasons.** The first bad row raises `LedgerError` with `line` (physical line number, header = line 1, blank lines count) and `reason`; `str(error)` is `line {line}: {reason}`. Reasons:
  - date not `YYYY-MM-DD` → `date '2026-3-1' is not YYYY-MM-DD`
  - well-formed but not a calendar date → `date '2026-02-30' is not a calendar date`
  - amount not a decimal number (incl. `NaN`, `Infinity`) → `amount 'abc' is not a number`
  - more than two decimal places → `amount '1.505' has more than 2 decimal places`
  - zero amount → `amount must not be zero`
  - currency not exactly `ILS`/`USD`/`EUR` (case-sensitive) → `unknown currency 'usd'`
  - empty category → `empty category`; empty id → `empty id`
  - field count differs from the header's → `expected 6 fields, got 5`
  - id seen before → `duplicate id 't1' (first seen on line 2)` on the later row's line
- **FR4 — Header errors.** Missing required columns → `LedgerError(1, "missing column(s): …")` listing them in canonical order `id, date, amount, currency, category, memo`; a zero-byte file → `LedgerError(1, "missing header")`.

### Monthly report (t2 — R3, R4)

- **FR5 — Inputs.** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`. `RATES` is a module constant `{"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}` (ILS per unit).
- **FR6 — Selection.** Only transactions whose date falls in `month` count.
- **FR7 — Conversion.** Each amount becomes `amount × rates[currency] ÷ rates[base]` at full Decimal precision, before any summing.
- **FR8 — Figures.** `count` (transactions in the month), `income` (sum of positive converted amounts), `expense` (sum of negative ones), `net` (sum of all), and per category `CategoryTotal(name, total, count)`. Each figure is the exact sum quantized once to two places with `ROUND_HALF_EVEN`, independently — figures are not forced to add up. Every figure always shows two places (`5.00`).
- **FR9 — Ordering and top-N.** Categories are ordered by absolute total descending, ties by name ascending; `top=N` keeps the first N categories only, while `count`/`income`/`expense`/`net` still cover the whole month; `top=None` or a `top` above the number of categories keeps all.
- **FR10 — Empty month.** A month with no transactions is a zero report (`0.00` figures, empty categories), not an error.
- **FR11 — Serialisation.** `report.to_dict()` returns `month`, `base`, `count`, `income`, `expense`, `net`, `categories` (each `{"name", "total", "count"}`) with money as strings.
- **FR12 — Caller errors.** `ValueError` (never `LedgerError`) for a `month` not `YYYY-MM` with month 01–12, a `base` not in `rates`, or `top < 1`.

### Command line (t3 — R5)

- **FR13 — Invocation.** `python -m ledger report FILE --month YYYY-MM [--base {ILS,USD,EUR}] [--top N] [--json]`; `--base` defaults to `ILS`; `--top` is an integer ≥ 1; `--help` documents the options.
- **FR14 — Output.** Text (default) or JSON (`--json`, the `to_dict()` object) on stdout; see §4 for the exact format.
- **FR15 — Exit codes.** 0 on success with nothing on stderr; 2 on a usage error (no subcommand, missing `--month`, invalid month, `--top 0`, unknown base, FILE that cannot be opened) with nothing on stdout and a message on stderr; 3 on a data error with nothing on stdout and stderr exactly `error: {FILE}:{line}: {reason}` + newline, FILE as given on the command line.
- **FR16 — Tests drive the real entry point** via `subprocess` with `[sys.executable, "-m", "ledger", ...]`, relying on the installed package and no `sys.path` manipulation.

## 4. User Experience & Behavior

### Key flows

1. **See a month.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a short, fixed-format text summary on stdout (exit 0).
2. **See it in another currency / only the biggest categories.** Adds `--base USD` and/or `--top 3`; totals are converted and the category list is cut, while the month totals still cover every transaction.
3. **Feed another tool.** Adds `--json` and pipes a single JSON object whose money values are strings (no float precision loss).
4. **Fix a bad ledger.** The command exits 3, prints nothing on stdout, and stderr points to the exact file and line: `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`. The developer fixes that line and reruns.
5. **Mistype the command.** Exit 2, nothing on stdout, a usage message on stderr.

### Output format (text)

Exactly, in this order:

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
  freelance: 925.00 (1)
  groceries: -760.50 (2)
  software: -444.00 (1)
  travel: -321.00 (1)
```

One line per category, indented two spaces, `name: total (count)`, in report order. When the month has no transactions the last line is `categories: none` and the figures read `0.00`.

### Output format (JSON)

One object: `{"month", "base", "count", "income", "expense", "net", "categories": [{"name", "total", "count"}]}`, amounts as two-place strings, `count` as integers.

### States and messages the user sees

| Situation | Exit | stdout | stderr |
| --- | --- | --- | --- |
| Success | 0 | report | empty |
| Usage error | 2 | empty | a usage message |
| Data error (bad row / header) | 3 | empty | `error: {FILE}:{line}: {reason}` |

### Qualities

- **Deterministic**: the same file and arguments always produce byte-identical output.
- **Exact**: money never passes through binary floating point; every figure shows exactly two decimals.
- **Pinpointed errors**: a bad ledger is never summarised; the first problem is named by physical line number, counting the header and blank lines as an editor does.

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

- **Repository pre-conditions — verified against the checkout.** `pyproject.toml` declares `[tool.setuptools.packages.find] where = ["src"]` and `[tool.pytest.ini_options] testpaths = ["tests"]`; `.factory/testing.md` states the gate is `pip install -e ".[test]"` then `pytest` on Python 3.12 (`.github/workflows/ci.yml`), with no `conftest.py` or `sys.path` manipulation. `src/` holds only `guestbook` and `testbed_utils`; no `src/ledger/`, no `tests/test_ledger_*.py` and no `tests/fixtures/ledger/` exist yet. A new `src/ledger/` package is therefore picked up by the existing manifest without editing any existing file.
- **Python floor.** The manifest declares `requires-python >= 3.10`; the package must work there and on the CI's 3.12.
- **Standard library only.** The manifest's existing dependencies (`pypdf`, `flask`) are not used by `ledger`, and no dependency is added.
- **No edits to existing files** — including `pyproject.toml` (so no console-script entry; the command is `python -m ledger`), `README.md` and `CHANGELOG.md`.
- **New fixtures** under `tests/fixtures/ledger/`: `sample.csv` (header + nine rows: seven in 2026-03 giving the Scenario 9 categories, one 2026-02-27 groceries -99.99, one 2026-04-01; ids `t001`…`t009`; contents such that Scenarios 9, 10, 13, 16, 19, 20 hold), `bom_blank.csv`, `empty.csv` (zero bytes), `bad_amount.csv` (amount `-2.505` on line 3).
- **Build order.** t1 → t2 → t3; each work item depends on the previous one. No dependency on sibling stories.
- **Fixed rates** are a business constant of this story (ILS 1, USD 3.70, EUR 4.00 ILS per unit); they are never fetched.

## 7. Technical Design (deferred to STRUCTURE)

Module layout inside `src/ledger/`, how the CSV reader tracks physical line numbers, how `argparse` errors and unopenable files are mapped to exit 2, the `Report` type's shape beyond the named fields and `to_dict()`, and the test file split are for the STRUCTURE stage. Product-imposed constraints it must honour: `Decimal` end to end; rounding once per figure with `ROUND_HALF_EVEN`; physical line numbers (header = 1, blank lines counted); the exact reason strings, output lines and exit codes in §3–§5; tests through the installed package and a real subprocess.

## 8. Open Questions

None block the story; the acceptance criteria pin every behaviour the request names. The following are residual edge cases the story does not decide; STRUCTURE should pick the stated working assumption unless the product owner says otherwise.

1. **Negative zero after rounding.** A month whose expenses round to zero in the base currency (e.g. a single -0.01 ILS reported in EUR = -0.0025) could print `-0.00`. *Working assumption:* print `0.00`, consistent with the empty-month output in Scenarios 15 and 21.
2. **Ledger that is not valid UTF-8.** Not covered by Scenarios 22 or 23. *Working assumption:* a data error (exit 3, `error: …` on stderr), since the file opened but its content is bad.
3. **Header-level errors on the command line** (e.g. `empty.csv`). *Working assumption:* same as Scenario 23 — exit 3, stderr `error: {FILE}:1: missing header`.
4. **Line number of a quoted field spanning several physical lines.** *Working assumption:* the line on which the row starts.
5. **Category names** are compared exactly (case- and space-sensitive after stripping): `Groceries` and `groceries` are two categories.
