# Implementation plan — `ledger` monthly report from a CSV ledger (story 609a1854)

## Context

This story adds a new stdlib-only package, `ledger`, to `roeeoz/play1`. The work is on branch `halo/feat/609a1854-20261107-172627` and merges into `main`. The package provides `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`. It parses and validates a CSV ledger, where the first bad row stops the run with its physical line number and an exact reason. It totals one month by category in a base currency at fixed rates. Every figure is rounded once, half-to-even, after summing. Output is byte-exact text or JSON, with exit codes 0, 2 and 3. Acceptance criteria 1–25 cover the parser (Scenarios 1–8), the report (9–18) and the CLI (19–25). Criterion 26 allows exactly one new `CHANGELOG.md` line and otherwise only new files. The approved requirement is `spec.md`, the design is `hld.md` and the breakdown (t1 → t2 → t3) is `work-items.md`, all in this folder (`stories/609a1854/`).

## Research findings

**Packaging and discovery**
- `pyproject.toml:21-22` sets `[tool.setuptools.packages.find] where = ["src"]`. A new `src/ledger/__init__.py` is therefore discovered with no manifest edit.
- `requires-python = ">=3.10"` (`pyproject.toml:10`). The test extra is `pytest>=8` (`pyproject.toml:19`).
- `[tool.pytest.ini_options] testpaths = ["tests"]` with `addopts = "-q"` (`pyproject.toml:24-26`).
- No `ledger` name exists anywhere in `src/`, `tests/` or at the repo root. No root `ledger/` directory can shadow `-m ledger` when the tests run from the repo root.

**Gate and test layer**
- The gate is defined in `.github/workflows/ci.yml:12-24`: job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12.
- Job `gate` (`ci.yml:26-36`) fails only if a `CI_FAIL` file exists at the root. It is not a quality layer.
- `.factory/testing.md` declares one required layer: `package-api` (`pytest`, production-path, `runBy: canonical-gate`). The suite has no `conftest.py` and no `sys.path` manipulation, so tests import only through the installed distribution.
- No linter, formatter or type checker is configured.
- The local pod has Python 3.11.2. Python 3.10 is not available in either the pod or CI.

**Existing conventions to follow**
- Subprocess tests define `REPO_ROOT = Path(__file__).resolve().parent.parent` and call `subprocess.run(..., capture_output=True, text=True)` (`tests/test_hello_sh.py:5-14`, `tests/test_qa_s3_greeting.py:8`).
- Fixtures are located with `pathlib.Path(__file__).parent / "fixtures"` (`tests/test_num_summary_cli.py:11`).
- The existing `argparse` CLI is `src/testbed_utils/numsummary.py:76-98`. It uses `from __future__ import annotations`, module docstrings and private `_NAME` constants. It catches `(OSError, UnicodeDecodeError)` when reading a file (`numsummary.py:53`), which is the same pair `ledger` must turn into exit 2.
- Packages re-export their public names with `__all__` (`src/testbed_utils/__init__.py:8-26`).

**Changelog (PLAY-G4)**
- `CHANGELOG.md:3-5` has `## Unreleased` followed by one bullet in the form `- PLAY-114: add \`qa/s3-hello.sh\`, …`.
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rule 4 makes a missing changelog line a `PLAY-G4` blocker. Rule 3 forbids any file over 200 KB.

