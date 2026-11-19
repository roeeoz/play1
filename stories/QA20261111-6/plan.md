# Plan — Monthly expense report from a CSV ledger (QA20261111-6)

## Context

The story adds a new stdlib-only Python package `ledger` to `roeeoz/play1`. The package parses a UTF-8 CSV ledger into immutable `Transaction`s and stops at the first bad row with its physical line number (R1, R2). It builds an exact `Decimal` monthly report in ILS, USD or EUR, rounded once half-to-even (R3, R4). It exposes the report as `python -m ledger report FILE --month YYYY-MM [--base] [--top] [--json]` with exit codes 0/2/3 (R5). The change lands on the work branch `halo/feat/qa20261111-6-20261119-120939`, which merges into `main`. The approved requirement (25 acceptance criteria) is in `spec.md`, the design in `hld.md`, and the three work items (t1 parser, t2 report, t3 CLI) in `work-items.md`. All three files sit next to this file in `stories/QA20261111-6/`. This plan uses the scenario numbers from `spec.md` §5 as AC1–AC25 and the work-item criteria as t1.n / t2.n / t3.n.

## Research findings

**Change surface: all new files.** No existing file changes.
- `src/ledger/` does not exist, and nothing under `tests/` names `ledger`. Today `src/` holds only `guestbook/` and `testbed_utils/`, and `tests/fixtures/` holds only `empty.txt`, `numbers.txt`, `single.txt` and three PDFs.
- `pyproject.toml:22-23` sets `[tool.setuptools.packages.find] where = ["src"]`, so `pip install -e ".[test]"` installs `src/ledger/` without a manifest edit.
- `pyproject.toml:25-27` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- `pyproject.toml:9` sets `requires-python = ">=3.10"`, so the code must not use 3.11+ APIs.
- `pyproject.toml:13-17` defines `[project.scripts]`. The story adds no entry there, and `python -m ledger` runs through a new `src/ledger/__main__.py`.

**Contracts.**
- The package's public surface is fixed by `spec.md` FR2–FR8.
- `hld.md` §5 settles the cases the spec leaves open:
  - the order of the row checks;
  - the ASCII grammars for dates and amounts;
  - the `malformed CSV: ` prefix for CSV syntax errors;
  - the `duplicate column '…'` reason;
  - normalizing a rounded `-0.00` to `0.00`;
  - the `to_dict()` key order;
  - the `categories: none` line.
- The work items repeat these rules verbatim as t1.1–t3.9.
- There are no cross-repo contracts, APIs or events.

**Existing test conventions.**
- Tests are plain pytest modules organized as classes (`tests/test_num_summary_cli.py:36`).
- Tests find fixtures through `pathlib.Path(__file__).parent / "fixtures"` (`tests/test_num_summary_cli.py:11`).
- Subprocess-driven tests use `subprocess.run([...], capture_output=True, text=True, timeout=10)` (`tests/test_qa_s3_greeting.py:7-11`).
- The suite has no `conftest.py` and does no `sys.path` manipulation (`.factory/testing.md`). Tests import the package only through the installed distribution.

**Canonical gate.**
- `.factory/testing.md` declares `test-gate: pytest` and one required layer, `package-api` (production-path, `runBy: canonical-gate`).
- `.github/workflows/ci.yml:12-24` defines the `test` job: `pip install -e ".[test]"`, then `pytest` on Python 3.12.
- `.github/workflows/ci.yml:26-36` defines the `gate` job, which fails only when a `CI_FAIL` file exists at the repository root.
- The repo-gate skill (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) checks three rules: source under `src/`, tests under `tests/`, and no file over 200 KB. Its shell-script rule does not apply because the story adds no scripts.
- No linter, formatter or type checker is configured.

**Resolved unknowns.**
- I recomputed the `sample.csv` rows from `hld.md` §4 with stdlib `decimal`:
  - ILS: income `12925.00`, expense `-3025.50`, net `9899.50`
  - USD: income `3493.24`, expense `-817.70`, net `2675.54`

  These match AC9, AC10 and AC20.
- The repository has no `.gitattributes` or `.editorconfig`, and `.gitignore` has no `*.csv` rule. A BOM-prefixed file and a zero-byte file therefore commit unchanged.

**Remaining unknowns.** None block the plan.

## Locked decisions and assumptions

