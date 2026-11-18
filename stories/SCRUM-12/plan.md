# Implementation plan — SCRUM-12: Monthly expense report from a CSV ledger

## Context

SCRUM-12 adds a new stdlib-only Python package `ledger` to `play1`. It parses a UTF-8 CSV ledger into frozen transactions and rejects the first bad row with its physical line number (AC1–AC8). It builds a monthly report by category in ILS, USD or EUR, using fixed `Decimal` rates and a single `ROUND_HALF_EVEN` rounding per figure (AC9–AC18). It exposes the report as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]` with exit codes 0, 2 and 3 (AC19–AC25). The work lands in `play1` on branch `halo/feat/scrum-12-20261118-224230` and merges into `main`. "ACn" below means criterion n of `spec.md` §5. The approved requirement (`spec.md`), the design (`hld.md`) and the three-item breakdown (`work-items.md`: t1 parser, t2 report, t3 CLI) sit beside this file in `stories/SCRUM-12/`.

## Research findings

**Change surface (all new unless stated).**
- `src/ledger/` does not exist. Packaging already covers it: `pyproject.toml:24-25` (`[tool.setuptools.packages.find] where = ["src"]`) discovers any package under `src/`, so `pyproject.toml` needs no edit.
- `tests/fixtures/` exists (`numbers.txt`, `single.txt`, `empty.txt`, PDFs). `tests/fixtures/ledger/` does not.
- No `tests/test_ledger_*.py` exists.
- `CHANGELOG.md:3` holds `## Unreleased`, followed by four `- PLAY-…: add …` bullets (`CHANGELOG.md:5-8`). It is the only existing file this story edits.

**Repository conventions (read from existing code).**
- Tests are grouped in `class Test…` and locate fixtures with `FIXTURES = pathlib.Path(__file__).parent / "fixtures"` (`tests/test_num_summary_cli.py:11`).
- There is no `conftest.py` and no `sys.path` manipulation anywhere in `tests/` (also stated in `.factory/testing.md`).
- Existing CLI tests call `main()` in-process with `patch("sys.argv")` and `redirect_stdout` (`tests/test_num_summary_cli.py:18-31`). SCRUM-12 deliberately departs from this: AC25 requires `subprocess` with `[sys.executable, "-m", "ledger", …]`.
- Source modules start with a docstring and `from __future__ import annotations`, and use argparse (`src/testbed_utils/numsummary.py:1-8`).

**Contracts.**
- The Python API is fixed by `spec.md` FR1–FR6 and `hld.md` §5: `parse_csv(path)`, `parse_lines(lines)`, `Transaction`, `LedgerError(line, reason)`, `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`, `CategoryTotal(name, total, count)`, `RATES`, and the report's `to_dict()`.
- The CLI's text and JSON layouts and its stderr strings are byte-exact contracts (AC19–AC23).
- There are no cross-repo contracts and no external data. The rates are constants.

**Gate.**
- `.factory/testing.md` declares `test-gate: pytest`, a single layer `package-api` (production-path, `runBy: canonical-gate`). The precondition is `pip install -e ".[test]"`.
- CI job `test` in `.github/workflows/ci.yml` runs on Python 3.12. The second job, `gate`, fails only when a `CI_FAIL` file exists at the repository root.
- There is no linter, formatter or type checker.
- `requires-python = ">=3.10"` (`pyproject.toml:10`).
- The PR layout gate is `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`. Its rule 4, `PLAY-G4`, requires a line under `## Unreleased` in `CHANGELOG.md`. Rule 3 rejects any file over 200 KB. Rule 1 requires Python under `src/` and tests under `tests/`.

**Local environment (fact).**
- The local interpreter is Python 3.13.
- The installed editable `testbed-utils` points at another workspace (`…/delivery-12278c0e…/play1-79db628f23`). `pip install -e ".[test]"` must be re-run from this checkout before `import ledger` or `python -m ledger` can resolve.

**Resolved unknown — sample fixture content.** The spec fixes the totals, not the rows. These rows (ids `t001`…`t009`, in this order) reproduce AC9, AC10, AC16, AC19 and AC20 exactly. I checked the ILS/USD income, expense and net with `Decimal` and `ROUND_HALF_EVEN`. The rows are:

