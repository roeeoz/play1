# Plan — SCRUM-11 Monthly expense report from a CSV ledger

## Context

SCRUM-11 adds a new Python package, `ledger`, that uses only the standard library. It lives under `src/ledger/` in `play1` (branch `halo/feat/scrum-11-20261118-223416`, base `main`) and does three things:
- parses a CSV ledger with strict validation, and names the first bad row by its physical line number;
- totals one calendar month by category in a base currency (ILS, USD or EUR), with exact `Decimal` arithmetic and half-even rounding;
- exposes this as a library and as `python -m ledger report FILE --month YYYY-MM [--base …] [--top N] [--json]`, with exit codes 0, 2 and 3.

The acceptance criteria are Scenarios 1–25 in `spec.md` §5. The design is `hld.md` and the three-item breakdown (t1 → t2 → t3) is `work-items.md`. All three files sit beside this file in `stories/SCRUM-11/`.

## Research findings

**Manifest and packaging**
- `pyproject.toml` declares `[tool.setuptools.packages.find] where = ["src"]`, so a new `src/ledger/` package ships without editing the manifest.
- `requires-python = ">=3.10"`.
- The test extra is `pytest>=8`, and `[tool.pytest.ini_options] testpaths = ["tests"]`, `addopts = "-q"`.
- `[project.scripts]` exists but is out of bounds: the command is `python -m ledger`, so no console script is added.

**Existing code**
- `src/` holds only `guestbook/` and `testbed_utils/`.
- None of these exist yet: `src/ledger/`, `tests/test_ledger_*.py`, `tests/fixtures/ledger/`.

**Gate**
- Defined in `.factory/testing.md` and `.github/workflows/ci.yml` (job `test`): `pip install -e ".[test]"`, then `pytest`, on Python 3.12, with a 5-minute timeout.
- There is one declared layer, `package-api` (production-path, `runBy: canonical-gate`).
- No linter, formatter or type checker is configured.
- There is no `conftest.py` and no `sys.path` manipulation, so tests import the installed distribution.
- The `gate` job fails only if a `CI_FAIL` file exists at the repo root.

**Repository layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`)**
- Python source must be under `src/` and tests under `tests/`.
- No file may be larger than 200 KB.
- Rule 4 requires a new line under `## Unreleased` in `CHANGELOG.md`; without it the gate raises blocker `PLAY-G4`.
- `CHANGELOG.md:3` holds that heading. PLAY-156, PLAY-172 and PLAY-175 each added one line there.
- Rule 4 conflicts with the spec's "no edits to existing files" (see Clarification outcomes).

**Style precedents**
- `src/testbed_utils/numsummary.py:1-98` shows the CLI style: a module docstring, `from __future__ import annotations`, an `argparse.ArgumentParser(prog=…, description=_DESCRIPTION)`, and errors printed to `sys.stderr` before `sys.exit`.
- Subprocess tests already exist (`tests/test_hello_sh.py:11`, `tests/test_qa_s3_greeting.py:8`).
- Fixtures are found through `pathlib.Path(__file__).parent / "fixtures"` (`tests/test_num_summary_cli.py:11`).

**Contracts created**
These are all defined in `hld.md` §5 and are new:
- `LedgerError(line, reason)`, with `.line`, `.reason` and `str() == "line {line}: {reason}"`
- `Transaction` (a frozen dataclass)
- `parse_lines`, `parse_csv`
- `RATES`, `CategoryTotal`, `Report.to_dict()`, `monthly_report(...)`
- the CLI's exact output text and exit codes

There are no cross-repo contracts and no external data. The rates are a fixed constant.

**Checked arithmetic for the sample**
`hld.md` §7 proposes a `sample.csv` content set. It reproduces every figure:
- In ILS terms: freelance 231.25 EUR × 4.00 = 925.00; software -120.00 USD × 3.70 = -444.00; travel -80.25 EUR × 4.00 = -321.00. Expense is -1500 - 760.50 - 444 - 321 = -3025.50.
- In USD: 12000 / 3.70 → 3243.24, 12925 / 3.70 → 3493.24, -3025.50 / 3.70 → -817.70, 9899.50 / 3.70 → 2675.54.
- Scenario 11: 0.05 / 4 = 0.0125 → 0.01, and 3 × 0.0125 = 0.0375 → 0.04 (half-even).

**Local environment**
The local interpreter is Python 3.13. CI runs 3.12, and 3.10 is unavailable (`hld.md` §7).

