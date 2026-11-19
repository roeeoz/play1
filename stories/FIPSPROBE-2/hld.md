# HLD — FIPSPROBE-2: Read and validate a CSV ledger

## 1. System overview
- **What:** a new stdlib-only Python package `ledger` in `src/ledger/` of `roeeoz/play1`. It turns a UTF-8 CSV ledger into a list of transactions, in file order, with exact decimal amounts. It stops at the first malformed row and reports that row's physical line number and one fixed reason text.
- **Problem:** a row that is skipped or misread without warning makes a month's total wrong (RK1). This story is the trust layer that the report (FIPSPROBE-3) and the command line (FIPSPROBE-4) build on.
- **Responsibilities:**
  - read the file or the lines
  - check the header
  - check every row against the field rules
  - build the transactions
  - own the reason-text contract (RK2)
  - keep unreadable files separate from data errors

## 2. Architecture overview
- **One package, two layers.** Everything is in `roeeoz/play1`, repo `7054ee13-6ea2-4b4b-a4e4-db1f17cec6b8`.
  - **Public surface** (`src/ledger/__init__.py`, listed in `__all__`): `parse_csv`, `parse_lines`, `Transaction`, `LedgerError`, and an error type for unreadable files.
  - **Parsing and validation**, in module(s) of the implementer's choosing under `src/ledger/`:
    - one reader that walks the CSV records and tracks the line each record starts on
    - pure per-field rule functions, following the repo's "rules in pure functions" convention (`src/guestbook/validation.py`)
    - all reason texts kept in one place, as constants or format strings
- **Boundaries:**
  - This story owns `src/ledger/__init__.py` and the parsing modules.
  - FIPSPROBE-3 adds the report module later and only imports `Transaction`.
  - FIPSPROBE-4 adds `__main__.py` and the command line, and only imports the parse functions and the error types.
- **External dependencies:** none. The package uses only the standard library (`csv`, `decimal`, `datetime`, `re`, `dataclasses`). `pyproject.toml` already finds packages under `src/`.

## 3. Data flow
1. `parse_csv(path)` opens the file as `utf-8-sig` with `newline=""` and reads and decodes all of it. An `OSError` or `UnicodeDecodeError` becomes the unreadable-file error. Because the whole file is decoded first, a bad byte later in the file can never hide behind an earlier data error.
2. The decoded content goes to `parse_lines` as lines that keep their endings. Both functions share one code path, which guarantees AC21.
3. `parse_lines(lines)` prepares the lines:
   - it drops a leading `\ufeff` from the first line
   - it adds `\n` to any line that has no ending, so a quoted field that spans lines comes out the same with either input form
4. It feeds the lines to a strict `csv.reader`. A record's start line is the previous `line_num + 1`.
5. A record is blank if it is `[]` or a single field that is empty after trimming. Blank records are skipped.
6. The first non-blank record is the header. It is checked, and each required column is mapped to its position.
7. Each later record is trimmed field by field and checked in a fixed order. It either becomes a `Transaction` or immediately raises `LedgerError(line, reason)`.
8. If every row is valid, the function returns a list of `Transaction`s. If there is an error, it returns nothing.

Everything is synchronous and in memory. There are no events.

## 4. Components
| Component | Responsibility | In / Out | Repo |
| --- | --- | --- | --- |
| File reader (`parse_csv`) | Open and decode the file; keep unreadable input separate from data errors | path → list of `Transaction`, or an error | roeeoz/play1 |
| Line parser (`parse_lines`) | Drop the BOM, track record start lines, skip blank lines, check the header, check rows | iterable of str → list of `Transaction`, or `LedgerError` | roeeoz/play1 |
| Field rules | Pure checks per field (id, date, amount, currency, category, field count) | trimmed value → cleaned value, or a reason | roeeoz/play1 |
| `Transaction` | Immutable record | — | roeeoz/play1 |
| `LedgerError` and the unreadable-file error | Error types; the contract with FIPSPROBE-4 | — | roeeoz/play1 |

