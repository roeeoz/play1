# Implementation plan — FIPSPROBE-2: Read and validate a CSV ledger

## Context

This story adds a new stdlib-only package, `ledger`, under `src/ledger/` in `roeeoz/play1`. It lands on the work branch `halo/feat/fipsprobe-2-20261118-101149`, which merges into `main`. The package reads a UTF-8 CSV ledger, from a file (`parse_csv`) or from lines already in hand (`parse_lines`). It checks the header and every row and returns `Transaction`s in file order, with exact `Decimal` amounts. It stops at the first malformed row with `LedgerError(line, reason)`, which renders as `{line}: {reason}`. An unreadable file raises a separate error type. These parse functions and error types are the contract that FIPSPROBE-3 (the report) and FIPSPROBE-4 (the CLI) build on. The approved requirement is in `spec.md`, the design in `hld.md`, and the single work item `t1` in `work-items.md`. All three sit next to this file in `stories/FIPSPROBE-2/`.

## Research findings

- **What exists.** There is no `ledger` package and no `src/ledger/` directory. Everything in this story is new.
- **Packaging.** `pyproject.toml:318-319` (`[tool.setuptools.packages.find] where = ["src"]`) finds `src/ledger/` automatically once it has an `__init__.py`. The project needs `requires-python = ">=3.10"` (`pyproject.toml:305`), so the code must not use syntax newer than 3.10. Pytest uses `testpaths = ["tests"]` and `addopts = "-q"` (`pyproject.toml:321-323`). This story adds no new dependency.
- **Convention for pure rules.** `src/guestbook/validation.py:1-5` keeps rules in pure functions that return `(cleaned, error)` tuples (`:15-28`). The field-rule functions here follow the same shape.
- **Test style.** Tests are plain pytest modules. Some group cases into classes (`tests/test_numutils.py:10-30`). They import the installed package and need no `conftest.py`. File fixtures live under `tests/fixtures/`. A ledger test can just as well build its files in `tmp_path`.
- **Canonical gate.** `.factory/testing.md:3` says `test-gate: pytest`. CI (`.github/workflows/ci.yml:13-26`) runs `pip install -e ".[test]"` and then `pytest` on Python 3.12, on `ubuntu-latest`, with workflow-level `permissions: contents: read` (`:8-9`). There is no linter, formatter or type checker. The `gate` job (`ci.yml:28-40`) fails only when a `CI_FAIL` marker exists at the repo root.
- **Repository layout gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` checks four rules:
  - Python source lives under `src/` and tests under `tests/`.
  - No file in the diff is larger than 200 KB.
  - The diff adds a line under `## Unreleased` in `CHANGELOG.md` (rule `PLAY-G4`).
  - A new shell script is executable and starts with a shebang. It does not apply here, because this story adds no shell script.

  The last entry under `## Unreleased` is the PLAY-175 line, at `CHANGELOG.md:8`.
- **Behaviour of the standard library, checked on Python 3.12.15:**
  - With `csv.reader(..., strict=True)`, an unclosed quote at end of data raises `csv.Error: unexpected end of data`.
  - `a,"b"c` raises `csv.Error: ',' expected after '"'`.
  - A quoted field that spans lines comes back as one record, and `reader.line_num` reports its last physical line. Taking "the previous `line_num` + 1" as the start line therefore gives the first line of the record, as `hld.md` §3 step 4 says.
  - An empty line comes back as `[]`, and a whitespace-only line as a single whitespace field. Both are blank records under `hld.md` §6.
- **Contracts this story fixes.** These shapes and texts are quoted exactly from `hld.md` §5:
  - `Transaction(id, date, amount, currency, category, memo)`, a frozen dataclass.
  - `LedgerError.line`, `LedgerError.reason`, with `str(e) == f"{line}: {reason}"`.
  - The eleven reason texts (FR2 and FR6), plus `malformed CSV record`.
- **Unknowns left after research:**
  - The class name of the unreadable-file error. `hld.md` §5 does not name it. This plan picks one; see the assumptions below.
  - The text `malformed CSV record`. It still needs PO confirmation (`hld.md` §5–§6). It is not a blocker.

## Locked decisions and assumptions