**Remaining unknowns**
Only the CHANGELOG conflict remains.

## Locked decisions and assumptions

**Locked decisions**
- The package and modules are `src/ledger/{__init__,parser,report,cli,__main__}.py`. Tests are `tests/test_ledger_parse.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py`. Source: `hld.md` §2, `work-items.md`.
- Every reason string, the 13-line text output, the JSON shape and the exit codes 0/2/3 are byte-exact. Source: `spec.md` §3–§5.
- Money is `Decimal` end to end.
  - Conversion is `amount × rates[currency] ÷ rates[base]` at full precision.
  - Each figure is quantized once to `Decimal("0.01")` with `ROUND_HALF_EVEN`, independently of the others.
  - Negative zero is shown as `0.00`.
  - The computation runs in a local decimal context.
  - Source: `spec.md` FR7–FR8, `hld.md` §6.
- Validation runs in this order: blank (skip) → field count → date → amount → currency → category → id → duplicate. Source: `hld.md` §6.
- Line numbers:
  - A row's line is the previous `reader.line_num` + 1, so a row reports the line it starts on.
  - Header errors are reported on line 1.
  - In `expected N fields`, N is the header's actual field count.
  - Source: `hld.md` §6.
- Strict ASCII pre-checks (source: `hld.md` §6):
  - Date regex `[0-9]{4}-[0-9]{2}-[0-9]{2}`.
  - Amount regex: an optional `-`, ASCII digits, and an optional `.digits` part.
  - Month regex `^[0-9]{4}-(0[1-9]|1[0-2])$`.
- `parse_lines` strips a leading `\ufeff` itself. `parse_csv` opens with `encoding="utf-8-sig", newline=""`, does not swallow `OSError`, and turns a `UnicodeDecodeError` into `LedgerError(line, "file is not valid UTF-8")`. Source: `hld.md` §5–§6.
- The CLI (source: `hld.md` §6):
  - uses argparse with `add_subparsers(dest="command", required=True)`;
  - validates `--month` with a custom type;
  - restricts `--base` with `choices=["ILS", "USD", "EUR"]` and a default of `ILS`;
  - validates `--top` with a custom type that requires an integer ≥ 1.
- Usage errors and an unopenable FILE exit 2 through `parser.error`. A `LedgerError` exits 3 with `error: {FILE}:{line}: {reason}`. Source: `spec.md` FR15, `hld.md` §3.
- No third-party dependency and no change to `pyproject.toml` or `README.md`. Source: `spec.md` §6.

**Assumptions**
- **Categories are ordered by their quantized (displayed) absolute total**, then by name.
  - Evidence: Scenario 14 speaks of "equal absolute totals", meaning the reported figures.
  - If wrong: two categories whose exact sums differ below a cent could swap order. No scenario exercises this.
- **`Report.categories` is a `list[CategoryTotal]`, not a tuple.**
  - Evidence: Scenario 9 says "is the list of `CategoryTotal`".
  - If wrong: only the test's equality form changes.
- **`Report` and `CategoryTotal` are frozen dataclasses.** `Report` has the fields `month, base, count, income, expense, net, categories`.
  - Evidence: HLD §4 names these fields, and the style matches `Transaction`.
  - If wrong: the internal shape changes, but `to_dict()` stays the same.
- **The CLI calls `parse_csv(args.file)` and catches `OSError` → `parser.error(...)` (exit 2).** It does not open the file a second time.
  - Evidence: this still satisfies HLD §3 step 2 (open with `utf-8-sig`, `newline=""`, `OSError` → 2), because `parse_csv` opens exactly that way.
  - If wrong: nothing observable changes.
- **`CHANGELOG.md` is not touched until the developer answers** (spec rule).
  - If wrong: the layout gate reports `PLAY-G4`, and the line is added in t3.
- **The editable install with `src` layout exposes `ledger`** once the gate reinstalls. CI runs `pip install -e ".[test]"` on every run.
  - If wrong locally: re-run the editable install before running `pytest`.

## Solution proposal

Add `ledger` as a self-contained package with three layers: the parser, the report and the CLI. Each layer depends only on the layer below it. The package fits the existing `src` layout and the editable-install test path, so no existing file changes.

