# High-Level Design — SCRUM-12: Monthly expense report from a CSV ledger

## 1. System overview
- **What:** a new standard-library-only Python package `ledger` in `play1`. It parses a UTF-8 CSV ledger into immutable transactions, validates every row, builds a monthly report by category in a base currency (ILS, USD or EUR), and exposes it through a Python API and `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`.
- **Problem:** today you need a spreadsheet to total a month, and a malformed row silently produces a wrong total. The tool gives a deterministic summary, and a bad row is reported by its physical line number instead.
- **Responsibilities:** parsing and validation (R1, R2), aggregation and conversion (R3, R4), and the terminal interface with exit codes 0, 2 and 3 (R5).

## 2. Architecture overview
There is one repository, `play1`, and one new package, `src/ledger/`, made of three layered modules. Each layer imports only the layers below it.

| Layer | Module (indicative) | Depends on | Owner ticket |
|---|---|---|---|
| Model and parser | `src/ledger/parser.py` (the transaction type, the error type, both parse entry points) | stdlib (`csv`, `decimal`, `datetime`, `re`, `dataclasses`) | t1 |
| Report | `src/ledger/report.py` (rates constant, report and category-total types, `monthly_report`) | the parser layer's transaction type | t2 |
| CLI | `src/ledger/cli.py` and `src/ledger/__main__.py` | parser and report | t3 |
| Public API | `src/ledger/__init__.py` re-exports the public names | all of the above | t1 creates it, t2 extends it |

- **External dependencies:** none. Stdlib only, with pytest from the existing `[test]` extra.
- **Packaging:** `[tool.setuptools.packages.find] where = ["src"]` already discovers the new package. `pyproject.toml`, `[project.scripts]` and CI stay as they are.
- **Repo conventions:** code under `src/` and tests under `tests/` as `test_ledger_*.py`. Fixtures go in `tests/fixtures/ledger/`. Tests are grouped in `class Test…` and find fixtures through `pathlib.Path(__file__).parent / "fixtures"`. There is no `conftest.py` and no `sys.path` manipulation.

## 3. Data flow
Everything runs synchronously in one process. There are no events, I/O beyond reading one file, or network calls.
1. **CLI:** argparse parses the arguments. A usage error exits 2 with nothing on stdout.
2. **CLI → parser:** `parse_csv(FILE)` opens the file with `utf-8-sig` and `newline=""` and delegates to `parse_lines`. If the file can't be opened or contains invalid UTF-8, the CLI exits 2. The decode error is caught around the whole parse, because it can surface partway through iteration.
3. **Parser:** `csv.reader` reads the rows and the physical line of each row is tracked. Blank and whitespace-only rows are skipped. The header is mapped by name, then each row is validated in file order. The first bad row raises the data error with its line and reason.
4. **Report:** transactions are filtered to the month. Each amount is converted exactly as `amount × rates[currency] ÷ rates[base]`. The exact values are summed into income, expense, net and per-category totals, and each figure is quantized once to `0.01` with `ROUND_HALF_EVEN`. Categories are sorted by absolute total descending, then by name, and then truncated to `top`.
5. **CLI output:** the report is printed as the fixed text layout or as JSON from `to_dict()`, with exit 0. A ledger data error prints `error: {FILE}:{line}: {reason}` on stderr and exits 3.

## 4. Component breakdown
- **Model and parser (t1, repo `play1`)**
  - **In:** a path, or any iterable of text lines.
  - **Out:** a list of frozen transactions in file order, or a data error carrying `line` and `reason`, whose `str()` is `line {line}: {reason}`.
  - **Validation:** the exact reason strings of criteria 5–7. The data error is not a subclass of `ValueError`, so tests can tell it apart from caller errors.
- **Monthly report (t2, repo `play1`)**
  - **In:** transactions, month, base, top and rates.
  - **Out:** an immutable report with `month`, `base`, `count`, `income`, `expense`, `net` and the categories (name, total, count), plus `to_dict()`, which renders amounts as two-place strings.
  - **Caller errors:** invalid arguments raise `ValueError`.
