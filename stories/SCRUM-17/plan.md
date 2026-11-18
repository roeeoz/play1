## Context

SCRUM-17 adds a new stdlib-only Python package, `ledger`, to `roeeoz/play1`. The package reads a UTF-8 CSV ledger and validates it row by row. A bad row stops the parse with `LedgerError(line, reason)`, carrying the physical line number and an exact reason. From the parsed rows it builds a deterministic monthly report: count, income, expense, net and per-category totals, in base ILS, USD or EUR, at fixed `Decimal` rates, with one `ROUND_HALF_EVEN` rounding per figure. The same report is available from the terminal as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`, with exit codes 0, 2 and 3. Spec §5 has 26 acceptance criteria, in four groups:
- AC1–8: parsing and validation;
- AC9–18: the report;
- AC19–25: the CLI;
- AC26: the scope boundary.

The work lands on branch `halo/feat/scrum-17-20261118-233900`, which merges into `main`. It is split into three dependent work items: t1 → t2 → t3. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-17/`.

## Research findings

**Package discovery and layout**
- `pyproject.toml:23-24` discovers packages with `[tool.setuptools.packages.find] where = ["src"]`. A new `src/ledger/` package is therefore picked up with no manifest change.
- `pyproject.toml:10` sets `requires-python = ">=3.10"`.
- `pyproject.toml:12` lists the runtime deps `pypdf` and `flask>=3`. `ledger` uses neither.
- `pyproject.toml:27-28` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- `src/ledger/` and `tests/fixtures/ledger/` do not exist yet.
- No `ledger` module is importable in the environment: `import ledger` gives `ModuleNotFoundError`, so nothing shadows the new package name.

**Canonical gate**
- `.factory/testing.md` declares `test-gate: pytest` and one required layer, `package-api` (production-path, `runBy: canonical-gate`).
- `.github/workflows/ci.yml:12-24` defines job `test`: Python 3.12, `pip install -e ".[test]"`, then `pytest`.
- Job `gate` (`ci.yml:26-37`) fails only if a `CI_FAIL` file exists.
- No linter, formatter or type checker is configured.
- There is no `conftest.py` and no `sys.path` manipulation anywhere in `tests/`. Tests import the installed distribution.

**Local environment (fact)**
- The pod runs Python 3.13.
- `/usr/local/lib/python3.13/site-packages/__editable__.testbed_utils-0.1.0.pth` holds a path `.pth` that points at another workspace's `src`: `/root/.halo/workspaces/delivery-858118ad…/play1-79db628f23/src`.
- Until `pip install -e ".[test]"` runs in this checkout, local tests would import stale code, and `ledger` would be missing. After the reinstall, the path `.pth` exposes every package under this checkout's `src/`, so a new package needs no further reinstall.

**Existing test idioms**
- Subprocess tests use `subprocess.run([...], capture_output=True, text=True, timeout=10, cwd=…)` with `REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent` (`tests/test_qa_20261109_s1_a.py:6-15`).
- In-process CLI tests patch `sys.argv` and use `redirect_stdout` (`tests/test_num_summary_cli.py:1-9`). AC25 forbids this style for `ledger`.
- Tests are grouped as pytest classes (`TestNormalRun`, …) and function tests.
- `src/testbed_utils/numsummary.py` is the house CLI style: an `argparse` `main()`, a module docstring and `from __future__ import annotations`.

**Repository gate**
- The layout gate is `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`. It applies these rules:
  - rule 1: source under `src/`, tests under `tests/`;
  - rule 3: no file over 200 KB;
  - rule 4 (`PLAY-G4`, blocker): every PR adds a line under `## Unreleased` in `CHANGELOG.md`.
- `CHANGELOG.md:3` holds `## Unreleased`. The newest entry is `CHANGELOG.md:8` (PLAY-175), and entries read `- <KEY>: add \`<path>\`, …`.
- The glossary skill (`.factory/plugins/claims-dev/skills/glossary/SKILL.md`) defines "Net amount" as "before tax". The spec fixes the field name `net`, so it stays (HLD §7).

**Fixtures**
- `.gitignore` does not ignore `tests/fixtures/ledger/*.csv` (`git check-ignore` returns 1).
- Existing fixtures live flat in `tests/fixtures/`. The new subfolder is as the spec names it.

