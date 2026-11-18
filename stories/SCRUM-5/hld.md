# HLD: SCRUM-5, monthly expense report from a CSV ledger

## 1. System overview
- **What is built:** a new Python package, `ledger`, under `src/` in `play1`. It uses only the standard library.
- **The command:** `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`. It reads a CSV ledger and prints a deterministic monthly summary.
- **What each layer does:**
  - **Parse:** reads the file strictly and stops at the first bad row with an error that gives the line number.
  - **Report:** totals one month by category using exact `Decimal` arithmetic, converts currencies at fixed rates and rounds each figure once.
  - **Command line:** prints the report as text or JSON and exits with code 0, 2 or 3.

## 2. Architecture and boundaries
The modules have one-way dependencies: model ← parser ← report ← cli ← `__main__`.

| Module (under `src/ledger/`) | Responsibility | Ticket |
|---|---|---|
| `__init__.py` | Re-exports the public API with `__all__`, following the repository's package convention | t1 creates it, t2 extends it |
| model module | The `Transaction` frozen dataclass and `LedgerError(line, reason)` | t1 |
| parser module | `parse_lines(lines)` and `parse_csv(path)` | t1 |
| report module | `RATES`, `CategoryTotal`, the report value with `to_dict()`, and `monthly_report(...)` | t2 |
| cli module + `__main__.py` | argparse front end, output formatting, exit codes | t3 |

- **Tests:** `tests/test_ledger_*.py`, with fixtures in `tests/fixtures/ledger/`. There is no `conftest.py` and no `sys.path` changes.
- **Unchanged:** `pyproject.toml` already finds packages under `src/`, so it stays as it is. There are no external dependencies.

## 3. Data flow
Everything runs synchronously in one process.
1. The CLI parses its arguments. Any usage error exits 2.
2. It opens FILE as `utf-8-sig` with `newline=""`. If the file can't be opened (an `OSError`, including a directory), it exits 2.
3. `parse_lines` turns the file into a list of `Transaction` values. A `LedgerError` exits 3.
4. `monthly_report` builds the report.
5. The output is formatted in full, and only then written to stdout. This keeps stdout empty on any error.

## 4. Component decisions

### Parser (t1)
- **Reader:** `csv.reader(strict=True)`.
  - Each row's line number is the line where the row *starts*: the previous `line_num + 1`.
  - A leading `\ufeff` on the first line is stripped, so `parse_lines` and `parse_csv` behave the same.
- **Blank rows:** a row with no fields, or where every field is empty after stripping, is skipped. This covers blank lines, whitespace-only lines and comma-only lines. Blank rows still count toward line numbers.
- **Header:**
  - The first non-blank row is the header. If there is none, the error is `LedgerError(1, "missing header")`.
  - Header names are stripped. Columns other than the six named ones are ignored.
  - Missing columns are listed in the canonical order `id, date, amount, currency, category, memo`.
  - A duplicate required column name is a header error with the reason `duplicate column 'id'`.
- **Field count:** the expected count is the number of header columns, giving `expected {len(header)} fields, got {n}`.
- **Order of checks within a row:** field count, id empty, id duplicate, date, amount, currency, category.
- **Dates:** text must match ASCII `YYYY-MM-DD`, or the error is "is not YYYY-MM-DD". It must then be a valid calendar date, or the error is "is not a calendar date".
- **Amounts:**
  - The text must match ASCII `-?[0-9]+(\.[0-9]+)?`. Anything else is "is not a number", including `+`, exponents, `_`, NaN, Infinity and non-ASCII digits.
  - More than two digits after the point gives the decimal-places error. So `1.500` is rejected.
  - A value equal to zero (`0`, `-0`, `0.00`) gives `amount must not be zero`.
  - The value is `Decimal(text)`, so the scale is kept as written (`12000.00`).
- **Currency:** compared case-sensitively against ILS, USD and EUR.
- **Broken input:**
  - A `csv.Error` raises `LedgerError(line, "malformed CSV: <detail>")`.
  - A `UnicodeDecodeError` while reading raises `LedgerError(line, "invalid UTF-8")`, where `line` is the next line to be read.

