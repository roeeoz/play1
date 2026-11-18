# SCRUM-4: Monthly expense report from a CSV ledger (high-level design)

## 1. System overview
- **What is being built:** a new stdlib-only Python package `ledger` in play1 (`src/ledger/`, picked up automatically by the existing `packages.find where=["src"]`). It is three layers deep: parse a CSV ledger, build a one-month report in a base currency, and present that report from the terminal.
- **Problem it solves:** a terminal user gets either an exact total or an error naming the bad line. No partial or wrong figure is ever printed.
- **Responsibilities:**
  - strict row validation that stops at the first bad row;
  - exact Decimal arithmetic with one rounding step, ROUND_HALF_EVEN;
  - deterministic ordering and output;
  - distinct exit codes: 0 for success, 2 for usage errors, 3 for data errors.

## 2. Architecture overview
The package has three layers. Each depends only on the layer below it, and each ships in its own ticket.

| Layer | Module(s), as proposed | Ticket |
|---|---|---|
| Model and parser | `ledger/model.py` (transaction, data error, fixed rates), `ledger/parser.py` (`parse_csv`, `parse_lines`), `ledger/__init__.py` (public API) | t1 |
| Report | `ledger/report.py` (`monthly_report`, report and `CategoryTotal`, `to_dict`) | t2 |
| Command line | `ledger/cli.py` (argparse, rendering, exit-code mapping), `ledger/__main__.py` | t3 |

- **External dependencies:** none, only the standard library (`csv`, `decimal`, `datetime`, `re`, `argparse`, `json`). Python 3.10 or later, and CI runs 3.12.
- **Existing files:** none change. There is no `pyproject.toml` change and no console-script entry, because the entry point is `python -m ledger`.
- **Tests and fixtures:** tests go in `tests/test_ledger_*.py` and fixtures in `tests/fixtures/ledger/`.
- **Exact module names:** the implementer chooses these within the package. The ticket lanes are what fix the ownership boundaries.

## 3. Data flow
Everything runs synchronously in a single process.
1. **Read:** the CLI receives FILE. It opens FILE as UTF-8 with an optional BOM and `newline=""`. If the file cannot be opened, the CLI reports a usage error and exits 2.
2. **Parse:** `parse_lines` turns the lines into a list of immutable transactions in file order, or raises `LedgerError(line, reason)` at the first bad row. Blank and whitespace-only lines are skipped but still counted. A row is reported at the physical line where it starts.
3. **Report:** `monthly_report(transactions, month, base, rates, top)` works as follows:
   - it filters the transactions to the month;
   - it converts each amount as `amount × rates[cur] ÷ rates[base]` at full precision;
   - it sums income, expense, net and each category exactly;
   - it rounds each figure once to 0.01, half to even;
   - it orders the categories and cuts them to `top`.
4. **Render:** the CLI prints either the 13-line text layout or `json.dumps(report.to_dict())`, with every amount as a string, and exits 0. A `LedgerError` becomes `error: {FILE as typed}:{line}: {reason}` on stderr with exit 3. Nothing goes to stdout on either error path.

## 4. Component breakdown
All three components live in play1 (`86d449d4-e5db-42c9-8d61-17b798bdd7e2`).
- **Model and parser (t1)**
  - Input: a file path, or any iterable of text lines.
  - Output: a list of frozen transactions with `id`, `date`, `amount` (an exact Decimal, as written), `currency`, `category` and `memo`.
  - Errors: `LedgerError(line, reason)`, whose `str()` is `line {line}: {reason}`.
  - Also owns the fixed rates `RATES` (ILS 1, USD 3.70, EUR 4.00, in ILS per unit) and every fixture.
- **Monthly report (t2)**
  - Input: the transactions, a month `YYYY-MM`, a base (default ILS), the rates (default `RATES`) and `top` (default None).
  - Output: a report with `month`, `base`, `count`, `income`, `expense`, `net` and the ordered `categories`, each a `CategoryTotal(name, total, count)`. `to_dict()` gives a plain dictionary with amounts as two-decimal strings.
  - Errors: caller errors are `ValueError`, kept separate from `LedgerError`.