**Locked decisions**
- Standard library only. `decimal.Decimal` is used end to end. Each figure is quantized once to `0.01` with `ROUND_HALF_EVEN` (`spec.md` §2, FR6).
- No existing file changes, `pyproject.toml` included. No console script is added (`spec.md` Non-Goals).
- The module layout is `parser.py` (t1), `report.py` (t2), `cli.py` + `__main__.py` (t3), and `__init__.py` re-exports (`hld.md` §2).
- The layers depend in one direction only: `cli` → `report` → `parser`.
- `parse_csv` opens files with `encoding="utf-8-sig"` and `newline=""` and delegates to `parse_lines` (AC8).
- `parse_lines` also strips a leading U+FEFF (`hld.md` §5).
- The parser reads with `csv.reader(strict=True)` and tracks each record's start line itself (`hld.md` §6).
- Every reason string matches AC5–AC7 and t1.2/t1.5/t1.6 exactly. Row checks run in this order: field count → empty id → duplicate id → date → amount → currency → empty category.
- `RATES` is `{"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}` (AC10).
- The report does its arithmetic in a local Decimal context (prec 28, `ROUND_HALF_EVEN`).
- Categories sort by absolute rounded total descending, then by name ascending.
- `monthly_report` raises `ValueError` for caller errors (FR7, t2.9).
- CLI exit codes: usage error or unopenable/undecodable FILE → 2; `LedgerError` → 3 with stderr exactly `error: {FILE}:{line}: {reason}\n`. stdout is written only after the full output is built (FR8, `hld.md` §5).
- The CLI tests run `[sys.executable, "-m", "ledger", ...]` through `subprocess` (AC25).

**Assumptions**
- **CLI tests run with the repository root as working directory.** Evidence: AC19/AC23 give FILE as `tests/fixtures/ledger/...` and expect it echoed verbatim. If wrong, the expected stderr path would not match. Mitigation: compute the root from `pathlib.Path(__file__).resolve().parent.parent` and pass `cwd=` explicitly.
- **argparse's built-in usage errors give exit 2 and help gives exit 0 on stdout for `report --help`.** Evidence: this is stdlib argparse behaviour on 3.10 and 3.12. If wrong, AC22/AC24 fail visibly in the CLI tests.
- **Fixture memos are free text, with at least one empty.** Evidence: `hld.md` §4 leaves the memo content open. Consequence if wrong: none, because no criterion asserts a memo value in `sample.csv`.

## Solution proposal

The solution adds one new three-layer package. Each layer belongs to one work item and depends only on the layer below. The library raises exceptions and never prints or exits. Only `cli.py` maps errors to exit codes. This follows `hld.md` §2 and §6, and nothing in the repository contradicts it.

**Parser (`src/ledger/parser.py`).**
- `Transaction` is a `@dataclass(frozen=True)`.
- `LedgerError(Exception)` stores `line` and `reason`, and its `__str__` returns `f"line {line}: {reason}"`.
- `parse_lines` wraps the input iterable in a small generator that counts each physical line it yields and strips U+FEFF from the first line. That counter feeds `csv.reader(..., strict=True)`. Before each record is pulled, the counter value + 1 is that record's start line. This handles quoted multi-line memos, which `reader.line_num` would misreport.
- Blank records are skipped while still being counted. A blank record is `[]` or a single whitespace-only field.
- The first non-blank record is the header. The parser trims header names and checks for duplicate and missing columns (canonical order `id, date, amount, currency, category, memo`), then builds a name → index map.
- The parser validates each row in the locked order:
  - Dates are checked with `re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", …)` and then `datetime.date(int, int, int)` (not `fromisoformat`).
  - Amounts are checked with `re.fullmatch(r"[+-]?[0-9]+(\.[0-9]+)?", …)`. A fraction longer than 2 digits is rejected as text, and then the zero check runs on `Decimal(text)`.
- The parser tracks seen ids in a dict that maps each id to its first line.
- A `csv.Error` becomes `LedgerError(start, f"malformed CSV: {exc}")`.
- `parse_csv` is a `with open(path, encoding="utf-8-sig", newline="") as f: return parse_lines(f)`. It lets `OSError` and `UnicodeDecodeError` propagate.

