# Plan — SCRUM-13: Monthly expense report from a CSV ledger

## Context

SCRUM-13 adds a new Python package, `ledger`, under `src/ledger/` in `roeeoz/play1`. It uses the standard library only. It parses a UTF-8 CSV ledger into frozen `Transaction`s and stops at the first bad row with a `LedgerError(line, reason)`. It builds a one-month report (`monthly_report`) in ILS, USD or EUR with exact `Decimal` arithmetic and a single `ROUND_HALF_EVEN` quantization per figure. It exposes `python -m ledger report FILE --month YYYY-MM [--base] [--top] [--json]` with exit codes 0/2/3. The acceptance criteria are spec §5, Scenarios 1–25. Work goes on branch `halo/feat/scrum-13-20261118-225125`, which merges into `main`. The requirement (`spec.md`), the design (`hld.md`) and the breakdown into work items `t1` → `t2` → `t3` (`work-items.md`) sit beside this file in `stories/SCRUM-13/`.

## Research findings

**Packaging and discovery**
- `pyproject.toml:23-24` finds packages under `src/` (`where = ["src"]`). A new `src/ledger/` is picked up with no manifest change.
- `pyproject.toml:10` declares `requires-python = ">=3.10"`. The floor is 3.10, so no 3.11+ API may be used.
- `pyproject.toml:26-28` sets pytest `testpaths = ["tests"]` and `addopts = "-q"`.
- `pyproject.toml:14-18` lists the existing console scripts. `ledger` gets none: the HLD §6 rejects one because it would need a `pyproject.toml` edit.

**Existing code and tests**
- `src/` holds only `guestbook/` and `testbed_utils/`.
- None of these exist yet: `src/ledger/`, `tests/test_ledger_*.py`, `tests/fixtures/ledger/`.
- `tests/fixtures/` holds only `.txt` and `.pdf` files.
- There is no `conftest.py`, no `tests/__init__.py` and no `sys.path` manipulation. Tests import the installed package (`.factory/testing.md`).
- `git check-ignore` confirms that neither `src/ledger/*.py` nor `tests/fixtures/ledger/*.csv` matches `.gitignore`.
- No `ledger` module can be imported in the environment today (`importlib.util.find_spec('ledger')` → `None`), so nothing shadows the new package.

**Test precedents**
- Subprocess style: `tests/test_hello_sh.py:1-15` uses `subprocess.run(..., capture_output=True, text=True)` and `REPO_ROOT = Path(__file__).resolve().parent.parent`.
- Fixture paths: `tests/test_num_summary_cli.py:11` builds them as `pathlib.Path(__file__).parent / "fixtures"`.
- Existing CLI tests (`tests/test_hello_cli.py:12-22`) call `main()` in-process. Scenario 25 requires the subprocess form instead, so the CLI tests do not follow that precedent.

**Gate**
- `.factory/testing.md` declares one required layer, `package-api` (`pytest`, production-path, `runBy: canonical-gate`).
- `.github/workflows/ci.yml:17-23` runs `pip install -e ".[test]"`, then `pytest`, on Python 3.12.
- The `gate` job (`.github/workflows/ci.yml:25-37`) fails only if `CI_FAIL` exists at the repository root.
- No linter, formatter or type checker is configured.

**Repository layout gate**
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:12-20` has four rules:
  - Python source lives in `src/`.
  - Tests live in `tests/`.
  - No file in the diff is over 200 KB.
  - `PLAY-G4`: the PR adds a line under `## Unreleased` in `CHANGELOG.md`.
- `CHANGELOG.md:3` is `## Unreleased`. The last entry is `CHANGELOG.md:8` (PLAY-175), in the style `- <KEY>: add \`<path>\`, ….`