**Contracts touched**
- None outside the new package. No other module imports `ledger`, and no shared constant, schema or cross-repo value changes.
- The package-internal contracts are those in `hld.md` §5:
  - `ledger.parser`: `Transaction`, `LedgerError`, `parse_lines`, `parse_csv`.
  - `ledger.report`: `RATES`, `CategoryTotal`, `MonthlyReport.to_dict()`, `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.

**What must be created:** everything under `src/ledger/` and `tests/fixtures/ledger/`, plus `tests/test_ledger_{parser,report,cli}.py`.

**What exists:** only `CHANGELOG.md`, which gains one line.

**Sample figures checked against the spec**
- For March in ILS, the spec's figures hold when every row is ILS except freelance (250.00 USD × 3.70 = 925.00):
  - income 12000 + 925 = 12925.00
  - expense −1500 − 760.50 − 444 − 321 = −3025.50
  - net 9899.50
- The USD figures follow from the same data:
  - 12000 ÷ 3.70 = 3243.2432… → `3243.24`
  - income 3493.2432… → `3493.24`
  - expense −817.7027… → `-817.70`
  - net 2675.5405… → `2675.54`

**Remaining unknowns:** none that block the work. Python 3.10 behaviour cannot be executed anywhere in the gate. It is guarded by design (see the risks section).

## Locked decisions and assumptions

**Locked decisions**
- The layout is `src/ledger/{__init__,parser,report,cli,__main__}.py`, and each layer imports only earlier layers (`hld.md` §2).
- Tests are `tests/test_ledger_{parser,report,cli}.py`. Fixtures are `tests/fixtures/ledger/{sample,bom_blank,empty,bad_amount}.csv` (`hld.md` §2; `work-items.md` t1–t3).
- Standard library only, Python ≥ 3.10. Neither `pyproject.toml` nor any existing file is edited, apart from one `CHANGELOG.md` line (spec §2, FR6, criterion 26).
- The `CHANGELOG.md` line ships with t1 (`hld.md` §6).
- Exact reason strings, line semantics (header is line 1, blank lines count, a multi-line row is reported at its start) and check order (field count, id, date, amount, currency, category, duplicate id): spec Scenarios 5–7, A1–A5, `hld.md` §4.
- Parsing uses a plain `csv.reader` with a hand-built header index, so a repeated header name maps to its first occurrence. It does not use `DictReader` (`hld.md` §6).
- The amount check is text-first: optional sign, ASCII digits, optional fraction, at most two decimals as written. `1.500` is rejected (`hld.md` §6).
- Dates use the ASCII regex `[0-9]{4}-[0-9]{2}-[0-9]{2}` before calendar validation, so `fromisoformat` leniency in Python ≥ 3.11 is not relied on (`hld.md` §4).
- Conversion is `amount × rates[cur] ÷ rates[base]`, multiplying first, at 28-digit precision. Each figure is quantized once to `0.01` with `ROUND_HALF_EVEN`. The global context is never changed (spec FR4, `hld.md` §4).
- `month`, `base` and `top` problems in `monthly_report` raise `ValueError`, never `LedgerError` (Scenario 18).
- The CLI uses subparsers with `dest` and `required=True`. `--base` uses `choices`. `--month` and `--top` use `type=` validators. An unreadable FILE (`OSError`, `UnicodeDecodeError`) goes to `parser.error` and exits 2. A `LedgerError` prints `error: {FILE}:{line}: {reason}\n` and exits 3 (`hld.md` §4).
- CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", ...]` and no `sys.path` changes (Scenario 25).

**Assumptions**
- **A-P1. `LedgerError` subclasses `Exception`, not `ValueError`.**
  - Evidence: the spec keeps the two kinds distinct, and `UnicodeDecodeError` is a `ValueError`.
  - If wrong: nothing breaks. Any `except ValueError` in the CLI would still have to be ordered carefully.
- **A-P2. The amount regex is `[+-]?[0-9]+(\.[0-9]+)?`, applied with `re.fullmatch`.**
  - Under it, `.5`, `5.` and `+` are "is not a number".
  - Evidence: `hld.md` §4 says "optional sign, ASCII digits and an optional fractional part".
  - If wrong: a reviewer may expect `.5` to be accepted. Only the inline parser tests would change.
- **A-P3. Reason strings quote the trimmed raw value as `'{value}'` with an f-string, not `repr()`.**
  - Evidence: the exact strings in Scenario 5.
  - If wrong: a value containing `'` would print differently. No criterion covers that.
- **A-P4. The sample fixture puts every row in ILS except `freelance` (250.00 USD).**
  - The two March groceries rows split −760.50 (for example −500.25 and −260.25).
  - The 2026-02-27 row is groceries −99.99, and the 2026-04-01 row is any valid row.
  - Evidence: the arithmetic in Research findings.
  - If wrong: Scenarios 9, 10, 16, 19 and 20 fail, and the gate catches it.
- **A-P5. The report does its arithmetic inside `decimal.localcontext(decimal.Context(prec=28, rounding=ROUND_HALF_EVEN))`.**
  - This makes the figures independent of any caller's global context without changing it.
  - Evidence: `hld.md` §4 "default 28-digit context … never changed".
  - If wrong: no published figure changes.
- **A-P6. The CLI's `--month` validator reuses a module-private month check in `ledger/report.py`** (for example `_check_month`) instead of adding a public name.
  - Evidence: `hld.md` §6 says the CLI "reuses the report's month rule".
  - If wrong: the rule is duplicated in two places. There is no behavioural difference.

## Solution proposal

Build the three layers `hld.md` prescribes as one small package. Each module's tests reach it through the installed distribution, which matches the repository's single `package-api` layer. No existing module is extended. `ledger` stands alone beside `testbed_utils` and `guestbook`.

