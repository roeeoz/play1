# HLD: `ledger` monthly report (story 609a1854)

## 1. System overview
- **What:** a new Python package `src/ledger/` in roeeoz/play1, using only the standard library, run as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- **Problem:** produce a deterministic monthly summary of a CSV ledger in a chosen base currency. A bad row stops the run with its physical line number and an exact reason, and is never folded into a total.
- **Responsibilities:** parse and validate the CSV, aggregate and convert the figures, and drive the CLI with fixed output and exit codes (0 for success, 2 for usage errors, 3 for data errors).

## 2. Architecture overview
The package has three layers. Each layer imports only the layers before it.

| Layer | Files | Ticket |
|---|---|---|
| Model and parser | `src/ledger/__init__.py`, `src/ledger/parser.py` | t1 |
| Report | `src/ledger/report.py` | t2 |
| CLI | `src/ledger/cli.py`, `src/ledger/__main__.py` | t3 |

- **Discovery:** the existing `[tool.setuptools.packages.find] where=["src"]` setting picks up `ledger` because it has an `__init__.py`. `pyproject.toml` is not edited and no `[project.scripts]` entry is added.
- **Dependencies:** none outside the standard library (`csv`, `decimal`, `datetime`, `re`, `argparse`, `json`, `dataclasses`). Nothing may rely on behaviour newer than Python 3.10.
- **Tests:** `tests/test_ledger_parser.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py`, with fixtures in `tests/fixtures/ledger/` (`sample.csv`, `bom_blank.csv`, `empty.csv`, `bad_amount.csv`). Tests reach the code only through the installed package, matching the existing `package-api` pytest layer, which the CI job runs on Python 3.12.

## 3. Data flow
Everything runs synchronously in one process:
1. The CLI validates its arguments. Any problem is a usage error and exits 2.
2. `parse_csv(FILE)` opens the file with `utf-8-sig` and `newline=""` and passes it to `parse_lines`.
3. `parse_lines` returns a list of `Transaction` values or raises `LedgerError(line, reason)`, which the CLI turns into exit 3.
4. `monthly_report(transactions, month, base, top, rates)` returns a `MonthlyReport`.
5. The CLI prints either the text form or `json.dumps(report.to_dict())` to stdout and exits 0.

On any error, stdout stays empty.

## 4. Components
- **Parser (t1).** Input is an iterable of lines, or a path. Output is a list of `Transaction` values or a `LedgerError`.
  - **Line numbers:** the line where a row starts is the previous `csv.reader.line_num` plus 1. This handles multi-line quoted memos (A2).
  - **Blank lines:** a row is skipped when it is empty or all of its fields are blank. Blank lines before the header are skipped too (A4).
  - **BOM:** a leading `\ufeff` on the first line is removed in `parse_lines` as well as through `utf-8-sig`, so the two entry points behave the same (Scenario 8).
  - **Header:** the header-to-index map is built by hand, so a repeated column name maps to its first occurrence (A3; `DictReader` would keep the last). Names are trimmed and matched case-sensitively (A5).
  - **Missing columns:** reported in canonical order on line 1. An empty file, or one with only blank lines, raises `missing header` on line 1.
  - **Order of checks within a row:** field count against the header's field count (A1), empty id, date, amount, currency, empty category, then duplicate id. The first failure raises.
  - **Dates:** must match the ASCII-only pattern `[0-9]{4}-[0-9]{2}-[0-9]{2}`. Full-width digits and `20260301` are rejected even though Python 3.11's `fromisoformat` would accept them. A well-formed date that doesn't exist on the calendar gets `is not a calendar date`.
  - **Amounts:**
    - The text must be an optional sign, ASCII digits and an optional fractional part. Anything else, including NaN, Infinity, exponents, `_` and full-width digits, gets `is not a number`.
    - More than two digits after the point, counted as written, gets `has more than 2 decimal places`.
    - A value equal to zero, `-0.00` included, gets `must not be zero`.
    - Accepted text becomes a `Decimal` with exactly the text's value.
