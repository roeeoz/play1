# Plan — PLAY3-2: Read and validate a CSV ledger

## Context

PLAY3-2 adds a new stdlib-only package, `src/ledger/`, to roeeoz/play1. The work branch `halo/feat/play3-2-20261119-115318` was cut from `main`, and the pull request merges back into `main`. The package turns a UTF-8 CSV ledger into a list of validated `Transaction` records, in file order and with exact `Decimal` amounts. On the first bad row it raises `LedgerError(line, reason)` instead, where `line` is the row's physical line number and `reason` is one fixed text from the catalogue. The package has two entry points: `parse_csv(path)` reads a file and `parse_lines(lines)` reads lines already in memory. The story's 11 acceptance criteria cover the happy path (BOM, blank line, quoted fields), the reason-text catalogue, header errors, row errors, the order of checks and line numbering. This package is the foundation that PLAY3-3 (the report) and PLAY3-4 (the command line) build on. The approved requirement is `spec.md`, the design is `hld.md` and the single work item is in `work-items.md`. All three sit beside this file in `stories/PLAY3-2/`.

## Research findings

- **Package layout.** `pyproject.toml:23-24` finds packages under `src` (`where = ["src"]`), so `src/ledger/` is picked up with no manifest edit. `pyproject.toml:26-28` sets `testpaths = ["tests"]` and `addopts = "-q"`. `requires-python = ">=3.10"` (`pyproject.toml:10`). The runtime dependencies `pypdf` and `flask>=3` belong to other packages, and `ledger` adds none.
- **Nothing exists yet.** No `ledger` path exists on `origin/main` or on the work branch (`git ls-tree -r origin/main` finds no match). Everything in this change is new, and no existing file changes.
- **Existing idiom.** Each sibling package has an `__init__.py` with a module docstring, re-exports and `__all__` (`src/testbed_utils/__init__.py:1-26`, `src/guestbook/__init__.py:1-9`). Each module opens with a docstring, uses `from __future__ import annotations` and keeps pure functions with docstrings (`src/guestbook/validation.py:1-40`). Tests are flat `tests/test_*.py` files that import the installed package, use pytest fixtures such as `tmp_path`, and group cases in plain classes (`tests/test_guestbook_api.py:1-30`, `tests/test_num_summary_cli.py`). Static fixtures live in `tests/fixtures/`.
- **Gate.** The gate is defined in `.factory/testing.md:3-10` and run by the `test` job in `.github/workflows/ci.yml:12-24`: `pip install -e ".[test]"` then `pytest`, on Python 3.12. There is one declared layer, `package-api` (production-path, `runBy: canonical-gate`). There is no `conftest.py` and no `sys.path` manipulation, so tests can only import through the installed distribution. No linter, formatter or type checker is configured. The `gate` job (`ci.yml:26-38`) only checks for a `CI_FAIL` marker.
- **Layout gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` has three rules: source under `src/`, tests under `tests/`, and no file in the diff over 200 KB.
- **No repository instructions.** The repo has no `AGENTS.md`, no `CLAUDE.md` and no `.factory/memory/`.
- **Contracts this change creates.** These are fixed by `hld.md` §5 and are a cross-story contract (RK2):
  - the import surface `from ledger import Transaction, LedgerError, parse_csv, parse_lines`;
  - `Transaction` fields `id`, `date`, `amount`, `currency`, `category`, `memo`;
  - `LedgerError.line`, `LedgerError.reason`, and `str(err) == f"{line}: {reason}"`;
  - the reason texts of `spec.md` FR5, quoted exactly.
- **Line counting verified.** A local stdlib check confirmed that `csv.reader.line_num` gives each row's start line as the previous `line_num + 1`. This counts the header, the empty line (which yields `[]`) and both lines of a quoted value that spans two lines.
- **External data.** None. The parser reads only a local file.
- **Remaining unknowns.** None block the plan. The residual `csv.Error` paths (a NUL byte on 3.10, and malformed `parse_lines` items) are accepted in `hld.md` §7.

## Locked decisions and assumptions

**Locked decisions**
- The FR5 reason-text catalogue, quoted verbatim, with the offending value written as typed and wrapped in plain single quotes (not `repr`) (`spec.md` §3 FR5; `hld.md` §5).
- Line numbers are physical lines: the header, blank lines and the BOM line all count, and a row spanning several lines reports its first line (`spec.md` FR6).
- Values are taken as written and never trimmed. Only `memo` may be empty. Currency must be exactly `ILS`, `USD` or `EUR`, case-sensitive (`spec.md` FR4).
- Parsing stops at the first error. No partial list is returned alongside it (`spec.md` FR3).
- The public surface and types: `Transaction` is a frozen dataclass whose `date` is a `datetime.date` and whose `amount` is a `decimal.Decimal`. `LedgerError` subclasses `Exception` and not `ValueError` (`hld.md` §5).
- The amount pattern is `-?[0-9]+(\.[0-9]+)?` and the date pattern is `[0-9]{4}-[0-9]{2}-[0-9]{2}`, each checked before the stdlib parser runs (`hld.md` §6).
- Each data row is checked in this fixed order (`hld.md` §6):
  1. field count;
  2. first empty field, in the order id, date, amount, currency, category;
  3. date;
  4. amount: first the pattern, then the number of decimals;
  5. currency;
  6. duplicate id.
- Header rules (`hld.md` §6):
  - the header is the first non-blank row;
  - the first missing required column is reported before any duplicate;
  - names match exactly;
  - extra columns are ignored, including empty or repeated extra names.
- `parse_csv` opens the file with `encoding="utf-8-sig", newline=""`. `OSError` and `UnicodeDecodeError` propagate unchanged. `parse_lines` strips one leading BOM (`hld.md` §3).
- The CSV field-size limit is raised to `2**31 - 1` before reading, and the default (non-strict) dialect is used (`hld.md` §6).
- Stdlib only, and no float anywhere (Epic PRD; RK1).

**Assumptions**
- **Module name.** The parsing module is `src/ledger/parse.py`. Evidence: `hld.md` §2 leaves the name to the implementer and suggests `parse.py`. If this is wrong, only an internal import path changes, because consumers import from `ledger`.
- **Test file.** Tests go in one file, `tests/test_ledger_parse.py`, and build their ledgers inline. `parse_csv` cases write them to `tmp_path`, so no static fixture is needed. Evidence: `work-items.md` names this file and makes `tests/fixtures/ledger/` optional. If this is wrong, the only effect is to move inputs into fixture files.
- **README.** Updating the README is not part of this story. Evidence: no acceptance criterion or work item asks for it. If this is wrong, a later story or a one-line follow-up adds it.

## Solution proposal

Add the package alongside `testbed_utils` and `guestbook` in the same idiom: a module of pure functions plus an `__init__.py` that re-exports the public surface.

- **`src/ledger/__init__.py`.** A docstring, then a re-export of `Transaction`, `LedgerError`, `parse_csv` and `parse_lines` from `ledger.parse`, and `__all__`.
- **`src/ledger/parse.py`, in four parts:**
  1. **Records.** `Transaction` is a `@dataclass(frozen=True)` with six fields. `LedgerError(Exception)` stores `line` and `reason` and defines `__str__` as `f"{line}: {reason}"`. Passing the same string as the exception's args keeps `repr` useful.
  2. **Pattern constants.** Module-level compiled ASCII regexes for the amount and the date, used with `fullmatch`. A `CURRENCIES` frozenset holds `ILS`, `USD` and `EUR`. A `REQUIRED` tuple holds `id, date, amount, currency, category, memo` in catalogue order.
  3. **`parse_lines(lines)`, which owns the whole algorithm in one pass.** It strips a BOM from the first item, then raises `csv.field_size_limit` and builds a `csv.reader`. For each row it computes the start line as the previous `line_num` + 1 and skips `[]` rows. The first non-blank row is the header: it is validated and turned into a name → index map built from the first occurrence of each required name. Every later row runs through a private row validator, which returns a `Transaction` or raises `LedgerError`. A `seen` dict of id → start line answers the duplicate-id check. If the reader finishes without finding a header, the function raises `LedgerError(1, "missing header")`.
  4. **`parse_csv(path)`.** It opens the file with `utf-8-sig` and `newline=""`, and returns `parse_lines(f)` inside the `with` block. It wraps no exceptions, so `OSError` and `UnicodeDecodeError` pass through unchanged.
- **Amount check.** An amount that fails the pattern gives `invalid amount`. One that matches but has more than two digits after the point gives the decimals text. Only then is it converted with `Decimal(raw)`, so `Decimal` never sees an unvalidated string.
- **Date check.** A date that fails the pattern gives `invalid date`. One that matches goes through `datetime.date.fromisoformat`, and its `ValueError` (for example `2026-02-30`) is mapped to the same `invalid date` text.
- **Why one module.** It keeps the change small and readable (about 120–150 lines), and PLAY3-3 and PLAY3-4 add their own modules later.
- **Alternatives rejected:**
  - `csv.DictReader`: it hides duplicate header names and short rows.
  - Collecting every error: the spec lists this as a non-goal.
  - Converting with `Decimal()` or `fromisoformat` without the patterns first: both accept `1e2`, `NaN`, `+5`, non-ASCII digits, `20260301` and `2026-W10-1` (`hld.md` §6).
  - A `ValueError` subclass for `LedgerError`: a caller catching it would also swallow `UnicodeDecodeError`.
  - Leaving the field-size limit alone: an unterminated quote would then surface as a `csv.Error` that no catalogue text covers.

## Ordered implementation steps

1. **Records.** Create `src/ledger/parse.py` with a module docstring, `Transaction` and `LedgerError`. Create `src/ledger/__init__.py` with the re-exports and `__all__`.
   - Criterion: work-item AC 7 (the error has `line` and `reason`, renders as `{line}: {reason}` and is not a `ValueError`).
   - Test: `package-api` in `tests/test_ledger_parse.py`. Assert the import surface, `str(err)`, `isinstance(err, ValueError) is False`, and that a `Transaction` is frozen.
2. **Header handling in `parse_lines`.**
   - Add BOM stripping, the raised field-size limit, `csv.reader` with start-line tracking, blank-row skipping, and header validation (missing header, then the first missing column, then the first duplicate required column).
   - Accept extra columns, including empty or repeated extra names, and a header-only ledger.
   - Criteria: story AC 6 and AC 9; work-item AC 2 (header part) and AC 3.
   - Tests: `package-api`. An empty file and a blanks-only file give `1: missing header`. A header without `date` and a header with `amount` twice give their texts at the header line, including a header preceded by blank lines. A case-mismatched name (`Date`) counts as missing. A trailing comma and a repeated extra column are accepted. A header-only ledger returns `[]`.
3. **Row validation in the fixed order.** Add these checks to the private row validator:
   - field count, giving `expected {n} fields, got {m}`;
   - the first empty required field, giving `missing {name}`;
   - the date: pattern, then calendar date;
   - the amount: pattern, then decimals, then `Decimal`;
   - the currency;
   - the duplicate id, giving `duplicate id '<id>' (first seen on line N)`.

   Build `Transaction` from the header's index map, so column order does not matter.
   - Criteria: story AC 2–5, 7, 8 and 10; work-item AC 2, 4 and 5.
   - Tests: `package-api`. Use parametrized cases, one per input listed in work-item AC 4, each asserting `err.line` and the exact `err.reason`. Add the line-17 decimals case, the line 4 → 9 `T-7` case, `usd`, `" 12.00"`, the whitespace-only row and the 5-field row. Add multi-fault rows that show the order (for example, a short row with a bad date reports the field count, and a bad date with a bad amount reports the date). Add negative, positive and zero amounts, `-0`, an empty memo, shuffled column order and an extra column.
4. **Line numbering and the happy path.**
   - Check that start lines count the header, blank lines and the BOM line, that a quoted memo spanning lines 5–6 reports line 5, and that a valid ledger with a BOM, a blank line and quoted fields (comma, doubled quote, line break) returns every row in order.
   - Criteria: story AC 1 and AC 11; work-item AC 1 and AC 6.
   - Tests: `package-api`. Assert `amount == Decimal("1.10")` with `type(amount) is Decimal` and `date == datetime.date(...)`. Assert no float field.
5. **`parse_csv`.** Add the file entry point.
   - Criteria: story AC 1 (file path); work-item AC 8 and AC 10.
   - Tests: `package-api`, using `tmp_path`:
     - the same content written as UTF-8 with a BOM and `\r\n` gives the same results as `parse_lines` over `content.splitlines(keepends=True)`, including the error line numbers;
     - a missing path raises `FileNotFoundError`, which is an `OSError` and not a `LedgerError`;
     - a file holding byte `\xff` raises `UnicodeDecodeError`;
     - `str` and `pathlib.Path` paths both work.
6. **Oversized unterminated quote.**
   - Criterion: work-item AC 9.
   - Test: `package-api`. In `tmp_path`, write a ledger whose row starting on a known line opens a quote that is never closed, followed by more than 128 KiB (`131072` characters) of content. Assert `LedgerError` at that line with `expected 6 fields, got N`, matched with a regex on `N` or computed exactly. Generate the file at test time and never commit it, so no diff file comes near the 200 KB rule.
7. **Run the gate.** Run `pip install -e ".[test]"` (dependencies come from PyPI in a fresh environment; `ledger` itself adds none), then `pytest` from the repo root.
   - Criterion: work-item AC 11.
   - Layer: `package-api`.

Implicit invariants:
- **Validation and error paths.** These are the core of steps 2–6. Every FR5 text is asserted verbatim at least once.
- **Authorization and tenancy.** Not applicable: the parser reads a local file named by the caller.
- **Concurrency.** Not applicable. Setting `csv.field_size_limit` changes process-global state, but setting the same value on every call is idempotent.
- **Generated deliverables.** None. No new binary is added, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1–7 | t1 | Add the ledger package: parse and validate a CSV ledger |

The breakdown has one work item, and every step belongs to it. No work item is left without a step.

## Verification and CI gate

- **Canonical gate.** Run `pip install -e ".[test]"` and then `pytest` from the repo root (`.factory/testing.md`, `.github/workflows/ci.yml:21-24`). Run it once locally on the committed SHA. The provider CI run at the exact head is the authoritative result for the `package-api` layer.
- **Layers.** `package-api` is the only declared layer. It is required, production-path and runnable unprivileged in a pod. No other layer exists, and none is added.
- **What the gate must show.**
  - The whole suite passes on Python 3.12, including the existing tests, unchanged.
  - `tests/test_ledger_parse.py` has at least one passing test for each of story AC 1–11 and work-item AC 1–10, and each FR5 reason text appears verbatim in an assertion.
  - `import ledger` resolves through the editable install.
  - No new entry appears in `[project].dependencies`.
- **Layout gate.** New source is under `src/ledger/`, the new test is under `tests/`, and no file in the diff is over 200 KB.
- **Provider CI, `.factory/testing.md` and `.factory/delivery-assets`.** No change to any of them is needed.

## Risks and scope guards

**Risks**
- **Reason texts drift from FR5 (RK2).** Mitigation: the tests assert every text verbatim, and the values are wrapped in plain quotes, not `repr`.
- **A float slips in (RK1).** Mitigation: the amount stays a string until it has been validated, then goes straight to `Decimal`, and a test asserts the type.
- **Global field-size limit.** `csv.field_size_limit` is process-global, so raising it also affects other `csv` users in the same process. This is accepted by `hld.md` §6, and no other module in the repo uses `csv`.
- **Stale local install.** A developer's existing editable install may need `pip install -e ".[test]"` again before `import ledger` resolves (`hld.md` §7). CI always installs fresh.
- **Residual `csv.Error`.** A NUL byte on Python 3.10, or `parse_lines` items that break the one-line-per-item contract, propagate as `csv.Error`. This is accepted in `hld.md` §7 and is not tested as a `LedgerError`.

**Scope guards: the implement phase must NOT:**
- edit `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/testing.md`, `README.md`, or anything under `src/testbed_utils/`, `src/guestbook/` or the existing `tests/`;
- add `__main__.py`, a CLI, a console script, monthly totals, currency conversion or rounding (those belong to PLAY3-3 and PLAY3-4);
- add a third-party dependency, a `conftest.py` or `sys.path` manipulation;
- reword, translate or reformat any FR5 reason text, or change the fixed order of checks;
- trim values, accept a lowercase currency, or wrap `OSError` or `UnicodeDecodeError` in `LedgerError`;
- commit a fixture file over 200 KB;
- create `CI_FAIL`;
- skip, xfail, delete or weaken any test to get green. A check that cannot pass is reported blocked.

## Clarification outcomes

None. The spec's open point, the order of checks for a row with several faults, is settled by `hld.md` §6, and no locked source conflicts with the repository.