**Parser (`src/ledger/parser.py`)**
- `Transaction` is `@dataclass(frozen=True)` with `id: str`, `date: datetime.date`, `amount: Decimal`, `currency: str`, `category: str`, `memo: str`.
- `LedgerError(Exception)` stores `line` and `reason`. Its `__str__` returns `line {line}: {reason}`.
- `parse_lines(lines)` handles BOM, line numbers and blank rows this way:
  - It wraps the iterable in a generator that strips a leading `\ufeff` from the first line only.
  - It feeds that generator to `csv.reader`.
  - It tracks `start = previous reader.line_num + 1` for each row, which gives A2's physical start line.
  - It skips rows that are empty or whose fields are all blank after `strip()`.
- The first surviving row is the header:
  - Names are trimmed.
  - The `{name: first index}` map is built with `setdefault`.
  - Missing canonical names are reported on line 1 as `missing column(s): a, b` in canonical order.
  - No surviving row at all means `LedgerError(1, "missing header")`.
- Each data row is checked in the locked order, and the first failure raises:
  1. `len(row) != len(header)` gives `expected N fields, got M`.
  2. An empty trimmed id gives `empty id`.
  3. The date regex, then `datetime.date(y, m, d)` inside `try/except ValueError`, gives the two date reasons.
  4. The amount regex, then the fraction length, then `Decimal(text) == 0`, gives the three amount reasons.
  5. A currency not in `("ILS", "USD", "EUR")` gives `unknown currency '…'`.
  6. An empty trimmed category gives `empty category`.
  7. An id already in the `{id: line}` map gives `duplicate id '…' (first seen on line N)`.
- `parse_csv(path)` opens the path with `encoding="utf-8-sig", newline=""` and returns `parse_lines(f)`.

**Report (`src/ledger/report.py`)**
- Define `RATES = {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}`.
- Define frozen `CategoryTotal(name, total, count)` and `MonthlyReport(month, base, count, income, expense, net, categories)`.
- `to_dict()` emits keys in the order `month, base, count, income, expense, net, categories`, with `str()` amounts.
- `monthly_report` first validates its arguments, raising `ValueError`:
  - `month` must fullmatch `[0-9]{4}-(0[1-9]|1[0-2])`.
  - `base` must be in `rates`.
  - `top` must be `None` or ≥ 1.
- It then filters transactions on `(date.year, date.month)`.
- It converts each amount exactly once and accumulates exact sums:
  - positive amounts into income;
  - negative amounts into expense;
  - every amount into net;
  - each amount into its category's total and count.
- It quantizes each figure independently with `Decimal("0.01")` and `ROUND_HALF_EVEN`.
- It sorts categories by `(-abs(total), name)` and slices `[:top]`.
- An empty month yields `Decimal("0.00")` zeros and `[]` because the sums start at `Decimal(0)`.

**CLI (`src/ledger/cli.py`, `src/ledger/__main__.py`)**
- `main(argv=None) -> int` builds an `ArgumentParser`.
  - The subparsers use `dest="command", required=True`.
  - The `report` subparser takes `FILE`, plus `--month` (required, `type=` the month validator), `--base` (`choices=list(RATES)`, default `ILS`), `--top` (`type=` a positive-int validator) and `--json` (`store_true`).
  - Help text documents all four options (A7).
- Data flow in `main`:
  1. Call `parse_csv`.
  2. Turn `OSError` or `UnicodeDecodeError` into `parser.error(...)`, which exits 2.
  3. On `LedgerError`, write `f"error: {args.file}:{e.line}: {e.reason}\n"` to stderr and return 3.
  4. Otherwise build the report, render the full output string, write it once to stdout and return 0.
- Text rendering prints the six header lines, then `categories:` and one `  {name}: {total} ({count})` line per category. When there are none, it prints `categories: none`. The JSON form is `json.dumps(report.to_dict())` plus a newline.
- `__main__.py` is `raise SystemExit(main())`.
- Because output is rendered fully before anything is written, stdout stays empty on every error path.

**Alternatives rejected**
- `csv.DictReader`: it keeps the last duplicate column and hides the field count, which breaks A1 and A3.
- Plain `Decimal(text)`: it accepts `NaN`, `1E+3` and `1_000`.
- `date.fromisoformat`: it is lenient on Python ≥ 3.11.
- A `[project.scripts]` entry: the spec forbids editing `pyproject.toml`.
- In-process `main()` CLI tests, the `numsummary` style: Scenario 25 mandates a subprocess.
- Rounding per transaction: it contradicts Scenario 11.

## Ordered implementation steps

