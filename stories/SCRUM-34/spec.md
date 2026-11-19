# Feature Specification Document — Monthly expense report from a CSV ledger (SCRUM-34)

> Status: READY_FOR_SPEC. The developer settled both intake questions on 2026-11-19 (see §8).

## 1. Feature Overview

**What is being built.** A new, standard-library-only Python package `ledger` in the play1 repository. It reads a CSV ledger, totals one calendar month by category in a chosen base currency, and runs from the terminal as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has no quick, deterministic way to see a month's income, expenses and largest categories without opening a spreadsheet. A malformed row can also quietly produce a wrong total. The tool must point at the bad row by its line number and must not print a figure.

**Target users / actors.**
- *Primary:* a developer who keeps a ledger as a UTF-8 CSV file and works from the terminal (story persona).
- *Secondary:* a developer who uses the package from Python code, through the three entry points `parse_csv` / `parse_lines`, `monthly_report` and the `Report.to_dict()` output.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository, except one added line under `## Unreleased` in `CHANGELOG.md`.

### Goals
- G1. Parse a CSV ledger into ordered, validated transactions (R1, R2). Columns are matched by header name, whatever their order.
- G2. Reject the first bad row with its physical line number and an exact, human-readable reason, and produce no total (R2).
- G3. Produce a deterministic monthly report: income, expense, net, transaction count, and per-category totals ordered by size, with optional top-N (R3).
- G4. Convert currencies at fixed rates with exact decimal arithmetic. Round once, after summing, half to even, always to two places (R4).
- G5. Expose this from the terminal as `python -m ledger report` with text and JSON output and distinct exit codes for usage errors (2) and data errors (3) (R5).

### Non-Goals
- File formats other than CSV.
- Live or fetched exchange rates. Rates are fixed.
- Persistent configuration (no config files, no environment variables).
- Charts or any graphical output.
- Any third-party dependency. The package uses the standard library only.
- Changes to any existing file of the repository, except one added line under `## Unreleased` in `CHANGELOG.md`, which the repository's PR gate requires of every pull request (§6).
- Reports over several months, date ranges, or currencies beyond ILS/USD/EUR.

## 3. Functional Requirements

**Parsing (t1 — R1, R2)**
- FR1. The input is a UTF-8 CSV ledger (a leading BOM is allowed). It has a header row naming `id, date, amount, currency, category, memo` in any order. Extra columns are ignored, and columns are matched by name.
- FR2. Every field is stripped of surrounding whitespace. Blank and whitespace-only lines are skipped but still count toward physical line numbers (the header is line 1). Quoted fields keep embedded commas.
- FR3. Each valid row becomes an immutable `Transaction(id, date, amount, currency, category, memo)`, returned in file order. The amount keeps exactly the value written in the file, and the memo may be empty.
- FR4. Validation stops at the first bad row with `LedgerError(line, reason)`, whose `str()` is `line {line}: {reason}`. The exact reasons are listed in AC 5–7 (bad date format, non-calendar date, non-number amount including NaN/Infinity, more than 2 decimal places, zero amount, unknown or wrongly cased currency, empty category, empty id, field-count mismatch, duplicate id, missing columns, missing header).
- FR4a. An amount may carry an optional leading sign (`+5` and `-5` are numbers). Exponent notation (`1e2`) and thousands separators (`1,000`) are not decimal numbers and are rejected with `amount '{text}' is not a number`.
- FR5. There are two entry points with identical behaviour: `parse_lines(iterable of lines)` and `parse_csv(path)`.

**Report (t2 — R3, R4)**
- FR6. `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` keeps only the transactions dated in `month` (`YYYY-MM`).
- FR7. Each amount is converted as `amount × rates[currency] ÷ rates[base]` at full precision. Sums are exact. `income` (sum of positives), `expense` (sum of negatives), `net` and each category total are each rounded once to two places with `ROUND_HALF_EVEN`, independently of one another.
- FR8. Categories are reported as `CategoryTotal(name, total, count)`, ordered by absolute total descending, with ties broken by name ascending. `top` keeps the first N, but `count`/`income`/`expense`/`net` always cover the whole month.
- FR9. An empty month is a valid zero report. `to_dict()` renders amounts as two-place strings.
- FR10. Caller errors (bad `month`, unknown `base`, `top < 1`) raise `ValueError`, never `LedgerError`.

**Command line (t3 — R5)**
- FR11. `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR (default ILS)] [--top N≥1] [--json]`.
- FR12. Success exits 0 with the report on stdout (text or JSON, exact formats in AC 19–21) and nothing on stderr.
- FR13. A usage error exits 2: no subcommand, missing or invalid `--month`, invalid `--top`/`--base`, or a FILE that cannot be opened. stdout is empty and a message goes to stderr.
- FR14. A data error exits 3: stdout is empty and stderr is exactly `error: {FILE}:{line}: {reason}`, where FILE is the path as given.
- FR15. `report --help` exits 0 and documents `--month`.