- **Command line (t3)**
  - Input: argv.
  - Output: stdout or stderr, and the exit code. Usage errors exit 2 (argparse errors, a month that does not validate, an unopenable FILE). Data errors exit 3.

## 5. Interface contracts
- **Public library API:** the spec fixes these names: `parse_csv`, `parse_lines`, `Transaction`, `LedgerError` (with `.line` and `.reason`), `RATES`, `monthly_report`, `CategoryTotal`, and the report's `to_dict()`. They can be imported from the `ledger` package.
- **Error messages:** the reason strings are an exact contract, given in Scenarios 5–7 and extended in §6.
- **Command line:** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N>=1] [--json]`, with `prog` set explicitly to `python -m ledger`.
  - The text layout is fixed by Scenario 19. An empty month shows `categories: none`.
  - The JSON shape is fixed by Scenarios 15 and 20.
- There are no cross-repository contracts.

## 6. Key technical decisions
- **Amount syntax:** only ASCII, matching an optional `+` or `-`, one or more digits, then optionally `.` and one or more digits. Anything else is `amount '<raw>' is not a number`, including NaN, Infinity, exponents, underscores, non-ASCII digits and a bare `.5`.
  - More than 2 digits as written after the point gives `has more than 2 decimal places`, so `1.500` is rejected.
  - A value equal to zero, including `-0.00`, gives `amount must not be zero`.
  - Why: the spec keeps each amount exactly as written and demands exact reasons, and a strict ASCII grammar is the same on every Python version.
- **Dates:** an ASCII `YYYY-MM-DD` pattern check comes first, then a calendar check. `date.fromisoformat` is not relied on, because its leniency differs between 3.10 and 3.11+. The month argument uses the same ASCII care, with months 01–12.
- **The header:**
  - Columns are matched by trimmed name.
  - Missing columns are listed in the canonical order `id, date, amount, currency, category, memo`.
  - A duplicated column name is `LedgerError(1, "duplicate column '<name>'")`.
  - "expected N fields" uses the header's column count.
- **Order of checks within a row:** field count, then id, date, amount, currency, category, and duplicate id last. The first failure wins.
- **BOM:** `parse_lines` strips a leading U+FEFF from the first line, so it matches `parse_csv`, which opens the file with `utf-8-sig`.
- **Text that isn't valid UTF-8:** `parse_csv` turns a decode failure into `LedgerError(<line where decoding failed>, "file is not valid UTF-8")`, so the CLI exits 3.
- **Decimal context:** all arithmetic runs in a local context, so the results are deterministic whatever the caller's context. Quantize with ROUND_HALF_EVEN to `0.01`, then normalize negative zero to `0.00`.
- **Ordering:** categories are sorted by absolute rounded total descending, then name ascending. Sorting on the rounded totals keeps the order consistent with the figures shown.
- **CLI validation:** argparse handles usage errors (exit 2, stderr). An invalid `--month` and `--top` below 1 are rejected by argparse type checks. An unopenable FILE goes through `parser.error`, which also exits 2.
- **Alternatives considered:**
  - A single module: rejected, because it breaks the file-disjoint, layered tickets.
  - A console-script entry: rejected, because it would change `pyproject.toml`, which the spec forbids.
  - In-process CLI tests: rejected, because Scenario 25 requires a subprocess.

## 7. Risks and constraints
- **Repo gate PLAY-G4:** the spec forbids editing CHANGELOG, and the gate blocks any PR that does not touch it. Every ticket's PR will be flagged, so a human must waive it knowingly. This is the main delivery risk.
- **Python versions:** argparse on 3.10 needs `dest=` on the subparsers and an explicit `prog`. The date and month checks must not depend on the version.
- **Fixture bytes:** the BOM in `bom_blank.csv` and the zero-byte `empty.csv` must survive commits, and the repo has no `.gitattributes`.
- **Scale:** a single pass, in memory. A personal ledger is small, so there is no performance concern. Security: the program reads only the path the user gives it, and there is no network access.
