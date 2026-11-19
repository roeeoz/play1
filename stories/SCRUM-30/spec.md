# Feature Specification Document — SCRUM-30: Monthly expense report from a CSV ledger

> Status: **READY_FOR_SPEC** — the developer ruled that the story text and its acceptance criteria are the whole requirement, and that where they are silent the simplest reading is taken and recorded as an assumption (§8).

## 1. Feature Overview

**What is being built.** A new, stdlib-only Python package `ledger` in the play1 repository (`src/ledger/`, tests in `tests/test_ledger_*.py`, fixtures in `tests/fixtures/ledger/`). It reads a CSV ledger, validates every row, and reports one calendar month by category in a chosen base currency, both as a library (`parse_csv` / `parse_lines`, `monthly_report`) and as a command line (`python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`).

**Problem statement.** A developer who keeps a personal or small-team ledger as a CSV file has no deterministic way to get a month's income, expenses and largest categories from the terminal without opening a spreadsheet; and a malformed row silently produces a wrong total instead of being pointed at.

**Target users / actors.**
- *Primary:* a developer keeping a CSV ledger, running the report from a terminal (text or JSON output).
- *Secondary:* a developer calling the package from Python code (parser and report functions).

**Traceability.** Requirements R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line) · epic steps 1–8 · risks RK1, RK2. Priority **Must**, size **M (≈5)**, delivered as three dependent work items: t1 model and CSV parser → t2 monthly report → t3 command line.

## 2. Goals & Non-Goals
### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository other than one new line under `## Unreleased` in `CHANGELOG.md`.

### Goals
- G1 — Parse a UTF-8 CSV ledger (header-named columns in any order, BOM and blank lines tolerated) into typed, immutable transactions in file order (R1).
- G2 — Reject the first invalid row with its physical line number and an exact, human-readable reason, so a bad row never yields a wrong total (R2).
- G3 — Total one calendar month: transaction count, income, expense, net and per-category totals ordered by absolute size, optionally limited to the top N (R3).
- G4 — Convert to a base currency (ILS, USD or EUR) at fixed rates, at full precision, rounding each figure once after summing, half-to-even, always to two places (R4).
- G5 — Expose it as `python -m ledger report` with an exact text format, a lossless JSON format, `--help`, and distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals
- Other file formats (anything but CSV).
- Live or fetched exchange rates; currencies other than ILS, USD, EUR.
- Persistent configuration (config files, saved defaults).
- Charts or any graphical output.
- Any third-party dependency (stdlib only, no new entry in `pyproject.toml` dependencies).
- Changes to any existing file of the repository, other than one new line under `## Unreleased` in `CHANGELOG.md`, which the repository's PR gate requires (assumption A1, §8).
- Reports over ranges other than one calendar month (multi-month, year, custom periods).
- Editing or writing ledgers; the package only reads them.

## 3. Functional Requirements