**Parser (`src/ledger/parser.py`, t1)**
- `parse_lines` wraps the input iterable so the first line has a leading `\ufeff` stripped, then feeds it to `csv.reader`.
- The header is the first row with any non-blank field. If there is none, it raises `LedgerError(1, "missing header")`.
- Header names are stripped and mapped to their indexes. Missing names are reported in canonical order (`id, date, amount, currency, category, memo`).
- For each later row:
  1. Record the start line as the previous `line_num` + 1.
  2. Skip the row if every field is blank.
  3. Check that the field count equals the header's.
  4. Strip all fields.
  5. Validate in the locked order.
  6. Track ids in a `dict` of id → line to detect duplicates.
- Date: an ASCII regex check, then `datetime.date(int, int, int)`. A `ValueError` here becomes "not a calendar date".
- Amount:
  - An ASCII regex check. This rejects NaN, Infinity, exponents, `+`, `_` and non-ASCII digits, so `decimal.InvalidOperation` can never be raised.
  - A fractional part longer than 2 digits → "has more than 2 decimal places".
  - A value that equals zero → "must not be zero".
  - `Decimal(text)` keeps the text's exponent, so `12000.00` stays `Decimal("12000.00")`.
- `parse_csv` opens the path and delegates to `parse_lines`. It catches `UnicodeDecodeError` around the iteration and reports it on the line being read.

**Report (`src/ledger/report.py`, t2)**
- `monthly_report` first validates `month`, `base` and `top`, raising `ValueError`.
- It then runs under `decimal.localcontext(decimal.Context(prec=28, rounding=ROUND_HALF_EVEN))` and:
  1. filters by `(date.year, date.month)`;
  2. converts each amount as `amount * rates[currency] / rates[base]`;
  3. builds exact sums: income from positive amounts, expense from negative amounts, net from all, and per category a sum and a count;
  4. quantizes each figure once with a `_money` helper that also maps any zero to `Decimal("0.00")`;
  5. sorts the categories by `(-abs(total), name)` and slices them to `top`.
- `to_dict()` emits the keys in order, `str()` for money and `int` for counts.

**CLI (`src/ledger/cli.py` + `src/ledger/__main__.py`, t3)**
- `main(argv=None)` builds argparse with a `report` subparser. It calls `parse_csv`, mapping `OSError` → `parser.error` (exit 2) and `LedgerError` → the exact stderr line plus `sys.exit(3)`.
- It calls `monthly_report` and prints either the text format or `json.dumps(report.to_dict())`.
- `__main__.py` calls `main()` under the guard `if __name__ == "__main__"`, which also covers running it as `python -m`.

**Alternatives rejected**
`hld.md` §6 lists the rejected alternatives: `argparse.FileType`, reading columns by position, lenient `Decimal()` parsing, and rounding before summing. In addition:
- **Opening the file in the CLI and calling `parse_lines`** was rejected. It duplicates the open/decode handling that `parse_csv` already owns.
- **Ordering categories by exact sum** was rejected. Users see the quantized figures, and Scenario 14 is defined on those.

## Ordered implementation steps

**t1 — model and parser**
1. Create the fixtures in `tests/fixtures/ledger/`. Test layer: `package-api` (used by steps 3 and 6).
   - `sample.csv`: the header and the nine rows `t001`…`t009`, using the HLD §7 content set (two groceries rows in ILS summing to -760.50, for example -460.25 and -300.25). Add one row dated 2026-04-01 in any category. Use at least one USD row and one EUR row. (AC 1, 9, 10, 13, 16, 19, 20)
   - `bom_blank.csv`: starts with the UTF-8 BOM bytes `EF BB BF`, has a blank line and a whitespace-only line, one empty memo and one quoted memo with a comma. (AC 3)
   - `empty.csv`: a true zero-byte file. (AC 7)
   - `header_only.csv`. (AC 4)
2. Add `src/ledger/parser.py` (AC 1–8). Test layer: `package-api`.
   - Define `LedgerError(Exception)`, which stores `line` and `reason` and calls `super().__init__(f"line {line}: {reason}")`.
   - Define the frozen dataclass `Transaction`.
   - Define the private ASCII regexes and `parse_lines` / `parse_csv`, as in the Solution proposal.
   - Add `from __future__ import annotations` and module and function docstrings.
   - Use only the stdlib. Use no 3.11+ API: no `date.fromisoformat` leniency, no `ExceptionGroup`.