**Arithmetic check**
The spec's figures were recomputed with `decimal`:
- 12000/3.70 → `3243.24`
- 925/3.70 → `250.00`
- 12925/3.70 → `3493.24`
- −3025.50/3.70 → `-817.70`
- 9899.50/3.70 → `2675.54`
- 0.05/4.00 → `0.01`
- 3 × (0.05/4.00) → `0.04`

All match AC9–11 and AC20.

**Contracts touched**
- There is no cross-repo contract.
- The new public library surface is spec FR2–FR13: `parse_lines`, `parse_csv`, `Transaction`, `LedgerError`, `RATES`, `CategoryTotal`, `monthly_report` and `to_dict()`.
- The new CLI surface is AC19–24.
- `pyproject.toml` stays untouched. There is no console script (AC26, HLD §6).

**Remaining unknowns**
None blocks the work. The silences are resolved as assumptions below.

## Locked decisions and assumptions

**Locked decisions**
- Stdlib only, with `Decimal` end to end. Each figure is quantized exactly once, with `ROUND_HALF_EVEN`, and the global decimal context is never changed. Sources: spec §2, §7; HLD §6.
- Exact error reasons apply byte for byte (AC5–7). `str(LedgerError)` is `line {line}: {reason}`.
- `RATES` is `{"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}`. Conversion is `amount × rates[currency] ÷ rates[base]`, applied before summing (AC10).
- Caller errors in `monthly_report` raise `ValueError`, never `LedgerError` (AC18).
- CLI exit codes:
  - 0 on success;
  - 2 on a usage error or an unopenable file, with stdout empty;
  - 3 on a data error, with stderr exactly `error: {FILE}:{line}: {reason}\n` (AC22–23).
- CLI tests drive `[sys.executable, "-m", "ledger", ...]` through `subprocess` (AC25).
- Diff scope (AC26, spec A1):
  - new files only under `src/ledger/`, `tests/` and `tests/fixtures/ledger/`;
  - plus one `- SCRUM-17: …` line under `## Unreleased` per work item.
- Design choices (HLD §6):
  - Use `argparse` with `prog="ledger"`.
  - Validate lexically before converting dates and amounts.
  - Report the physical start line of a record.
  - Give the field-count reason from the header's actual length.
  - Strip a leading `﻿` in `parse_lines`.
  - Normalise `-0.00` to `0.00`.
  - Break ties on the rounded absolute total, then the name.
- Module ownership (work-items.md):
  - t1 creates `src/ledger/__init__.py`;
  - t2 extends it with the report exports;
  - t3 does not touch it.

**Assumptions**
- **AS1 — Header row.** The header is the first non-blank record. If no record exists, the parser raises `LedgerError(1, "missing header")`, which covers both a zero-byte file and blank-only lines (work-items t1).
  - Evidence: AC7 and the t1 summary.
  - If wrong: only a contrived file with leading blank lines before the header changes behaviour.
- **AS2 — Blank lines.** A blank record is either a `csv.reader` row of length 0, or a row of length 1 whose only field is whitespace. A row like `,,,,,` is not blank; it is validated and fails with `empty id`.
  - Evidence: FR1 skips "blank and whitespace-only lines".
  - If wrong: a separator-only row would be skipped silently rather than rejected.
- **AS3 — Validation order within a row.** Checks run in this order: field count, then id, date, amount, currency, category, then duplicate id.
  - Evidence: the spec defines each reason in isolation but not the order between them.
  - If wrong: a row with two faults reports a different one of them. No AC pins this.
- **AS4 — `--month` validation.** The CLI's `--month` validator reuses the report module's month check, so the CLI and the library agree on what is valid.
  - If wrong: nothing changes for users.
- **AS5 — CLI tests.** CLI tests run with `cwd=REPO_ROOT` and pass the relative path `tests/fixtures/ledger/...`. That relative path is what AC23 compares on stderr.
- **AS6 — Fixture contents.** All-ILS rows, as listed in step 1.
  - Evidence: the t1 summary requires all-ILS rows so that the USD figures in AC10 and AC20 hold.

## Solution proposal

A three-layer package under `src/ledger/`, where each layer imports only the ones below it.

**`model` + `parser` (t1)**
- `src/ledger/model.py` holds:
  - `Transaction`, a `@dataclass(frozen=True)`;
  - `LedgerError(Exception)`, with `.line`, `.reason` and `__str__` returning `line {line}: {reason}`;
  - the canonical column tuple `("id", "date", "amount", "currency", "category", "memo")`;
  - `CURRENCIES = ("ILS", "USD", "EUR")`.
