# Feature Specification Document — Monthly expense report from a CSV ledger

> Status: in-progress intake draft (NOT_READY — one blocking question open, see §8).

## 1. Feature Overview

**What is being built.** A new, stdlib-only Python package `ledger` in the play1 repository (`src/ledger/`, tests under `tests/`). It reads a CSV ledger, validates it row by row, builds a deterministic monthly report (income, expense, net, totals per category) in a chosen base currency, and exposes this as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.

**Problem.** A developer who keeps a personal or small-team ledger as a CSV file has no quick, trustworthy way to see one month's summary from the terminal. Spreadsheets are heavy, and ad-hoc scripts silently produce wrong totals when a row is malformed.

**Target user.** A developer who keeps a ledger as a CSV file and works from the terminal (personal or small-team use). The surface is developer-facing: a Python library API (`parse_csv`, `parse_lines`, `monthly_report`) and a command line.

**Traceability.** Story SCRUM-17, traced to the epic's requirements R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding) and R5 (command line), steps 1–8, risks RK1 and RK2. The epic PRD and backlog were not available to this turn; the story's own text is the authority used here.

## 2. Goals & Non-Goals

### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals

- G1 — Parse a UTF-8 CSV ledger into ordered, immutable transactions, matching columns by name (R1).
- G2 — Reject a bad ledger at its first bad row, naming the physical line number and an exact reason, instead of producing a wrong total (R2).
- G3 — Total one calendar month: count, income, expense, net and per-category totals ordered by size, optionally limited to the top N (R3).
- G4 — Convert every amount to a base currency (ILS, USD or EUR) at fixed rates, with exact decimal arithmetic and a single half-to-even rounding per figure (R4).
- G5 — Offer the report from the terminal as text or JSON, with distinct exit codes for success (0), usage errors (2) and data errors (3) (R5).

### Non-Goals