**Report (`src/ledger/report.py`).**
- `RATES`, `CategoryTotal(name, total, count)` and `MonthlyReport(month, base, count, income, expense, net, categories)` are frozen dataclasses. `categories` is stored as a tuple so the report stays immutable, and `to_dict()` converts it to a list.
- `monthly_report` validates its arguments first: `month` must match `[0-9]{4}-(0[1-9]|1[0-2])`; `base` must be in `rates`; `top` must be `None` or an `int` (not a `bool`) ≥ 1; every rate must be positive.
- It filters transactions with `t.date.year`/`t.date.month` and raises `ValueError` for a currency missing from `rates`.
- Inside `decimal.localcontext()` with prec 28 and `ROUND_HALF_EVEN`, it converts each amount as `amount * rates[cur] / rates[base]` and accumulates unrounded sums for income, expense, net and each category.
- It quantizes each figure once, then adds `Decimal("0.00")` to normalize signed zero. This addition is the HLD's `-0.00` → `0.00` rule.
- It sorts categories by `(-abs(total), name)` and slices to `top`.

**CLI (`src/ledger/cli.py`, `src/ledger/__main__.py`).**
- `argparse.ArgumentParser(prog="python -m ledger")` gets a required `report` subparser with `FILE`, required `--month` (type validator using the same month regex), `--base choices=("ILS","USD","EUR") default="ILS"`, `--top` (int ≥ 1 validator) and `--json`.
- `main(argv=None) -> int` runs these steps:
  - Calls `parse_csv` and maps `OSError`/`UnicodeDecodeError` to `parser.error(...)`, which exits 2.
  - Maps `LedgerError` to a stderr write and `return 3`.
  - Builds the report.
  - Renders the full output string (text layout, or `json.dumps(report.to_dict())` plus `\n`).
  - Writes that string to stdout once and returns 0.
- `__main__.py` is `raise SystemExit(main())`.
- The month regex lives in `report.py`, and `cli.py` imports it so both validate months by one rule.

**Alternatives rejected.**
- *`csv.DictReader`:* it cannot report field-count mismatches or duplicate headers.
- *Trying `Decimal()`/`date.fromisoformat()` without a grammar:* both accept `NaN`, `1e3`, `.5` and `20260301`.
- *Adding a `[project.scripts]` entry:* the spec forbids editing `pyproject.toml`.
- *Driving the CLI tests through in-process `main()` as `test_num_summary_cli.py` does:* AC25 requires `subprocess` on the installed package.

## Ordered implementation steps

1. **Create the fixtures** in `tests/fixtures/ledger/` (new):
   - `sample.csv`: the header plus rows `t001`–`t009` exactly as listed in `hld.md` §4, with at least one empty memo.
   - `bom_blank.csv`: starts with the BOM bytes `EF BB BF`, has an empty line and a whitespace-only line between its two rows, one empty memo, and one memo quoted because it contains a comma.
   - `empty.csv`: zero bytes.
   - `bad_amount.csv`: the header, one valid row, and a third line whose amount is `-2.505`.

   Write the BOM and zero-byte files through a byte-exact method; editors and formatters can strip a BOM or add a newline. Covers AC1, AC3, AC7 and AC23 (t1.1, t1.3, t1.4, t1.8). Test layer: `package-api` (pytest), which asserts the bytes in step 3.
2. **Create `src/ledger/parser.py` and `src/ledger/__init__.py`** as the Solution proposal describes (`Transaction`, `LedgerError`, `parse_lines`, `parse_csv`). `__init__.py` re-exports the four names and declares `__all__`. Covers AC1–AC8 (t1.1–t1.8). Invariants:
   - validation stops at the first bad row;
   - row checks run in the locked order;
   - the parser converts no types before its grammar checks pass;
   - `OSError`/`UnicodeDecodeError` are never wrapped;
   - the code uses no 3.11+ APIs.

   Test layer: `package-api`.
3. **Create `tests/test_ledger_parser.py`** with one test (or parametrized case) per t1 criterion:
   - the sample's nine rows, their types, and `FrozenInstanceError` on assignment;
   - header in another order, stripped fields, extra columns, case-sensitive header names, and a duplicate column;
   - `bom_blank.csv`, plus assertions that its BOM bytes are present and that `empty.csv` has size 0;
   - header-only input, `missing header` (zero bytes, and blank lines only), and the missing-columns reason;
   - every reason string in t1.5, including `NaN`/`Infinity`/`1e3`/`1_000`/`.5`/`5.`/`٣`/empty, `1.500`, `-0.00`/`+0.0`, and a `+5` amount being accepted;
   - check-order precedence;
   - the start line of a multi-line quoted memo;
   - an unterminated quote giving a `malformed CSV: ` reason;
   - `parse_lines` matching `parse_csv` for `io.StringIO`, a list with newlines, a list without newlines, and a leading `﻿`;
   - `OSError` and `UnicodeDecodeError` from `parse_csv` (the bad-UTF-8 file goes in `tmp_path`);
   - `bad_amount.csv` raising with line 3.

   Import only `from ledger import ...`, with no `sys.path` manipulation. Covers AC1–AC8 (t1.1–t1.9). Test layer: `package-api`.
