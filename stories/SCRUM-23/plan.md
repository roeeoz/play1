# Plan — SCRUM-23 Monthly expense report from a CSV ledger

## Context

SCRUM-23 adds a new stdlib-only Python package `ledger` to the `play1` repository. It parses a UTF-8 CSV ledger into immutable transactions and fails on the first bad row, naming its physical line (AC 1–8). It builds a one-month report per category in a base currency at fixed rates, with exact `Decimal` arithmetic and one half-to-even rounding per figure (AC 9–18). It exposes the report as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`, with exit codes 0/2/3 (AC 19–25). The change lands on the work branch `halo/feat/scrum-23-20261119-013411`, which merges into `main`. The work is split into three sequential work items: t1 (parser), t2 (report) and t3 (CLI). The approved requirement is in `spec.md`, the design in `hld.md` and the breakdown in `work-items.md`, all three beside this file in `stories/SCRUM-23/`.

## Research findings

**Repository layout and manifest**
- `pyproject.toml:23-24` discovers packages with `[tool.setuptools.packages.find] where = ["src"]`, so a new `src/ledger/` package is installed with no manifest change.
- `pyproject.toml:26-28` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- `pyproject.toml:10` sets `requires-python = ">=3.10"`. Code must not use 3.11+ features such as `datetime.date.fromisoformat` leniency, `typing.Self` or `ExceptionGroup`.
- The local interpreter is Python 3.13. CI runs Python 3.12.
- `pyproject.toml:14-18` declares console scripts for other tools. This story adds none: it uses a `__main__.py` instead (hld §6).

**Existing code**
- `src/` currently contains `testbed_utils/` and `guestbook/`. There is no `src/ledger/`, no `tests/test_ledger_*.py` and no `tests/fixtures/ledger/`, so everything this story builds is new.
- CLI pattern to follow: `src/testbed_utils/numsummary.py:76-98` uses `argparse.ArgumentParser`, prints errors to `sys.stderr` and calls `sys.exit(code)`. `src/testbed_utils/hello.py:21` is the same kind of CLI.
- Subprocess test pattern to follow: `tests/test_hello_sh.py:2-24`, `tests/test_qa_s3_greeting.py:8` and `tests/test_qa_20261109_s1_a.py:12` all call `subprocess.run(...)` and assert on `returncode`, `stdout` and `stderr`.
- Fixture path pattern to follow: `tests/test_num_summary_cli.py:11` defines `FIXTURES = pathlib.Path(__file__).parent / "fixtures"`.

**Canonical gate**
- `.factory/testing.md` declares one required layer, `package-api` (production-path, command `pytest`, `runBy: canonical-gate`). It is run as `pip install -e ".[test]"` followed by `pytest`, which is the `test` job in `.github/workflows/ci.yml:40-52` (Python 3.12, 5-minute timeout).
- No `conftest.py` exists and nothing manipulates `sys.path`. Tests therefore import the installed distribution.
- No linter, formatter, type checker or coverage tool is configured.
- The `gate` job in `ci.yml:54-66` fails only if a `CI_FAIL` file exists at the repository root.

**Pull-request layout gate**
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-20` sets four rules: source in `src/` and tests in `tests/`; any new shell script is executable with a shebang; no file is 200 KB or larger; and the diff adds a line under `## Unreleased` in `CHANGELOG.md`, otherwise blocker `PLAY-G4`.
- `CHANGELOG.md:3` has the `## Unreleased` heading. Its existing entries use the form `- PLAY-NNN: …`.

**Other repository context**
- No `AGENTS.md`, `CLAUDE.md` or `.factory/memory/` exists. There is no `.factory/delivery-assets`, and this story adds no binary deliverables.

**Contracts**
- All contracts are internal to the new package and are fixed by spec AC 5–7, AC 15, AC 19–23 and hld §5:
  - the public names re-exported from `ledger/__init__.py`;
  - the reason texts;
  - the key order of `to_dict()`;
  - the 13-line text format;
  - the exit codes;
  - the stderr format `error: {FILE}:{line}: {reason}\n`.
- No cross-repository value or external data source is involved.

**Behaviour of `csv` and `decimal` that the design relies on (verified stdlib behaviour)**
- `csv.reader.line_num` counts physical source lines consumed. A row therefore starts on the previous `line_num + 1`, including after blank lines and quoted multi-line fields.
- `csv.reader` yields `[]` for an empty line and `['   ']` for a whitespace-only line. Both must be treated as blank.
- `Decimal("abc")` raises `decimal.InvalidOperation`. `Decimal("NaN")` and `Decimal("Infinity")` parse successfully, so they must be rejected with `is_finite()`.
- `Decimal("12000.00")` keeps its exponent of -2.
- `Decimal(0).quantize(Decimal("0.01"))` is `Decimal("0.00")`.