| id | date | amount | currency | category |
|---|---|---|---|---|
| t001 | 2026-02-27 | -99.99 | ILS | groceries |
| t002 | 2026-03-01 | 12000.00 | ILS | salary |
| t003 | 2026-03-02 | -1500.00 | ILS | rent |
| t004 | 2026-03-05 | -310.50 | ILS | groceries |
| t005 | 2026-03-10 | 250.00 | USD | freelance |
| t006 | 2026-03-12 | -120.00 | USD | software |
| t007 | 2026-03-18 | -450.00 | ILS | groceries |
| t008 | 2026-03-25 | -80.25 | EUR | travel |
| t009 | 2026-04-01 | -1500.00 | ILS | rent |

Results:
- **ILS:** income 12925.00, expense -3025.50, net 9899.50.
- **USD:** income 3493.24, expense -817.70, net 2675.54. Salary is 3243.24 and freelance is 250.00.
- Memo values are free text. At least one memo is empty, so AC1's "possibly empty" is exercised.

**Remaining unknowns.** None block the plan. The spec's assumptions A1–A3 cover the gaps.

## Locked decisions and assumptions

**Locked decisions**
- Stdlib only; `Decimal` end to end; the only rounding is a single quantize to `0.01` with `ROUND_HALF_EVEN` per figure (spec §2, FR5).
- `RATES = {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}` (AC10).
- Every reason string in AC5–AC7 is exact, and `str(LedgerError)` is `line {line}: {reason}` (FR3).
- `parse_csv` opens with `encoding="utf-8-sig"`, `newline=""` and delegates to `parse_lines` (AC8).
- `LedgerError` is not a `ValueError` subclass. Caller errors raise `ValueError` (`hld.md` §4, FR6).
- Module split: `parser.py` (t1), `report.py` (t2), `cli.py` and `__main__.py` (t3). `__init__.py` is created in t1 and extended in t2 (`hld.md` §2).
- Strict ASCII regexes for dates and amounts, so the parser never relies on the permissive `date.fromisoformat` (`hld.md` §6).
- A row's line is the previous `csv.reader.line_num + 1` (`hld.md` §6).
- argparse with required subparsers. `type=` validators handle `--month` and `--top`, and `choices` handles `--base` (`hld.md` §6).
- CLI tests use `subprocess` with `sys.executable -m ledger` (AC25).
- `pyproject.toml`, `[project.scripts]` and CI stay untouched. `CHANGELOG.md` gets exactly one added line, owned by t3 (spec A1, `work-items.md` t3).
- Python 3.10 floor (`pyproject.toml:10`, `hld.md` §7).

**Assumptions**
- **A2 (spec).** The `expected N fields` count is the header's own field count. *Evidence:* spec §8. *If wrong:* only the message for headers with extra columns changes.
- **A3 (spec).** A FILE that is not valid UTF-8 gives exit 2. *Evidence:* spec §8 and the t3 acceptance criteria. *If wrong:* one CLI test changes.
- **`parse_lines` strips a leading BOM from its first line**, so it matches `parse_csv` exactly. *Evidence:* AC8 says "behaves exactly as" `parse_csv`, and t1's acceptance criteria say this explicitly. *If wrong:* harmless, because `parse_csv` already removes the BOM through `utf-8-sig`.
- **The duplicate-id check and the field-count check happen before field validation.** On a row with the wrong field count, the field-count reason wins. The duplicate-id check runs after the row's own fields are valid. *Evidence:* none in the sources; this is the simplest order. *If wrong:* a row with several faults reports a different reason, and no AC covers that case.
- **Empty `--month` value errors, the missing-file test and the non-UTF-8 test use `tmp_path`, not new committed fixtures.** *Evidence:* the spec and t1 name only four fixtures. *If wrong:* none.

## Solution proposal

The feature is one new layered package, `src/ledger/`. Each layer imports only the layers below it. Nothing existing is refactored. The only edit to an existing file is the changelog line.

