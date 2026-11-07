# Feature Specification Document (DRAFT, not ready: P0 on CHANGELOG scope is open)

## 1. Feature Overview
- **What:** A new stdlib-only Python package `ledger` in roeeoz/play1. It provides `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`, which totals one month of a CSV ledger by category in a base currency.
- **Problem:** A developer who keeps a ledger as a CSV file wants a deterministic monthly summary (income, expenses, net, largest categories) from the terminal, without a spreadsheet. A bad row should be pointed to by its line number, never folded silently into a wrong total.
- **Actor:** A developer who keeps a personal or small-team ledger as a CSV file.

## 2. Goals & Non-Goals
### Story context
The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

> PENDING P0: under option (a), the last sentence becomes "…changes to any existing file of the repository, except one line describing the change under `## Unreleased` in `CHANGELOG.md`." Under option (b) it stays as written, and repository rule PLAY-G4 must be changed first in separate work.

### Goals
- Parse a CSV ledger into validated transactions. Stop at the first bad row and report its physical line number and an exact reason.
- Build a monthly report in a chosen base currency. Round once, after summing. Order categories by absolute total and support an optional top-N.
- Provide a CLI with text and JSON output and distinct exit codes: 0 for success, 2 for usage errors, 3 for data errors.

### Non-Goals
- Other file formats, live exchange rates, persistent configuration, charts, third-party dependencies, and changes to existing repository files (subject to the P0 decision).

## 3. Functional Requirements
- **FR1 (R1, t1) CSV parsing:** `parse_lines(lines)` and `parse_csv(path)` return frozen `Transaction(id, date, amount, currency, category, memo)` values in file order. Columns are matched by header name, fields are trimmed, and extra columns are ignored. A BOM, blank lines and whitespace-only lines are ignored. Quoted memos keep their commas. A header with no data rows gives an empty list. (Scenarios 1–4, 8)
- **FR2 (R2, t1) Row validation:** The first bad row raises `LedgerError(line, reason)`, where `str()` is `line {line}: {reason}`. The exact reasons are listed in Scenarios 5–7. See A1–A5 for the cases the story leaves open.
- **FR3 (R3, t2) Monthly report:** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` gives the month, base, count, income, expense, net, and categories. Categories are ordered by absolute total descending, with ties broken by name ascending. An empty month gives a zero report. `to_dict()` returns amounts as strings. (Scenarios 9, 13–16)
- **FR4 (R4, t2) Conversion and rounding:** Each amount is converted as `amount × rates[currency] ÷ rates[base]` at full precision. Each figure is summed exactly, then quantized once to two places with `ROUND_HALF_EVEN`. An invalid month, base or top raises `ValueError`. (Scenarios 10–12, 17–18)
- **FR5 (R5, t3) CLI:** Text and JSON output are byte-exact as in Scenarios 19–21. Usage errors exit 2 and data errors exit 3. Errors print nothing on stdout and a message on stderr. (Scenarios 19–25)

### Assumptions where the story is silent (simplest reading, per the developer's instruction)
- **A1 Field count with extra columns:** N in `expected N fields, got M` is the number of fields in the header row. A six-column header gives `expected 6 fields, got 5`, as in Scenario 5. A seven-column header gives `expected 7 fields, got 5`.
- **A2 Multi-line quoted rows:** A row whose quoted memo spans several physical lines is reported at the physical line where the row starts. Its later lines still count toward the line numbers of the rows after it.
- **A3 Duplicate header column:** The header is not rejected. The first column carrying a name is the one used, and no new error message is introduced.
- **A4 Blank lines before the header:** Blank or whitespace-only lines before the header are skipped, and the first non-blank line is the header. Line numbers stay physical. A file containing only blank lines gives `LedgerError(1, "missing header")`, as the empty file does.
- **A5 Header names:** Header names are trimmed like fields and matched case-sensitively against `id, date, amount, currency, category, memo`.
- **A6 Several usage errors at once:** Every usage error exits 2 with nothing on stdout and a message on stderr. Which message appears when two apply at once is not specified.
- **A7 Help text:** Only `--month` must appear in `report --help`. Documenting `--base`, `--top` and `--json` is welcome but not required.

## 4. User Experience & Behavior
- The text report has exactly the layout in Scenario 19: seven summary lines, then category lines indented by two spaces. An empty month shows `categories: none`.
- JSON output is a single object with amounts as strings (Scenario 20).
- A data error appears on stderr exactly as `error: {FILE}:{line}: {reason}`, where FILE is the path as typed (Scenario 23).
- `--help` documents `--month` (Scenario 24).
- The output is deterministic: the same file and arguments always give byte-identical output.

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

> PENDING P0: under option (a), one criterion is added: the pull request adds one line describing the change under `## Unreleased` in `CHANGELOG.md` and changes no other existing file of the repository. Under option (b), nothing is added here.

## 6. Dependencies & Constraints
- roeeoz/play1, base branch `main`. Python 3.10 or newer. CI runs `pip install -e ".[test]"` and then `pytest` on 3.12. No linter, formatter or type checker is configured.
- The repository rules require source under `src/`, tests under `tests/`, no file over 200 KB, and a `CHANGELOG.md` entry under `## Unreleased` (PLAY-G4). That last rule is the open P0, because the story forbids changes to existing files. The rule runs on every pull request and cannot be waived per ticket.
- Work items are ordered t1 → t2 → t3.
- The project already depends on `pypdf` and `flask`. The `ledger` package adds no dependency.

## 7. Technical Design (deferred to STRUCTURE)
Deferred to STRUCTURE. Constraints the product imposes:
- Scenarios 19, 20 and 23 require byte-exact stdout and stderr.
- The published figures assume the default `Decimal` context: 28 digits of precision before rounding once with `ROUND_HALF_EVEN`.
- The CLI tests must use a subprocess (Scenario 25).

## 8. Open Questions
- **P0:** the story's scope rule conflicts with repository rule PLAY-G4 (the CHANGELOG entry). Option (a) narrows the scope to allow one `## Unreleased` line. Option (b) changes the rule in the repository first. The developer has repeated the instruction to take the simplest reading where the story is silent, but the story is explicit here, so the choice stays open.
- **Settled by assumption:** A1–A7 above, per the developer's instruction to take the simplest reading where the story is silent.
- The epic PRD, the sibling stories and the Confluence research were not available. This spec relies on the story text alone, which the developer confirmed is the whole requirement.