- **Report (t2).** Input is the transactions, month, base, top and rates. Output is a `MonthlyReport` holding month, base, count, income, expense, net and a list of `CategoryTotal(name, total, count)`, plus a `to_dict()` that returns amounts as strings.
  - **Arguments:** `month`, `base` and `top` are checked first, and any problem raises `ValueError`. `month` must match `[0-9]{4}-(0[1-9]|1[0-2])`.
  - **Conversion:** each amount becomes `amount × rates[cur] ÷ rates[base]` under the default 28-digit context, multiplying before dividing. The global decimal context is never changed.
  - **Rounding:** each figure is summed exactly, then quantized once to `0.01` with `ROUND_HALF_EVEN`, independently of the other figures.
  - **Ordering:** categories are sorted by absolute total descending, then by name ascending. `top` cuts only the categories list.
- **CLI (t3).** Input is argv. Output is stdout, stderr and the exit code.
  - **Arguments:** `argparse` subparsers are set with `dest` and `required=True`, so a missing subcommand exits 2, including on Python 3.10. `--base` takes `choices` and defaults to ILS. `--month` and `--top` use custom `type=` validators. Any problem goes to `parser.error`, which exits 2.
  - **Unreadable FILE:** `OSError` or `UnicodeDecodeError` from `parse_csv` goes to `parser.error` and exits 2.
  - **Data errors:** a `LedgerError` writes `error: {FILE}:{line}: {reason}\n` to stderr, with FILE exactly as typed, and exits 3.

## 5. Interface contracts (inside the package)
- **From `ledger.parser`:** `Transaction`, a frozen dataclass of `id, date, amount, currency, category, memo`; `LedgerError(line, reason)`, whose `str()` is `line {line}: {reason}`; `parse_lines`; `parse_csv`.
- **From `ledger.report`:** `RATES`; `CategoryTotal`; `MonthlyReport` with `to_dict()`; and `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.
- **Re-exports:** `ledger/__init__.py` re-exports the public names of the layers that exist. t2 takes ownership of `__init__.py` to add the report names.
- **Output formats:** the text and JSON layouts must match Scenarios 19–21 byte for byte. JSON keys are emitted in the order `month, base, count, income, expense, net, categories`, with amounts as strings.

## 6. Key technical decisions
- **Text-first amount check** instead of plain `Decimal()` parsing, which accepts `1_000`, `1E+3` and NaN. Trade-off: `1.500` is rejected for having more than 2 decimal places.
- **A plain `csv.reader` with hand-built indexes** instead of `DictReader`. This is what gives first-column-wins (A3), the field-count check (A1) and correct starting line numbers (A2).
- **Usage errors for unreadable files:** `UnicodeDecodeError` is treated as "FILE cannot be opened" (exit 2), because there is no row line number to report.
- **CLI validation reuses the report's month rule** where it can, but the CLI raises `ArgumentTypeError` and exits 2, never with a traceback.
- **The `CHANGELOG.md` line goes in t1**, so the first change set already meets PLAY-G4. It appears exactly once in the story's PR and describes the `ledger` report command.

## 7. Risks and constraints
- **Criterion 26 and the plan folder:** the PR diff will include `stories/609a1854/*`. Those planning documents are treated as outside the criterion, as earlier stories' folders already on `main` show.
- **Changelog conflict:** other stories also edit `## Unreleased`, so a merge conflict on that one line is likely. Resolve it by keeping both lines.
- **Name shadowing:** running `-m ledger` from a directory that contains a `ledger/` folder would load that folder instead of the installed package. CLI tests run from the repo root and pass absolute fixture paths, except where FILE must be shown as typed.
- **Stale local installs:** an older editable install may not see the new package until `pip install -e .` is run again. CI installs fresh.
- **Decimal overflow:** sums that need more than 28 significant digits would make `quantize` raise. This is out of realistic range and not handled.
- **Scope:** no edits to `pyproject.toml`, existing tests or existing fixtures, and no file over 200 KB.
