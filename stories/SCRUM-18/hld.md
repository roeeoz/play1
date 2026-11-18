# SCRUM-18 — High-Level Design: monthly expense report from a CSV ledger

## 1. System overview
- **What:** a new stdlib-only Python package `ledger` in `play1` (`src/ledger/`, tests in `tests/`). It reads a UTF-8 CSV ledger, validates every row, and reports one month's income, expense, net and per-category totals in a base currency.
- **Surfaces:**
  - A Python API: `parse_csv`, `parse_lines` and `monthly_report`, plus `Transaction`, `LedgerError`, `RATES`, `CategoryTotal` and the report type.
  - A CLI: `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- **Responsibilities:**
  - Parse strictly and stop at the first bad row, reporting its physical line.
  - Keep money exact: `Decimal` end to end, rounded once after summing with ROUND_HALF_EVEN.
  - Produce deterministic text and JSON output with distinct exit codes (0, 2, 3).

## 2. Architecture overview
The package has three layers, each depending only on the layer below it:

| Layer | Module(s) | Owner ticket | Depends on |
|---|---|---|---|
| Model and parser | `src/ledger/_parse.py` (name is the implementer's choice), `src/ledger/__init__.py` | t1 | stdlib (`csv`, `decimal`, `datetime`, `re`, `dataclasses`) |
| Report | `src/ledger/report.py` | t2 | the parser layer's `Transaction` |
| CLI | `src/ledger/cli.py`, `src/ledger/__main__.py` | t3 | the parser and report layers' public API |

- **Boundaries:**
  - Only the parser layer raises `LedgerError`.
  - The report layer raises only `ValueError`, for caller errors.
  - The CLI is the only layer that maps errors to exit codes and to stdout/stderr.
- **External dependencies:** none. Packaging is unchanged: `pyproject.toml` already discovers packages under `src/`, and `__main__.py` is enough for `python -m ledger`.
- **Repository conventions:**
  - `__init__.py` re-exports the public API through `__all__`, following `testbed_utils`.
  - Test file basenames are unique (`test_ledger_*.py`) because there is no `tests/__init__.py`.

## 3. Data flow
Everything runs synchronously in a single process:

1. **Read:** the CLI parses the arguments and opens FILE (`utf-8-sig`, `newline=""`).
2. **Parse:** `parse_lines` maps the header by name, skips blank and whitespace-only records while still counting their lines, validates each row, and builds frozen `Transaction`s in file order.
3. **Report:** `monthly_report` filters to the month, converts each amount to the base currency at full precision, sums income, expense, net and each category, quantizes each figure once, sorts categories by absolute total descending then name ascending, and truncates to `top`.
4. **Output:** the CLI renders text or `to_dict()` as JSON on stdout and exits 0.
5. **Errors:**
   - A `LedgerError` becomes `error: {FILE}:{line}: {reason}` on stderr, exit 3.
   - A usage error or an unreadable file becomes a message on stderr, exit 2.
   - In both cases nothing is written to stdout.

## 4. Component breakdown
All components are in repository play1 (`86d449d4-e5db-42c9-8d61-17b798bdd7e2`).

- **Parser (t1)**
  - Inputs: a path, or an iterable of text lines.
  - Outputs: `list[Transaction]`, or `LedgerError(line, reason)`.
- **Report (t2)**
  - Inputs: transactions, `month`, `base`, `top`, `rates`.
  - Outputs: a report value (`month`, `base`, `count`, `income`, `expense`, `net`, `categories`) with a `to_dict()` that gives amounts as strings. Raises `ValueError` for bad arguments.
- **CLI (t3)**
  - Inputs: argv.
  - Outputs: stdout, stderr and the exit code.

## 5. Interface contracts
These are the public names the spec fixes. Everything else is internal.

- **`Transaction`:** a frozen dataclass with fields `id` (str), `date` (`date`), `amount` (`Decimal`, exactly as in the text), `currency`, `category` and `memo` (all str).
- **`LedgerError`:**
  - Carries `.line` (int) and `.reason` (str).
  - `str(error)` is `line {line}: {reason}`.
  - The reason strings are exactly those in criteria 5–7.
- **`parse_csv(path)`:** opens the file with `utf-8-sig` and `newline=""`, then delegates to `parse_lines`.
- **`parse_lines(lines)`:** behaves exactly as `parse_csv`, including stripping a leading BOM.
- **`RATES`:** maps `ILS` → `Decimal("1")`, `USD` → `Decimal("3.70")` and `EUR` → `Decimal("4.00")`.
- **`monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`:**
  - Returns the report.
  - Each category is a `CategoryTotal(name, total, count)`.
  - `to_dict()` matches the shape in criteria 15 and 20.
- **CLI:**
  - Text layout as in criteria 19 and 21. JSON is `to_dict()`.
  - Exit codes: 0 for success, 2 for usage errors and unreadable files, 3 for data errors.
- **Cross-repo contracts:** none.

## 6. Key technical decisions
- **Line tracking:** each record is reported at its *start* line, derived from the reader's line counter before each read, not the end line (A3). Blank and whitespace-only records are skipped but still counted.
- **Strict syntax checks before the stdlib converts:**
  - Dates must match an ASCII `[0-9]{4}-[0-9]{2}-[0-9]{2}` pattern before calendar validation. Python 3.11+ `fromisoformat` alone would accept other forms.
  - Amounts must match a plain decimal pattern (optional sign, ASCII digits, optional fraction). This rejects `NaN`, `Infinity`, `1e2` and `1_000` as "is not a number".
- **Order of checks within a row:** field count, then empty id, date, amount (number, then more than 2 decimal places, then zero), currency (case-sensitive), empty category, and duplicate id last (citing the first line).
- **Header:**
  - An empty input gives `missing header`.
  - Missing columns are listed in the canonical order `id, date, amount, currency, category, memo`.
  - Extra columns are ignored.
  - If a column name appears twice, the first occurrence wins.
  - The field-count message uses the header's own column count (A2).
- **Money:**
  - All arithmetic runs inside a local Decimal context, isolated from the caller's.
  - Each amount converts as `amount × rates[currency] ÷ rates[base]`.
  - Each figure is summed exactly and then quantized once to `0.01` with ROUND_HALF_EVEN, independently of the others.
  - A result of negative zero is shown as `0.00`.
- **CLI:**
  - Built on `argparse`, with a required subparser and type and choices validation, so all usage errors exit 2.
  - `OSError` and `UnicodeDecodeError` while reading FILE are routed to the parser's usage-error path (exit 2).
  - FILE is echoed exactly as typed.
- **Tests:**
  - Parser and report tests are in-process.
  - CLI tests run `subprocess` with `[sys.executable, "-m", "ledger", …]` and a fixed `cwd`.
  - Fixture bytes that tooling may strip (the BOM, whitespace-only lines, the zero-byte file) are asserted in the tests.
- **Alternatives considered:**
  - `csv.DictReader` was rejected: it can't report start lines, and it picks the last duplicate column.
  - Floats were rejected because they lose exactness.
  - A single PR was rejected in favour of three, matching the story's three work items, each mergeable on its own.

## 7. Risks and constraints
- **Multi-line quoted rows:** using the reader's line counter as-is would report a row's end line. The parser must track the start line, and t1's tests cover this.
- **Python 3.10 floor:** `requires-python >=3.10`, so the package must avoid 3.11-only APIs. CI runs 3.12.
- **Fixture fidelity:** there is no `.gitattributes`, so editors or tooling may silently strip the BOM or the whitespace-only lines.
- **PLAY-G4:** every PR adds one SCRUM-18 line under `## Unreleased`. The edits are sequential, with no concurrent edits to `CHANGELOG.md`.
- **Scope:** no existing file other than `CHANGELOG.md` is changed, and the existing test suite must keep passing unchanged.
- **Scale and security:** these are personal ledgers read in one pass in memory, with no network access and no code execution from data, so there are no meaningful concerns.