4. **Create `src/ledger/report.py`** (`RATES`, `CategoryTotal`, `MonthlyReport` with `to_dict()`, `monthly_report`, and the month regex), and **extend `src/ledger/__init__.py`** to re-export `RATES`, `CategoryTotal`, `MonthlyReport` and `monthly_report`. This is the t1 → t2 ownership handoff. Covers AC9–AC18 (t2.1–t2.9). Invariants:
   - the report uses a local Decimal context;
   - each figure is rounded once;
   - signed zero is normalized;
   - caller errors raise `ValueError`, never `LedgerError`;
   - the report is immutable.

   Test layer: `package-api`.
5. **Create `tests/test_ledger_report.py`** covering:
   - `RATES`;
   - March in ILS (all figures and the category list as `CategoryTotal` values);
   - March in USD (salary, freelance, income, expense, net);
   - 0.05 ILS in EUR giving `0.01` once and `0.04` three times;
   - an unchanged result under a caller `decimal.localcontext` with prec 3 / `ROUND_UP`;
   - `str()` showing two places;
   - a -0.01 ILS transaction in EUR giving `0.00` and not `-0.00`;
   - `top=2`, `top` larger than the category count, and `top=None`;
   - a tie broken by name;
   - `2026-05`, including `to_dict()` equality and key order;
   - `2026-02`;
   - custom rates;
   - each `ValueError` case (the six bad months, an unknown base, `top` 0/-1/`True`/`"2"`, an unknown transaction currency, a non-positive rate);
   - `FrozenInstanceError` on the report.

   Build inputs from `parse_csv` of `sample.csv` or from `Transaction(...)` directly. Covers AC9–AC18 (t2.1–t2.10). Test layer: `package-api`.
6. **Create `src/ledger/cli.py` and `src/ledger/__main__.py`** as the Solution proposal describes. The text layout prints six header lines. Then it prints `categories:` followed by `  {name}: {total} ({count})` for each category, or prints the single line `categories: none` when the list is empty. Every line ends with `\n`. Covers AC19–AC24 (t3.1–t3.7). Invariants:
   - usage errors are raised before any file is read;
   - stdout stays empty on every error path;
   - stderr stays empty on success;
   - FILE is echoed exactly as given.

   Test layer: `package-api` (subprocess).
7. **Create `tests/test_ledger_cli.py`.** A `run(*args)` helper calls `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, timeout=10, cwd=REPO_ROOT)`. Assert the exit code, stdout and stderr for:
   - the 13-line text report, with byte-identical output across two runs;
   - `--base USD --top 1 --json` (via `json.loads`);
   - `--month 2026-05`, whose output ends with the four zero lines;
   - each usage error (exit 2, empty stdout, non-empty stderr): no subcommand, missing `--month`, `--month 2026-13`, `--top 0`, `--base GBP`, a missing file, a directory, and an invalid-UTF-8 file in `tmp_path`;
   - `bad_amount.csv`, which exits 3 with the exact stderr;
   - `report --help`, which exits 0 and documents `--month`, `--base`, `--top` and `--json`.

   Covers AC19–AC25 (t3.1–t3.9). Test layer: `package-api`.
8. **Run the gate** after each work item: from the repository root, run `pip install -e ".[test]"`, then `pytest`. Confirm that no new file exceeds 200 KB and that no `CI_FAIL` file exists. Covers t1.9, t2.10 and t3.9. Test layer: the canonical gate.

**Dependencies.** No new dependencies are needed. The packages are stdlib only, and `pytest>=8` already comes from the existing `test` extra. `pip install -e ".[test]"` fetches it fresh and does not assume a warm cache.

**Generated deliverables.** None. The fixtures are hand-authored text, and no binary file is ≥ 1 MiB, so `.factory/delivery-assets` does not apply.

**Authorization and concurrency.** Not applicable. The code reads one local file, uses no shared state, makes no network calls and writes nothing.

## Work-item mapping

