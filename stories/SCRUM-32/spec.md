# Feature Specification Document — Monthly expense report from a CSV ledger (SCRUM-32)

> Status: draft — PARTIALLY_READY. One blocking question is open (§8, Q1: the story's scope collides with the repository's changelog gate). Points where the story is silent are recorded as assumptions A1–A3 (§8).

## 1. Feature Overview

**What is being built.** A new, standard-library-only Python package `ledger` in the play1 repository (under `src/`, tests under `tests/`) that reads a CSV ledger, validates every row, and produces a deterministic monthly report — income, expense, net and per-category totals in a chosen base currency — through a library API and the command `python -m ledger report`.

**Problem.** A developer who keeps a ledger as a CSV file has to open a spreadsheet to see a month's summary, and a malformed row silently produces a wrong total. The feature gives the summary from the terminal and turns a bad row into an error that names its line number.

**Target users / actors.**
- *Developer keeping a personal or small-team CSV ledger* — runs the command and reads the text or JSON report.
- *Developer calling the library* — uses `parse_csv` / `parse_lines` and `monthly_report` from Python.

**Traceability.** Requirements R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line); steps 1–8; risks RK1, RK2. Priority Must, size M (≈5). Delivered as three dependent work items: t1 model and CSV parser → t2 monthly report → t3 command line.

## 2. Goals & Non-Goals
### Story context

The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

### Goals
- Parse a UTF-8 CSV ledger (header columns matched by name, any order) into ordered, immutable transactions (R1).
- Reject the first invalid row with an error naming its physical line number and an exact reason, never a wrong total (R2).
- Report one calendar month: count, income, expense, net, and category totals ordered by absolute size, optionally limited to the top N (R3).
- Convert ILS/USD/EUR into a chosen base currency at fixed rates, with exact Decimal arithmetic and a single half-to-even rounding per figure (R4).
- Offer `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]` with exact text/JSON output and distinct exit codes for usage (2) and data (3) errors (R5).
- Be deterministic: the same file and arguments always give byte-identical output.

### Non-Goals
- Other file formats (Excel, JSON, OFX, …).
- Live or fetched exchange rates; currencies other than ILS, USD, EUR.
- Persistent configuration (config files, saved defaults).
- Charts or any graphical output.
- Any third-party dependency for the `ledger` package.
- Changes to any existing file of the repository — **subject to Q1 (§8)**: the repository's pull-request gate requires a `CHANGELOG.md` line.
- Multi-month or date-range reports, editing or writing ledgers.

## 3. Functional Requirements

