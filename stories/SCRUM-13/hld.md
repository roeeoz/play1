# HLD — SCRUM-13: Monthly expense report from a CSV ledger

## 1. System overview
- **What:** a new Python package `ledger` (standard library only) under `src/ledger/` in `play1`. It parses a CSV ledger into immutable transactions and stops at the first bad row, reporting its physical line number. It builds a one-month report in a base currency (ILS, USD or EUR) with exact `Decimal` arithmetic and exposes `python -m ledger report`.
- **Problem:** there is no quick, deterministic monthly total from a CSV ledger, and malformed rows give silently wrong totals.
- **Responsibilities:** parse and validate (R1, R2); aggregate, convert and round (R3, R4); run the command line with text and JSON output and exit codes (R5).

## 2. Architecture overview
It is a single in-process library with a thin CLI layer and no services, I/O beyond reading one file, network access or persistent state.

```
src/ledger/
  __init__.py   public re-exports (Transaction, LedgerError, parse_lines, parse_csv,
                RATES, CategoryTotal, monthly_report)          owner: t1, extended by t2
  model + parser module(s)  Transaction, LedgerError, parse_lines, parse_csv   owner: t1
  report module             RATES, CategoryTotal, report type, monthly_report  owner: t2
  cli module + __main__.py  argparse CLI, output rendering, exit-code mapping  owner: t3
tests/
  test_ledger_parse.py (t1) · test_ledger_report.py (t2) · test_ledger_cli.py (t3)
  fixtures/ledger/ sample.csv, bom_blank.csv, empty.csv (t1) · bad_amount.csv (t3)
```
- **Dependency direction:** cli → report → model/parser. The parser never imports the report or CLI modules, and the report never imports the CLI.
- **External dependencies:** the stdlib only (`csv`, `decimal`, `datetime`, `dataclasses`, `argparse`, `json`, `re`, `sys`). There are no `pyproject.toml` changes, because `src/` packages are auto-discovered.
- Exact module file names inside `src/ledger/` are the implementer's choice. The ownership lanes above are binding.

## 3. Data flow
The flow is synchronous throughout:
1. The CLI parses argv; usage errors exit 2.
2. It opens FILE (`utf-8-sig`, `newline=""`). An OSError or a decode error exits 2.
3. `parse_lines` builds the transaction list. A `LedgerError` exits 3 with `error: {FILE}:{line}: {reason}`.
4. `monthly_report(transactions, month, base, top)` filters to the month and converts each amount at full precision. It sums income (amounts > 0), expense (< 0), net and per-category totals, quantizes each once to `0.01` with ROUND_HALF_EVEN, then orders and slices the categories.
5. The CLI renders text or `json.dumps(report.to_dict())` to stdout only after everything has succeeded, so a failure never leaves partial stdout.

## 4. Components
| Component | Responsibility | In → Out | Repo |
|---|---|---|---|
| Model | `Transaction` (frozen dataclass) and `LedgerError(line, reason)`, where `str` is `line {line}: {reason}` | — | play1 |
| Parser | Header mapping, tolerances, row validation, physical line tracking | iterable of text lines or a path → `list[Transaction]` | play1 |
| Report | Filter, convert, sum, round, order, top-N, `to_dict()`, caller `ValueError`s | transactions and arguments → report (frozen) | play1 |
| CLI | argparse `report` subcommand, rendering, exit codes 0/2/3 | argv → stdout, stderr, exit code | play1 |

