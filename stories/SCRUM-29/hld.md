# High-Level Design — Monthly expense report from a CSV ledger (SCRUM-29)

## 1. System Overview

- **What:** a new stdlib-only package `ledger` at `src/ledger/` in play1. It parses a UTF-8 CSV ledger into validated, frozen transactions, builds a deterministic one-month report in a base currency (ILS/USD/EUR), and exposes `python -m ledger report FILE --month YYYY-MM [--base] [--top] [--json]`.
- **Problem:** get a monthly summary from the terminal. A malformed row must be reported by physical line number, never turned into a silently wrong total.
- **Responsibilities:** parsing + validation (t1), aggregation + money arithmetic (t2), command line + exit-code contract (t3).

## 2. Architecture Overview

- **Fits the existing repo as-is:** `pyproject.toml` already discovers every package under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets `testpaths = ["tests"]`. `python -m ledger` therefore needs only `src/ledger/__main__.py`, with no manifest change, no `[project.scripts]` entry and no new dependency. Existing packages (`src/testbed_utils/`, `src/guestbook/`) are untouched.
- **Modules (all new):**
  - `src/ledger/__init__.py` holds the public re-exports. t1 creates it; t2 and t3 each add their own exports (sequential handoff).
  - `src/ledger/model.py` + `src/ledger/parser.py` hold `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` and the supported-currency set (t1).
  - `src/ledger/report.py` holds `RATES`, `CategoryTotal`, the report value with `to_dict()`, and `monthly_report` (t2).
  - `src/ledger/cli.py` + `src/ledger/__main__.py` hold argparse, rendering and exit codes (t3).
  - The exact split of files inside `src/ledger/` is the implementer's choice. The rule that matters is the ownership lane per ticket in `work-items.md`.
- **Tests:** `tests/test_ledger_parser.py` (t1), `tests/test_ledger_report.py` (t2), `tests/test_ledger_cli.py` (t3). Fixtures go under `tests/fixtures/ledger/`. The suite imports through the installed distribution only: there is no `conftest.py` and no `sys.path` manipulation (`.factory/testing.md`).
- **External dependencies:** none. The package uses stdlib `csv`, `decimal`, `datetime`, `dataclasses`, `re`, `argparse` and `json`. It must work on Python ≥ 3.10 (`requires-python`); CI runs 3.12 (`.github/workflows/ci.yml`).

## 3. Data Flow Design

All processing is synchronous and in-process, with no I/O beyond reading one file:

1. CLI (`python -m ledger report …`): argparse validates `--month` / `--base` / `--top` and exits 2 on a usage error.
2. The CLI calls `parse_csv(FILE)`, which opens the file with `encoding="utf-8-sig"` and `newline=""` and passes it to `parse_lines`. A file that cannot be opened or is not valid UTF-8 exits 2. A `LedgerError` exits 3.
3. `parse_lines` reads the header (matching columns by name), then each record. It skips blank lines but counts them, validates each row in a fixed order, and stops at the first bad row. It returns `list[Transaction]` in file order.
4. `monthly_report(transactions, month, base, top, rates)` filters to the month and converts each amount at full `Decimal` precision. It sums income, expense, net and per-category totals exactly, quantizes each figure once with `ROUND_HALF_EVEN`, then orders and truncates the categories.
5. The CLI renders the report as text (fixed lines) or as JSON (`report.to_dict()`) to stdout and exits 0.

## 4. Component Breakdown

| Component | Responsibility | Inputs → Outputs | Repo / ticket |
|---|---|---|---|
| Model & parser | Header matching, row validation, `LedgerError(line, reason)`, two entry points | path or iterable of lines → `list[Transaction]` | play1 / t1 |
| Monthly report | Month filter, conversion, exact sums, one rounding, ordering, top-N, `to_dict()` | transactions + month/base/top/rates → report value | play1 / t2 |
| Command line | argparse, text/JSON rendering, exit codes 0/2/3, `__main__` | argv + FILE → stdout/stderr + exit code | play1 / t3 |

## 5. Interface Contracts

The spec names these as public (in-process Python API, re-exported from `ledger`):

