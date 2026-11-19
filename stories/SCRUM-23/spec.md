# Feature Specification Document — Monthly expense report from a CSV ledger (SCRUM-23)

> Status: **in-progress draft (NOT_READY)** — one blocking question open, see §8.

## 1. Feature Overview

**What is built.** A command-line monthly report over a CSV ledger: `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`. It reads a UTF-8 CSV ledger, validates every row, and totals one month by category in a chosen base currency. It ships as a new stdlib-only Python package `ledger` under `src/`, with its tests under `tests/`.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has no way to get a monthly summary from the terminal without a spreadsheet. A malformed row can silently produce a wrong total. The report must be deterministic, and a bad row must be pointed at by its line number instead.

**Target users / actors.**
- *Primary:* a developer who keeps a ledger as a CSV file and works in the terminal.
- *Secondary:* a developer who calls the package from Python (`parse_csv` / `parse_lines`, `monthly_report`). The library surface is part of the product, because the acceptance criteria name it.

**Delivery shape (from the story).** One story, delivered as three dependent work items: t1, the model and CSV parsing (R1, R2); t2, the monthly report (R3, R4); and t3, the command line (R5). Traces to R1–R5, steps 1–8 and risks RK1 and RK2. Priority: Must. Size: M (≈5).

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals
- Parse a CSV ledger whose columns can come in any order into typed, immutable transactions, matching each column by its name.
- Reject the first bad row with its physical line number and an exact, documented reason, so the tool never prints a wrong total.
- Total one calendar month by category, as income, expense and net, in a base currency (ILS, USD or EUR) at fixed rates. Use exact decimal arithmetic and round once, half to even.
- Show the result from the terminal as human-readable text or as lossless JSON, with exit codes that tell success (0), a usage error (2) and a data error (3) apart.

### Non-Goals
- Other file formats (XLSX, OFX, JSON input, …).
- Live or fetched exchange rates. The rates are fixed constants, and the library takes them as a parameter.
- Persistent configuration (config files, saved defaults).
- Charts or any graphical output.
- Any third-party dependency. The package uses the standard library only.
- Changes to any existing file of the repository. **Open:** this collides with the repository's pull-request gate (§6, §8 Q1).
- Multi-month or year reports, budgets, editing the ledger, and currencies other than ILS, USD and EUR.

## 3. Functional Requirements