**Local environment: the editable install points elsewhere (fact)**
- The pod has `testbed-utils` installed editable.
- Its `__editable__.testbed_utils-0.1.0.pth` points at `/root/.halo/workspaces/delivery-12278c0e3d51d219068ac02b956b6958/…/src`, a different workspace.
- Until `pip install -e ".[test]"` is re-run from this checkout, `import ledger` fails and `testbed_utils` resolves to another tree.
- The `.pth` is a plain path entry for `src/`. After one reinstall, every package under `src/`, including `ledger`, can be imported.

**`csv` behaviour (verified with Python 3.13)**
- `csv.reader(...).line_num` counts physical lines.
- A blank line yields `[]`. A whitespace-only line yields `['   ']`.
- A record with a quoted field spanning lines 4–5 reports `line_num == 5`. So "previous `line_num` + 1" is the record's first physical line, as HLD §6 states.
- `parse_lines` keeps a leading `﻿` in the first header cell (`'﻿a'`), so it must strip it explicitly.

**Contracts touched**
- There are no cross-repo contracts. The public names are fixed by spec §7 and HLD §5: `Transaction`, `LedgerError` (`.line`, `.reason`), `parse_lines`, `parse_csv`, `RATES`, `CategoryTotal`, `monthly_report`, `report.to_dict()`.
- The wire formats are fixed by spec §5: error reasons, text lines, JSON keys and exit codes.

**Arithmetic check (the sample fixture can reproduce every stated figure)**
- March in ILS:
  - income = 12000.00 + 250.00 USD × 3.70 = 12925.00
  - expense = −1500.00 − 760.50 − 444.00 − 321.00 = −3025.50
  - net = 9899.50
- In USD:
  - salary 12000 / 3.70 = 3243.2432… → `3243.24`
  - income 3493.2432… → `3493.24`
  - expense −817.7027… → `-817.70`
  - net 2675.5405… → `2675.54`
- Scenario 11: 0.05 / 4 = 0.0125 → `0.01`. Three of them sum to 0.0375 → `0.04` under `ROUND_HALF_EVEN`.

**Remaining unknowns:** none blocking. The residual edge behaviours are listed as assumptions below.

## Locked decisions and assumptions