### t1 — model and CSV parsing (R1, R2)
- **FR1 Transaction.** An immutable value with `id` (str), `date` (calendar date), `amount` (Decimal, exactly the text's value — `12000.00` stays `12000.00`), `currency` (str), `category` (str), `memo` (str, may be empty).
- **FR2 Two entry points.** `parse_lines(lines)` accepts any iterable of text lines; `parse_csv(path)` opens the file as UTF-8 (a leading BOM tolerated) and behaves exactly like `parse_lines` on its content. Both return transactions in file order.
- **FR3 Header.** The first line is the header; the six columns `id, date, amount, currency, category, memo` are matched by name in any order; extra columns are ignored. Missing columns → `line 1: missing column(s): …` listing the missing names in that canonical order. An empty file → `line 1: missing header`. A header with no data rows → empty list, no error.
- **FR4 Leniency.** Field values are trimmed of surrounding spaces; blank and whitespace-only lines are skipped (but still counted for line numbers); standard CSV quoting is honoured (a quoted memo keeps its comma).
- **FR5 Validation**, stopping at the first bad row, raising `LedgerError` with `line` (physical line, header = 1, blank lines counted), `reason`, and `str(error) == "line {line}: {reason}"`. Exact reasons:
  - date not `YYYY-MM-DD` → `date '2026-3-1' is not YYYY-MM-DD`
  - well-formed but impossible date → `date '2026-02-30' is not a calendar date`
  - amount not a decimal number, incl. `NaN`/`Infinity` → `amount 'abc' is not a number`
  - more than two decimal places → `amount '1.505' has more than 2 decimal places`
  - zero amount → `amount must not be zero`
  - currency not exactly `ILS`/`USD`/`EUR` (case-sensitive) → `unknown currency 'usd'`
  - empty category → `empty category`; empty id → `empty id`
  - field count ≠ header's → `expected 6 fields, got 5`
  - repeated id → `duplicate id 't1' (first seen on line 2)` on the second occurrence's line.

### t2 — monthly report (R3, R4)
- **FR6 Inputs.** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`; `RATES` = `{ILS: 1, USD: 3.70, EUR: 4.00}` as Decimals (ILS per unit).
- **FR7 Selection.** Only transactions whose date falls in `month` count.
- **FR8 Conversion.** Each amount becomes `amount × rates[currency] ÷ rates[base]` at full Decimal precision before summing.
- **FR9 Figures.** `count`; `income` = sum of positive converted amounts; `expense` = sum of negative ones; `net` = sum of all; each `CategoryTotal(name, total, count)`. Each figure is its own exact sum quantized once to two places, `ROUND_HALF_EVEN`, always shown with two places; figures are not forced to add up.
- **FR10 Ordering & top-N.** Categories ordered by absolute total descending, ties by name ascending; `top=N` keeps the first N categories only and never changes `count`/`income`/`expense`/`net`; `top` larger than the category count or `None` keeps all.
- **FR11 Empty month** → count 0, all figures `0.00`, no categories.
- **FR12 Serialization.** `to_dict()` gives `month`, `base`, `count`, `income`, `expense`, `net` (amounts as two-place strings) and `categories` as a list of `{name, total, count}`.
- **FR13 Caller errors** raise `ValueError` (never `LedgerError`): `month` not `YYYY-MM` with month 01–12; `base` not a key of `rates`; `top` < 1.

### t3 — command line (R5)
- **FR14 Command.** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR (default ILS)] [--top N (N ≥ 1)] [--json]`; `--help` documents `--month`.
- **FR15 Text output** (exit 0, empty stderr): `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`, then `categories:` followed by one `  name: total (count)` line per category in report order, or `categories: none` when there are none.
- **FR16 JSON output** (`--json`, exit 0): the `to_dict()` object; amounts are strings.
- **FR17 Usage errors** → exit 2, nothing on stdout, a message on stderr: no subcommand, missing `--month`, invalid month, `--top` < 1, `--base` outside ILS/USD/EUR, FILE that cannot be opened.
- **FR18 Data errors** → exit 3, nothing on stdout, stderr exactly `error: {FILE}:{line}: {reason}\n`, FILE as typed on the command line.

## 4. User Experience & Behavior

**Key flow — terminal report.** The developer runs `python -m ledger report ledger.csv --month 2026-03` and reads a thirteen-line plain-text summary (fixed `label: value` lines, categories indented by two spaces, largest first). Adding `--base USD` restates every figure in USD; `--top 2` shows only the two largest categories while the headline figures still cover the whole month; `--json` gives one machine-readable JSON object with amounts as strings for scripting.

**Key flow — bad data.** When the ledger has a bad row, the developer sees nothing on stdout and one line on stderr, e.g. `error: ledger.csv:3: amount '-2.505' has more than 2 decimal places`, and the exit code is 3 — they can jump straight to line 3 in their editor. No partial or wrong report is ever printed.

**Key flow — wrong invocation.** A mistyped command (missing `--month`, `--month 2026-13`, `--base GBP`, `--top 0`, a missing file) exits 2 with a usage-style message on stderr and nothing on stdout.

**States.** success (exit 0, report on stdout, empty stderr) · usage error (exit 2) · data error (exit 3). An empty month is a success, not an error: zeros and `categories: none`.

**Output qualities.** Plain ASCII-friendly text with no colour or decoration; every amount always has exactly two decimal places; output is deterministic (same input → same bytes); stdout carries only the report and stderr only errors, so the command composes in shell pipelines.

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

- **Target repository rules (play1, branch `main`).** Python source under `src/`, tests under `tests/` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 1) — the story complies. Files ≤ 200 KB (rule 3) — complies.
- **Changelog gate — collides with the story.** The same gate's rule 4 (`PLAY-G4`, a blocker) requires every pull request to add a line under `## Unreleased` in the existing `CHANGELOG.md`; the story's context rules out "changes to any existing file of the repository". See Q1.
- **Test gate.** `.factory/testing.md` and `.github/workflows/ci.yml`: `pip install -e ".[test]"` then `pytest` on Python 3.12, with no `conftest.py` or `sys.path` manipulation — matches Scenario 25. The manifest (`pyproject.toml`, `[tool.setuptools.packages.find] where = ["src"]`) discovers `src/ledger/` with no manifest edit, so `python -m ledger` works after the editable install.
- **No third-party dependency** for `ledger` (the repository's existing `pypdf`/`flask` dependencies are untouched and not used).
- **Fixed rates** ILS 1, USD 3.70, EUR 4.00 (ILS per unit), never fetched.
- No dependency on other stories; t2 depends on t1, t3 on t2.

## 7. Technical Design (deferred to STRUCTURE)

Module layout, the dataclass definitions, the CSV reader approach, argparse wiring and how exit codes are produced are for STRUCTURE. Product-imposed constraints: stdlib only; `decimal.Decimal` end to end with one `ROUND_HALF_EVEN` quantization per figure; `parse_csv` opens with `utf-8-sig` and `newline=""`; CLI tests run through `subprocess` with `sys.executable -m ledger`. The exact rows of `tests/fixtures/ledger/sample.csv` are not given by the story; STRUCTURE must author them so Scenarios 1, 9, 10, 16, 19 and 20 all hold (e.g. freelance is 250.00 USD, giving 925.00 ILS).

## 8. Open Questions (if any remain)

- **Q1 (P0, blocking) — `CHANGELOG.md` vs. "no changes to existing files".** The play1 gate fails any pull request that does not add a line under `## Unreleased` in `CHANGELOG.md` (rule `PLAY-G4`), but the story puts "changes to any existing file of the repository" out of scope. The gate cannot be waived. Options: (a) narrow the exclusion to "changes to any existing file except one added line under `## Unreleased` in `CHANGELOG.md`"; (b) keep the exclusion and change the gate rule in the repository first, in a separate change. **Recommendation: (a)** — it is the only option that lets this story's pull request pass the gate without prior repository work, and an appended changelog line does not alter any existing behaviour. An answer that the changelog must stay untouched would make (b) necessary.
  The developer's instruction (take the simplest reading where the story is silent) does not settle Q1: the story is not silent here, it explicitly excludes changes to existing files, and the gate explicitly requires one. No assumption can satisfy both, and a gate exemption cannot be recorded. Until it is answered, the risk is that the delivered pull request either breaks the story's stated scope (if it adds the changelog line) or fails the `PLAY-G4` blocker (if it does not). If the stage is approved as it stands, the working assumption is option (a).
  The developer repeated the same instruction a second, third and fourth time without choosing (a) or (b), so Q1 remains unsettled by the developer; it is recorded here as an unresolved point with option (a) as the working assumption and the risk above, and the intake stays not ready until it is answered or the stage is approved as it stands.

### Assumptions (simplest reading where the story is silent, per the developer's instruction)

- **A1 — a FILE that is not valid UTF-8** (was Q2). Treated like a FILE that cannot be opened: exit 2, nothing on stdout, a message on stderr. The library raises no `LedgerError` for it (it has no reliable line number). Risk: low; not covered by any acceptance criterion.
- **A2 — exponent amounts** such as `1E+2` (was Q3). "A decimal number" is read as plain decimal notation (optional sign, digits, optional point and digits); an exponent form is rejected as `amount '1E+2' is not a number`. Risk: low; a ledger using exponent notation would be rejected with a line-numbered error, never mis-totalled.
- **A3 — `sample.csv` contents.** The story fixes only the totals; STRUCTURE authors rows that make Scenarios 1, 9, 10, 16, 19 and 20 hold together.