**Parsing (R1, R2 — work item t1)**
- **FR1 — Input.** A UTF-8 CSV ledger, which may start with a BOM. Its header row names `id`, `date`, `amount`, `currency`, `category` and `memo` in any order. Extra columns are ignored. Fields are trimmed of surrounding whitespace. Blank and whitespace-only lines are skipped, but they still count toward line numbers. Quoted fields keep their embedded commas.
- **FR2 — Output.** A list of `Transaction` values in file order. Each is a frozen value with these fields: `id` (str), `date` (date), `amount` (an exact Decimal that keeps the text's scale), `currency` (str), `category` (str) and `memo` (str, possibly empty). A file with only a header row gives an empty list.
- **FR3 — Two entry points.** `parse_lines(lines)` takes any iterable of lines. `parse_csv(path)` opens the file with encoding `utf-8-sig` and `newline=""`, then delegates to `parse_lines`. Both behave the same way.
- **FR4 — Validation.** Parsing stops at the first bad row and raises `LedgerError(line, reason)`, where `str(error)` is `line {line}: {reason}`. The reasons are the exact texts in AC 5–7: date format, calendar date, non-number amount (including NaN and Infinity), more than two decimal places, zero amount, unknown currency (compared case-sensitively), empty category, empty id, wrong field count, duplicate id (naming the first line), missing column(s) in canonical order, and missing header.

**Report (R3, R4 — work item t2)**
- **FR5 — Month filter.** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` keeps only the transactions dated in `month` (`YYYY-MM`).
- **FR6 — Conversion.** Each amount is converted as `amount × rates[currency] ÷ rates[base]` at full Decimal precision. `RATES` is ILS 1, USD 3.70 and EUR 4.00, expressed in ILS per unit.
- **FR7 — Figures.** The report has `count`, `income` (the sum of positive amounts), `expense` (the sum of negative amounts) and `net`, plus a total and count per category. Each figure is the exact sum, rounded once to two places with ROUND_HALF_EVEN and independently of the others. Figures always show two places.
- **FR8 — Ordering and top-N.** Categories are ordered by absolute total, descending, with ties broken by name ascending. `top=N` keeps the first N categories, but income, expense, net and count still cover the whole month.
- **FR9 — Empty month.** A month with no transactions gives a zero report: all figures are `0.00` and the category list is empty. It is not an error.
- **FR10 — Serialisation.** `report.to_dict()` gives the JSON-ready shape, with amounts as strings.
- **FR11 — Caller errors.** A bad `month`, a `base` that is not in `rates`, or `top < 1` raises `ValueError`, never `LedgerError`.

**Command line (R5 — work item t3)**
- **FR12 — Invocation.** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`. `--base` defaults to ILS, and `--top` accepts integers of at least 1.
- **FR13 — Output.** By default the report prints in the exact 13-line text format of AC 19. With `--json` it prints the JSON object of AC 20.
- **FR14 — Exit codes.** `0` on success and for `--help`. `2` on a usage error, including a file that cannot be opened, with nothing on stdout and a message on stderr. `3` on a data error, with nothing on stdout and stderr exactly `error: {FILE}:{line}: {reason}`.

## 4. User Experience & Behavior

- **Main flow.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads the plain-text summary on stdout: month, base, transaction count, income, expense, net, then the categories, indented by two spaces, largest absolute total first.
- **Machine flow.** With `--json`, stdout is one JSON object whose amounts are strings, so a script can consume it without losing precision.
- **Empty month.** The report still prints, with zero figures and the line `categories: none`.
- **Bad data.** Nothing is printed on stdout. stderr names the file as given and the physical line, e.g. `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`. The exit code is 3, so the developer can fix the exact line.
- **Wrong usage.** Exit code 2, nothing on stdout and a message on stderr. `--help` documents `--month`.
- **Look-and-feel.** The output is plain terminal text with no colour, tables or charts. The text format is exact, line for line, as AC 19 and AC 21 define it. Output is deterministic: the same input always gives byte-identical output.

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

- **Repository fit, verified against `main`.** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest's `testpaths = ["tests"]`. The CI `test` job (`.github/workflows/ci.yml`) runs `pip install -e ".[test]"` and then `pytest` on Python 3.12, as `.factory/testing.md` declares. No `src/ledger/` and no `tests/test_ledger_*.py` exist yet, so the story's preconditions hold. Because the new package is discovered automatically, `pyproject.toml` needs no change.
- **Pull-request gate collision (blocking).** The repository's layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 4) fails every pull request whose diff does not add a line under `## Unreleased` in the existing `CHANGELOG.md`. It reports a blocker with id `PLAY-G4`. The story's context puts "changes to any existing file of the repository" out of scope. The two cannot both hold. See §8 Q1.
- **Other gate rules, already met by the story.** Python source lives under `src/` and tests under `tests/` (rule 1). No shell scripts are involved (rule 2). The fixtures are small, far below 200 KB (rule 3).
- **Stdlib only.** The package adds no runtime or test dependency beyond the existing `pytest` test extra.
- **Glossary.** The repository's glossary skill (`.factory/plugins/claims-dev/skills/glossary`) covers invoice and claims terms. It writes a month as `YYYY-MM`, which this story's `--month` already uses. Ledger, income and expense are not invoice terms, so the glossary does not otherwise apply.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, the internals of the CLI parser, how the error mapping is implemented, and the content of the fixture files beyond what AC 1, 3, 7, 9, 10, 16 and 23 pin down are all for STRUCTURE to decide. The sample fixture must contain rows whose currencies give exactly the ILS and USD figures in AC 9, 10 and 20. For example, freelance 925.00 ILS equals 250.00 USD.

## 8. Open Questions

- **Q1 (P0, blocking) — the CHANGELOG entry versus "no changes to existing files".** The repository's gate requires each PR to add a line under `## Unreleased` in `CHANGELOG.md` (rule PLAY-G4). The story forbids changes to any existing file. The gate cannot be exempted. The options are:
  - **(a)** Narrow the out-of-scope clause to "changes to any existing file of the repository, except the one required `CHANGELOG.md` entry under `## Unreleased`."
  - **(b)** Change the repository's gate rule first, in a separate change.

  *Recommendation: (a).* It is a one-line, append-only edit that every earlier story in this repository made (PLAY-156, PLAY-172 and PLAY-175 all appear there), and (b) widens the work beyond this story.
- No other product-level gaps. The behaviour, exact messages, outputs and exit codes are fully stated in the story's 25 criteria.