**Locked decisions**
- Stdlib only.
- No change to any existing file. The one exception is a single `CHANGELOG.md` line per work item (HLD §7, following PLAY-175's precedent; repo rule `PLAY-G4`).
- Public names, signatures and defaults:
  - `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`;
  - `RATES` = `{"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}`.
  (spec FR6–FR7, HLD §5)
- Exact reason strings, text lines, JSON object and exit codes (spec §5, Scenarios 5–7 and 19–23). `str(LedgerError)` is `line {line}: {reason}`.
- Line tracking uses `csv.reader` and `line_num`, with a record's line = previous `line_num` + 1. Blank or whitespace-only records are skipped but still counted (HLD §6).
- Within-row check order (HLD §6):
  1. field count
  2. empty id
  3. duplicate id
  4. date shape, then calendar date
  5. amount shape (ASCII `[+-]?\d+(\.\d+)?`), then more than two decimal places, then zero
  6. currency (case-sensitive)
  7. category
- The field count is compared with the header's own cell count (HLD §6, spec A3).
- Month rule: ASCII `^\d{4}-(0[1-9]|1[0-2])$`. Plain `ValueError` for caller errors (HLD §6, spec FR12).
- Conversion is per transaction at full precision. Each figure is quantized once to `0.01` with `ROUND_HALF_EVEN`. Categories are ordered by (−|total|, name) (spec FR7–FR9).
- Dependency direction: cli → report → parser/model. Ownership lanes are t1 parser, t2 report, t3 cli. Module file names are the implementer's choice (HLD §2).
- CLI (HLD §6):
  - `add_subparsers(required=True)`, `choices` for `--base`, and custom types for `--month` and `--top`;
  - a file that cannot be opened or decoded exits 2;
  - a `LedgerError` exits 3 with `error: {FILE}:{line}: {reason}`;
  - nothing goes to stdout on any error.
- CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", ...]`, `cwd` at the repository root and no `sys.path` manipulation (spec Scenario 25).

**Assumptions**
- **Header line.** The header is the first record `csv.reader` yields, including a blank one.
  - With no records at all, parsing raises `LedgerError(1, "missing header")`.
  - A first line that is blank (`[]`) is also treated as `missing header`.
  - Evidence: the spec says "the first line is the header".
  - If wrong: only an untested edge message changes.
- **Repeated header name.** When a named column repeats, its first occurrence is used (HLD §6).
- **Signed zero.**
  - Quantizing a small negative exact sum (for example −0.004 after conversion) yields `Decimal("-0.00")`.
  - The report normalizes every quantized zero to `Decimal("0.00")` so that output never shows `-0.00`.
  - Evidence: spec §4 says figures show `0.00`.
  - If wrong: a cosmetic difference in an edge that no criterion tests.
- **Sort key.** Categories are sorted on the exact (pre-quantization) total, then by name. Scenario 14 ties are equal in both exact and quantized form.
  - Evidence: HLD §6 allows either key and asks for the choice to be documented. The exact total avoids reordering by rounding.
  - If wrong: no stated figure changes.
- **Sign convention.** Income sums amounts > 0, expense sums amounts < 0, and net sums all amounts. `count` is the number of the month's transactions. `CategoryTotal.count` is per category.
- **Report type.** The report is a frozen dataclass whose `categories` is a `tuple` or `list` of `CategoryTotal`.
  - Scenario 9 compares with a list. Tests compare with `list(report.categories)`, or the field is built as a list on a frozen dataclass.
  - Prefer a tuple for immutability, and assert with `list(...)` in tests.
- **Messages for unreadable files.**
  - A file that cannot be opened or decoded prints one stderr line, `error: {FILE}: {OS or decode message}`, and exits 2.
  - The spec requires only "a message on stderr".
- **`--month` value.**
  - In `report`, `--month` is a required option (`required=True`) with a custom type that reuses the report module's month rule.
  - The CLI imports that rule from the report module. It does not duplicate the regex.
- **Header-level errors on the CLI** exit 3 as `error: {FILE}:1: {reason}` (spec A2, work item t3).

## Solution proposal

Add a self-contained package, `src/ledger/`, laid out as HLD §2 describes. Proposed module names (the implementer's choice, lanes binding):
- `src/ledger/model.py`: `Transaction` and `LedgerError`.
- `src/ledger/parser.py`: `parse_lines` and `parse_csv`.
- `src/ledger/report.py`: `RATES`, `CategoryTotal`, `MonthlyReport`, `monthly_report`, and the month validator.
- `src/ledger/cli.py`: `main(argv=None) -> int`.
- `src/ledger/__main__.py`: `raise SystemExit(main())`.
- `src/ledger/__init__.py`: re-exports the public names.

**Parser**
- `parse_lines` wraps the iterable in `csv.reader` and keeps `prev = reader.line_num` between records, so that each record's line is `prev + 1`.
- On the header record:
  - strip a leading `﻿` from cell 0;
  - trim the cells;
  - build a name → first-index map;
  - report missing names in the canonical tuple order.
- For each later record:
  - skip it if every cell is whitespace;
  - otherwise trim the cells and run the fixed check order, raising `LedgerError(line, reason)` on the first failure.
- On success, record `id → line` for the duplicate check.
- Amount:
  - Match `re.fullmatch(r"[+-]?[0-9]+(\.[0-9]+)?", text)`. ASCII-only classes reject `NaN`, `Infinity`, exponents, `_` and non-ASCII digits.
  - Then check the fractional length (> 2 is an error).
  - Then build `Decimal(text)` and reject zero.
- Date:
  - Match `re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", text)`, then `date.fromisoformat` inside `try`/`except ValueError`, which gives "not a calendar date".
- `parse_csv(path)` opens with `encoding="utf-8-sig", newline=""` and returns `parse_lines(f)` inside the `with` block.
- `LedgerError` subclasses `ValueError`. It stores `line` and `reason`, and `__str__` returns `f"line {line}: {reason}"`.

**Report**
- `monthly_report` validates its arguments first:
  - the month rule;
  - `base in rates`;
  - `top is None or top >= 1`, with `bool` rejected as well.
- It filters with `t.date.year == y and t.date.month == m`.
- It converts each amount as `t.amount * rates[t.currency] / rates[base]` in the default context.
- It accumulates exact sums (income, expense, net, per-category total and count). It then quantizes each with `Decimal("0.01")` and `ROUND_HALF_EVEN`, normalizing a signed zero.
- It sorts categories by `(-abs(exact), name)` and slices `[:top]`.
- Plain `Decimal` addition is used, never `sum(start=0.0)`. Accumulators start at `Decimal(0)`.
- `MonthlyReport.to_dict()` returns the keys in spec order, with `str()` amounts.

**CLI**
- `argparse.ArgumentParser(prog="python -m ledger")` with `add_subparsers(dest="command", required=True)`.
  - Setting `dest` is required: Python 3.10's argparse otherwise raises `TypeError` while formatting the "required" error.
- The `report` subparser has:
  - `file`;
  - `--month`, required, with a month type that raises `argparse.ArgumentTypeError`;
  - `--base`, with `choices=["ILS","USD","EUR"]` and `default="ILS"`;
  - `--top`, with an int ≥ 1 type;
  - `--json`, as `store_true`.
- argparse already exits 2 on usage errors and 0 on `--help` (help text on stdout).
- `main` calls `parse_csv(args.file)` and handles exceptions in this order:
  1. `LedgerError` → stderr `error: {file}:{e.line}: {e.reason}`, return 3.
  2. `OSError` / `UnicodeDecodeError` → one stderr line, return 2.
- It then calls `monthly_report`, renders the whole output to one string, and writes it to stdout only at the end.
- Text output is the 13-line form, or `categories: none` when the month has no categories. JSON output is `json.dumps(report.to_dict())`.

**Alternatives rejected**
- A console-script entry: it needs a `pyproject.toml` edit.
- In-process `main()` CLI tests: Scenario 25 forbids them.
- A hand-rolled line splitter: it breaks quoting.
- `Decimal(text)` as the number test: it accepts `NaN`, `1e3` and `1_0`.
- Rounding per transaction: it violates Scenario 11.

## Ordered implementation steps

### Work item t1 — model and parser

1. **Create the model.** Write `src/ledger/model.py` with `Transaction` (`@dataclass(frozen=True)`; fields `id`, `date`, `amount`, `currency`, `category`, `memo`) and `LedgerError(ValueError)` with `.line`, `.reason` and `__str__`.
   - Advances: Scenarios 1 and 5.
   - Test layer: `package-api` (pytest), via `tests/test_ledger_parse.py`.
2. **Create the parser.** Write `src/ledger/parser.py` with `parse_lines` and `parse_csv`, as the Solution proposal describes.
   - Covers:
     - header mapping (any order, extra columns ignored, first occurrence wins);
     - BOM stripping in both entry points;
     - skipping blank and whitespace-only records while still counting them;
     - first-physical-line numbering, including multi-line quoted fields;
     - the full check order and exact reason strings;
     - stopping at the first error.
   - Advances: Scenarios 2–8.
   - Test layer: `package-api`.
3. **Create `src/ledger/__init__.py`.** Re-export `Transaction`, `LedgerError`, `parse_lines` and `parse_csv`, and list them in `__all__`.
   - Advances: Scenarios 1 and 8 (public import surface).
   - Test layer: `package-api`.
4. **Add the fixtures**, all UTF-8 and LF line endings, each well under 200 KB:
   - `tests/fixtures/ledger/sample.csv`: the header plus `t001`…`t009`. March:
     - salary 12000.00 ILS;
     - rent −1500.00 ILS;
     - freelance 250.00 USD;
     - two groceries rows in ILS summing to −760.50 (for example −410.25 and −350.25);
     - software −444.00 ILS;
     - travel −321.00 ILS;
     - at least one empty memo and one ordinary memo.

     Outside March: `2026-02-27` groceries −99.99 ILS and one `2026-04-01` row. The memos must not need quoting, so the file stays simple.
   - `tests/fixtures/ledger/bom_blank.csv`: a leading BOM, a blank line and a whitespace-only line between two valid rows, one empty memo, and one memo `"a, b"`. Write it as bytes so the BOM is real.
   - `tests/fixtures/ledger/empty.csv`: zero bytes.
   - Advances: Scenarios 1, 3 and 7. The sample also feeds Scenarios 9, 10, 13, 16, 19 and 20.
   - Test layer: `package-api`.
5. **Write `tests/test_ledger_parse.py`** with one test per scenario, using `pytest.mark.parametrize` for the Scenario 5 reasons:
   - every listed reason, plus `NaN`, `Infinity`, `1e3`, `1_0` and a non-ASCII digit (for example `'١'`) → "is not a number";
   - a row with several bad fields → the first check in the fixed order;
   - a multi-line quoted memo followed by a bad row → the correct line;
   - extra header columns → `expected 7 fields, got 6`-style count;
   - Scenario 6, with a blank line between the duplicates;
   - Scenario 7: missing columns, and `empty.csv`;
   - Scenario 8: `parse_lines(io.StringIO(text))` equals `parse_csv(path)` on the same content, with and without a BOM;
   - frozen-ness: assigning to a field raises `dataclasses.FrozenInstanceError`;
   - `Decimal("12000.00")` keeps its exponent: compare `str(t.amount)`.

   Locate fixtures with `Path(__file__).parent / "fixtures" / "ledger"`.
   - Advances: Scenarios 1–8.
   - Test layer: `package-api`.
6. **Add the t1 CHANGELOG line.** Append one line after `CHANGELOG.md:8`, for example ``- SCRUM-13: add the `ledger` package with its CSV ledger parser (`parse_csv`, `parse_lines`).``
   - Satisfies: `PLAY-G4`.
   - Test layer: none (repository layout gate only).

### Work item t2 — report

7. **Create `src/ledger/report.py`** with:
   - `RATES`;
   - `CategoryTotal` (frozen; `name`, `total`, `count`);
   - `MonthlyReport` (frozen; `month`, `base`, `count`, `income`, `expense`, `net`, `categories`, and `to_dict()`);
   - a module-level month validator;
   - `monthly_report`, as the Solution proposal describes.

   It imports only `Transaction`, from the model module.
   - Advances: Scenarios 9–18.
   - Test layer: `package-api`.
8. **Extend `src/ledger/__init__.py`.** Add `RATES`, `CategoryTotal` and `monthly_report` to the imports and to `__all__`.
   - Advances: the Scenario 9–18 public surface.
   - Test layer: `package-api`.
9. **Write `tests/test_ledger_report.py`.** Build transactions from `parse_csv(sample.csv)` for Scenarios 9, 10, 13, 15 and 16, and construct `Transaction` directly for Scenarios 11, 12, 14 and 17.
   - Scenario 9: assert `str()` forms as well as values, because `Decimal("9899.5") == Decimal("9899.50")` would hide a missing quantize.
   - Scenario 15: assert `to_dict()` equality exactly.
   - Scenario 18: parametrize the six bad months, an unknown base and `top=0`, and assert the raised error is a `ValueError` that is not a `LedgerError`.
   - Determinism: two calls give equal reports.
   - Immutability: assigning a field raises `FrozenInstanceError`.
   - Advances: Scenarios 9–18.
   - Test layer: `package-api`.
10. **Add the t2 CHANGELOG line** under `## Unreleased`, after t1's line.
    - Satisfies: `PLAY-G4`.

### Work item t3 — CLI

11. **Create `src/ledger/cli.py`** with `build_parser()` and `main(argv=None) -> int`, as the Solution proposal describes.
    - The `--month` type reuses the report module's validator.
    - `--top` parses as `int` and must be ≥ 1, otherwise it raises `ArgumentTypeError`.
    - Handle `LedgerError` before `OSError` / `UnicodeDecodeError`. `UnicodeDecodeError` is a `ValueError`, and so is `LedgerError`.
    - Write stdout once, after success.
    - Do not modify the parser or report modules.
    - Advances: Scenarios 19–24.
    - Test layer: `package-api` (subprocess).
12. **Create `src/ledger/__main__.py`.** It calls `raise SystemExit(main())` from `ledger.cli`.
    - Advances: Scenarios 19 and 25.
    - Test layer: `package-api`.
13. **Add `tests/fixtures/ledger/bad_amount.csv`.** Line 1 is the header, line 2 is a valid row, and line 3 is a row with amount `-2.505`.
    - Advances: Scenario 23.
    - Test layer: `package-api`.
14. **Write `tests/test_ledger_cli.py`.**
    - Use a helper that runs `subprocess.run([sys.executable, "-m", "ledger", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)`. Pass fixture paths relative to the repository root (`tests/fixtures/ledger/...`), so that Scenario 23's FILE echo is checked as given.
    - Scenario 19: compare stdout exactly with the 13-line string plus its trailing newline, and check stderr is `""`.
    - Scenario 20: `json.loads` equality.
    - Scenario 21: check the suffix.
    - Scenario 22: parametrize no subcommand, a missing `--month`, `--month 2026-13`, `--top 0`, `--base GBP` and a missing file. Each must give exit 2, stdout `""` and non-empty stderr.
    - Non-UTF-8 file: write bytes `b"\xff\xfe..."` to `tmp_path`, and expect exit 2, one stderr line and no `Traceback` in stderr.
    - Scenario 23: stderr is exact, with `"\n"`.
    - Header errors via `tmp_path`: exit 3 with `error: {FILE}:1: missing header` and `missing column(s): …`.
    - Scenario 24: `--help` exits 0 and `--month` appears in stdout.
    - Determinism: two runs give identical stdout.
    - Advances: Scenarios 19–25.
    - Test layer: `package-api`.
15. **Add the t3 CHANGELOG line** under `## Unreleased`, after t2's line.
    - Satisfies: `PLAY-G4`.

**Implicit invariants**
- Authorization and tenancy: not applicable. This is a local, single-user CLI.
- Concurrency: none. The code is pure and synchronous. Idempotency is covered by the determinism tests.
- Validation and error paths: the parametrized error tests in steps 5, 9 and 14.

**Dependencies:** stdlib only, so nothing new is acquired. `pytest>=8` comes from the existing `test` extra (`pyproject.toml:21`) through `pip install -e ".[test]"`.

**Generated deliverables:** none. The fixtures are hand-written source files, not generated, and no binary of 1 MiB or more is added, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title (from `work-items.md`) |
|---|---|---|
| 1–6 | t1 | ledger: Transaction model, LedgerError and CSV parser (parse_lines / parse_csv) with fixtures |
| 7–10 | t2 | ledger: monthly_report with fixed-rate conversion, half-even rounding, ordering, top-N and to_dict |
| 11–15 | t3 | ledger: `python -m ledger report` CLI with text/JSON output and exit codes 0/2/3 |

All three work items have steps. Each work item builds and passes `pytest` on its own: t1 needs nothing from later items, t2 needs only t1, and t3 needs t1 and t2.

## Verification and CI gate

**Canonical gate** (from `.factory/testing.md` and `.github/workflows/ci.yml:17-23`), run from the repository root in this order:
1. `pip install -e ".[test]"`
2. `pytest`

Run it once locally on the committed SHA.
- The local re-install is mandatory: the pod's existing editable install points at another workspace's `src/` (see Research findings).
- After the install, confirm that `python -c "import ledger, testbed_utils; print(ledger.__file__, testbed_utils.__file__)"` shows paths inside this checkout.

**Required layer:** `package-api` (`pytest`, production-path).
- It runs unprivileged in a pod.
- The authoritative credit is the provider run of the `test` job at the exact head, on Python 3.12.

**Provider CI:** no configuration change is needed. The new test files fall under `testpaths = ["tests"]` automatically.

**The gate must show:**
- `pytest` exits 0, and the full suite passes, including every existing test.
- `tests/test_ledger_parse.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py` are collected and pass, in the files each work item adds.
- No test is skipped or marked xfail.
- The `gate` job is green, because no `CI_FAIL` file exists.

**Repository layout gate:**
- Source is in `src/ledger/` and tests are in `tests/`.
- No file is larger than 200 KB.
- `CHANGELOG.md` gains one line under `## Unreleased` per work item.

**Diff boundary:** `git diff --stat main...HEAD -- . ':!stories/SCRUM-13'` lists only new files under `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`, plus `CHANGELOG.md`.

## Risks and scope guards

**Risks and mitigations**
- **Stale editable install** (`import ledger` fails, or tests run against another tree): re-install from this checkout before `pytest`, and verify `__file__` paths as described in the Verification section.
- **Python 3.10 compatibility:**
  - Pass `dest` to `add_subparsers`.
  - Do not use `datetime.date.fromisoformat` extended formats (3.11+), `tomllib`, `ExceptionGroup` or `StrEnum`.
  - The shape regex runs before `fromisoformat`.
- **Precision loss in conversion:** USD and EUR rates do not divide evenly. The default 28-digit context keeps errors far below `0.005` at ledger scale.
  - Do not quantize before summing.
  - Do not mix in `float` anywhere, including in `to_dict` and JSON.
- **Exception ordering in the CLI:** `LedgerError` and `UnicodeDecodeError` are both `ValueError`s. Catch `LedgerError` first, and never catch a bare `ValueError`, which would turn data errors into usage errors.
- **Partial stdout on error:** render the whole output to one string before writing anything.
- **Fixture drift:** the sample's rows must reproduce every figure the spec states. The t2 and t3 tests re-check them, so a fixture change in t1 surfaces at once.
- **Shadowing in subprocess tests:** `-m` puts `cwd` on `sys.path`. Running from the repository root is safe because no `ledger` entry exists there. Never create one.

**Scope guards (the implement phase must NOT)**
- Edit `pyproject.toml` (no console script, no dependency), `.github/workflows/ci.yml`, `.factory/`, `README.md`, any existing test or fixture, or `src/guestbook/` / `src/testbed_utils/`.
- Edit or reorder existing `CHANGELOG.md` lines. Each work item only appends one line under `## Unreleased`.
- Add a third-party dependency, `conftest.py`, `tests/__init__.py` or any `sys.path` manipulation.
- Fetch exchange rates, read configuration files, support other formats, date ranges or currencies beyond ILS, USD and EUR.
- Let a later work item modify an earlier item's modules, beyond t2 adding exports to `__init__.py`. t3 must not touch the parser or report modules.
- Add a linter, formatter or type-checker configuration.
- Make a failing check green by deleting, skipping, `xfail`-ing or loosening an assertion (for example, replacing an exact stdout or stderr comparison with `in`). A blocked check is reported as blocked.
- Create `CI_FAIL`.
- Edit `stories/SCRUM-13/spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None. No question was needed. The residual edge behaviours are recorded as assumptions under Locked decisions and assumptions.