**Repository**
- FR16. The pull request adds exactly one line under `## Unreleased` in `CHANGELOG.md`. That is its only change to an existing file; everything else it adds is new files (`src/ledger/…`, `tests/test_ledger_*.py`, `tests/fixtures/ledger/…`).

## 4. User Experience & Behavior

**Key flows**
1. *Monthly summary:* the developer runs `python -m ledger report ledger.csv --month 2026-03`. They see a fixed, line-oriented text report: month, base, transaction count, income, expense, net, then `categories:` and one two-space-indented `name: total (count)` line per category, largest first.
2. *Machine-readable output:* adding `--json` prints one JSON object. Amounts are strings with two decimal places, so no precision is lost.
3. *Different currency / shorter list:* `--base USD` and `--top N` change the base currency and how many categories are listed. The headline figures still cover the whole month.
4. *Bad data:* the developer sees one line, `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`, and nothing else. This tells them exactly which line in their file to fix.

**States the user observes**
- Success (exit 0), usage error (exit 2, argparse-style message on stderr), data error (exit 3, single `error:` line on stderr). In both error states stdout is empty, so a wrong or partial total is never printed.
- Empty month: a normal report with zeros and `categories: none`.

**Qualities**
- Determinism: the same file and arguments always give byte-identical output. Category order is fully defined (absolute total, then name).
- Every money figure is shown with exactly two decimal places.
- No network access, and no configuration is read.

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
26. Scenario 26 — Boundary: amount spellings. Given a row whose amount is `+5`, When parsed, Then its amount is `Decimal("5")`; Given a row whose amount is `1e2`, When parsed, Then `LedgerError` is raised with the reason `amount '1e2' is not a number`; Given a row whose amount is `"1,000"` (quoted), When parsed, Then `LedgerError` is raised with the reason `amount '1,000' is not a number`.
27. Scenario 27 — Scope: existing files. Given the story's pull request, When its diff is inspected, Then the only change to an existing file of the repository is one added line under `## Unreleased` in `CHANGELOG.md`, and every other change is a new file under `src/ledger/`, `tests/` or `tests/fixtures/ledger/`.

## 6. Dependencies & Constraints (product-level)

Verified against the checkout (`play1`, branch based on `main`):

- **Pre-conditions hold.** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest `testpaths = ["tests"]`. `.github/workflows/ci.yml` runs `pip install -e ".[test]"` then `pytest` on Python 3.12. `.factory/testing.md` declares that as the only test gate. Neither `src/ledger/` nor `tests/test_ledger_*.py` exists yet, and nor does `tests/fixtures/ledger/`. A new package under `src/` is picked up without editing `pyproject.toml`, and `python -m ledger` needs no console-script entry.
- **Repository PR gate.** The `play1 layout gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4) blocks every pull request that does not add a line under `## Unreleased` in `CHANGELOG.md` (blocker `PLAY-G4`). The developer chose to narrow the story's out-of-scope line accordingly: that one added line is the only change to an existing file this story allows (FR16, AC 27).
- Other gate rules are met by the story as written: Python source goes under `src/` and tests under `tests/`, there are no shell scripts, and the fixture files are tiny.
- The `Claims glossary` skill (`.factory/plugins/claims-dev/skills/glossary`) covers invoices and claims code. The ledger is not invoices code, so its terms do not apply. Its `YYYY-MM` month convention matches this story anyway.
- Product constraints: standard library only, no network, fixed rates. Python ≥ 3.10 per `pyproject.toml`.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, the internal shape of `Report`, CSV-reading mechanics, how argparse errors map to exit 2, and how an unopenable FILE is reported are left to the STRUCTURE stage. The product fixes only the observable contracts in §5: names, signatures, messages, output formats and exit codes. The three work items (t1 → t2 → t3) are dependent, in that order.

## 8. Open Questions

No product question remains open. Settled at intake (2026-11-19):

- **Q1 (was P0) — CHANGELOG entry versus "no changes to any existing file".** Decided (a): the out-of-scope line now reads "changes to any existing file of the repository, except one added line under `## Unreleased` in `CHANGELOG.md`". The repository's rule stands unchanged.
- **Q2 (was P1) — amount spellings.** Decided: an optional leading sign is accepted; exponent notation and thousands separators are rejected as `amount '…' is not a number` (FR4a, AC 26). The developer's ledgers use neither form.