### t1 — model and CSV parsing (R1, R2)
- **FR1 Transaction.** A frozen dataclass `Transaction` with `id: str`, `date: datetime.date`, `amount: Decimal` (exactly the text's value — `12000.00` stays `Decimal("12000.00")`), `currency: str`, `category: str`, `memo: str` (possibly empty).
- **FR2 Entry points.** `parse_lines(lines)` takes any iterable of lines (e.g. `io.StringIO`); `parse_csv(path)` opens the path with encoding `utf-8-sig` and `newline=""` and behaves exactly as `parse_lines` on its content. Both return `list[Transaction]` in file order.
- **FR3 Header.** Columns are matched by name, in any order; columns beyond the six are ignored. Missing columns → `LedgerError(1, "missing column(s): …")` listing the missing names in canonical order `id, date, amount, currency, category, memo`. Zero-byte file → `LedgerError(1, "missing header")`. Header only → `[]`.
- **FR4 Row tolerance.** A UTF-8 BOM is ignored; blank and whitespace-only lines are skipped but still count toward line numbers; fields are trimmed of surrounding whitespace; quoted fields (e.g. a memo containing a comma) keep their content.
- **FR5 Row validation.** The first invalid row raises `LedgerError(line, reason)`; `line` is the physical line (header = 1, blank lines count); `str(error) == f"line {line}: {reason}"`. Exact reasons:

  | Case | Reason |
  | --- | --- |
  | date not `YYYY-MM-DD` | `date '2026-3-1' is not YYYY-MM-DD` |
  | well-formed but not a calendar date | `date '2026-02-30' is not a calendar date` |
  | amount not a decimal number (incl. `NaN`, `Infinity`) | `amount 'abc' is not a number` |
  | more than two decimal places | `amount '1.505' has more than 2 decimal places` |
  | zero amount | `amount must not be zero` |
  | currency not ILS/USD/EUR (case-sensitive) | `unknown currency 'usd'` |
  | empty category | `empty category` |
  | empty id | `empty id` |
  | field count ≠ header's | `expected 6 fields, got 5` |
  | duplicate id | `duplicate id 't1' (first seen on line 2)` (error on the second row's line) |

### t2 — monthly report (R3, R4)
- **FR6** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` returns a report with `month`, `base`, `count`, `income`, `expense`, `net` and `categories: list[CategoryTotal(name, total, count)]`, plus `to_dict()` (amounts as strings, two places).
- **FR7 Month filter.** Only transactions dated in `month` (`YYYY-MM`, month 01–12) count.
- **FR8 Conversion.** Each amount converted as `amount × rates[currency] ÷ rates[base]` at full Decimal precision before summing. `RATES` is a module constant: `ILS → Decimal("1")`, `USD → Decimal("3.70")`, `EUR → Decimal("4.00")`; `rates` is a parameter.
- **FR9 Rounding.** Each figure (`income`, `expense`, `net`, each category total) is its own exact sum quantized to two places with `ROUND_HALF_EVEN`; figures are not forced to add up. Always two decimal places (`5.00`, `-2.00`).
- **FR10 Ordering & top-N.** Categories ordered by absolute total descending, ties by name ascending; `top=N` keeps the first N categories only (totals still cover the whole month); `top=None` or `top` ≥ category count keeps all.
- **FR11 Empty month** is a zero report: `count` 0, `0.00` figures, no categories.
- **FR12 Caller errors** raise `ValueError` (never `LedgerError`): bad `month`, `base` not a key of `rates`, `top < 1`.

### t3 — command line (R5)
- **FR13** `python -m ledger report FILE --month YYYY-MM [--base {ILS,USD,EUR}] [--top N] [--json]`; `--base` defaults to ILS; `--top` integer ≥ 1.
- **FR14 Text output** (exit 0, empty stderr): `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, `categories:` then one `  name: total (count)` line per category; an empty month prints `categories: none`.
- **FR15 JSON output** (`--json`): the `to_dict()` object, amounts as strings.
- **FR16 Exit codes.** 0 success (incl. `--help`); 2 usage error (no subcommand, missing/invalid `--month`, `--top 0`, `--base GBP`, unopenable FILE) — nothing on stdout, a message on stderr; 3 data error — nothing on stdout, stderr exactly `error: {FILE}:{line}: {reason}\n`, FILE as given.
- **FR17 Tests** drive the CLI via `subprocess` with `[sys.executable, "-m", "ledger", ...]` against the installed package, no `sys.path` manipulation.

## 4. User Experience & Behavior

**Flow 1 — monthly text report.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a fixed 7-line summary followed by indented category lines, largest first. The output is deterministic: the same file and arguments always print byte-identical output.

**Flow 2 — machine-readable report.** Adding `--json` prints one JSON object whose amounts are strings with two decimals, so no precision is lost when piped into other tools. `--base USD|EUR` reports in another currency; `--top N` shortens the category list without changing the totals.

**Flow 3 — bad ledger.** If any row is invalid, the developer gets no report at all (nothing on stdout) and a single line on stderr, `error: <FILE>:<line>: <reason>`, pointing at the physical line to fix; exit code 3. Only the first bad row is reported.

**Flow 4 — wrong invocation.** A malformed command line (missing `--month`, invalid month, `--top 0`, unsupported base, unopenable file, no subcommand) prints a message on stderr, nothing on stdout, exit code 2. `report --help` documents the options, including `--month`.

**Observable qualities.**
- Output format is exact (Scenario 19 / 20 / 21): labels, two-space indent, `name: total (count)`, `categories: none` for an empty month.
- Every amount is shown with exactly two decimal places, including zeros (`0.00`).
- Exit codes distinguish success (0), caller mistakes (2) and ledger data problems (3), so scripts can branch on them.
- Error reasons are the exact strings of §3 FR5 — they are part of the product surface.

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
26. Scenario 26 — Regression / scope boundary: existing behaviour is untouched. Given the pull request that delivers the story, When its diff and the test gate are inspected, Then the existing test suite passes unchanged, and no existing file of the repository is modified other than one new line added under `## Unreleased` in `CHANGELOG.md`.

## 6. Dependencies & Constraints (product-level)

- **Pre-conditions verified against the repository (`main` @ `b7b5d0a`).** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest `testpaths = ["tests"]`; `.factory/testing.md` and `.github/workflows/ci.yml` run `pip install -e ".[test]"` then `pytest` on Python 3.12; there is no `conftest.py` and no `sys.path` manipulation. No `src/ledger/` and no `tests/test_ledger_*.py` exist; `tests/fixtures/ledger/` is new. `python -m ledger` needs no `[project.scripts]` entry, so `pyproject.toml` stays untouched.
- **Repository PR gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`), applied mechanically to every PR:**
  - Rule 1 — Python source under `src/`, tests under `tests/`: the story complies.
  - Rule 3 — no file over 200 KB: fixtures are small; complies.
  - **Rule 4 — the PR must add a line under `## Unreleased` in `CHANGELOG.md`, else a `PLAY-G4` blocker.** `CHANGELOG.md` already exists, so this **collides with the story's out-of-scope "changes to any existing file of the repository"**. No exemption from the gate can be granted, so the story's exclusion is narrowed to allow exactly that one line (assumption A1, §8; Scenario 26).
- **Glossary (`.factory/plugins/claims-dev/skills/glossary`)** applies to invoices/claims code; the ledger is not invoices, so its terms (`net`, `month`) stay as the story states. "Billing period … `YYYY-MM`" happens to match the month format.
- **Story template conformance (Harel `stories-he`).** The story has happy paths, boundaries, edges and errors, but no *regression* or *scope-boundary* scenario that says what must not change (the existing suite, existing files). The Definition of Ready requires one; Scenario 26, added with assumption A1, supplies it.
- **Language.** The story was published in English; this spec keeps it in English so its acceptance criteria stay word for word.
- Python ≥ 3.10 (`requires-python`), stdlib only.

## 7. Technical Design (deferred to STRUCTURE)

Module layout inside `src/ledger/`, the CSV-reading approach, how line numbers are tracked through the csv reader, argparse configuration and how usage vs data errors are mapped to exit codes, the error-class hierarchy and the test layout are STRUCTURE's to design. Product constraints it must honour: stdlib only; `Decimal` end to end; exact strings and exit codes from §3 and §5; `parse_csv` opens with `utf-8-sig` and `newline=""`; tests exercise the installed package.

## 8. Open Questions

No blocking question remains. The developer ruled that the story text and its acceptance criteria are the whole requirement and that, where they are silent, the simplest reading is taken and recorded here. Each assumption below is that reading; the risk it carries is noted.

**Assumptions adopted at intake**
- **A1 — `CHANGELOG.md` line.** The repository's PR gate (rule PLAY-G4, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) blocks any PR that does not add a line under `## Unreleased` in `CHANGELOG.md`, and no exemption can be granted. The simplest reading that lets the story ship is to narrow the out-of-scope exclusion to "any existing file other than that one `CHANGELOG.md` line" (Story context updated accordingly) and to add Scenario 26 as the regression / scope-boundary criterion the story template's Definition of Ready requires. *Risk:* if the product owner meant the exclusion literally, the gate rule must change in the repository first, as a separate change.
- **A2 — one row with several problems.** The field count is checked first, then the fields in canonical order `id, date, amount, currency, category, memo`, then the duplicate id; the first failure is reported. *Risk:* low — only which reason is shown for a multiply-broken row.
- **A3 — amount notation.** An amount in exponent form (`1e3`) is rejected as `amount '1e3' is not a number`; a leading `+` is accepted. *Risk:* low — such ledgers are unusual.
- **A4 — a FILE that is not valid UTF-8** exits 2 (it cannot be read, like an unopenable file), with a message on stderr and nothing on stdout. *Risk:* a user might expect exit 3; no line number can be given for the exit-3 format.
- **A5 — `expected N fields, got M`:** N is the header's field count (6 for the canonical header; more when extra columns are present).
- **A6 —** header names are matched after trimming, case-sensitively; ids and category names are compared after trimming, case-sensitively.
- **A7 —** a file holding only a BOM and/or blank lines is reported as `LedgerError(1, "missing header")`, like a zero-byte file.
- **A8 —** the sample fixture's per-row content is STRUCTURE's to author, constrained by Scenarios 1, 9, 10, 16 and 20.

**Not verified.** The epic's PRD, User Story Backlog and Confluence research were not available to this intake; the story was read as published.