1. **Add the fixtures.** Covers criteria 1, 3, 7 and 23; layer `package-api`.
   - Create `tests/fixtures/ledger/sample.csv`: the header plus `t001`…`t009` per A-P4, including at least one quoted memo.
   - Create `tests/fixtures/ledger/bom_blank.csv`: written as bytes, starting with `EF BB BF`, with a blank line and a whitespace-only line between two rows, one empty memo and one `"…, …"` memo.
   - Create `tests/fixtures/ledger/empty.csv`: zero bytes.
   - Create `tests/fixtures/ledger/bad_amount.csv`: header, one valid row, then line 3 with amount `-2.505`.
   - Keep the BOM and trailing whitespace intact. The tests assert the raw bytes so that editor normalisation cannot silently defeat a fixture.
2. **Create `src/ledger/parser.py`** with `Transaction`, `LedgerError`, `parse_lines` and `parse_csv` as described in the Solution proposal.
   - Covers criteria 1–8; layer `package-api`.
   - Invariants:
     - Validation stops at the first failure, in the locked order.
     - No partial list is returned on error.
     - Only ASCII `[0-9]` is used in regexes, never `\d`.
     - `re.fullmatch` is used, never `re.match` with `$`.
3. **Create `src/ledger/__init__.py`.** It needs a module docstring, re-exports of the parser names and `__all__`. Covers criterion 1; layer `package-api`.
4. **Write `tests/test_ledger_parser.py`.** Covers criteria 1–8; layer `package-api`.
   - Use one test per scenario, with inline `io.StringIO` cases for the error table, parametrized over every reason string in Scenario 5.
   - Also cover:
     - each check-order collision, for example a row with an empty id and a bad date reports `empty id`;
     - a seven-column header giving `expected 7 fields, got 5`;
     - a duplicate header column (first one wins);
     - blank lines before the header;
     - a file of only blank lines giving `missing header`;
     - a multi-line quoted memo followed by a bad row with the correct line;
     - `-0.00`, `NaN`, `Infinity`, `1E+3`, `1_000` and full-width digits;
     - `20260301` and full-width dates;
     - case-sensitive `usd` and header names;
     - `parse_lines` on BOM text equal to `parse_csv` on the BOM file;
     - `bad_amount.csv` giving `(3, "amount '-2.505' has more than 2 decimal places")`;
     - `Transaction` being frozen (`dataclasses.FrozenInstanceError`).
5. **Add the changelog bullet.** Add one bullet under `## Unreleased` in `CHANGELOG.md`, in the existing style, describing the `ledger` report command (`python -m ledger report`). Covers criterion 26; no test layer, since this is checked by review and by the PLAY-G4 repo gate.
6. **Create `src/ledger/report.py`** with `RATES`, `CategoryTotal`, `MonthlyReport.to_dict()`, the private month check (A-P6) and `monthly_report`, as described in the Solution proposal.
   - Covers criteria 9–18; layer `package-api`.
   - Invariants:
     - Arguments are validated before any work.
     - `ValueError` only, never `LedgerError`.
     - The local context only, so the global context is untouched.
     - One quantize per figure.
7. **Update `src/ledger/__init__.py`.** Extend it to re-export the report names and update `__all__`. Covers criteria 9–10; layer `package-api`.
8. **Write `tests/test_ledger_report.py`.** Covers criteria 9–18; layer `package-api`.
   - Cover Scenarios 9–18 with the exact `Decimal` and `str` values, plus `to_dict()` key order for the empty month.
   - Check the 0.05 ILS → EUR cases (`0.01`, and `0.04` for three).
   - Check ties by name, `top` larger than the category count, and `top=None`.
   - Check every invalid month listed, an unknown base and `top=0`, each with `pytest.raises(ValueError)`. Also assert the error is not a `LedgerError`.
   - Assert `decimal.getcontext()` is unchanged after a call.
   - Load the sample through `parse_csv` on the fixture.
9. **Create `src/ledger/cli.py` and `src/ledger/__main__.py`** as described in the Solution proposal. Covers criteria 19–24; layer `package-api`.
   - Invariants:
     - Exit codes are exactly 0, 2 and 3.
     - stdout is empty on every error.
     - There is no traceback for the unreadable-FILE cases (missing, directory, invalid UTF-8).
     - FILE is echoed exactly as typed.
     - No `argparse` feature newer than 3.10 is used (no `exit_on_error` reliance, no `suggest_on_error`).