**Locked decisions**
- Stdlib only. Never use a float for an amount. Amounts are `Decimal` exactly as written (`spec.md` §6–§7; `hld.md` §2 and §6).
- The public surface is `parse_csv`, `parse_lines`, `Transaction`, `LedgerError` and an unreadable-file error type, all listed in `src/ledger/__init__.py` `__all__` (`hld.md` §2; `work-items.md` t1).
- The reason texts are exactly as given in `spec.md` FR2 and FR6, and the header errors are on line 1 (`spec.md` FR2 and FR6; `hld.md` §5).
- Validation order: field count, then id (empty, then duplicate), then date, then amount (not a number, then decimal places), then currency, then category (`hld.md` §6; t1 AC12).
- Header check order: missing columns first, in the order `id, date, amount, currency, category, memo`. Duplicates are checked next, in the same order. Names are trimmed and compared case-sensitively. Extra columns are ignored (`hld.md` §6).
- An amount must match the ASCII regex `^[+-]?[0-9]+(\.[0-9]+)?$` before the decimal places are counted and before `Decimal(...)` is called. A date must match `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` before `date.fromisoformat` is called (`hld.md` §6).
- The CSV reader is strict, and any `csv.Error` becomes `LedgerError(start_line, "malformed CSV record")` (`hld.md` §6; t1 AC14).
- `parse_csv` reads and decodes the whole file (`utf-8-sig`, `newline=""`) before it parses anything. `OSError` and `UnicodeDecodeError` become the unreadable-file error, which does not subclass `LedgerError` and chains the cause (`hld.md` §3 and §5).
- `parse_csv` and `parse_lines` share one code path (`hld.md` §3; spec AC21).
- The story must not modify `pyproject.toml`, CI files, `src/guestbook/` or `src/testbed_utils/`. It must not add `__main__.py`, a report module or a CLI (`work-items.md` t1).
- One line goes under `## Unreleased` in `CHANGELOG.md` (repo-gate `PLAY-G4`; t1).

**Assumptions**
- **The unreadable-file error is named `LedgerReadError(Exception)`.**
  - Evidence: `hld.md` §5 leaves the name open and only requires a separate, non-`LedgerError` type.
  - If wrong: FIPSPROBE-4 imports a different name, and the fix is a one-line rename before that story starts.
- **Module layout.** The package has three modules:
  - `src/ledger/errors.py`, for the two error types and all the reason-text constants and format strings
  - `src/ledger/rules.py`, for the pure field rules
  - `src/ledger/parser.py`, for `Transaction`, `parse_lines` and `parse_csv`

  Evidence: `hld.md` §2 leaves the layout to the implementer but wants the texts in one place and the rules kept pure. If wrong, the cost is cosmetic, because the public surface is the same.
- **`parse_csv` hands its decoded content to the shared path as `io.StringIO(content, newline="")`.** Evidence: `str.splitlines` would split on `\x0b`, `\x1c` and `\u2028`. That would change physical line numbers and the content of quoted fields, and AC21 would break. If wrong, line numbers drift for such characters, so a test covers one.
- **The `malformed CSV record` text stands.** Evidence: `hld.md` §5 and t1 AC14 use it as the default. If the PO picks another text, only the constant in `errors.py` and its test change.

## Solution proposal

**Approach.** Add one small package in three layers, all pure Python:

- **Reason texts and errors (`errors.py`).**
  - All twelve texts live here as module constants or format strings, so the parser and the later CLI cannot drift apart (RK2).
  - `LedgerError(Exception)` stores `line` and `reason`, calls `super().__init__(f"{line}: {reason}")`, and so keeps `args` equal to `str()`.
  - `LedgerReadError(Exception)` holds a readable message and is raised `from` the original `OSError` or `UnicodeDecodeError`.
- **Field rules (`rules.py`).**
  - There is one pure function per field: id (empty only), date, amount, currency and category.
  - Each one takes the trimmed value and returns `(cleaned, reason)`, with exactly one of the two `None`. This mirrors `src/guestbook/validation.py:15-28`.
  - The duplicate-id check and the field-count check need parser state, so they stay in the parser.
  - The amount rule checks the ASCII regex first, then counts the digits after `.` (more than two is an error), then builds `Decimal(value)`. `+3` becomes `Decimal('3')` and `-12.50` stays `Decimal('-12.50')`.
  - The date rule checks the ASCII regex, then calls `date.fromisoformat`. A `ValueError` becomes `invalid date '{value}'`.
  - The currency rule checks membership in `("ILS", "USD", "EUR")`, case-sensitively.
- **Parser (`parser.py`).**
  - `Transaction` is a `@dataclass(frozen=True)` with the fields from `hld.md` §5.
  - `parse_lines(lines)`:
    - Strip a leading `\ufeff` from the first line.
    - Append `\n` to any line that lacks a `\n` or `\r` ending.
    - Feed the lines to `csv.reader(..., strict=True)`.
    - Track `start = previous line_num + 1` for each record, and wrap the reader's `next()` so that a `csv.Error` raises `LedgerError(start, MALFORMED)`.
    - Skip blank records.
    - Treat the first non-blank record as the header, map each required column to its index, and report header errors on line 1.
    - For each data row: check the field count, trim every field, run the rules in the locked order, then check for a duplicate id against a `dict[id, first_line]`.
    - Collect the transactions in a local list, and return the list only after every row has passed.
  - `parse_csv(path)` opens the file with `encoding="utf-8-sig", newline=""`, calls `read()`, and maps any `OSError` or `UnicodeDecodeError` to `LedgerReadError`. It then returns `parse_lines(io.StringIO(content, newline=""))`. Because the whole file is decoded first, an invalid byte always wins over an earlier data error (AC20, t1 AC16).