## 5. Interface contracts (shared with FIPSPROBE-3 and FIPSPROBE-4)
- **`parse_csv(path)`** takes a `str` or an `os.PathLike`.
- **`parse_lines(lines)`** takes an iterable of `str`, with or without line endings.
- Both return a `list[Transaction]` in file order, and both raise the same `LedgerError` for the same content.
- **`Transaction`** is a frozen dataclass with these fields:
  - `id: str`
  - `date: datetime.date`
  - `amount: decimal.Decimal`: exactly as written; negative is an expense, positive is income, zero is allowed
  - `currency: str`: one of `ILS`, `USD`, `EUR`
  - `category: str`
  - `memo: str`, which may be empty

  All text values are trimmed. Extra columns are not kept.
- **`LedgerError(Exception)`** has `.line: int` and `.reason: str`, and `str(e) == f"{line}: {reason}"`. Its `args` match its `str()`.
- **Unreadable-file error:** a separate exception type that does not inherit from `LedgerError`. It wraps the underlying `OSError` or `UnicodeDecodeError` as its cause and carries a readable message. FIPSPROBE-4 maps it to exit code 2 and `LedgerError` to exit code 3.
- **Reason texts (the contract):**
  - Header problems, always on line 1:
    - `missing header`
    - `missing column '{name}'`
    - `duplicate column '{name}'`
  - Row problems:
    - `row has {n} fields, expected {m}`
    - `empty id`
    - `duplicate id '{value}' (first seen on line {line})`
    - `invalid date '{value}'`
    - `amount '{value}' is not a number`
    - `amount '{value}' has more than 2 decimal places`
    - `unknown currency '{value}'`
    - `empty category`
    - and `malformed CSV record`, pending PO confirmation (see §6)

## 6. Key technical decisions
- **Validation order** for a row with several problems: field count, then id (empty, then duplicate), then date, then amount (not a number, then decimal places), then currency, then category. The first failure is reported.
- **Header checks:**
  - Names are trimmed and compared exactly, case-sensitively.
  - Missing columns are checked first, in the order id, date, amount, currency, category, memo. Duplicate required columns are checked next, in the same order.
  - Extra columns are ignored, even if they repeat.
  - Header errors are reported on line 1, as FR2 says.
- **Amount:** the trimmed value must match the ASCII pattern `^[+-]?[0-9]+(\.[0-9]+)?$`, or the reason is "not a number". More than two digits after the point gives "more than 2 decimal places". Only then is the value passed to `Decimal(value)`. `\d` is never used, and no float is ever created. `12.`, `.5`, `1e3`, `NaN` and `1_000` are rejected, and `+3` becomes `Decimal('3')`.
- **Date:** the value must match the ASCII pattern `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` before `date.fromisoformat` is called. Without this, Python 3.10 and 3.12+ disagree on inputs such as `20260301`.
- **Duplicate ids:** trimmed ids are compared exactly and case-sensitively. The parser remembers the line where each id was first seen.
- **Blank line:** a record that is `[]` or a single whitespace-only field. A line like `,,,,,` is not blank and is reported as `empty id`.
- **Strict CSV reader:** a `csv.Error` (bad quoting, an unclosed quote at the end of the file, or the field-size limit) becomes `LedgerError(record_start_line, "malformed CSV record")`. A lenient reader would quietly corrupt fields, which goes against R2.
- **Read the whole file first rather than streaming it,** so unreadable input always wins over data errors (FR8, AC20). Ledgers are small personal files.
- **Alternatives considered and rejected:**
  - Letting `OSError` or `UnicodeDecodeError` through: FIPSPROBE-4 would then have to know about stdlib exception types.
  - A `ValueError` wrapper, as in `numsummary`: it would be easy to confuse with other `ValueError`s.
  - Making `parse_csv` accept a stream: no consumer needs it.

## 7. Risks and constraints
- **Reason texts drifting (RK2):** all texts live in one place, and tests assert the exact strings.
- **Float leaking in (RK1):** no float is used, and tests assert that `type(amount) is Decimal` and that the value is exactly what was written.
- **Stdlib behaviour that differs by Python version:** handled by the ASCII patterns. CI runs 3.12, and the package supports `>=3.10`.
- **AC21 is fragile** around the BOM and line endings. The shared code path, plus a test that runs both functions on the same fixture, covers it.
- **Size:** the whole file is held in memory. That is fine for personal ledgers, and there is no scale requirement.
- **Repo gate:** the PR must add a line under `## Unreleased` in `CHANGELOG.md` (rule PLAY-G4), and no file may exceed 200 KB. `pytest` is the only quality gate.