**Fixture arithmetic (resolves RK1)**
- Conversion is linear, so any `sample.csv` whose March rows convert to the ILS totals in AC 9 also reproduces AC 10 and AC 20.
- Checked results: 12000/3.70 → 3243.24; 12925/3.70 → 3493.24; −3025.50/3.70 → −817.70; 9899.50/3.70 → 2675.54.
- The proposed rows are in step 2.

**Remaining unknowns**
- None block the work. The small residual choices are recorded as assumptions below.

## Locked decisions and assumptions

**Locked decisions**
- The package is named `ledger`, lives under `src/ledger/` and uses the standard library only. No existing file changes except one `CHANGELOG.md` line per pull request. Sources: spec §2, §6 and A1.
- The public names are `parse_lines`, `parse_csv`, `Transaction` (a frozen dataclass with `id, date, amount, currency, category, memo`), `LedgerError` (`.line`, `.reason`, `str` = `line {line}: {reason}`), `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`, `RATES`, `CategoryTotal(name, total, count)` and report `.to_dict()`. Source: hld §5.
- The reason texts are exactly those in AC 5–7, and the same template applies to other values. Sources: spec A3 and hld E1.
- `parse_csv` opens files with `encoding="utf-8-sig", newline=""` and delegates to `parse_lines`. Source: AC 8.
- Money is a `Decimal` throughout. Each figure is the exact sum, quantized once to `0.01` with `ROUND_HALF_EVEN`. Sources: AC 10–12 and hld §6.
- Categories are ordered by absolute total descending, then by name ascending. `top` applies to the category list only. Sources: AC 13–14.
- A bad `month`, a `base` missing from `rates`, or `top < 1` raises `ValueError`, never `LedgerError`. Source: AC 18.
- The CLI is reached through `python -m ledger` via `__main__.py`, and `pyproject.toml` stays untouched. Source: hld §6.
- Exit codes are 0 (success and `--help`), 2 (usage error, including a FILE that cannot be opened) and 3 (data error). Sources: AC 22–24.
- The CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", ...]` and no `sys.path` manipulation. Source: AC 25.
- Within a row, checks run in this order: field count, date, amount, currency, category, id, duplicate id. Source: hld E2.
- A file with no non-blank line raises `LedgerError(1, "missing header")`. Source: hld E3.
- A file that cannot be decoded as UTF-8 is a usage error with exit 2. Source: hld E5.

**Assumptions**
- **P1 — Header names are trimmed.** Required-column matching is case-sensitive, as the spec spells the names. If a header name has a leading `﻿`, it is stripped in `parse_lines` too, so a `StringIO` holding a BOM behaves like `parse_csv` (AC 8).
  - Evidence: FR1 trims fields, and AC 8 requires both entry points to behave the same.
  - If wrong: only headers with padding or a BOM inside a `StringIO` behave differently.
- **P2 — Ordering and top-N use the quantized category totals** (the displayed values).
  - Evidence: AC 14 compares totals as they are reported.
  - If wrong: the order changes only for ties below one cent.
- **P3 — A transaction whose currency is not a key of a caller-supplied `rates` raises `ValueError`** when it falls inside the month.
  - Evidence: AC 18 treats `rates` mismatches as caller errors.
  - If wrong: a different exception type is raised for a case the spec does not test.
- **P4 — A figure that rounds to negative zero is normalised to `0.00`.**
  - Evidence: AC 15 requires `"0.00"`. A negative zero only arises from sub-cent sums.
  - If wrong: an output of `-0.00` instead of `0.00` for a sub-cent negative sum.
- **P5 — Usage-error stderr text is argparse's own message**, or `error: …` for a file that cannot be opened.
  - Evidence: spec A2 says any non-empty message is acceptable.
  - If wrong: the wording changes, but no AC is affected.
- **P6 — The `CHANGELOG.md` entry uses the form `- SCRUM-23: …`**, one line per work item, appended under `## Unreleased`.
  - Evidence: `CHANGELOG.md:5-8` and spec A1.
  - If wrong: the wording of the entry changes, but rule PLAY-G4 is still met.

## Solution proposal

Build one package with three layers. Each layer depends only on the layer below, and each layer is one work item (hld §2).

