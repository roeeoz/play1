# Feature Specification Document — Monthly expense report from a CSV ledger (SCRUM-25)

> Status: NOT_READY — one blocking question open (see §8).

## 1. Feature Overview

- **What is built:** a new, standard-library-only Python package `ledger` (under `src/`, tests under `tests/`) that reads a CSV ledger, validates every row, and produces a monthly report — income, expense, net, transaction count and per-category totals — in a chosen base currency, from the command line as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- **Problem:** a developer who keeps a personal or small-team ledger as a CSV file has no way to get a month's summary from the terminal without opening a spreadsheet, and a malformed row today would silently produce a wrong total instead of being pointed at.
- **Target user:** a developer keeping a CSV ledger (persona from the story's "Persona / Role" row) who runs the report in a terminal or a script.
- **Delivered as:** one story, three dependent work items — t1 model and CSV parser (R1, R2), t2 monthly report (R3, R4), t3 command line (R5).

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

> Pending §8 Q1: the last sentence collides with the repository's pull-request gate, which requires a `CHANGELOG.md` entry. This paragraph is copied word for word until the developer settles it.

### Goals

- Parse a UTF-8 CSV ledger into ordered, validated transactions; reject the first bad row with its physical line number and an exact reason (R1, R2).
- Build a deterministic monthly report — month, base currency, count, income, expense, net and category totals ordered by absolute size, optionally limited to the top N — with fixed-rate conversion and a single half-to-even rounding after summing (R3, R4).
- Expose the report through `python -m ledger report` as text or JSON, with distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals

- Other file formats (Excel, JSON, OFX, …) as input.
- Live or fetched exchange rates; currencies other than ILS, USD, EUR.
- Persistent configuration (config files, saved defaults).
- Charts or any graphical output.
- Any third-party dependency for the package.
- Changes to any existing file of the repository (subject to §8 Q1).
- Multi-month ranges, budgets, or editing the ledger.

## 3. Functional Requirements

**Parsing (t1 — R1, R2)**

- FR1 — Input is a UTF-8 CSV file (an optional BOM is ignored) or any iterable of text lines; both entry points (`parse_csv(path)`, `parse_lines(lines)`) behave identically.
- FR2 — The header row names the six columns `id, date, amount, currency, category, memo` in any order; columns are matched by name; extra columns are ignored; missing columns are an error on line 1 listing them in canonical order; an empty file is `missing header`.
- FR3 — Fields are trimmed; blank and whitespace-only lines are skipped but still counted for line numbers (header = line 1); quoted fields may contain commas.
- FR4 — Each row becomes an immutable `Transaction(id, date, amount, currency, category, memo)` in file order; the amount keeps its exact written value.
- FR5 — Validation stops at the first bad row and raises `LedgerError(line, reason)`, `str` = `line {line}: {reason}`, with the exact reasons listed in criteria 5–7 (date format, calendar date, non-number incl. NaN/Infinity, more than 2 decimals, zero, unknown currency (case-sensitive), empty category, empty id, field-count mismatch, duplicate id with first-seen line).

**Report (t2 — R3, R4)**

- FR6 — `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` keeps only transactions dated in `month` (`YYYY-MM`).
- FR7 — Each amount is converted `amount × rates[currency] ÷ rates[base]` at full precision; income = sum of positives, expense = sum of negatives, net = income + expense; each figure and each category total is the exact sum rounded once to two places, half to even, independently, always shown with two places.
- FR8 — Categories are `CategoryTotal(name, total, count)`, ordered by absolute total descending, ties by name ascending; `top` limits the list only, never the totals or count.
- FR9 — An empty month is a zero report, not an error. `report.to_dict()` gives a JSON-ready mapping with amounts as strings.
- FR10 — Bad arguments (malformed month, unknown base, `top < 1`) raise `ValueError`, never `LedgerError`.

**Command line (t3 — R5)**

- FR11 — `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR (default ILS)] [--top N≥1] [--json]` prints the 13-line-style text report (criterion 19) or the JSON object (criterion 20) and exits 0.
- FR12 — Usage errors (no subcommand, missing/invalid `--month`, invalid `--top`/`--base`, unopenable FILE) exit 2 with a stderr message and empty stdout.
- FR13 — Data errors exit 3 with stderr exactly `error: {FILE}:{line}: {reason}` and empty stdout, FILE as given.
- FR14 — `--help` on `report` exits 0 and documents `--month`.

## 4. User Experience & Behavior

- **Main flow:** the developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a plain-text summary: `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, then `categories:` with one two-space-indented `name: total (count)` line per category, largest first. An empty month prints `categories: none`.
- **Scripting flow:** `--json` prints one JSON object whose money values are strings with two decimal places, so nothing loses precision.
- **Bad data:** the developer sees exactly one line on stderr, `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`, nothing on stdout, exit status 3 — pointing at the line to fix rather than printing a wrong total.
- **Bad usage:** a message on stderr, nothing on stdout, exit status 2.
- **Qualities:** output is deterministic (same file and arguments → byte-identical output); every amount always shows two decimal places; no network access; works with only the Python standard library.

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

- **Repository (play1, base `main`):** setuptools src layout — `[tool.setuptools.packages.find] where = ["src"]` in `pyproject.toml` discovers a new `src/ledger/` with no manifest change; pytest `testpaths = ["tests"]`. The test gate (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`) is `pip install -e ".[test]"` then `pytest` on Python 3.12; no conftest and no `sys.path` manipulation, matching criterion 25. Pre-conditions hold: no `src/ledger/` and no `tests/test_ledger_*.py` exist today.
- **Pull-request gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 1 (source under `src/`, tests under `tests/`) and rule 3 (no file over 200 KB) are met by the story as written. **Rule 4 (PLAY-G4) requires every pull request to add a line under `## Unreleased` in the existing `CHANGELOG.md`; a PR that does not touch it gets a blocker.** This collides with the story's "no changes to any existing file" — see §8 Q1.
- **CI `gate` job:** fails iff a `CI_FAIL` file exists at the repo root; the story must not create one.
- **Constraints:** standard library only; fixed rates, never fetched; `Decimal` money; Python ≥ 3.10 (`requires-python`), CI on 3.12.
- **Delivery order:** t1 → t2 → t3 (each work item depends on the previous one).