- `src/ledger/parser.py` holds `parse_lines(lines)` and `parse_csv(path)`.
  - `parse_csv` opens with `encoding="utf-8-sig", newline=""` and delegates to `parse_lines`.
  - `parse_lines` wraps `csv.reader`. It tracks `reader.line_num` to derive each record's physical start line (previous `line_num` + 1). It strips a leading `﻿` from the first header cell and trims header names.
  - It resolves the six required names to their indexes and ignores extra columns. If names are missing, the error lists them in canonical order.
  - It then validates each non-blank row:
    - the date must match `^[0-9]{4}-[0-9]{2}-[0-9]{2}$` (ASCII), then convert with `date(y, m, d)`;
    - the amount must match `^[+-]?[0-9]+(\.[0-9]+)?$`, then pass the decimals-count check, then `Decimal(text)` with a zero check;
    - the currency is checked by case-sensitive membership.
  - It records each id's first line in order to detect duplicates.

**`report` (t2)**
- `src/ledger/report.py` holds:
  - `RATES`;
  - `CategoryTotal`, a frozen dataclass with `name`, `total` and `count`;
  - `MonthlyReport`, a frozen dataclass with `month`, `base`, `count`, `income`, `expense`, `net` and `categories`, plus `to_dict()`;
  - `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.
- `monthly_report` works in this order:
  1. Validate `month` against `^[0-9]{4}-(0[1-9]|1[0-2])$`, check that `base in rates`, and check `top is None or top >= 1`. Each failure raises `ValueError`.
  2. Filter transactions by `(date.year, date.month)`.
  3. Convert each amount at full precision.
  4. Sum exactly: positive amounts into income, negative into expense, and each amount into its category.
  5. Quantize each sum once with `Decimal("0.01")` and `ROUND_HALF_EVEN`, then normalise negative zero.
  6. Sort categories by `(-abs(total), name)`, then slice `[:top]`.
- An empty sum starts from `Decimal("0")`, so an empty month yields `Decimal("0.00")`.

**`cli` + `__main__` (t3)**
- `src/ledger/cli.py` defines `main(argv=None) -> int`. It builds an `argparse` parser:
  - `prog="ledger"`;
  - a required subparser `report`;
  - the positional `FILE`;
  - `--month` with a `type=` validator that raises `argparse.ArgumentTypeError`;
  - `--base` with `choices=["ILS", "USD", "EUR"]` and `default="ILS"`;
  - `--top` with a positive-int `type=`;
  - `--json`.
- On `OSError` or `UnicodeDecodeError` from `parse_csv`, it calls `parser.error(...)`, which exits 2.
- On `LedgerError`, it writes `f"error: {args.file}:{err.line}: {err.reason}\n"` to stderr and returns 3.
- Output is rendered only after the parse and the report both succeed, so stdout stays empty on every error path.
  - Text output is the AC19 line set, or `categories: none` when there are no categories.
  - JSON output is `json.dumps(report.to_dict())`.
- `src/ledger/__main__.py` holds only `raise SystemExit(main())`.

**Alternatives rejected**
- A `ledger` console script: it changes `pyproject.toml`, which AC26 forbids.
- Plain `Decimal(text)` for amounts: it accepts NaN, Infinity, `1E+2` and `1_000`.
- `date.fromisoformat`: on Python 3.11+ it accepts `20260301`.
- Rounding per transaction: it breaks AC11.
- In-process CLI tests: AC25 forbids them.
- One combined module: it would blur work-item ownership. Three small modules match the HLD §2 table.

## Ordered implementation steps

Before running tests locally, run `pip install -e ".[test]"` in this checkout, because the existing editable `.pth` points at another workspace. CI installs fresh. Steps 1–5 are t1, 6–8 are t2, 9–11 are t3.

1. **Add the t1 fixtures** (new) in `tests/fixtures/ledger/`. AC1, AC3, AC7.
   - `sample.csv`: header `id,date,amount,currency,category,memo`, then nine all-ILS rows in this order:
     - `t001` 2026-02-27 −99.99 groceries
     - `t002` 2026-03-01 12000.00 salary
     - `t003` 2026-03-02 −1500.00 rent
     - `t004` 2026-03-05 −412.30 groceries
     - `t005` 2026-03-10 925.00 freelance
     - `t006` 2026-03-14 −444.00 software
     - `t007` 2026-03-20 −348.20 groceries
     - `t008` 2026-03-25 −321.00 travel
     - `t009` 2026-04-01 −1500.00 rent
   - With these rows, March sums to income 12925.00 and expense −3025.50.
   - `bom_blank.csv`: a UTF-8 BOM, the header, a blank line, row 1 with an empty memo, a whitespace-only line, and row 2 with a quoted memo that contains a comma.
   - `empty.csv`: zero bytes. Write it without a trailing newline.
   - Test layer: `package-api` (consumed by steps 4–5).
2. **Add `src/ledger/model.py`** (new) with `Transaction`, `LedgerError`, the canonical column tuple and the currency set. AC1, AC5.
   - Test layer: `package-api`, via step 5.
3. **Add `src/ledger/parser.py`** (new) with `parse_lines` and `parse_csv`, as in the Solution proposal. AC1–8.
   - Error paths to cover:
     - every reason in AC5, built from the trimmed raw text with `'…'` quoting;
     - parsing stops at the first bad row;
     - the duplicate-id message cites the first line;
     - the field-count message uses `len(header)`;
     - a header-only file returns `[]`.
   - The parser does no I/O beyond `parse_csv`'s open.
   - Test layer: `package-api`.
4. **Add `src/ledger/__init__.py`** (new). Give it a module docstring and re-export `Transaction`, `LedgerError`, `parse_lines` and `parse_csv` in `__all__`. AC1, AC8.
   - Test layer: `package-api`.
5. **Add the parser tests** in `tests/test_ledger_parse.py` (new). AC1–8.
   - Build inline cases with `io.StringIO`. Cover:
     - the reordered header with padded fields and an extra column;
     - each AC5 reason, including `20260301`, non-ASCII digits, `NaN`, `Infinity`, `1E+2`, `1_000`, `1.500`, `0`, `0.00`, `-0.00` and `usd`;
     - the duplicate id across a blank line;
     - the missing columns;
     - a file of blank lines only.
   - Run `parse_csv` against the fixtures through `pathlib.Path(__file__).parent / "fixtures" / "ledger"`.
   - Assert `parse_lines(StringIO(text)) == parse_csv(path)` for `sample.csv` and `bom_blank.csv`. Assert that `Transaction` is frozen (`dataclasses.FrozenInstanceError`).
   - Add the t1 line under `## Unreleased` in `CHANGELOG.md` (AC26).
   - Test layer: `package-api`.