- **CLI (t3, repo `play1`)**
  - **In:** argv.
  - **Out:** stdout, stderr and an exit code. `__main__.py` makes `python -m ledger` the real entry point.

## 5. Interface contracts
- **Python API:** exported from `ledger`, with the shapes fixed by the spec: `parse_csv(path)`, `parse_lines(lines)`, `Transaction`, `LedgerError(line, reason)`, `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`, `CategoryTotal(name, total, count)`, `RATES`, and the report's `to_dict()`.
- **CLI:** `python -m ledger report FILE --month YYYY-MM [--base {ILS,USD,EUR}] [--top N>=1] [--json]`.
  - **Exit 0:** the report on stdout, nothing on stderr.
  - **Exit 2:** a usage error; nothing on stdout, a message on stderr.
  - **Exit 3:** a data error; nothing on stdout, and stderr is exactly `error: {FILE}:{line}: {reason}\n`, with FILE as the user typed it.
- **Text layout:**
  - Seven lines: `month:`, `base:`, `transactions:`, `income:`, `expense:`, `net:` and `categories:`.
  - Then one `  name: total (count)` line per category.
  - An empty month prints `categories: none`.
- **JSON layout:** `{month, base, count, income, expense, net, categories:[{name,total,count}]}`. Amounts are strings and counts are integers.
- There are no cross-repo contracts.

## 6. Key technical decisions
- **Decimal everywhere, rounded once.** Exact sums are kept, and each figure is quantized independently. The default Decimal context (28 digits) is enough for ledger magnitudes, so no local context is used.
- **Strict input syntax, using regexes over ASCII digits** (`[0-9]`, not `\d`):
  - **Dates:** the date must match `YYYY-MM-DD` before a `date` is built, so the parser doesn't rely on the permissive `date.fromisoformat` of Python 3.11+.
  - **Amounts:** only an optional sign, digits and an optional fraction are accepted. Underscores, exponents, NaN and Infinity give `is not a number`. More than 2 decimals is a separate reason, and zero (including `-0`) is rejected.
- **Physical line numbers.**
  - Each row's start line is the previous reader `line_num + 1`, so blank lines count and a quoted multi-line row reports its first line.
  - Header errors are reported at the header's own line, which is line 1 in every spec case.
  - Empty input, including input with only blank lines, gives `missing header` at line 1.
- **Three modules instead of one file,** so each work item owns its own file and the dependency direction stays one-way.
- **argparse with required subparsers** (`dest` set, so Python 3.10 gives a proper message). The `type=` validators for `--month` and `--top` and `choices` for `--base` give exit 2 for free. An unopenable or undecodable FILE goes through the parser's error path, also exit 2. Data errors are mapped explicitly to exit 3 without usage text.
- **CLI tests run the real entry point** with `subprocess` and `[sys.executable, "-m", "ledger", …]`. This is new to the repo, but nothing prevents it.
- **Alternatives rejected:**
  - `csv.DictReader` loses control over the field-count check and the line tracking.
  - A console script in `[project.scripts]` would change an existing file, which the spec excludes.
  - `float` is ruled out by the spec.

## 7. Risks and constraints
- **Python floor 3.10, CI on 3.12:** no APIs or behaviour newer than 3.10.
- **Byte-exact output:** criteria 19–23 compare stdout and stderr exactly, including the trailing newline. The sample fixture must reproduce the totals of criteria 9, 10, 16, 19 and 20. Non-ILS rows must convert to exact two-place ILS values, for example −80.25 EUR gives −321.00 ILS and −120.00 USD gives −444.00 ILS.
- **Changelog gate `PLAY-G4`:** exactly one line under `## Unreleased`, owned by t3.
- **Local test runs:** `pip install -e ".[test]"` must be run from this checkout first, because the existing editable install points at another workspace.
- **Review noise:** the repo's claims glossary and reviewer (which define words like "net") cover the invoice code, not this package.
- **Scale and security:** single-file, in-memory, offline. Files are a personal or small-team size. Reading the file is the only I/O, and nothing is fetched.