- Other input or output file formats (only CSV in, text/JSON out).
- Live or fetched exchange rates; rates are fixed constants (overridable only as a library parameter).
- Persistent configuration (no config file, no environment settings).
- Charts or any graphical output.
- Any third-party dependency — the package uses the Python standard library only.
- Changes to any existing file of the repository (see the open question in §8 about `CHANGELOG.md`, which the repository's gate requires every pull request to touch).
- Currencies other than ILS, USD and EUR; multi-month or date-range reports.

## 3. Functional Requirements

### Parsing and validation (work item t1 — R1, R2)

- **FR1 — Input.** A ledger is UTF-8 text (a leading BOM is ignored) with a header row naming `id`, `date`, `amount`, `currency`, `category`, `memo` in any order; extra columns are ignored. Fields are trimmed of surrounding spaces; CSV quoting is honoured (a quoted memo may contain a comma). Blank and whitespace-only lines are skipped but still count toward line numbers.
- **FR2 — Entry points.** `parse_lines(lines)` takes any iterable of lines; `parse_csv(path)` opens the file as `utf-8-sig` with `newline=""` and delegates to `parse_lines`. Both return a list of `Transaction` values in file order.
- **FR3 — Transaction.** A frozen dataclass with `id` (str), `date` (`datetime.date`), `amount` (`Decimal`, exactly the text's value), `currency` (str), `category` (str), `memo` (str, possibly empty).
- **FR4 — Validation.** Parsing stops at the first bad row and raises `LedgerError(line, reason)`, `str()` = `line {line}: {reason}`, with the exact reasons listed in acceptance criteria 5–7 (date format, calendar date, non-numeric amount incl. NaN/Infinity, more than two decimals, zero amount, case-sensitive unknown currency, empty category, empty id, field-count mismatch, duplicate id, missing columns, missing header).
- **FR5 — Empty data.** A header-only file yields an empty list without error.

### Monthly report (work item t2 — R3, R4)

- **FR6 — Inputs.** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`; `RATES` = ILS 1, USD 3.70, EUR 4.00 as Decimals (ILS per unit).
- **FR7 — Selection.** Only transactions dated in `month` count.
- **FR8 — Conversion.** Each amount is converted as `amount × rates[currency] ÷ rates[base]` at full Decimal precision, before summing.
- **FR9 — Figures.** `count`; `income` (sum of positives), `expense` (sum of negatives), `net`; per-category `CategoryTotal(name, total, count)`. Each figure is its exact sum quantized once to two places with `ROUND_HALF_EVEN`, independently (figures need not add up).
- **FR10 — Ordering and top-N.** Categories are ordered by absolute total descending, ties by name ascending; `top` keeps the first N while the headline figures still cover the whole month.
- **FR11 — Empty month.** Zero report: count 0, all figures `0.00`, no categories.
- **FR12 — Serialization.** `report.to_dict()` gives `month`, `base`, `count`, and amounts as two-place strings; categories as `{name, total, count}`.
- **FR13 — Caller errors.** Invalid `month` (not `YYYY-MM` with month 01–12), `base` not in `rates`, or `top < 1` raise `ValueError`, never `LedgerError`.

### Command line (work item t3 — R5)

- **FR14 — Command.** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`; `--base` defaults to ILS; `--top` is an integer ≥ 1; `--help` documents `--month`.
- **FR15 — Output.** Text format (criterion 19 / 21) or JSON object equal to `to_dict()` (criterion 20).
- **FR16 — Exit codes.** 0 success; 2 usage error (no subcommand, missing/invalid `--month`, invalid `--top`/`--base`, FILE cannot be opened) with nothing on stdout and a message on stderr; 3 data error with nothing on stdout and exactly `error: {FILE}:{line}: {reason}` on stderr.
- **FR17 — Tests drive the real entry point** through `subprocess` with `[sys.executable, "-m", "ledger", ...]`, relying on the installed package.

## 4. User Experience & Behavior

**Main flow.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a thirteen-line (for the sample) plain-text summary: month, base, transaction count, income, expense, net, then `categories:` with one indented `name: total (count)` line per category, biggest first. Adding `--json` gives the same report as a single JSON object with amounts as strings, for piping into other tools. `--base USD` or `--base EUR` restates every figure in that currency; `--top N` shortens the category list only.

**Output format qualities.** Every amount is shown with exactly two decimal places (`5.00`, `-2.00`); output is deterministic — the same file and flags always give byte-identical output. An empty month shows zero figures and `categories: none`.

**Errors the user sees.**
- A bad row: exit 3, stdout empty, stderr exactly `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places` — the path as typed, the physical line number, the exact reason.
- A wrong command line or an unopenable file: exit 2, stdout empty, a usage message on stderr.

No colours, interactivity, persistent state or network access.

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

- **Repository (play1, target branch `main`).** Python src layout: `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest `testpaths = ["tests"]`; no `src/ledger/` and no `tests/test_ledger_*.py` exist today (pre-condition verified).
- **Test gate.** `.factory/testing.md` and `.github/workflows/ci.yml`: `pip install -e ".[test]"` then `pytest`, on Python 3.12; no linter or formatter is configured. The suite has no `conftest.py` and no `sys.path` manipulation, which is what criterion 25 relies on.
- **Layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`), run on every pull request: source under `src/`, tests under `tests/`, no file over 200 KB, and **every pull request must add a line under `## Unreleased` in `CHANGELOG.md`** (rule PLAY-G4, a blocker). `CHANGELOG.md` is an existing file, which collides with the story's "no changes to any existing file" — see Q1 in §8.
- **No third-party dependency** for `ledger`; the repository's existing runtime dependencies (`pypdf`, `flask`) are untouched and not used.
- **Fixed rates** ILS 1, USD 3.70, EUR 4.00 (ILS per unit); no network access.
- Delivery is three dependent work items in order: t1 (model and parser) → t2 (report) → t3 (command line).

## 7. Technical Design (deferred to STRUCTURE)

Module layout, class shapes beyond those named in the criteria, argument parsing mechanics, fixture contents beyond what the criteria pin, and how the three work items are split into pull requests are for the STRUCTURE stage. Product-imposed constraints it must keep: stdlib only; `Decimal` end to end with a single `ROUND_HALF_EVEN` quantization per figure; exact error texts and exit codes as in §5; tests importing only the installed package.

## 8. Open Questions (if any remain)

- **Q1 (blocking) — `CHANGELOG.md` vs. "no changes to any existing file".** The repository's layout gate fails any pull request that does not add a line under `## Unreleased` in `CHANGELOG.md` (rule PLAY-G4), and the gate cannot be waived. Options: (a) narrow the out-of-scope line to "changes to any existing file of the repository other than one line per pull request under `## Unreleased` in `CHANGELOG.md`"; (b) keep the exclusion as written, which means changing the gate rule in the repository first, in a separate change. **Recommendation: (a)** — it is the only option the current gate can pass, and a changelog line does not change any existing behaviour. If agreed, the story's context row is updated accordingly and a scope-boundary criterion is added: "the pull request changes no existing file except that `CHANGELOG.md` line, and the existing test suite still passes."
- **Note (non-blocking).** The epic PRD, backlog and Confluence research referenced by the story were not available to this turn; the story's own acceptance criteria were used as the authority and are internally consistent (the March, USD and rounding figures were cross-checked arithmetically).