- **Missing header.** If no non-blank record exists, raise `LedgerError(1, "missing header")`.

**Key decisions.**
- **One code path for both entry points.** It guarantees AC21. Stripping the BOM in `parse_lines` makes both input forms equivalent, even though `utf-8-sig` already removes the BOM on the file path.
- **Check the duplicate id after the empty id and before the date.** This is the locked order.
- **Do not keep extra columns.** They are mapped away when the `Transaction` is built.

**Alternatives rejected.**
- **A lenient `csv.reader`** silently corrupts fields and goes against R2.
- **Streaming the file** would let a data error mask a decoding error, which goes against FR8 and AC20.
- **`csv.DictReader`** hides how the header maps to positions, cannot detect duplicate header names, and makes the field-count check awkward.
- **Letting `OSError` through to callers** would push stdlib exception handling into FIPSPROBE-4 (`hld.md` §6).

## Ordered implementation steps

1. **Create `src/ledger/errors.py`** (new).
   - Add the reason-text constants and format strings for the three header texts, the eight row texts from FR6, and `malformed CSV record`.
   - Add `LedgerError(line, reason)` with `.line`, `.reason`, and `str()`/`args` equal to `f"{line}: {reason}"`.
   - Add `LedgerReadError`.
   - Use `from __future__ import annotations` and no syntax newer than 3.10.
   - Advances: spec AC19, AC20; t1 AC15, AC16. Test layer: `package-api` (pytest).
2. **Create `src/ledger/rules.py`** (new). Add the pure functions for id-empty, date, amount, currency and category, returning `(cleaned, reason)`, with the ASCII regexes exactly as in `hld.md` §6. Never call `float`.
   - Advances: spec AC10–AC14, AC16; t1 AC5, AC7–AC10. Test layer: `package-api`.
3. **Create `src/ledger/parser.py`** (new).
   - Add the `Transaction` frozen dataclass.
   - Add `parse_lines`: handle the BOM and line endings, run the strict reader with start-line tracking, map `csv.Error` to `LedgerError`, skip blank records, check the header (missing, then duplicate, all on line 1), then check each row in the locked order with duplicate-id tracking. Return nothing on error.
   - Add `parse_csv`: read the whole file, map `OSError` and `UnicodeDecodeError` to `LedgerReadError`, and delegate through `io.StringIO(content, newline="")`.
   - Advances: spec AC1–AC9, AC15, AC17, AC18, AC21; t1 AC1–AC4, AC6, AC11–AC14, AC17. Test layer: `package-api`.
4. **Create `src/ledger/__init__.py`** (new). Re-export `parse_csv`, `parse_lines`, `Transaction`, `LedgerError` and `LedgerReadError`, and list them in `__all__`. Add no `__main__.py`.
   - Advances: the t1 public surface. Test layer: `package-api` (tests import only through `ledger`).
5. **Create `tests/test_ledger_parse.py`** (new). Import from `ledger` only. Write the ledgers into `tmp_path` and feed `parse_lines` lists of strings, with no binary fixtures. Group the tests by AC and assert exact `line` and `reason` values. Cover:
   - **Happy path.** A ledger with a BOM, a blank line, quoted commas, doubled quotes and a memo spanning lines. Check the order and that `type(amount) is Decimal` with the value equal to the text as written (AC1).
   - **Header.** A reordered header with one extra column (AC6). `memo` missing, `Memo` instead of `memo`, `id` twice, an empty file, and a file of only blank lines (AC7, AC8).
   - **Field count.** A five-field row (AC9).
   - **Id.** An empty id and a whitespace-only id (AC10). Line 4 and line 9 give exactly `duplicate id 'T-7' (first seen on line 4)`, and `T-7` and `t-7` are both accepted (AC3, AC5).
   - **Dates.** `2026-13-01`, `2026-02-30`, `01/03/2026` and `20260301` are rejected, and a valid date becomes a `datetime.date` (AC11).
   - **Amounts.** `abc`, `1,000.00`, `12.`, `.5`, `1e3`, `NaN` and a non-ASCII digit such as `١٢` are rejected (AC12). `12.345` on line 17 gives line 17 (AC2). `-12.50`, `+3`, `0` and `7.5` are accepted exactly, and the negative one is an expense (AC13).
   - **Currency.** `ILS`, `USD` and `EUR` are accepted, and `usd` and `Eur` are rejected (AC4, AC16).
   - **Category and memo.** An empty category is rejected and an empty memo is accepted (AC14, AC15).
   - **Trimming.** ` USD ` and padded fields are trimmed (AC17).
   - **Validation order.** A row with several problems reports the first one in the locked order (t1 AC12).
   - **Line numbers.** A header, two blank lines and a malformed row gives line 4. A memo spanning lines 5–6 gives line 5. A whitespace-only line is skipped, and `,,,,,` gives `empty id` (AC18).
   - **Malformed CSV.** An unclosed quote and `a,"b"c` each give `malformed CSV record` at the record's start line (t1 AC14).
   - **Error shape.** `.line`, `.reason`, `str(e)` and `e.args` (AC19).
   - **Unreadable file.** A missing path, and invalid UTF-8 placed after an earlier data error, both raise `LedgerReadError` and are not instances of `LedgerError` (AC20).
   - **Parity.** `parse_csv` and `parse_lines` agree with a BOM, with a multi-line memo, and with lines given with and without endings, for both a success and an error. Include one memo containing `\u2028` (AC21).