1. **Model and parser (t1)**
   - `src/ledger/model.py` holds:
     - `Transaction`, a `@dataclass(frozen=True)`;
     - `LedgerError(Exception)`, which stores `line` and `reason` and whose `__str__` returns `line {line}: {reason}`;
     - the constants `REQUIRED_COLUMNS = ("id", "date", "amount", "currency", "category", "memo")` and `CURRENCIES = ("ILS", "USD", "EUR")`.
   - `src/ledger/parser.py`, function `parse_lines(lines)`:
     - Wrap `lines` in `csv.reader`. Track the start line of each row as the previous `reader.line_num + 1`.
     - Skip rows whose fields are all blank once trimmed.
     - Treat the first non-blank row as the header. Strip a BOM, trim the names and report missing columns in `REQUIRED_COLUMNS` order.
     - Validate each data row in the order fixed by hld E2.
     - Keep a dictionary from `id` to its first line, to detect duplicates.
   - **Validation helpers:**
     - Dates: `re.fullmatch(r"\d{4}-\d{2}-\d{2}", s, re.ASCII)`, then `datetime.date(int, int, int)` inside `try/except ValueError`. This works on Python 3.10, where `fromisoformat` is stricter.
     - Amounts: `Decimal(s)`, with `InvalidOperation` and non-finite values reported as "is not a number"; then `-exponent > 2`, reported as "more than 2 decimal places"; then `== 0`, reported as "must not be zero".
   - `parse_csv(path)`: open the file with `encoding="utf-8-sig", newline=""` and return `parse_lines(f)`.

2. **Report (t2)**
   - `src/ledger/report.py` holds:
     - `RATES`;
     - `CategoryTotal`, a frozen dataclass;
     - `MonthlyReport`, a frozen dataclass with `month, base, count, income, expense, net, categories: list[CategoryTotal]` and `to_dict()`;
     - `monthly_report`.
   - `monthly_report` works in this order:
     1. Validate the arguments: `month` with `re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", month, re.ASCII)`, `base in rates`, and `top is None or top >= 1`.
     2. Filter the transactions by `(date.year, date.month)`.
     3. Convert each amount as `amount * Decimal(rates[cur]) / Decimal(rates[base])` in the default context. Precision 28 is enough.
     4. Accumulate the exact income (positive amounts), expense (negative amounts), net, and each category's total and count.
     5. Quantize each figure once, applying P4.
     6. Sort by `(-abs(total), name)` and slice `[:top]`.
   - `to_dict()` emits the keys in AC 15 order. Amounts are produced with `format(d, "f")`, which always gives two places and never scientific notation.

3. **Command line (t3)**
   - `src/ledger/cli.py`, `main(argv=None) -> int`:
     - An argparse parser with a required `report` subparser. Its arguments are positional `file`, `--month` (required, `type=` a validator that raises `argparse.ArgumentTypeError`), `--base` (`choices=["ILS","USD","EUR"]`, default `ILS`), `--top` (`type=` a positive-int validator) and `--json`.
     - Argparse already exits 2 with a message on stderr, and exits 0 for `--help` with output on stdout.
     - `OSError` and `UnicodeDecodeError` from `parse_csv` → print `error: …` to stderr and return 2.
     - `LedgerError` → print `error: {args.file}:{e.line}: {e.reason}` to stderr and return 3.
     - Otherwise print the text or JSON format and return 0.
   - `src/ledger/__main__.py`: `raise SystemExit(main())`.
   - The output is built in full before it is printed, so stdout stays empty on any error.
   - The `--month` rule (`YYYY-MM`, months 01–12) is defined once, as a helper in `report.py`, and the CLI reuses it (hld E4).

**Alternatives rejected**
- A `[project.scripts]` entry: it would change `pyproject.toml`, which spec §2 forbids.
- Rounding each row: AC 11 forbids it.
- Using `enumerate` over csv rows for line numbers: it miscounts blank lines and multi-line quoted fields.
- A single module: work-item ownership and reviewability favour the three-layer split the HLD names, though module names stay a suggestion.
- `float` anywhere in the money path: RK2.

## Ordered implementation steps

1. **Create the model.** Create `src/ledger/model.py` with `Transaction`, `LedgerError`, `REQUIRED_COLUMNS` and `CURRENCIES`. Create `src/ledger/__init__.py`, re-exporting `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` and listing them in `__all__`. Advances AC 1 and AC 5 (the `str(error)` form). Covered by `package-api` (pytest), new `tests/test_ledger_parser.py`.