3. Add `src/ledger/__init__.py`, which re-exports `LedgerError`, `Transaction`, `parse_csv` and `parse_lines` in `__all__`. Test layer: `package-api`.
4. Add `tests/test_ledger_parse.py` (AC 1–8, plus the edge cases from t1). Test layer: `package-api`. Cover:
   - the sample's order, field types and exact `Decimal` values;
   - a free header order, stripping and extra columns;
   - BOM and blank lines;
   - the header-only file;
   - each FR3 reason and its exact line (parametrized `io.StringIO` inputs, including NaN and Infinity);
   - that parsing stops at the first bad row;
   - a duplicate id across a blank line;
   - missing columns and `empty.csv`;
   - parity between `parse_lines` and `parse_csv` (using `tmp_path`, including a BOM);
   - a multi-line quoted memo reported on its start line;
   - whitespace-only input → `missing header`;
   - `+5`, `1E2`, `1_000` and `١٢` → not a number;
   - `20260301` → not YYYY-MM-DD;
   - invalid UTF-8 bytes written to `tmp_path` → `file is not valid UTF-8`;
   - that `Transaction` is frozen (assigning to a field raises `dataclasses.FrozenInstanceError`).

**t2 — report**
5. Add `src/ledger/report.py` (AC 9–18). Test layer: `package-api`. It contains:
   - `RATES`;
   - the frozen dataclasses `CategoryTotal(name, total, count)` and `Report`, with `to_dict()`;
   - `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`;
   - the month regex `_MONTH_RE`, and the `ValueError` checks that run before any computation;
   - the local decimal context, with each figure quantized once and negative zero normalized.
6. Extend `src/ledger/__init__.py` to also export `RATES`, `CategoryTotal`, `Report` and `monthly_report` (the handoff from t1 to t2). Test layer: `package-api`.
7. Add `tests/test_ledger_report.py` (AC 9–18, negative zero, determinism, serialization). Test layer: `package-api`. Cover:
   - Scenarios 9, 10, 13, 15 and 16 from `parse_csv(sample.csv)`;
   - Scenarios 11, 12, 14 and 17 from hand-built `Transaction` values;
   - `-0.01` ILS in EUR → expense `Decimal("0.00")` with `str` equal to `0.00`;
   - month, base and `top` errors: assert `ValueError`, and assert it is not a `LedgerError`;
   - key order in `to_dict()`;
   - results unchanged inside a `decimal.localcontext` set to `prec=3, rounding=ROUND_DOWN`.

**t3 — command line**
8. Add the fixture `tests/fixtures/ledger/bad_amount.csv`: the header, one valid row, and `-2.505` on line 3 (AC 23).
9. Add `src/ledger/cli.py` (AC 19–24, header errors on the command line). Test layer: `package-api`.
   - `_DESCRIPTION`, and `_month` and `_top` argparse types that raise `argparse.ArgumentTypeError`.
   - `main(argv: list[str] | None = None)`, which builds the parser as in the Solution proposal.
   - Text rendering: 7 header lines; then `  {name}: {total} ({count})` for each category, or `categories: none` when there are none.
   - JSON via `json.dumps(report.to_dict())`.
   - Error mapping: `OSError` → `parser.error(f"cannot open '{file}': {exc.strerror}")`, which exits 2; `LedgerError` → `print(f"error: {args.file}:{e.line}: {e.reason}", file=sys.stderr)` followed by `sys.exit(3)`.
   - Successful runs write nothing to stderr.
10. Add `src/ledger/__main__.py`, which imports `main` from `ledger.cli` and runs it (AC 19, 25).
11. Add `tests/test_ledger_cli.py` (AC 19–25, header errors, invalid UTF-8, determinism). Test layer: `package-api`.
    - Use a `run(*args)` helper that calls `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, timeout=30)`.
    - Fixture paths come from `pathlib.Path(__file__).parent / "fixtures" / "ledger"`, and expected strings are built from the exact path argument passed.
    - Cover:
      - exact stdout for Scenario 19;
      - the parsed JSON for Scenario 20;
      - the trailing lines for Scenario 21;
      - the six usage errors for Scenario 22, each with exit 2, empty stdout and non-empty stderr, using `tmp_path / "missing.csv"` and a directory as the files that cannot be opened;
      - exact stderr for Scenario 23;
      - `empty.csv` → `error: {FILE}:1: missing header`;
      - invalid UTF-8 → exit 3;
      - `--help` mentions `--month`;
      - two identical runs produce byte-identical stdout.
    - Add no `sys.path` manipulation.
12. Pending the answer to the clarification question: add one line under `## Unreleased` in `CHANGELOG.md` **only if** the developer chooses option (b). The layout gate (`PLAY-G4`) checks it; no test layer covers it.

