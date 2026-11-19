# HLD — PLAY3-2: Read and validate a CSV ledger

## 1. System overview

- **What:** a new stdlib-only package `src/ledger/` that turns a UTF-8 CSV ledger into a list of validated transactions (exact `Decimal` amounts, file order), or stops at the first bad row with `LedgerError(line, reason)` carrying the physical line and one reason text from the spec's FR5 catalogue.
- **Why:** it is the foundation of the epic (PLAY3-1); "Monthly report by category in a base currency" (PLAY3-3) consumes the transactions and "python -m ledger report command line" (PLAY3-4) prints the error unchanged (RK2).
- **Out:** reports, conversion, rounding, `__main__`/CLI, exit codes — PLAY3-3 and PLAY3-4.

## 2. Architecture overview

- **Where it lands (verified in the checkout):** `pyproject.toml` discovers packages with `[tool.setuptools.packages.find] where = ["src"]` and runs pytest from `testpaths = ["tests"]`; sibling packages `src/testbed_utils/` and `src/guestbook/` follow the same pattern (pure functions in a module, tests in `tests/test_*.py` importing the installed package, no `conftest.py`, no `sys.path` tweaks — `.factory/testing.md`). `src/ledger/` does not exist yet on `main` or the work branch, so nothing is changed, only added. No `pyproject.toml` edit is needed: the package is picked up by discovery and has no dependency.
- **Modules:** one package `src/ledger/` — `__init__.py` re-exports the public surface (`Transaction`, `LedgerError`, `parse_csv`, `parse_lines`); the parsing and validation code live in one module beside it (implementer's choice of name, e.g. `parse.py`). PLAY3-3 and PLAY3-4 will add their own modules to the package and import only the public surface.
- **External dependencies:** Python stdlib only (`csv`, `decimal`, `datetime`, `re`, `dataclasses`). Supported runtimes: `requires-python = ">=3.10"`; CI runs 3.12 (`.github/workflows/ci.yml`).
- **Gates the PR meets:** `pip install -e ".[test]" && pytest` (the declared `package-api` layer, `.factory/testing.md`); the play1 layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`: source under `src/`, tests under `tests/`, no file over 200 KB). There is no linter or formatter configured. The claims glossary skill concerns invoice code and does not apply.

## 3. Data flow

All synchronous, in-process, single pass:

1. `parse_csv(path)` opens the file with `encoding="utf-8-sig"`, `newline=""` and hands its lines to `parse_lines`. Opening/reading failures (`OSError`) and undecodable bytes (`UnicodeDecodeError`) propagate unchanged — they are never turned into `LedgerError`, so PLAY3-4 can exit 2 for them and 3 for data errors.
2. `parse_lines(lines)` strips one leading BOM from the first line (so in-memory text decoded with plain `utf-8` behaves like the file), feeds the lines to `csv.reader`, and computes each row's physical start line as `previous reader.line_num + 1` (verified: a row whose quoted memo spans lines 3–4 starts at 3; blank lines are counted).
3. Header: the first non-blank row. Checked, then mapped name → column index.
4. Each later non-blank row is validated in the fixed order of §6 and becomes a `Transaction`; the first failure raises `LedgerError` and nothing is returned.
5. Result: `list[Transaction]` in file order (empty for a header-only ledger).

## 4. Component breakdown

| Component | Responsibility | In / Out | Repository |
| --- | --- | --- | --- |
| `Transaction` record | Immutable record of one validated row | six values → `id: str`, `date: datetime.date`, `amount: decimal.Decimal`, `currency: str`, `category: str`, `memo: str` | roeeoz/play1 |
| `LedgerError` | The one data-error type | `line: int`, `reason: str`; `str(err) == f"{line}: {reason}"` | roeeoz/play1 |
| Header + row validation | FR1–FR6 rules and the FR5 texts | CSV rows with start lines → transactions or `LedgerError` | roeeoz/play1 |
| `parse_lines` / `parse_csv` | The two entry points (FR7) | lines / a path → `list[Transaction]` | roeeoz/play1 |

## 5. Interface contracts

The public surface PLAY3-3 and PLAY3-4 build on, importable as `from ledger import Transaction, LedgerError, parse_csv, parse_lines`:

- `parse_csv(path)` — `path` is a `str` or `os.PathLike`; returns `list[Transaction]`; raises `LedgerError` for a data error; lets `OSError` and `UnicodeDecodeError` propagate (unreadable file ≠ data error, spec §7).
- `parse_lines(lines)` — `lines` is any iterable of `str`, one physical line per item, each with its line terminator as file iteration or `str.splitlines(keepends=True)` yields it (the last may lack one). Same rules, texts and line numbers as `parse_csv`.
- `Transaction` — frozen dataclass with the six fields above; `amount` is the `Decimal` of the text as written (`"1.10"` → `Decimal("1.10")`, sign kept, `"-0"` accepted as zero); `date` is a `datetime.date`; the strings are exactly as written (no trimming).
- `LedgerError(line, reason)` — subclass of `Exception` (deliberately **not** `ValueError`, so a caller catching it never swallows `UnicodeDecodeError`); attributes `line` and `reason`; `str()` is `"{line}: {reason}"`. PLAY3-4 prints `error: {FILE}:{err.line}: {err.reason}`.
- The reason texts are exactly the FR5 catalogue; the quoted part is the value or name as written, rendered with plain single quotes around the raw text (`f"'{value}'"`, not `repr`, so a value holding a quote is not escaped).

## 6. Key technical decisions

Each was settled by running the stdlib (Python 3.14 locally; the behaviours below are the same on 3.12, CI's version, unless noted).

- **Strict ASCII patterns before stdlib parsers.** `Decimal()` alone accepts `1e2`, `NaN`, `Infinity`, `1_000`, `+5`, `.5`, `5.` and Arabic-Indic digits (`١٢`); `date.fromisoformat` accepts `20260301` and `2026-W10-1` on 3.11+; regex `\d` matches non-ASCII digits. So:
  - **amount** must fully match `-?[0-9]+(\.[0-9]+)?` (ASCII digits, optional leading minus, no plus, no exponent, no separators, no spaces) or the reason is `invalid amount '<raw>'`; a match with more than two digits after the point gives `amount '<raw>' has more than 2 decimal places` (so `12.345` and `12.3400` both get the decimals text, `1,200.00` and ` 12.00` the invalid text).
  - **date** must fully match `[0-9]{4}-[0-9]{2}-[0-9]{2}` and be a real calendar date, else `invalid date '<raw>'`.
  - **currency** must equal `ILS`, `USD` or `EUR` exactly, else `unknown currency '<raw>'`.
- **Fixed check order per data row** (the spec left it to this stage): (1) field count `expected {header_count} fields, got {row_count}`; (2) first empty of id, date, amount, currency, category → `missing {name}`; (3) date; (4) amount (invalid, then decimals); (5) currency; (6) duplicate id `duplicate id '<id>' (first seen on line N)`, N being the start line of the first row with that exact id.
- **Header rules.** The header is the first non-blank row; a file with no non-blank row → line 1, `missing header`. Names match exactly (case-sensitive, untrimmed, BOM already removed). Check (1) the first missing required column in the order id, date, amount, currency, category, memo → `missing column '<name>'`; then (2) the first required name appearing twice, in header order → `duplicate column '<name>'`. Extra columns are ignored, including repeated or empty extra names (a trailing comma must not fail a ledger).
- **Blank line** = a physically empty line (the csv reader yields `[]`); it is skipped but counted. A whitespace-only line is a row with one field → `expected 6 fields, got 1`.
- **Line numbers** come from `csv.reader.line_num` (row start = previous `line_num` + 1), so header, blank lines, the BOM line and every line of a multi-line quoted value are counted.
- **CSV field-size limit.** `csv` raises `csv.Error: field larger than field limit (131072)` when a field exceeds 128 KiB — in practice an unterminated quote swallowing the rest of a big file. The catalogue has no text for that, so the parser raises the module's limit (to a value that fits a C long on every platform, e.g. `2**31 - 1`) before reading; the swallowed row then fails within the catalogue as `expected 6 fields, got N` at the line where it starts. The csv reader is used in its default (non-strict) dialect.
- **No floats anywhere**; amounts stay `Decimal` as written (RK1). Rounding is PLAY3-3's.
- **Alternatives rejected:** `csv.DictReader` (hides duplicate header names and row field counts); collecting all errors (spec non-goal).

## 7. Risks, constraints and assumptions

- **Assumption — residual `csv.Error`.** With the limit raised and the default dialect, `parse_csv` on CI's Python 3.12 has no remaining path to `csv.Error`. Two remain outside the contract and propagate unchanged (not as `LedgerError`): a NUL byte on Python 3.10 (3.11+ accepts it), and `parse_lines` items that break the one-line-per-item contract (a lone `\r` inside an item). Risk: low — PLAY3-4 would show a traceback rather than a line number for such input.
- **Assumption — editable install.** A fresh `pip install -e ".[test]"` (CI) picks up the new package; a developer's pre-existing editable install may need re-running it locally before `import ledger` resolves.
- **Constraint:** the reason texts are a cross-story contract (RK2); PLAY3-4 prints them unchanged, so the tests assert each FR5 text verbatim.
- **Scale:** a single pass holding one list of transactions and a dict of seen ids — linear in file size; personal ledgers are small, no streaming API is required.
- **Security:** reads a local file the developer names; no execution, network or writing.