2. **Add the t1 fixtures.** All files are UTF-8, under 1 KB, and are not binary deliverables.
   - `tests/fixtures/ledger/sample.csv`: header `id,date,amount,currency,category,memo` and these rows:
     - `t001` 2026-03-01 `12000.00` ILS salary
     - `t002` 2026-03-02 `-1500.00` ILS rent
     - `t003` 2026-03-05 `250.00` USD freelance
     - `t004` 2026-03-07 `-400.00` ILS groceries
     - `t005` 2026-03-14 `-360.50` ILS groceries
     - `t006` 2026-03-15 `-111.00` EUR software (= −444.00 ILS)
     - `t007` 2026-03-20 `-321.00` ILS travel
     - `t008` 2026-02-27 `-99.99` ILS groceries
     - `t009` 2026-04-01 `-1500.00` ILS rent
     - At least one row has an empty memo.
   - `tests/fixtures/ledger/bom_blank.csv`: a BOM, two rows, blank and whitespace-only lines between them, one empty memo, and one quoted memo containing a comma.
   - `tests/fixtures/ledger/empty.csv`: zero bytes.
   - `tests/fixtures/ledger/bad_amount.csv`: a header, one valid row, and on line 3 an amount of `-2.505`.

   Advances AC 1, 3, 7 and 23. Covered by `package-api`.

3. **Implement the parser.** Implement `src/ledger/parser.py` (`parse_lines`, `parse_csv`) as described in the solution proposal: physical line tracking, blank skipping, header and missing-column handling, the check order from hld E2, and duplicate ids. Advances AC 1–8. Covered by `package-api`.
   - **Error paths to cover:** every reason in AC 5; duplicate id across a blank line (AC 6); missing columns and missing header (AC 7); a blank-only file → `missing header` (E3).
   - **Validation invariants:** `NaN`, `Infinity` and `-0.00` are rejected; `12000.00` keeps its scale; currency matching is case-sensitive.

4. **Test the parser.** Add `tests/test_ledger_parser.py`.
   - It imports `from ledger import …` with no `sys.path` changes or `conftest.py`, and locates fixtures with `pathlib.Path(__file__).parent / "fixtures" / "ledger"`.
   - **Tests to include:**
     - one test or parametrised case per AC 1–8;
     - `parse_lines(io.StringIO(text))` compared with `parse_csv` on the same text (AC 8);
     - frozen-ness (`dataclasses.FrozenInstanceError`);
     - `bad_amount.csv` → line 3.
   - The tests also assert the sample rows' (id, date, amount, currency, category). This fixes RK1 in t1.
   - Covered by `package-api`.

5. **Add the t1 changelog line.** Append `- SCRUM-23: add the \`ledger\` package's transaction model and validating CSV parser.` under `## Unreleased` in `CHANGELOG.md`. This is gate PLAY-G4; no test layer applies (it is a layout gate).

6. **Implement the report.** Create `src/ledger/report.py` with `RATES`, `CategoryTotal`, `MonthlyReport` with `to_dict()`, the shared month-validation helper and `monthly_report`, as described in the solution proposal. Advances AC 9–18. Covered by `package-api`.
   - **Error paths:** `ValueError` for each bad month in AC 18, for an unknown `base`, for `top` of 0 or below, and for a transaction currency missing from `rates` (P3).
   - **Invariant:** no `float` anywhere. `rates` values are wrapped in `Decimal(...)` so that int Decimals work (AC 17).

7. **Export the report names.** Edit `src/ledger/__init__.py` to also re-export `monthly_report`, `RATES` and `CategoryTotal`. Advances AC 9 and 10. Covered by `package-api`.

8. **Test the report.** Add `tests/test_ledger_report.py`, which builds transactions from `parse_csv(sample.csv)` and from `Transaction(...)` literals.
   - **Tests to include:**
     - AC 9 and AC 10, including USD income, expense and net;
     - AC 11 (the 0.05 ILS rows in EUR → `0.01`, and three rows → `0.04`);
     - AC 12, checked with `str(...)`;
     - AC 13 (`top=2`, a large `top`, and `None`);
     - AC 14 (a tie);
     - AC 15 (equality of `to_dict()` and its key order);
     - AC 16, AC 17 and AC 18 (parametrised).
   - Covered by `package-api`.

9. **Add the t2 changelog line.** Append `- SCRUM-23: add \`ledger.monthly_report\`, the monthly report by category in a base currency.` under `## Unreleased`.

10. **Implement the CLI.** Create `src/ledger/cli.py` (`main(argv=None) -> int`, the argparse layout, the formatter for the 13-line text format with `categories: none`, JSON via `json.dumps(report.to_dict())`, and the mapping of errors to exit codes). Create `src/ledger/__main__.py`. Advances AC 19–24. Covered by `package-api` through subprocess tests.
    - **Invariants:**
      - Nothing is written to stdout before the outcome is known.
      - FILE is echoed exactly as given.
      - Output is deterministic: no clock, no locale, no colour.
      - A FILE that cannot be decoded as UTF-8 exits 2 (E5).

