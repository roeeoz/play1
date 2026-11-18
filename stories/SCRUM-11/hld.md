# HLD — SCRUM-11 Monthly expense report from a CSV ledger

## 1. System overview
- **What:** a new stdlib-only Python package `ledger` in `play1` (`src/ledger/`, tests under `tests/`). It parses and validates a CSV ledger, totals one calendar month by category in a base currency (ILS, USD or EUR), and exposes this both as a library and as `python -m ledger report FILE --month YYYY-MM [--base …] [--top N] [--json]`.
- **Problem:** a spreadsheet gives no deterministic answer and silently turns malformed rows into wrong totals. This package stops at the first bad row and names it by physical line number.
- **Responsibilities:** parse and validate (t1), aggregate and convert (t2), present results and map exit codes (t3).

## 2. Architecture overview
Everything is in one repo (`play1`), as a single in-process package with three layers. Each layer depends only on the one below it:

| Layer | Module(s) | Owner ticket | Depends on |
| --- | --- | --- | --- |
| Model and parser | `src/ledger/parser.py`, `src/ledger/__init__.py` | t1 | stdlib (`csv`, `decimal`, `datetime`, `re`, `dataclasses`) |
| Report | `src/ledger/report.py` | t2 | parser's `Transaction` |
| Command line | `src/ledger/cli.py`, `src/ledger/__main__.py` | t3 | parser (`parse_csv`, `LedgerError`) and report (`monthly_report`, `to_dict`) |

- **External dependencies:** none. No changes to `pyproject.toml`: the existing `packages.find where=["src"]` picks the package up.
- **Package API:** `src/ledger/__init__.py` re-exports the public library API. t1 creates it, and t2 extends it with the report names (an explicit sequential handoff). t3 does not touch it.

## 3. Data flow
Everything is synchronous and in-process; there are no events.
1. The CLI parses its arguments. An argument error exits 2.
2. The CLI opens FILE with `utf-8-sig` and `newline=""`. An `OSError` exits 2.
3. `parse_lines` turns the CSV rows into `list[Transaction]`. The first error raises `LedgerError(line, reason)`, which exits 3 with `error: {FILE}:{line}: {reason}`.
4. `monthly_report` filters by month, converts each amount at full precision, sums the exact values, quantizes each figure once (half-even, two places), orders the categories and applies top-N, producing a `Report`.
5. The CLI prints either the text format or `json.dumps(report.to_dict())` to stdout and exits 0.

## 4. Components
- **Parser (t1).** Input: an iterable of text lines, or a path. Output: an ordered list of frozen `Transaction` values, or a `LedgerError` carrying `.line`, `.reason` and `str() == "line {line}: {reason}"`.
  - Tracks the physical line where each row *starts*, counting blank lines and the header.
  - Skips blank and whitespace-only rows before checking the field count.
  - Matches columns by header name, case-sensitively, and ignores extra columns.
- **Report (t2).** Input: transactions, `month`, `base`, `top`, and `rates` (default: the `RATES` constant). Output: a `Report` holding `month`, `base`, `count`, `income`, `expense`, `net` and a list of `CategoryTotal(name, total, count)`, plus `to_dict()`. Raises `ValueError` for caller errors.
- **CLI (t3).** Input: argv. Output: stdout (report), stderr (messages), exit code 0, 2 or 3. `__main__.py` delegates to the CLI's main function.

## 5. Interface contracts (fixed now, because the next ticket builds on them)
- **`LedgerError`:** an `Exception` subclass with public attributes `line: int` and `reason: str`; `str(e) == f"line {line}: {reason}"`. The CLI depends on `.line` and `.reason`.
- **`Transaction`:** a frozen dataclass with fields `id, date, amount, currency, category, memo`, typed as in spec FR2.
- **`parse_lines(lines)` / `parse_csv(path)`:** signatures as in spec FR1. `parse_csv` must not swallow `OSError`: the CLI turns that into exit 2.
- **`monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`**, `RATES`, and `CategoryTotal(name, total, count)`, as in spec FR5. `Report.to_dict()` returns the keys `month, base, count, income, expense, net, categories`, with money as two-place strings and counts as ints.
- **CLI contract:** spec FR13–FR15 and §4 (the 13-line text format; `categories: none` for an empty month).
- **Cross-repo contracts:** none.