- `parse_csv(path)` and `parse_lines(lines)` → `list[Transaction]`. `Transaction` is a frozen dataclass with fields `id`, `date`, `amount`, `currency`, `category`, `memo` (AC 1).
- `LedgerError(line, reason)` has `.line` and `.reason` attributes and `str()` == `line {line}: {reason}` (AC 5).
- `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` returns a report with `month`, `base`, `count`, `income`, `expense`, `net` and `categories` (a list of `CategoryTotal(name, total, count)`), plus `to_dict()` (AC 9, 15). `RATES` = `{"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}` (AC 10).
- CLI: `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
  - Success: exit 0, report on stdout, empty stderr.
  - Usage error: exit 2, empty stdout, a message on stderr.
  - Data error: exit 3, empty stdout, stderr exactly `error: {FILE}:{line}: {reason}\n`.
  - Text format per AC 19/21. JSON keys per AC 20, with amounts as strings.
- No cross-repo contracts.

## 6. Key Technical Decisions

- **Strict lexical validation before `Decimal` / `date`.** Amount and date text are matched against ASCII-only patterns first, because the stdlib is laxer than the spec (verified on Python 3.13):
  - `Decimal("1_000")` → 1000, `Decimal("1e2")` → `1E+2`, and `Decimal("NaN")` / `Decimal("Infinity")` all parse.
  - `date.fromisoformat("20260301")` succeeds on 3.11+.
  - `re` `\d` matches non-ASCII digits such as `２０２６`.
  - The grammar is therefore pinned: an amount is an optional `+`/`-` sign, ASCII digits, and optionally a `.` followed by ASCII digits. A date is `[0-9]{4}-[0-9]{2}-[0-9]{2}`.
- **Decimal places are counted as written.** `1.500` has three decimal places and is rejected. `12000.00` is kept as `Decimal("12000.00")` (AC 1).
- **Arithmetic in a local decimal context.** The report computes in `decimal.localcontext()` at the default precision (28) with `ROUND_HALF_EVEN`. Its figures therefore do not depend on, and do not change, the caller's thread context. 28 digits is far beyond the two places the report needs.
- **One rounding per figure.** Exact sums are quantized to `0.01` once each, independently (AC 11).
- **argparse is used for usage errors.** It already exits 2 with usage on stderr, and `--help` goes to stdout with exit 0. A FILE that cannot be opened is turned into the same exit-2 path by the CLI. The CLI never lets a traceback escape for the cases listed in §7.
- **Alternatives rejected:**
  - Third-party CSV/money libraries, because the spec requires stdlib only.
  - A `[project.scripts]` console entry, because it changes an existing file and the spec only asks for `python -m ledger`.
  - Float arithmetic, because it is non-deterministic for money.

## 7. Edge Cases Settled by This Design

The spec leaves these cases open; this design settles each one and the owning ticket carries it as an acceptance criterion.

**Parser (t1)**
- **Line numbers.** Lines count physically from 1, and blank lines count. A record's line is the line it *starts* on. For a quoted field spanning lines, `csv.reader.line_num` reports the end line, so the implementation must track the start. A row that fails reports that start line.
- **Blank lines.** A blank or whitespace-only line is skipped wherever it appears, including before the header. A line of commas only (`,,,,,`) is a data row, not a blank line, and fails as `empty id`.
- **Header.** The header is the first non-blank line. Header names are trimmed and matched case-sensitively, so `Amount` is not `amount` and the missing `amount` column is reported. A file that is empty, or blank throughout, raises `LedgerError(1, "missing header")`. Missing columns are listed in canonical order (AC 7).
- **Duplicate header names (spec A3).** A header naming a required column twice raises `LedgerError(<header line>, "duplicate column(s): amount")`. Names are listed in canonical order. Duplicated extra columns are ignored.
- **BOM.** `parse_lines` also strips a leading U+FEFF from the first line, so `parse_lines` and `parse_csv` behave identically on the same text (AC 8).
- **Field count.** The reason is `expected {N} fields, got {M}`, where N is the header's field count, extra columns included. This is checked first for a row.
- **Validation order within a row.** The first failing check wins: field count, empty id, date format, calendar date, amount is a number, amount has at most 2 places, amount non-zero, currency, empty category, duplicate id. The duplicate-id check runs only on an otherwise valid row.
- **Amount grammar.**
  - Accepted: an optional sign, ASCII digits, and optionally `.` followed by digits, after trimming.
  - Rejected with `amount '<text>' is not a number` (the reason quotes the trimmed text): `NaN`, `Infinity`, `1e2`, `1_000`, `5.`, `.5`, empty text, and non-ASCII digits.
  - `+5` → `Decimal("5")`.
  - `-0.00` and `0` → `amount must not be zero`.
  - `1.500` → `amount '1.500' has more than 2 decimal places`.
- **Date grammar.** The text must match `[0-9]{4}-[0-9]{2}-[0-9]{2}` (ASCII only). `20260301` and `2026-3-1` get the "is not YYYY-MM-DD" reason. A matching text that is not a real date gets "is not a calendar date".
- **Currency.** Exact, case-sensitive membership in `ILS`, `USD`, `EUR`, after trimming.

**Report (t2)**
- **Negative zero.** A quantized figure that comes out as `-0.00` is normalised to `0.00`. Example: -0.01 ILS in base EUR is exactly -0.0025, which rounds to `-0.00`.
- **Ordering and ties.** Categories are ordered by the absolute value of the *rounded* total, descending, then by name ascending (code-point order, case-sensitive). The displayed order therefore always agrees with the displayed figures.
- **Missing rate.** A transaction whose currency has no entry in `rates` raises `ValueError` naming the currency. This is a caller error, like an unknown `base`.
- **`top`.** `top` must be `None` or an `int` ≥ 1. `bool` and other types raise `ValueError`.
- **`month`.** `month` must fully match `[0-9]{4}-(0[1-9]|1[0-2])` (ASCII only). Anything else raises `ValueError`.

**CLI (t3)**
- **Unreadable FILE.** A FILE that does not exist, is a directory, cannot be read for lack of permission, or is not valid UTF-8 (spec A2) exits 2. stdout is empty and stderr gets one message naming the file. No traceback is printed.
- **Usage validation.** `--month` is validated with the same rule as the report, and a bad value exits 2 through argparse. `--base` choices are exactly `ILS`, `USD`, `EUR`, case-sensitive. `--top` must be an integer ≥ 1. A missing subcommand exits 2.
- **Output.** stdout is written only after parsing and the report succeed, so an error never leaves a partial report.
  - Text: one line per item with `\n` endings and no trailing blank line.
  - JSON: a single `json.dumps(report.to_dict())` line followed by `\n`, with default ASCII escaping, so the bytes are deterministic.

## 8. Risks, Constraints & Assumptions

- **Repository gates (apply to every work item).**
  - Layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): source goes under `src/`, tests under `tests/`, and no file may exceed 200 KB.
  - **Rule 4 / `PLAY-G4`:** every PR adds one line under `## Unreleased` in `CHANGELOG.md`. t1, t2 and t3 each add their own line (spec A1). They run sequentially, so the edits to `CHANGELOG.md` never collide.
  - Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`): `pip install -e ".[test]"`, then `pytest` on Python 3.12. No linter or formatter is configured.
- **Claims glossary** (`.factory/plugins/claims-dev/skills/glossary/SKILL.md`): it covers invoice/claims code and does not apply to this personal-ledger package. The spec's names (`Transaction`, `income`, `expense`, `net`) are kept.
- **Fixture risk (RK).** `tests/fixtures/ledger/sample.csv` must reproduce AC 9, 10, 13, 16 and 20 exactly.
  - Verified arithmetic: a salary of 12000.00 ILS and a freelance of 250.00 USD (= 925.00 ILS) give USD income 3493.24.
  - Expense -3025.50 ILS converts to -817.70 USD, and net 9899.50 ILS converts to 2675.54 USD.
  - Any USD/EUR expense rows must convert exactly (e.g. 120.00 USD = 444.00 ILS, 80.25 EUR = 321.00 ILS), so the ILS figures stay as AC 9 states.
  - t1 owns the fixture and t2 asserts the figures against it, so a wrong fixture fails in t2 at the latest.
- **Scale.** The whole ledger is read into memory, in a single pass and at O(rows) cost. That is fine for a personal or small-team ledger. Streaming and very large files are out of scope.
- **Security.** The command reads exactly the file path the user gives and evaluates nothing. It makes no network access (rates are fixed), uses no configuration and writes no files.
- **Python versions.** The package must use nothing newer than Python 3.10 (`requires-python >=3.10`), even though CI runs 3.12.
- **Assumptions carried from the spec.**
  - **A1:** each PR adds one `CHANGELOG.md` line.
  - **A2:** a non-UTF-8 FILE exits 2.
  - **A3:** a duplicate required column is rejected, settled in §7.
  - The epic PRD/backlog (R1–R5, RK1, RK2) were not supplied. This design relies on the story text alone.