11. **Test the CLI.** Add `tests/test_ledger_cli.py` with a helper that runs `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, cwd=REPO_ROOT)`, where `REPO_ROOT = pathlib.Path(__file__).parent.parent`. Fixtures are passed as the relative path `tests/fixtures/ledger/…`, so the stderr in AC 23 is predictable. Advances AC 19–25. Covered by `package-api`.
    - Because `ledger` lives under `src/` and not at the repository root, `cwd=REPO_ROOT` does not shadow the installed package (AC 25).
    - **Assertions:**
      - exact stdout for AC 19;
      - `json.loads` equality for AC 20;
      - stdout ending for AC 21;
      - parametrised usage errors for AC 22 (exit 2, empty stdout, non-empty stderr);
      - exact stderr for AC 23;
      - help output for AC 24;
      - byte-identical output across two runs.

12. **Add the t3 changelog line.** Append `- SCRUM-23: add the \`python -m ledger report\` command line.` under `## Unreleased`.

**Dependencies:** none new. `pip install -e ".[test]"` installs the existing `pypdf`, `flask` and `pytest`. A developer whose environment holds an older editable install must re-run it so that `ledger` is discovered; CI always installs fresh.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1, 2, 3, 4, 5 | t1 | ledger: transaction model and validating CSV parser (R1, R2) |
| 6, 7, 8, 9 | t2 | ledger: monthly report by category in a base currency (R3, R4) |
| 10, 11, 12 | t3 | ledger: `python -m ledger report` command line (R5) |

Every work item has steps. The AC coverage is: t1 covers AC 1–8, t2 covers AC 9–18 and t3 covers AC 19–25.

## Verification and CI gate

- **Canonical gate.** Run from the repository root, in this order: `pip install -e ".[test]"`, then `pytest`. This is the `test` job in `.github/workflows/ci.yml` on Python 3.12, and the only declared layer, `package-api` (production-path, `runBy: canonical-gate`).
  - Run the gate once locally on the committed SHA of each work item. The provider CI run at the exact head is authoritative.
  - The layer runs unprivileged in a pod. No layer needs another environment.
- **What the gate must show for each work item.**
  - `pytest` is green, covering the existing suite and the new `tests/test_ledger_parser.py`, then `tests/test_ledger_report.py`, then `tests/test_ledger_cli.py`. Every AC owned by the work item is asserted by at least one test.
  - No `CI_FAIL` file exists, so the `gate` job is green.
  - The diff adds a `## Unreleased` line (rule PLAY-G4), keeps code in `src/` and tests in `tests/`, and has no file of 200 KB or more.
- **No change to provider CI configuration.** No `.factory/testing.md` change is needed, because the new tests sit under the existing `package-api` layer. There is no `.factory/delivery-assets` obligation, because nothing binary is added.
- **Python 3.10 compatibility.** No 3.10 interpreter runs in CI. The implement phase must avoid 3.11+ APIs by construction. If a 3.10 interpreter is available, the same `pytest` can optionally be run under it.

## Risks and scope guards

**Risks**
- **RK1 — fixture arithmetic.** Mitigation: the rows in step 2 reproduce AC 9, 10 and 20 exactly. t1 asserts the row data, and t2 and t3 consume the fixture unchanged.
- **RK2 — rounding or precision drift.** Mitigation: `Decimal` is used end to end, there is a single `quantize` per figure, and JSON amounts are strings. AC 11 and AC 12 are tested.
- **Line numbers drift on multi-line quoted fields or blank lines.** Mitigation: use `reader.line_num` tracking, not `enumerate`. AC 6 tests the blank-line case.
- **A stale local editable install hides `ledger`.** Mitigation: reinstall before running `pytest`. CI is unaffected.
- **`CHANGELOG.md` is shared by all three work items.** They are strictly sequential and each one appends its own line, so no conflict is expected.

**Scope guards: the implement phase must not**
- Change `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/**`, `README.md`, `src/testbed_utils/**`, `src/guestbook/**` or any existing test or fixture. In `CHANGELOG.md`, only append one line under `## Unreleased`.
- Add a `conftest.py`, manipulate `sys.path` or `PYTHONPATH` in tests, or add a `[project.scripts]` entry.
- Add any third-party dependency, or add live rates, configuration files, other input formats, or month or year ranges.
- Use `float` in any money path, or round before summing.
- Create a `CI_FAIL` file.
- Make any test green by deleting, skipping, `xfail`-ing or weakening it. A failing required check is reported as blocked, not suppressed.

## Clarification outcomes

None