### Report (t2)
- **Filter:** only transactions whose date is in the requested month count.
- **Conversion:** each amount is converted as `amount × rates[cur] ÷ rates[base]` inside a local `decimal` context (prec ≥ 28), so the result doesn't depend on the caller's global context.
- **Sums:** exact. Income is the sum of positive amounts and expense the sum of negative ones.
- **Rounding:** each figure is quantized to `0.01` with `ROUND_HALF_EVEN` once, independently of the others.
- **Category order:** absolute total descending, then name ascending. Ordering uses the rounded totals.
- **Top-N:** the `top` slice applies to the categories only.
- **Argument checks** (`ValueError`):
  - `month` must match `^[0-9]{4}-(0[1-9]|1[0-2])$`;
  - `base` must be a key of `rates`;
  - `top` must be at least 1.
- **`to_dict()`:** gives the key order month, base, count, income, expense, net, categories. Amounts are written as strings.

### Command line (t3)
- **Argument parsing:** argparse with a required `report` subcommand.
  - `--base` uses `choices=ILS,USD,EUR`.
  - `--month` and `--top` use `type=` validators, so bad values are usage errors (exit 2).
- **File errors:** an open failure goes through `parser.error`, which exits 2 with usage text on stderr.
- **Data errors:** stderr is exactly `error: {FILE}:{line}: {reason}\n`, with FILE as typed, and the exit code is 3.
- **Text output:** the six header lines (`month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:`), then `categories:` followed by one `  name: total (count)` line per category. An empty month prints `categories: none` instead. Thirteen lines in total for the sample month.
- **JSON output:** `json.dumps(report.to_dict())` with a trailing newline.

## 5. Interface contracts (inside the repository only)
- **Parser:** `parse_lines(iterable[str]) -> list[Transaction]`. `parse_csv(path)` returns the same.
- **Report:** `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` returns the report.
- **`LedgerError`:** carries `.line` (int) and `.reason` (str). `str(error)` is `line {line}: {reason}`.
- **CLI contract:** exit codes 0, 2 and 3, and the byte-exact output in spec Scenarios 19–24.

## 6. Fixtures
t1 creates them so that later tickets never need to change them.
- **`sample.csv`:** a header plus nine rows, ids t001–t009.
  - **March 2026, seven rows:**
    - salary 12000.00 ILS;
    - rent -1500.00 ILS;
    - freelance 250.00 USD (= 925 ILS);
    - groceries ×2 in ILS, summing to -760.50;
    - software -120.00 USD (= -444 ILS);
    - travel -80.25 EUR (= -321 ILS).
  - **One row on 2026-02-27:** groceries -99.99 ILS.
  - **One row on 2026-04-01:** any category.
  - **Checked:** these rows give the ILS figures in Scenario 9 and the USD figures in Scenario 20 (3493.24, -817.70, 2675.54, and salary 3243.24).
- **`bom_blank.csv`:** starts with the bytes `EF BB BF`, has blank and whitespace-only lines, one row with an empty memo and one with a quoted memo containing a comma.
- **`empty.csv`:** zero bytes.
- **`bad_amount.csv`** (added in t3): physical line 3 has the amount `-2.505`.

## 7. Risks and constraints
- **`PLAY-G4` CHANGELOG blocker:** the spec keeps all existing files unchanged, so every pull request gets this blocker. This is still an open human decision; option (a) is recommended.
- **Local editable install:** the current install points at another workspace. Run `pip install -e ".[test]"` again before running pytest locally. CI is not affected.
- **Python versions:** CI uses 3.12, local is 3.13, and the project allows ≥3.10. The regex checks before `fromisoformat` and `Decimal` keep parsing the same across versions.
- **Subprocess tests:** they run with `cwd` set to the repository root, found from `__file__`, and with fixed relative FILE paths, so the stderr comparison is byte-exact.
- **Scale:** the ledger is small and held in memory. There are no performance or security concerns beyond strict input validation.