6. **Add `src/ledger/report.py`** (new) with `RATES`, `CategoryTotal`, `MonthlyReport` with `to_dict()`, and `monthly_report`, as in the Solution proposal. AC9–18.
   - Invariants:
     - validate arguments before reading transactions;
     - leave the global `decimal` context alone, because quantize takes the rounding argument explicitly;
     - normalise negative zero for every figure;
     - `to_dict()` emits `str()` of the quantized Decimals and `categories` as a list of `{"name", "total", "count"}`.
   - Test layer: `package-api`.
7. **Extend `src/ledger/__init__.py`**: re-export `RATES`, `CategoryTotal`, `MonthlyReport` and `monthly_report`, and leave the t1 exports unchanged. AC9.
   - Test layer: `package-api`.
8. **Add the report tests** in `tests/test_ledger_report.py` (new). AC9–18.
   - Cover:
     - the sample in ILS and in USD, with exact `Decimal` equality and the category order;
     - single and triple 0.05 ILS rows in EUR;
     - the 5/−2 string forms;
     - `top=2`, a `top` larger than the category count, and `top=None`;
     - a tie on name;
     - `2026-05` and its `to_dict()`;
     - `2026-02`;
     - custom rates;
     - every AC18 `ValueError` case, asserting with `pytest.raises(ValueError)` and checking that the error is not a `LedgerError`;
     - case-sensitive categories;
     - a check that `decimal.getcontext()` is unchanged.
   - Build in-memory transactions with `Transaction(...)` directly.
   - Add the t2 changelog line.
   - Test layer: `package-api`.
9. **Add `src/ledger/cli.py`** and `src/ledger/__main__.py` (new), as in the Solution proposal. AC19–24.
   - Avoid argparse features from Python 3.14 (`suggest_on_error`, `color`).
   - Map `OSError` and `UnicodeDecodeError` to exit 2 through `parser.error`.
   - Never build the stderr line from `str(err)`.
   - Test layer: `package-api`, via step 11.