## 7. Technical Design (deferred to STRUCTURE)

Module layout, the exact CLI argument parser, how usage errors are produced (e.g. which component maps an unopenable file to exit 2), the fixture file contents beyond what the criteria pin (rows, currencies of the sample so that criteria 9, 10, 16 and 20 hold), and the test structure are decided by the STRUCTURE stage. Product-imposed constraints: the `python -m ledger` entry point must work from the installed package; output must be deterministic.

## 8. Open Questions (if any remain)

- **Q1 (P0, blocking) — CHANGELOG.md vs. "no changes to any existing file".** The repository's pull-request gate rule PLAY-G4 blocks any PR whose diff does not add a line under `## Unreleased` in `CHANGELOG.md`, an existing file; the story's Context puts "changes to any existing file of the repository" out of scope. The gate cannot be exempted. Options: (a) amend the scope to "no changes to any existing file other than one line under `## Unreleased` in `CHANGELOG.md`"; (b) keep the scope and first change the repository's gate rule in a separate change. **Recommendation: (a)** — it is the only option this story can deliver on its own, and every recent PR in the repo (PLAY-156, PLAY-172, PLAY-175) already adds such a line. Answering (b), or that the rule is being retired, would change the pick.
  - **Status (turn 2):** the developer directed that the story text and criteria are the whole requirement and that silences be resolved by the simplest reading. The story is not silent here — it explicitly excludes changes to existing files — so no reading resolves the collision without either breaking the stated scope or failing PLAY-G4. **Unsettled; recorded with its risk:** if the stage is approved as it stands, the implementation either (i) adds the `CHANGELOG.md` line, deviating from the written scope (and the scope gate may flag it), or (ii) honours the scope and the PR is blocked by PLAY-G4 and cannot be merged until the rule changes. Approving as-is is the developer's call; the intake does not grant it.
  - **Status (turn 3):** the developer repeated the same direction without choosing (a) or (b). The point remains unsettled and blocking, with the risk above unchanged. The intake has not chosen for the developer. To unblock it, the developer can answer "(a)" or "(b)", or approve the stage as it stands knowing the risk.
- **Assumption (non-blocking, simplest reading, per the developer's direction):** in criterion 5, `expected 6 fields, got 5` illustrates a six-column header; with extra columns the expected count is the header's field count (`expected {header field count} fields, got {row field count}`).
- **Note (non-blocking):** the story's size "M (≈5)" does not match the story template's scale (M ≈ 3, L ≈ 5); it does not affect the build.