6. **Edit `CHANGELOG.md`.** Add one line under `## Unreleased`, after `CHANGELOG.md:8`: `- FIPSPROBE-2: add the \`ledger\` package — CSV ledger parsing and validation with line-numbered errors.`
   - Advances: t1 AC18 and repo-gate `PLAY-G4`. Test layer: none, because this is a documentation rule checked by the repo-gate review.
7. **Run the gate** from a clean temporary worktree at the committed SHA: `pip install -e ".[test]"`, then `pytest`. The dependencies come from that install (PyPI, with no warm cache assumed). `ledger` itself adds none.
   - Advances: t1 AC18. Test layer: `package-api`.

**Invariants the implement phase must cover.**
- **Validation and error paths.** Every reason text and the first-error-wins rule. No partial list is ever returned.
- **Authorization, tenancy and concurrency.** Not applicable: the package is a pure, synchronous library with no shared state.
- **Idempotency.** Repeated parses of the same content give identical results, because the duplicate-id map lives inside each call.
- **Generated deliverables.** None.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–7 | `t1` — Add stdlib-only ledger package: CSV ledger parsing and validation with line-numbered errors |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate**, in order and from a clean temporary worktree at the committed SHA:
  1. `pip install -e ".[test]"`
  2. `pytest`

  This matches `.factory/testing.md` `test-gate: pytest` and `.github/workflows/ci.yml` (Python 3.12, `ubuntu-latest`).
- **Required layer.** `package-api` (pytest, production-path through the installed distribution). It runs unprivileged in a pod. The provider run at the exact head is the authoritative result.
- **Python version.** CI runs only 3.12. The 3.10 compatibility of the date and amount rules comes from the ASCII regexes, not from a CI matrix. This plan adds no matrix.
- **What the gate must show:**
  - all existing tests still pass
  - every test in `tests/test_ledger_parse.py` passes, with each of spec AC1–AC21 and t1 AC1–AC17 covered by at least one test that imports `ledger`
  - the `gate` job stays green, with no `CI_FAIL` file
- **Repo-gate review.** The `CHANGELOG.md` line is present, and no file is larger than 200 KB.
- **No CI change.** The change does not touch provider CI. `.factory/testing.md` needs no update, and `.factory/delivery-assets` does not apply, because the story adds no binary deliverable.

## Risks and scope guards

**Risks**
- **The reason texts drift (RK2).** Mitigation: keep the texts in `errors.py` only, and have the tests assert the full strings.
- **A float leaks into an amount (RK1).** Mitigation: check the regex before calling `Decimal(str)`, and have the tests assert `type(...) is Decimal` and the exact value.
- **Line numbers go wrong around multi-line records or a BOM, or the two entry points disagree.** Mitigation: use the shared code path, compute the start line from `line_num`, and keep the parity tests in step 5.
- **The standard library behaves differently across versions** (`date.fromisoformat`, Unicode digits accepted by `Decimal`). Mitigation: check the ASCII regexes before converting.
- **The PO changes `malformed CSV record`.** The change is confined to one constant and one test.

**Scope guards: the implement phase must NOT:**
- edit `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/**`, `src/guestbook/` or `src/testbed_utils/`
- add `src/ledger/__main__.py`, a report module, rates, rounding or any CLI (those belong to FIPSPROBE-3 and FIPSPROBE-4)
- add a dependency, a `conftest.py`, `sys.path` hacks, or a new test framework or CI job
- change any reason text from `spec.md` FR2 and FR6, or collect several errors per parse
- delete, skip, `xfail` or weaken any existing or new test to make the gate green; a check that cannot run is reported as blocked
- edit `spec.md`, `hld.md` or `work-items.md`

## Clarification outcomes

None. No question blocked the plan. The pending text `malformed CSV record` and the name of the unreadable-file error are carried as assumptions above.