| Step | Work item |
|---|---|
| 1. Fixtures | t1 — ledger: Transaction model, LedgerError and CSV parser (parse_lines / parse_csv) with fixtures |
| 2. `parser.py`, `__init__.py` | t1 — ledger: Transaction model, LedgerError and CSV parser (parse_lines / parse_csv) with fixtures |
| 3. `test_ledger_parser.py` | t1 — ledger: Transaction model, LedgerError and CSV parser (parse_lines / parse_csv) with fixtures |
| 4. `report.py`, `__init__.py` re-exports | t2 — ledger: monthly_report with fixed overridable rates, exact Decimal totals and half-even rounding |
| 5. `test_ledger_report.py` | t2 — ledger: monthly_report with fixed overridable rates, exact Decimal totals and half-even rounding |
| 6. `cli.py`, `__main__.py` | t3 — ledger: `python -m ledger report` command line with text/JSON output and exit codes 0/2/3 |
| 7. `test_ledger_cli.py` | t3 — ledger: `python -m ledger report` command line with text/JSON output and exit codes 0/2/3 |
| 8. Gate | t1, t2, t3 (each on its own change set) |

Every work item maps to at least one step.

## Verification and CI gate

- **Canonical gate.** Run from the repository root, in this order: `pip install -e ".[test]"`, then `pytest` (`.factory/testing.md`, `.github/workflows/ci.yml` `test` job, Python 3.12). Run it once locally on the committed SHA. The provider CI run at the exact head is the authoritative result.
- **Required layer.** The only declared required layer is `package-api` (production-path, pytest). It runs unprivileged in a pod. It also covers the CLI, because `tests/test_ledger_cli.py` starts `python -m ledger` from the editable install. No other layer exists, and none is added.
- **`gate` job.** It stays green as long as no `CI_FAIL` file is added.
- **repo-gate rules.** All source is under `src/ledger/`, all tests and fixtures are under `tests/`, every file is under 200 KB, and there are no shell scripts.
- **Provider CI configuration.** None needed; CI is the repository's own and stays unchanged.
- **`.factory/delivery-assets`.** Not applicable (no binary ≥ 1 MiB).
- **Done means:**
  - `pytest` passes with the three new modules collected and every pre-existing test still passing;
  - each t1/t2/t3 criterion has at least one asserting test;
  - the CI `test` and `gate` jobs are green on the PR head.

## Risks and scope guards

**Risks**
- *Fixture corruption.* An editor or formatter can strip the BOM from `bom_blank.csv` or add a newline to `empty.csv`. Mitigation: step 3 asserts the raw bytes, so a stripped fixture fails loudly.
- *Python version drift.* CI runs 3.12, but `requires-python` is ≥ 3.10. Mitigation: avoid 3.11+ APIs (`datetime.UTC`, `typing.Self`, `except*`, the `fromisoformat` basic format).
- *Start-line tracking.* The start line could be miscounted around multi-line quoted fields and blank lines. Mitigation: dedicated tests in step 3 (blank-line duplicate-id case, multi-line memo).
- *Signed zero.* `quantize` can yield `-0.00`. Mitigation: normalize with `+ Decimal("0.00")`; the step 5 test covers it.
- *Working directory.* CLI tests depend on it for the echoed path. Mitigation: pass `cwd=REPO_ROOT` explicitly.
- *Import-name shadowing.* A third-party package named `ledger` could shadow this one. CI's fresh environment has none, so the risk is accepted (`hld.md` §7).
- *Non-ASCII category names.* They can fail to print on a non-UTF-8 stdout. The fixtures are ASCII, so the risk is accepted (`hld.md` §7).

**Scope guards: the implement phase must NOT:**
- edit any pre-existing file, including `pyproject.toml`, `README.md`, `.github/workflows/ci.yml`, `.factory/**`, `src/testbed_utils/**`, `src/guestbook/**` and existing tests or fixtures;
- add a console script or `[project.scripts]` entry;
- add a `conftest.py`, `sys.path` manipulation, or any third-party dependency;
- add input formats, live exchange rates, currencies beyond ILS/USD/EUR, configuration files, multi-month reports, or multi-error reporting;
- restrict FILE paths to the working directory as `numsummary.read_text` does, since the spec names no such restriction;
- reword any reason string, exit code, or output line fixed by `spec.md` §5 or `hld.md` §5;
- edit `spec.md`, `hld.md` or `work-items.md`;
- delete, skip, `xfail` or loosen a failing check to make the gate green; a check that cannot pass is reported as blocked.

## Clarification outcomes

None. No question was needed: `spec.md`, `hld.md` and the repository agree, and every open point is settled in `hld.md` §5–§6 or stated as an assumption above.