**Parser (`parser.py`, t1)**
- `Transaction` is a `@dataclass(frozen=True)` with fields `id`, `date`, `amount`, `currency`, `category`, `memo`.
- `LedgerError(Exception)` stores `line` and `reason`. Its `__str__` returns `f"line {line}: {reason}"`.
- `parse_lines` wraps the input iterable in `csv.reader`:
  - **Line tracking:** it records `start = previous line_num + 1` per row, so blank lines and multi-line quoted rows count correctly.
  - **Blank rows:** it skips rows where every field is empty after stripping.
  - **First line:** it strips a leading `﻿` from the first line before reading.
  - **Header:** the first non-blank row is the header. Missing names are reported in the canonical order `id, date, amount, currency, category, memo` at the header's line. No non-blank row at all gives `LedgerError(1, "missing header")`.
  - **Each data row is validated in this fixed order:**
    1. field count
    2. `id` non-empty
    3. date regex `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, then `datetime.date(...)` with `ValueError` mapped to "not a calendar date"
    4. amount regex `^[+-]?[0-9]+(\.[0-9]+)?$` ("not a number"), then more than two fraction digits ("more than 2 decimal places"), then zero, including `-0` ("must not be zero")
    5. currency in a fixed set, compared case-sensitively
    6. `category` non-empty
    7. duplicate id against a dict of id to first line
- `parse_csv` opens with `utf-8-sig` and `newline=""`, then delegates to `parse_lines`.

**Report (`report.py`, t2)**
- `CategoryTotal` and `MonthlyReport` are frozen dataclasses. `MonthlyReport.categories` is a tuple, which keeps the report immutable. `to_dict()` renders amounts with `str()` of the quantized `Decimal` (always two places) and counts as `int`.
- **Validation:** `monthly_report` validates `month` with `^[0-9]{4}-(0[1-9]|1[0-2])$`, `base in rates`, and `top is None or top >= 1`. Any failure raises `ValueError`.
- **Conversion:** each transaction in the month (`t.date.year`/`month` match) converts at full precision as `amount * rates[currency] / rates[base]`.
- **Summing:** every sum starts at `Decimal(0)`, so an empty month quantizes to `Decimal("0.00")`, never to the `int` 0.
- **Rounding:** each figure is quantized once to `Decimal("0.01")` with `ROUND_HALF_EVEN`.
- **Ordering:** categories sort by key `(-abs(total), name)`, using the quantized totals, and are then sliced to `top`.
- `__init__.py` re-exports `RATES`, `monthly_report`, `MonthlyReport` and `CategoryTotal`.

**CLI (`cli.py` and `__main__.py`, t3)**
- `main(argv=None) -> int` builds an argparse parser with `add_subparsers(dest="command", required=True)` and a `report` subparser:
  - positional `file`
  - `--month` (required, with a `type=` validator that raises `argparse.ArgumentTypeError` for anything but `YYYY-MM` with month 01–12)
  - `--base` (`choices=["ILS", "USD", "EUR"]`, default `ILS`)
  - `--top` (a `type=` validator for an integer of at least 1)
  - `--json` (`store_true`)
- argparse already gives exit 2 with stderr only for every usage error in AC22 except the file.
- **Error mapping:** `parse_csv` runs inside a `try`:
  - `OSError` or `UnicodeDecodeError` → `parser.error(...)`, which exits 2. The decode error can surface mid-iteration, so the `try` wraps the whole parse.
  - `LedgerError` → write `error: {args.file}:{e.line}: {e.reason}\n` to stderr and return 3.
- **Output:**
  - Text output is the fixed thirteen-line layout. An empty month prints `categories: none`.
  - JSON output is `json.dumps(report.to_dict())` plus a newline.
  - stdout is written only after the report is fully built, so nothing reaches stdout on an error.
- `__main__.py` calls `sys.exit(main())`.

**Alternatives rejected**
- `csv.DictReader`: it hides the field-count mismatch and line tracking (`hld.md` §6).
- A `[project.scripts]` entry: it edits an existing file, which the spec excludes.
- A single module: work items would not own separate files.
- `float`: excluded by the spec.
- In-process CLI tests, as in the existing convention: excluded by AC25.

## Ordered implementation steps

1. **Add the ledger fixtures (AC1, AC3, AC7, AC23; t1).** Create:
   - `tests/fixtures/ledger/sample.csv`: header `id,date,amount,currency,category,memo` plus the nine rows in the research table.
   - `tests/fixtures/ledger/bom_blank.csv`: UTF-8 BOM, header, then two valid rows. Separate them with one empty line and one whitespace-only line. Give one row an empty memo and the other a quoted memo containing a comma.
   - `tests/fixtures/ledger/empty.csv`: zero bytes.
   - `tests/fixtures/ledger/bad_amount.csv`: header on line 1, one valid row on line 2, and a row with amount `-2.505` on line 3.

   Commit them with LF line endings. Test layer: consumed by `package-api` (pytest).
2. **Create the model and error types (AC1, AC5; t1).** Add `src/ledger/parser.py` with `Transaction` and `LedgerError`. Test layer: `package-api`.
3. **Add the parse entry points (AC1–AC8, AC6, AC7; t1).** Implement `parse_lines` and `parse_csv` in `src/ledger/parser.py` as described in the solution proposal, including:
   - the line tracking, header mapping and validation order
   - the exact reason strings
   - the BOM strip in `parse_lines`

   Use no API newer than 3.10, and no `\d`. Test layer: `package-api`.
4. **Create the package root (AC1, AC8; t1).** Add `src/ledger/__init__.py` with a module docstring and `__all__`, re-exporting `parse_csv`, `parse_lines`, `Transaction` and `LedgerError`. Test layer: `package-api`.
5. **Write the parser tests (AC1–AC8; t1).** Add `tests/test_ledger_parser.py` with `Test…` classes, importing from `ledger`:
   - **AC1:** the sample parses to nine transactions in order with the exact types and values, and `dataclasses.FrozenInstanceError` is raised on assignment.
   - **AC2:** reordered header, padded fields and an extra column.
   - **AC3:** `bom_blank.csv`.
   - **AC4:** header only.
   - **AC5:** each reason, parametrized: `2026-3-1`, `2026-02-30`, `abc`/`NaN`/`Infinity`, `1.505`, `0` and `-0`, `usd`, empty category, empty id, a five-field row. Assert the exact line (including a blank line before the row) and `str()`. Also assert that parsing stops at the first bad row and that `LedgerError` is not a `ValueError`.
   - **AC6:** duplicate id across a blank line, giving line 4 with `(first seen on line 2)`.
   - **AC7:** missing columns and `empty.csv`.
   - **AC8:** `parse_lines(io.StringIO(text))` equals `parse_csv(path)` for the sample and for the BOM text.
   - **A2:** a seven-column header gives `expected 7 fields, got 6`.

   Test layer: `package-api`.
6. **Add the report module (AC9–AC18; t2).** Add `src/ledger/report.py` with `RATES`, `CategoryTotal`, `MonthlyReport` (including `to_dict()`) and `monthly_report`, as described in the solution proposal. The `ValueError` messages name the bad argument. Test layer: `package-api`.
7. **Re-export the report API (AC10; t2).** Extend `src/ledger/__init__.py` to re-export `RATES`, `monthly_report`, `MonthlyReport` and `CategoryTotal`, and update `__all__`. Test layer: `package-api`.
8. **Write the report tests (AC9–AC18; t2).** Add `tests/test_ledger_report.py`. Build transactions from `sample.csv` through `parse_csv`, and build ad-hoc ones directly with `Transaction(...)`. Cover:
   - **AC9:** March in ILS, all fields and the category order.
   - **AC10:** USD, plus the exact `RATES` value.
   - **AC11:** 0.05 ILS in EUR gives 0.01, and three such transactions give 0.04.
   - **AC12:** `str()` of each figure gives two places.
   - **AC13:** top 2, top larger than the category count, and `None`.
   - **AC14:** a tie is ordered by name.
   - **AC15:** the empty month and its exact `to_dict()`.
   - **AC16:** February.
   - **AC17:** custom rates.
   - **AC18:** parametrized bad months, bad base and `top=0`, each asserting `ValueError` and not `LedgerError`.

   Test layer: `package-api`.
9. **Add the CLI (AC19–AC24; t3).** Add `src/ledger/cli.py` with `main(argv=None)`, as described in the solution proposal. Add `src/ledger/__main__.py`, which calls `sys.exit(main())`. Do not use colour or prompts. Test layer: `package-api`.
10. **Write the CLI tests (AC19–AC25; t3).** Add `tests/test_ledger_cli.py`. A helper runs `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, cwd=REPO_ROOT)`, where `REPO_ROOT = pathlib.Path(__file__).parent.parent`, so relative FILE paths match AC19 and AC23 as typed. Cover:
    - **AC19:** exact stdout and an empty stderr.
    - **AC20:** `json.loads(stdout)` equals the exact object.
    - **AC21:** stdout ends with the four lines.
    - **AC22, parametrized:** no subcommand, missing `--month`, `--month 2026-13`, `--top 0`, `--base GBP`, a missing file in `tmp_path`, and a `tmp_path` file with invalid UTF-8 bytes (A3). Each gives exit 2, an empty stdout and a non-empty stderr.
    - **AC23:** an exact stderr string with a trailing newline and an empty stdout.
    - **AC24:** `--help` exits 0 and stdout contains `--month`.
    - **Determinism:** two runs give identical bytes.

    Use no `sys.path` edits (AC25). Test layer: `package-api`. The tests need the editable install, which CI already performs.
11. **Add the changelog line (gate `PLAY-G4`; t3).** Append exactly one bullet after `CHANGELOG.md:8`, for example ``- SCRUM-12: add the `ledger` package and `python -m ledger report`, a monthly expense report from a CSV ledger.``. Change nothing else in the file. Test layer: none, because the PR layout gate checks it, not pytest.

**Implicit invariants**
- **Authz, tenancy and concurrency:** not applicable. The tool is single-process, offline and reads one file.
- **Idempotency:** output is deterministic. It never depends on dict ordering of input, time or locale, and the sort key is total.
- **Validation and error paths:** covered by steps 3, 6 and 9.

**Dependencies:** none new. Run `pip install -e ".[test]"` from this checkout; pytest comes from the existing `test` extra. There are no generated deliverables and no binaries; all fixtures are a few hundred bytes.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–5 | t1 — ledger: transaction model and validating CSV parser (R1, R2) |
| 6–8 | t2 — ledger: monthly report with fixed-rate conversion and half-even rounding (R3, R4) |
| 9–11 | t3 — ledger: `python -m ledger report` command line, exit codes and changelog (R5) |

Every work item has steps. Each work item's tests pass on their own: t1 needs only its fixtures and the parser, t2 adds only `report.py` and the re-exports, and t3 adds only the CLI and the changelog line.

## Verification and CI gate

**Canonical gate.** Run it from the repository root, once, on the committed SHA:
1. `pip install -e ".[test]"`: mandatory locally, because the current editable install points at another workspace.
2. `pytest`

There is no lint, format or type-check step.

**Required layer.** `package-api` (production-path, `runBy: canonical-gate`). It runs in a pod, unprivileged. The provider's `test` job on Python 3.12 at the exact head is authoritative. `gate` stays green because no `CI_FAIL` file is added.

**Done means:**
- `pytest` passes in full: the existing suite unchanged, plus `tests/test_ledger_parser.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py`.
- Every AC1–AC25 has at least one asserting test.
- The CLI tests pass through the installed package only.
- The PR layout gate passes: one added `## Unreleased` line, Python under `src/` and `tests/`, no file over 200 KB, and no shell scripts.