10. **Write `tests/test_ledger_cli.py`.** Covers criteria 19–25; layer `package-api`.
    - Use a `run(*args)` helper over `subprocess.run([sys.executable, "-m", "ledger", *args], cwd=REPO_ROOT, capture_output=True, text=True)`.
    - Check exact stdout for Scenario 19 (13 lines), `json.loads` equality for Scenario 20, and the trailing four lines for Scenario 21.
    - Cover each usage error in Scenario 22. Missing-file, directory (`tmp_path`) and invalid-UTF-8 cases (bytes written to `tmp_path`) each expect exit 2, empty stdout, non-empty stderr and no `Traceback`.
    - Pass the relative path `tests/fixtures/ledger/bad_amount.csv` for Scenario 23 and assert the exact stderr.
    - Check that `report --help` exits 0 and mentions `--month`.
    - Check that two identical runs give byte-identical stdout.
11. **Run the gate.** Run `pip install -e ".[test]"` and then `pytest` from the repo root after each work item, so that each work item is green on its own. Re-run the install, because an older editable install may not see the new package.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1, 2, 3, 4, 5 | t1 | ledger: transaction model and validating CSV parser (+ CHANGELOG line) |
| 6, 7, 8 | t2 | ledger: monthly report with fixed-rate conversion and single half-even rounding |
| 9, 10 | t3 | ledger: `python -m ledger report` CLI with text/JSON output and exit codes 0/2/3 |
| 11 | t1, t2, t3 | Gate run after each work item |

Every work item has at least one step. No planning gap.

## Verification and CI gate

**Canonical gate.** Run from the repo root, in this order: `pip install -e ".[test]"`, then `pytest`. This mirrors `.github/workflows/ci.yml` job `test` and `.factory/testing.md`. Run it once locally on the committed SHA. The Stop hook and the provider CI on Python 3.12 run it again, and the provider run at the exact head is authoritative.

**Required layer.** `package-api` (`pytest`) is the only required layer, and it runs fully in a pod. The pod's Python 3.11.2 is close enough to exercise everything except the 3.10 floor. No other layer exists, and none is added.

**What the gate must show:**
- Every pre-existing test still passes.
- `tests/test_ledger_parser.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py` pass, with at least one test per acceptance criterion (1–25).
- The `gate` job is green, meaning no `CI_FAIL` file.
- The diff against `main` is exactly:
  - the new files under `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`;
  - one added line in `CHANGELOG.md`;
  - the planning folder `stories/609a1854/`, which is outside criterion 26 per `hld.md` §7.
- Every file is under 200 KB.

**Not needed:** provider CI configuration, `.factory/testing.md` changes and `.factory/delivery-assets` entries. No binary is added; the fixtures are a few hundred bytes.

## Risks and scope guards

**Risks**
- **Python 3.10 floor is unverified.** Neither the pod (3.11) nor CI (3.12) runs 3.10.
  - Mitigation: use `required=True` with `dest` on subparsers, the regex date check, and no 3.11+ APIs (`datetime.UTC`, `tomllib`, `ExceptionGroup`, `StrEnum`, `typing.Self`). Use `from __future__ import annotations` as `numsummary.py` does.
- **Fixture normalisation.** Editors or tools may strip the BOM or trailing whitespace from `bom_blank.csv`.
  - Mitigation: write the fixture as bytes and assert its raw bytes in the parser tests.
- **Changelog conflict.** Another story's `## Unreleased` line may conflict on merge. Resolve by keeping both lines.
- **Name shadowing.** A `ledger/` directory in the working directory would shadow the package. The CLI tests pin `cwd=REPO_ROOT`, where none exists.
- **`-0.00` on net.** Net could print `-0.00` when a tiny negative exact sum rounds to zero. No criterion covers this, so leave it as specified rather than adding normalisation.
- **Decimal overflow.** Values beyond 28 significant digits are out of realistic range and are not handled (`hld.md` §7).

**The implement phase must NOT:**
- edit `pyproject.toml` or add a `[project.scripts]` entry;
- edit any existing source, test or fixture file;
- touch `README.md` or `.github/workflows/ci.yml`;
- add a `conftest.py` or any `sys.path` manipulation;
- add any third-party dependency;
- change the global `decimal` context;
- add a second `CHANGELOG.md` line, or change the existing one;
- add a `CI_FAIL` file;
- add a linter, formatter or new test framework;
- refactor `testbed_utils` or `guestbook`;
- add features beyond the spec, such as other formats, live rates, config files or extra subcommands;
- change any reason string, output line or exit code from the spec's exact text;
- skip, delete, `xfail` or weaken any test to make the gate green. A check that cannot pass is reported as blocked.

## Clarification outcomes

None. No question was needed: the spec's A1–A7 were confirmed by the developer, and the remaining open points are recorded as assumptions A-P1–A-P6.