Invariants the steps must cover:
- No authorization or tenancy surface exists: the package reads a file the user names, locally.
- No concurrency exists, and the package keeps no state between calls.
- Validation and error paths are the core of t1 and t3 and are tested exhaustively above.
- `ValueError` and `LedgerError` never cross over: one is never raised in place of the other.

Dependency acquisition: `pip install -e ".[test]"` brings in only `pytest` beyond the existing deps. `ledger` needs nothing new. There are no generated deliverables and no binaries; the fixtures are tiny text files.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1, 2, 3, 4 | t1 — ledger: Transaction model, LedgerError and validating CSV parser |
| 5, 6, 7 | t2 — ledger: monthly report with fixed-rate conversion, half-even rounding, top-N and to_dict |
| 8, 9, 10, 11, 12 (conditional) | t3 — ledger: `python -m ledger report` command line with text/JSON output and exit codes 0/2/3 |

Every work item has steps. Each work item's tests run green on their own: t1 needs only the parser, t2 adds the report on top of t1, and t3 adds the CLI on top of t2.

## Verification and CI gate

- Canonical gate, run once from the repo root on the committed SHA: `pip install -e ".[test]"`, then `pytest`. This matches the CI job `test` in `.github/workflows/ci.yml` (Python 3.12).
- The only declared layer is `package-api` (`.factory/testing.md`). It runs unprivileged in a pod, but the provider run at the exact head is authoritative.
- Subprocess CLI tests need the editable install to be present. They run in a pod, take about 100 ms each, and are bounded by `timeout=30`.
- No provider CI configuration changes are needed, and `.factory/delivery-assets` does not apply (there are no binaries ≥ 1 MiB).
- The `.factory/testing.md` obligation is met by putting all new tests under `tests/` as `test_*.py`, importing the installed `ledger`.
- **Done means:**
  - `pytest` passes the full suite: the existing tests plus `test_ledger_parse.py`, `test_ledger_report.py` and `test_ledger_cli.py`, with zero failures or skips in the new files.
  - Every Scenario 1–25 has at least one assertion.
  - The CI job `gate` stays green (no `CI_FAIL` file).
  - The layout gate passes, or reports only `PLAY-G4` if the developer chooses option (a).
- Python 3.10 cannot run locally (only 3.13 here, 3.12 in CI). This is covered by avoiding 3.11+ APIs and relying on the regex pre-checks. Report it as an unverified layer, not as passed.

## Risks and scope guards

**Risks**
- **Off-by-one line numbers on blank, BOM or multi-line rows (RK1/RK2).** Mitigation: use the previous `line_num` + 1 rule, and pin each case in a test (step 4).
- **The fixture must be byte-exact.** `empty.csv` must be zero bytes, and `bom_blank.csv` must start with the BOM. Mitigation: write them as bytes, and assert `stat().st_size == 0` and the leading BOM bytes in a test.
- **Rounding drift.** Mitigation: use a local context, quantize only at the end, and include a test that perturbs the global context.
- **`decimal.InvalidOperation` or an `OSError` leaking from `parse_csv`.** Mitigation: an amount regex that runs before `Decimal()`, and tests for both paths.
- **The CHANGELOG conflict with the layout gate.** Mitigation: the clarification question.

**Scope guards: the implement phase must NOT**
- edit any existing file: `pyproject.toml` (no console script, no dependency), `README.md`, `.github/workflows/ci.yml`, `.factory/*`, `src/testbed_utils/*`, `src/guestbook/*`, existing tests and fixtures, or `CHANGELOG.md` unless option (b) is chosen;
- add a `conftest.py`, `sys.path` hacks or a third-party dependency;
- read files other than the one named;
- use the network, fetch live exchange rates, or write to disk outside pytest's `tmp_path`;
- report more than the first bad row;
- change any reason string, output line or exit code from the spec;
- skip, `xfail`, delete or loosen a test to make the gate green. A layer that cannot run (Python 3.10) is reported as blocked, not faked.

## Clarification outcomes

One question is raised through the platform's plan conversation and is awaiting the developer's answer:
- **Question:** should the PR add a `CHANGELOG.md` line under `## Unreleased` (needed by the layout gate's rule 4, `PLAY-G4`), even though the spec forbids editing existing files?
- **Recommendation:** option (b), add the line in t3.
- **Until answered:** the plan follows the spec and does not touch the file (step 12 is conditional).