10. **Add `tests/fixtures/ledger/bad_amount.csv`** (new): header, one valid row, then line 3 with amount `-2.505`. AC23.
    - Test layer: `package-api`.
11. **Add the CLI tests** in `tests/test_ledger_cli.py` (new). AC19–25.
    - Use `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, timeout=10, cwd=REPO_ROOT)`, with relative fixture paths.
    - Cover:
      - the exact 13-line stdout and empty stderr;
      - USD with `--top 1 --json` parsed by `json.loads`;
      - text with `--top` listing only the kept categories;
      - the `2026-05` tail;
      - each exit-2 case with empty stdout and non-empty stderr: no subcommand, no `--month`, `2026-13`, `--top 0`, `GBP`, a missing file, and a non-UTF-8 file written to `tmp_path`;
      - the exact exit-3 stderr;
      - `report --help` exits 0 and contains `--month`;
      - two runs produce byte-identical output.
    - Add the t3 changelog line.
    - Test layer: `package-api`.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1–5 | t1 | ledger: transaction model and validating CSV parser (R1, R2) |
| 6–8 | t2 | ledger: monthly report with fixed-rate conversion and single half-even rounding (R3, R4) |
| 9–11 | t3 | ledger: `python -m ledger report` command line with text/JSON output and exit codes 0/2/3 (R5) |

Every work item has at least one step. Each work item also adds its own `- SCRUM-17: …` line under `## Unreleased` in `CHANGELOG.md`, for `PLAY-G4` and AC26.

## Verification and CI gate

**Canonical gate**
- Run from the repo root, once, on the committed SHA of each work item:
  1. `pip install -e ".[test]"`
  2. `pytest`
- This is the `package-api` layer declared in `.factory/testing.md`, run in CI by `.github/workflows/ci.yml:12-24` on Python 3.12.
- The gate also runs in a pod (Python 3.13 here). The provider run at the exact head is authoritative.

**What the gate must show**
- `pytest` passes with no failures and no skips added, for the existing suite plus the new files:
  - `tests/test_ledger_parse.py` (t1);
  - `tests/test_ledger_report.py` (t2);
  - `tests/test_ledger_cli.py` (t3).
- Each work item is green on its own; t2 and t3 build on the merged earlier items.
- Job `gate` stays green: no `CI_FAIL` file is added.

**CI and delivery obligations**
- No provider CI configuration changes.
- The layout gate must pass rules 1, 3 and 4 (`PLAY-G4`), so each PR's diff includes its changelog line.
- No `.factory/delivery-assets` entry is needed: every new file is a small text file, far below 1 MiB.

**AC26 self-check**
For each work item, confirm the following:
- `git diff --name-status main...HEAD` lists only additions under `src/ledger/`, `tests/` and `tests/fixtures/ledger/`, plus `M CHANGELOG.md`;
- the `CHANGELOG.md` change adds lines only;
- `pyproject.toml` is unchanged.

## Risks and scope guards

**Risks**
- **Stale editable install.** Local runs would import the other workspace's `src` and miss `ledger`. Mitigation: reinstall in this checkout before any local test run.
- **Changelog conflicts.** All three PRs append under the same `## Unreleased` heading. Mitigation: append at the end of the list; on conflict, update from `main` and keep both lines. Never drop an earlier entry.
- **Python version drift.** CI runs 3.12, the pod 3.13 and the floor is 3.10. Mitigation:
  - avoid `fromisoformat` leniency, `match` statements and 3.14 argparse options;
  - assert usage errors only on exit code and empty stdout, never on argparse wording (spec A3).
- **Python version drift in Decimal.** Decimal string forms such as `2.5E+2` before quantize. Mitigation: quantize every figure before exposing or stringifying it.
- **Glossary reviewer may flag `net`.** The spec fixes the name; keep it.

**Scope guards (the implement phase must NOT)**
- Edit any existing file other than adding lines under `## Unreleased` in `CHANGELOG.md`. That rules out `pyproject.toml` (no console script, no dependency), `README.md`, `src/testbed_utils/` and `src/guestbook/`.
- Add a third-party dependency, a `conftest.py`, or any `sys.path` manipulation.
- Change the global `decimal` context.
- Fetch rates or read configuration or the environment.
- Add output formats, multi-month reports or currencies beyond ILS, USD and EUR.
- Add a truncation marker to the text output under `--top` (spec A2).
- Make a failing check green by deleting, skipping, `xfail`-ing or weakening a test. A blocked layer is reported as blocked.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