**No new obligations.** No provider CI change is needed. `.factory/testing.md` is unchanged because the layer is the same. No `.factory/delivery-assets` entry is needed because there are no binaries of 1 MiB or more.

## Risks and scope guards

**Risks**
- **Byte-exact output (AC19–AC23).** A stray trailing space, a missing final newline, or argparse usage text on a data error breaks the tests. *Mitigation:* the tests assert full strings, and the data-error path returns 3 without calling `parser.error`.
- **Partial stdout on error.** *Mitigation:* parse and build the report before writing anything.
- **`sum()` of an empty sequence returns the `int` 0, and `str(0)` is not `0.00`.** *Mitigation:* start every sum at `Decimal(0)` and quantize every figure.
- **Using API newer than 3.10.** *Mitigation:* do not use `match` on types, `ExceptionGroup`, `datetime.UTC` or similar. Use `from __future__ import annotations` for `X | None` hints.
- **Stale editable install** makes the tests import nothing or a different checkout. *Mitigation:* re-install from this checkout before running pytest.
- **Fixture line endings or a BOM added by an editor change line numbers.** *Mitigation:* write the fixtures with explicit bytes, and assert the `bad_amount.csv` line 3 behaviour in both t1 and t3.
- **The repo's `claims-reviewer` agent and glossary target the invoices code.** Their naming rules (for example "net") do not apply to `ledger` (`hld.md` §7).

**Scope guards (do NOT)**
- Do not edit `pyproject.toml` (no `[project.scripts]` entry and no dependency), `.github/workflows/ci.yml`, `.factory/`, `README.md`, or any existing `src/` or `tests/` file.
- In `CHANGELOG.md`, change nothing beyond the one added line.
- Do not add a third-party dependency, a `conftest.py`, `sys.path` manipulation, a `CI_FAIL` file, or shell scripts.
- Do not support other formats, fetched rates, configuration files, colour or charts.
- Do not use `float` anywhere in money handling.
- Never make a failing check pass by skipping, `xfail`-marking, deleting or loosening a test or assertion. Report a blocked check as blocked.
- Do not edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None. No question was needed. The developer's intake ruling covers the gaps, and they are recorded as assumptions A1–A3.
