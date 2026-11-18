# Feature Specification Document — SCRUM-18: Monthly expense report from a CSV ledger

> Status: READY_FOR_SPEC. The developer's instruction: the story text and its acceptance criteria are the whole requirement; where they are silent, the simplest reading is taken and recorded as an assumption (§8).

## 1. Feature Overview

- **What is built:** a new, stdlib-only Python package `ledger` (under `src/`, tests under `tests/`) that reads a CSV ledger, validates every row, and reports one month's income, expense, net and per-category totals in a chosen base currency, from the terminal (`python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`) and as a Python API (`parse_csv`, `parse_lines`, `monthly_report`).
- **Problem:** a developer keeping a personal or small-team ledger in a CSV file has to open a spreadsheet to see a month's summary, and a malformed row silently produces a wrong total instead of being pointed at.
- **Target users:** a developer who keeps the ledger as a CSV file and works from the terminal (and, through the API, from Python).
- **Story shape:** one story delivered in three dependent work items — model and CSV parsing (t1), monthly report (t2), command line (t3). Priority Must, size M (≈5). Traces to R1–R5, steps 1–8, risks RK1, RK2. No blockers stated by the story.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository, except the one line under `## Unreleased` in `CHANGELOG.md` that the repository's pull-request gate requires of every change.

> Intake note: the row is the story's own text word for word, except for the final clause ("except the one line … every change"). It was added under assumption A1 (§8) so the row agrees with the repository's gate, which cannot be waived.

### Goals

- A developer runs one command and sees a month's income, expense, net and largest categories in a base currency, deterministically (same file, same arguments → same output, byte for byte).
- A bad row is never summed: the report refuses the file and points at the physical line number and the exact reason.
- Money is exact: amounts are kept as given, converted at full precision, summed, and only then rounded once to two places, half to even.
- Output is usable by people (text) and by scripts (JSON, amounts as strings so no precision is lost), with distinct exit codes for success (0), usage errors (2) and data errors (3).

### Non-Goals

- Other file formats (anything but a UTF-8 CSV with the six named columns).
- Live or fetched exchange rates; rates are the fixed constants (overridable only as a parameter of the Python API).
- Persistent configuration, charts, any third-party dependency.
- Changes to any existing file of the repository, other than the single `CHANGELOG.md` line under `## Unreleased` the repository's gate requires (assumption A1).
- Reporting across several months, date ranges or filters other than one `YYYY-MM` month.

## 3. Functional Requirements