## 6. Key technical decisions
- **Line tracking:** a row's start line is the previous row's `csv.reader.line_num` + 1, so a multi-line quoted row reports its first line.
- **Strict ASCII pre-checks:**
  - Dates must match `[0-9]{4}-[0-9]{2}-[0-9]{2}` before calendar validation. This stops Python 3.11+ from accepting a compact date like `20260301`, so 3.10 and 3.12 behave the same.
  - Amounts must be an optional `-`, ASCII digits, and an optional `.digits` part. Anything else (including NaN, Infinity, exponents, `_`, `+` and non-ASCII digits) is "not a number".
  - After that: more than 2 decimal places → its own reason; a value of zero → `amount must not be zero`.
- **Order of checks** within a row: blank (skip) → field count → date → amount → currency → category → id → duplicate id. A row with several faults reports the first one in this order.
- **Header handling:**
  - The header is the first non-blank line.
  - A zero-byte or entirely blank input raises `missing header` at line 1.
  - Missing columns are listed in canonical order, reported on the header's line (line 1 in every case the spec covers).
  - In `expected N fields, got M`, N is the header's actual field count.
- **BOM:** `parse_lines` strips a leading `\ufeff` from the first line itself. `parse_csv` also opens with `utf-8-sig`, so the two entry points match exactly.
- **Invalid UTF-8:** `parse_csv` turns a `UnicodeDecodeError` into a `LedgerError` with reason `file is not valid UTF-8`, reported on the line being read. The CLI exits 3.
- **Money:** `Decimal` throughout, computed in a local decimal context so a caller who changed the global context can't affect results. Each figure is quantized once with `ROUND_HALF_EVEN`, and negative zero becomes `0.00`.
- **Argument and caller validation:**
  - `month` must match `^[0-9]{4}-(0[1-9]|1[0-2])$`.
  - `base` must be a key of `rates`; `top` must be at least 1.
  - The CLI validates the same rules through argparse (a custom type plus `choices`), so these errors exit 2.
  - `monthly_report` raises `ValueError` itself, so a direct library call is also protected.
- **CLI structure:**
  - argparse with `add_subparsers(dest="command", required=True)`; a usage error exits 2 through `parser.error`.
  - FILE is opened inside the command so `newline=""` can be passed; argparse's `FileType` can't.
  - The CLI follows the repo's `numsummary.py` style for argparse, `from __future__ import annotations`, and a short description.
- **Alternatives rejected:**
  - `argparse.FileType`, which can't pass `newline=""`.
  - Reading columns by position.
  - Accepting whatever `Decimal()` parses (lenient, and varies with input).
  - Rounding each amount before summing (violates FR8).

## 7. Risks and constraints
- **Byte-exact output:** reason strings, the 13 output lines and exit codes are all exact. Off-by-one line numbers on blank or multi-line rows are the main risk (RK1/RK2), so t1 tests pin blank lines, the BOM, duplicate ids across a blank line, and a multi-line memo.
- **Python versions:** the floor is 3.10 but CI runs 3.12, and 3.10 isn't available locally. Avoid 3.11+-only APIs and depend on the ASCII pre-checks rather than `fromisoformat` leniency.
- **Exception boundaries:** `decimal.InvalidOperation` must never escape the parser, and `ValueError` must never be raised as `LedgerError` (or the reverse).
- **Subprocess tests:** they need the editable install (CI's precondition). No `sys.path` hacks; each test runs in roughly 100 ms, well within CI's 5-minute timeout.
- **Fixtures:**
  - `empty.csv` must be committed as a real zero-byte file.
  - `sample.csv` must produce the exact figures in Scenarios 9, 10, 13, 16, 19 and 20. One content set that works: salary 12000.00 ILS; rent -1500.00 ILS; freelance 231.25 EUR; two groceries rows in ILS summing to -760.50; software -120.00 USD; travel -80.25 EUR; groceries -99.99 ILS on 2026-02-27; plus one row on 2026-04-01.
- **Scale:** the whole file is read into memory, which is fine for personal or small-team ledgers. No network access, no persisted state, and no security surface beyond reading a file the user names.