## 5. Interface contracts
**Public library surface** (the names are fixed by the spec):
- `Transaction`, `LedgerError` (with `.line` and `.reason`), `parse_lines(lines)` and `parse_csv(path)`.
- `RATES`, `CategoryTotal(name, total, count)` and `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.
- The report has `month`, `base`, `count`, `income`, `expense`, `net`, `categories` and `to_dict()`.

**Exception typing:**
- `LedgerError` is a data error. It may subclass `ValueError`, so the CLI must handle it before any generic `ValueError` or decode-error handler.
- Report argument errors are plain `ValueError`.

**CLI contract:** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- Text output is exactly the line format of Scenarios 19 and 21.
- JSON output is the `to_dict()` object.
- Exit codes are 0, 2 and 3, as in FR16.

There are no cross-repo contracts.

## 6. Key technical decisions
**Line tracking**
- Read with `csv.reader` and use its `line_num`. A record's line is the previous `line_num` + 1, i.e. its first physical line, which holds for multi-line quoted fields too.
- Rows that are `[]` or contain only whitespace cells are skipped, but they still count as lines.

**BOM**
- `parse_csv` uses `utf-8-sig`.
- `parse_lines` also strips a leading `\ufeff` from the first header cell, so the two entry points behave identically (Scenario 8).

**Header**
- Cells are trimmed and matched by exact name. If a named column repeats, its first occurrence is used.
- Missing columns are listed in canonical order.
- Field-count validation compares each row against the header's own cell count (A3), with empty trailing cells counted.

**Within-row check order** (first failure wins, deterministic):
1. Field count.
2. Empty id.
3. Duplicate id, which names the first line seen.
4. Date: an ASCII `YYYY-MM-DD` shape check, then a calendar check.
5. Amount:
   - an ASCII shape check `[+-]?digits[.digits]`, which rejects `NaN`, `Infinity`, exponents, underscores and non-ASCII digits as "not a number";
   - then more than two decimal places;
   - then zero.
6. Currency, case-sensitive against ILS, USD and EUR.
7. Category.

**Money**
- `Decimal` is used end to end in the default 28-digit context.
- Conversion is `amount × rates[cur] ÷ rates[base]` per transaction, with no intermediate rounding.
- Each figure is quantized once, independently. Figures always carry two decimal places.

**Ordering:** sort by (−|total|, name) on the exact or quantized total. Rounding never reorders unequal exact totals in practice, so sorting on the quantized total is acceptable; the implementer documents the choice.

**Month validation:** ASCII `^\d{4}-(0[1-9]|1[0-2])$`. Anything else raises `ValueError`. A `base` not in `rates`, or `top < 1`, also raises `ValueError`.

**CLI**
- Uses `add_subparsers(required=True)`, `choices` for `--base`, and custom argument types for `--month` (reusing the same month rule) and `--top` (an integer ≥ 1).
- A file that cannot be opened or decoded is reported as a usage error: exit 2, a one-line stderr message, no traceback.

**Alternatives rejected**
- A hand-rolled line splitter (breaks CSV quoting).
- Using `Decimal()` acceptance alone as the number test (too permissive).
- A console-script entry (needs a `pyproject.toml` edit).

## 7. Risks & constraints
**Python floor:** Python ≥ 3.10 (CI runs 3.12, locally 3.13). No 3.11+-only APIs; `date.fromisoformat` is only called after the regex check.

**CHANGELOG gate vs. the spec**
- Repo gate PLAY-G4 requires a CHANGELOG line per PR, while the spec forbids changes to existing files.
- Following PLAY-175's precedent, each ticket adds exactly one `## Unreleased` line as the only touch to an existing file. The three tickets are sequential, so the file is handed over in order.

**Editable installs**
- A package added after `pip install -e` may need a re-install locally. CI installs fresh.
- Subprocess tests run with `cwd` at the repo root and pass explicit fixture paths, so a stray `ledger` folder in some other working directory can't shadow the package.

**Shared fixture:** `sample.csv` (owned by t1) must reproduce every figure in Scenarios 9, 10, 13, 16, 19 and 20. These are checked downstream by t2 and t3:
- freelance is 250.00 USD;
- all other March rows are ILS-exact;
- February has groceries at −99.99;
- one April row.

**Scale:** single-user files are parsed fully into memory, which is fine at ledger sizes. There are no performance or security surfaces beyond reading one user-supplied path.