- **FR1 — CSV parsing (R1, t1).** Input: a ledger file path (`parse_csv`) or any iterable of lines (`parse_lines`, same behaviour). The header names the six columns in any order; extra columns are ignored; fields are trimmed; a UTF-8 BOM, blank and whitespace-only lines are ignored; quoted fields (e.g. a memo with a comma) are honoured. Output: a list of frozen `Transaction(id, date, amount, currency, category, memo)` in file order, the amount exactly the text's Decimal value. A header-only file gives `[]`.
- **FR2 — Row validation (R2, t1).** The first bad row stops parsing with `LedgerError(line, reason)`, `line` the physical line number (header = 1, blank lines counted), `str(error)` = `line {line}: {reason}`. Reasons are exactly those listed in criteria 5–7: malformed date, non-calendar date, non-number amount (incl. NaN/Infinity), more than two decimals, zero amount, unknown (case-sensitive) currency, empty category, empty id, wrong field count, duplicate id (citing the first line), missing columns (canonical order), missing header (empty file).
- **FR3 — Monthly report (R3, t2).** Input: transactions, a month `YYYY-MM`, optional `base` (default ILS), optional `top` (default None), optional `rates` (default the `RATES` constant). Output: a report with `month`, `base`, `count`, `income`, `expense`, `net` and `categories` — `CategoryTotal(name, total, count)` ordered by absolute total descending, ties by name ascending, truncated to `top` while the totals still cover the whole month. `to_dict()` gives the JSON-shaped mapping with amounts as strings. An empty month is a zero report. Bad arguments raise `ValueError`, never `LedgerError`.
- **FR4 — Currency conversion and rounding (R4, t2).** Each amount converts as `amount × RATES[currency] ÷ RATES[base]` at full precision; each figure is the exact sum quantized once to two places with `ROUND_HALF_EVEN`, independently; figures always show two places and are not forced to add up.
- **FR5 — Command line (R5, t3).** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`, plus `--help`. Text output is the exact line layout in criteria 19 and 21; JSON output is `to_dict()`. Exit 0 on success; exit 2 with nothing on stdout and a message on stderr for usage errors and an unopenable FILE; exit 3 with nothing on stdout and `error: {FILE}:{line}: {reason}` on stderr for a bad row.

## 4. User Experience & Behavior

- **Main flow:** the developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a thirteen-line plain-text summary: `month`, `base`, `transactions`, `income`, `expense`, `net`, then `categories:` and one two-space-indented `name: total (count)` line per category, largest absolute total first. Amounts always show two decimal places.
- **Scripted flow:** with `--json` the same report is one JSON object whose amounts are strings; `--base` changes the currency every figure is expressed in; `--top N` keeps the N largest categories without changing the totals.
- **Empty month:** zero figures (`0.00`) and the line `categories: none`; still exit 0.
- **Bad data:** nothing on stdout; stderr reads `error: {FILE}:{line}: {reason}` exactly, with FILE as typed; exit 3. The developer goes straight to that line.
- **Wrong usage:** nothing on stdout, a message on stderr, exit 2.
- **Look and feel:** terminal-only, plain text, no colour or charts; output is deterministic.

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

- **Repository gate (play1 layout gate, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4):** every pull request must add a line under `## Unreleased` in `CHANGELOG.md`; a diff that does not touch it is a blocker (PLAY-G4). The gate reads neither this ticket nor its answers, so it cannot be exempted. The story's exclusion of changes to existing files is therefore read as excluding everything except that one line (assumption A1).
- **Same gate, rules 1–3:** Python source under `src/`, tests under `tests/` (the story already complies); no file over 200 KB.
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** `pip install -e ".[test]"` then `pytest` on Python 3.12; no conftest and no `sys.path` manipulation, so tests import the installed package — consistent with criterion 25. `pyproject.toml` already discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and `testpaths = ["tests"]`, so the pre-conditions hold and no manifest change is needed for `python -m ledger`.
- **Pre-conditions verified:** no `src/ledger/` and no `tests/test_ledger_*.py` exist on the work branch (`b7b5d0a`); only `src/guestbook` and `src/testbed_utils` exist.
- **Not applicable:** the repository's claims glossary and claims reviewer cover invoices code; the ledger is not invoice code, so their naming rules (e.g. "billing period") do not apply.
- **Language:** the story was published in English, so its acceptance criteria are kept word for word in English here; Harel's Hebrew story template governs story blocks written at breakdown, not the intake's copy of a published story.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, the `Transaction`/`Report`/`CategoryTotal`/`LedgerError` shapes beyond what the criteria name, argument parsing mechanism, and how physical line numbers are tracked through the CSV reader are left to STRUCTURE. Product constraints it must honour: stdlib only, `Decimal` end to end, the exact messages, outputs and exit codes in §5.

## 8. Open Questions

No blocking question remains. At the developer's instruction (the story text and its criteria are the whole requirement; where they are silent, take the simplest reading and record it), these assumptions stand. No acceptance criterion was added, dropped or reworded.

- **A1 — `CHANGELOG.md` line.** The repository's layout gate (rule PLAY-G4, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) fails any pull request that does not add a line under `## Unreleased` in `CHANGELOG.md`, and it cannot be exempted. The story's "no changes to any existing file" is read as "no existing file changes except that one added line naming SCRUM-18". Earlier stories in the repository (e.g. PLAY-175) were delivered the same way. *Risk:* if the developer meant the exclusion literally, the gate's rule has to be changed first, in a separate change, and this story waits for it.
- **A2 — field-count message.** In criterion 5, `expected N fields` uses the header's own column count, so a six-column header gives `expected 6 fields, got 5`. *Risk:* low. Only headers with extra columns show a different N.
- **A3 — multi-line quoted field.** A quoted field that spans several physical lines is reported at the line where its row starts. *Risk:* low. No criterion covers this case.
- **A4 — scope check.** No criterion checks the diff's scope (only new files plus the A1 line, with the existing suite passing unchanged). Harel's Definition of Ready expects one, but the developer ruled out adding criteria. Review checks it against the Story context row instead.
