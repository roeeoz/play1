# Implementation plan — SCRUM-29 Monthly expense report from a CSV ledger

## Context

SCRUM-29 adds a new stdlib-only Python package `ledger` to play1 (target branch `main`, work branch `halo/feat/scrum-29-20261119-024908`). The package parses a UTF-8 CSV ledger into validated, frozen transactions, reporting the first bad row by physical line number (AC 1–8). It builds a deterministic one-month report in ILS, USD or EUR with `Decimal` money and one `ROUND_HALF_EVEN` rounding per figure (AC 9–18). It exposes this through `python -m ledger report FILE --month YYYY-MM [--base] [--top] [--json]`, with exit codes 0, 2 and 3 (AC 19–25). The requirement is `spec.md`, the design is `hld.md` and the three-item breakdown (t1 parser, t2 report, t3 CLI) is `work-items.md`. All three sit beside this file in `stories/SCRUM-29/`.

## Research findings

**Change surface (facts, read on the work branch at `08eeedf`, identical to `main` at `b7b5d0a` outside `stories/`):**
- `pyproject.toml:21-22` sets `[tool.setuptools.packages.find] where = ["src"]`, so a new `src/ledger/` is picked up by the editable install. No manifest change is needed for `python -m ledger`, because a `__main__.py` is enough. `pyproject.toml:9` sets `requires-python = ">=3.10"`. `pyproject.toml:27` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/` do not exist yet. `tests/fixtures/` exists and holds flat fixtures for other tests (`empty.txt`, `numbers.txt`, PDFs).
- Existing packages `src/testbed_utils/` and `src/guestbook/` are unrelated and must stay untouched.
- `CHANGELOG.md:3` holds `## Unreleased`, followed by one bullet per story in the form `- PLAY-175: add …`.
- No `AGENTS.md`, `CLAUDE.md` or `.factory/memory/` exists in the repository.

**Existing conventions (facts):**
- `src/testbed_utils/numsummary.py:1-3` shows the repository's module style: a module docstring, `from __future__ import annotations` and `argparse`.
- `src/testbed_utils/__init__.py` re-exports the public API with an explicit `__all__`. `ledger/__init__.py` follows the same pattern.
- The existing CLI tests (`tests/test_hello_cli.py:12-23`, `tests/test_num_summary_cli.py:19-31`) call `main()` in-process. AC 25 requires the ledger CLI tests to use `subprocess` with `[sys.executable, "-m", "ledger", ...]` instead. That is still the `package-api` pytest layer, not a new one.

**Gate (facts):**
- `.factory/testing.md` declares one required layer, `package-api` (`pytest`, `runBy: canonical-gate`).
- `.github/workflows/ci.yml` job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. Job `gate` fails only if `CI_FAIL` exists at the root.
- No linter, formatter or type checker is configured.
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` holds the layout gate. Rule 1 puts source under `src/` and tests under `tests/`. Rule 3 rejects any file over 200 KB. Rule 4 (`PLAY-G4`) requires every pull request to add a `CHANGELOG.md` line under `## Unreleased`.

**Contracts touched:**
- The new public Python API re-exported from `ledger`: `parse_csv`, `parse_lines`, `Transaction`, `LedgerError`, `monthly_report`, `RATES` and `CategoryTotal` (hld §5).
- The CLI's stdout, stderr and exit-code contract (spec FR11–FR15).
- No cross-repo contract and no external data. Rates are fixed constants.

**Resolved unknowns (verified locally on Python 3.13):**
- **Fixture rows reproduce the AC figures.** I checked these March rows:
  - salary `12000.00 ILS`, rent `-1500.00 ILS`, freelance `250.00 USD`;
  - groceries `-400.25 ILS` and `-360.25 ILS`;
  - software `-120.00 USD`, travel `-80.25 EUR`.

  With exact `Decimal` conversion and one quantize per figure they give ILS `12925.00 / -3025.50 / 9899.50` and USD `3493.24 / -817.70 / 2675.54`, matching AC 9, 10 and 20. With `-0.01 ILS` in base EUR, `quantize` gives `-0.00`, which confirms that the negative-zero normalisation in hld §7 is needed.
- **Line tracking.** On `csv.reader`, a record's physical start line equals the previous `reader.line_num + 1`. A quoted field spanning lines advances `line_num` to the end line.
- **Blank lines.** An empty line yields `[]` and a whitespace-only line yields a single whitespace field. Both are "blank". `,,` yields empty fields and is a data row, so it fails as `empty id` (hld §7).

**Remaining unknowns:** none that block the plan.

## Locked decisions and assumptions

**Locked decisions:**
- **Package shape** (spec §2, hld §2): stdlib only, under `src/ledger/`, with tests under `tests/` and fixtures under `tests/fixtures/ledger/`. No `conftest.py` and no `sys.path` manipulation (`.factory/testing.md`).
- **Exact strings and values** (spec AC 5–7, 9–23):
  - every `LedgerError` reason text;
  - `str(error) == f"line {line}: {reason}"`;
  - the text report lines and the JSON keys;
  - the `error: {FILE}:{line}: {reason}` stderr format;
  - exit codes 0, 2 and 3.
- **Money rules** (spec AC 10, 11; hld §6):
  - `RATES = {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}`;
  - conversion is `amount × rates[currency] ÷ rates[base]` at full precision;
  - each figure is quantized once to `0.01` with `ROUND_HALF_EVEN`, independently;
  - arithmetic runs inside `decimal.localcontext()`.
- **Edge-case behaviour settled by the design** (hld §7):
  - the order of validation checks within a row;
  - the amount grammar (optional sign, ASCII digits, optional `.digits`) and the date grammar (`[0-9]{4}-[0-9]{2}-[0-9]{2}`);
  - case-sensitive header names;
  - `duplicate column(s): …` on the header line;
  - a record reports the line it starts on;
  - negative zero is normalised;
  - categories are ordered by the absolute value of the rounded total, then by name;
  - a missing rate raises `ValueError`;
  - `top` must be `None` or an `int` ≥ 1, and `bool` is rejected.
- **Work-item ownership** (`work-items.md`): t1 owns the model, parser and all four fixtures. t2 owns `report.py`. t3 owns `cli.py` and `__main__.py`. Each item only appends to `src/ledger/__init__.py`.
- **CHANGELOG** (spec A1, hld §8): each work item adds exactly one line under `## Unreleased` in `CHANGELOG.md`. No other existing file changes.
- **No manifest change** (hld §6): no `[project.scripts]` entry is added to `pyproject.toml`.

**Assumptions:**
- **The CHANGELOG line uses the story key**, as in `- SCRUM-29: add …`, matching the existing `PLAY-NNN:` bullets. Evidence: `CHANGELOG.md:5-8`. If wrong, only the wording changes.
- **CLI error messages.** A FILE that cannot be opened is reported through `parser.error(...)` (exit 2, usage plus message on stderr) or an equivalent `sys.exit(2)` after printing to stderr. Evidence: AC 22 fixes only the exit code and the empty stdout. If wrong, only the stderr text changes.
- **The subprocess tests run with the repository root as working directory** and pass FILE as the relative path `tests/fixtures/ledger/…`, which AC 23 echoes verbatim. Pytest runs from the root in CI (`ci.yml`). If wrong, the tests must set `cwd` explicitly. They should set `cwd` to the repo root anyway (derived from `Path(__file__).parent.parent`).
- **`bad_amount.csv` content.** It is the header, one valid row (line 2), then the `-2.505` row (line 3), with all dates in 2026-03. This follows from the work-items t1 AC.

## Solution proposal

The approach adds a self-contained `ledger` package next to the existing packages, with three layers that each depend only on the one below. It fits the src layout without touching `pyproject.toml`.

1. **`src/ledger/model.py`** holds:
   - `@dataclass(frozen=True) class Transaction` with fields `id`, `date`, `amount`, `currency`, `category` and `memo`;
   - `class LedgerError(Exception)`, which stores `.line` and `.reason` and has `__str__` return `f"line {self.line}: {self.reason}"`;
   - `CURRENCIES = ("ILS", "USD", "EUR")`;
   - `COLUMNS = ("id", "date", "amount", "currency", "category", "memo")`, the canonical order used for the missing and duplicate column messages.
2. **`src/ledger/parser.py`** holds `parse_lines(lines)` and `parse_csv(path)`.
   - `parse_lines` wraps the iterable so that a leading `"﻿"` on the first line is stripped, then feeds it to `csv.reader`.
   - It tracks `start = prev_line_num + 1` for every record and skips blank records (`[]`, or all-whitespace with a single field).
   - The first non-blank record is the header. Names are trimmed and matched case-sensitively. The parser checks for missing columns first, then for duplicate required columns, both reported on the header line.
   - Each data row is validated in the hld §7 order: field count, empty id, date regex, `date(y, m, d)` calendar check, amount regex, decimal places, zero, currency, empty category, duplicate id (the duplicate check keeps a dict from id to first line).
   - Amounts are built with `Decimal(text)` only after the ASCII regex `^[+-]?[0-9]+(\.[0-9]+)?$` matches. Decimal places are counted from the text, so `+5` gives `Decimal("5")` and `1.500` is rejected.
   - `parse_csv` opens the path with `encoding="utf-8-sig", newline=""` and delegates to `parse_lines`.
   - Uses `re.ASCII`-equivalent explicit `[0-9]` classes. It never uses `date.fromisoformat` (it accepts `20260301` on 3.11+) or `\d` (it matches non-ASCII digits).
3. **`src/ledger/report.py`** holds:
   - `RATES`;
   - `@dataclass(frozen=True) CategoryTotal(name, total, count)`;
   - `@dataclass(frozen=True) MonthlyReport(month, base, count, income, expense, net, categories)` with `to_dict()`, which turns amounts into `str` and categories into a list of `{"name", "total", "count"}`;
   - `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.

   `monthly_report` works in this order:
   1. Validate the arguments: `month` against `^[0-9]{4}-(0[1-9]|1[0-2])$`, `base in rates`, and `top` must be `None` or a non-`bool` `int` ≥ 1. A violation raises `ValueError`.
   2. Inside `decimal.localcontext()`, with `prec = 28` and `rounding = ROUND_HALF_EVEN` set explicitly, filter by `t.date.year`/`t.date.month`, convert each amount, and sum income, expense, net and per-category totals exactly.
   3. Quantize each figure once and replace `-0.00` with `+0.00`, for example with `q + 0` or `copy_abs` when it is zero.
   4. Sort by `(-abs(rounded_total), name)` and slice to `top`.
   5. A currency missing from `rates` raises `ValueError`.
4. **`src/ledger/cli.py`** holds `main(argv=None) -> int`, and **`src/ledger/__main__.py`** calls `sys.exit(main())`.
   - The `argparse` parser uses `prog="python -m ledger"` and a required subparser `report` (`dest="command", required=True`).
   - `report` takes the positional `FILE`, a required `--month` with a `type=` validator that raises `argparse.ArgumentTypeError` (same regex as the report), `--base` with `choices=["ILS", "USD", "EUR"]` and `default="ILS"`, `--top` with a `type=` validator for an int ≥ 1, and `--json` (`store_true`).
   - `parse_csv(FILE)` is wrapped as follows:
     - `OSError` or `UnicodeDecodeError` → usage error, exit 2;
     - `LedgerError` → `error: {FILE}:{e.line}: {e.reason}` on stderr, exit 3.
   - Rendering happens only after success, and stdout is written in one go.
   - The text output is the fixed lines, with `categories: none` when the list is empty.
   - The JSON output is `json.dumps(report.to_dict())` plus `"\n"`.

**Alternatives rejected:**
- A `[project.scripts]` console script: it changes an existing file and is not asked for (hld §6).
- Validating with `Decimal()` / `date.fromisoformat` alone: both are laxer than the spec (hld §6).
- Quantizing per transaction: it breaks AC 11.
- Testing the CLI in-process through `main()`: AC 25 requires the real `python -m` entry point.

## Ordered implementation steps

1. **Create the model.** Add `src/ledger/__init__.py` (docstring, re-exports, `__all__`) and `src/ledger/model.py` (`Transaction`, `LedgerError`, `COLUMNS`, `CURRENCIES`). Covers AC 1 and 5 (`str(error)`). Test layer: `package-api` (pytest).
2. **Create the fixtures.** Add the following under `tests/fixtures/ledger/`:
   - `sample.csv`: the header and rows `t001`…`t009` in file order. Seven March rows use the verified values from Research findings, one row is `2026-02-27 groceries -99.99 ILS` and one row is dated `2026-04-01`. At least one row has an empty memo.
   - `bom_blank.csv`: a UTF-8 BOM, blank and whitespace-only lines, one empty memo, and one quoted memo containing a comma.
   - `empty.csv`: zero bytes.
   - `bad_amount.csv`: `-2.505` on line 3.

   Keep the files LF-terminated and tiny. Covers AC 1, 3, 7 and 23. Test layer: `package-api`.
3. **Implement `parse_lines` and `parse_csv`** in `src/ledger/parser.py`, following the Solution proposal and hld §7. Export both from `__init__.py`. Covers AC 1–8. Test layer: `package-api`.
4. **Add `tests/test_ledger_parser.py`.** It must contain:
   - one test per AC 1–8;
   - a parametrized table of every exact reason, including `NaN`, `Infinity`, `1e2`, `1_000`, `5.`, `.5`, non-ASCII digits, `1.500`, `-0.00`, `20260301`, `+5` and `,,,,,`;
   - a duplicate id across a blank line;
   - a missing column and a duplicate required column;
   - a blank-throughout file raising `missing header`;
   - a multi-line quoted field and the start line it reports;
   - a multi-fault row, checking the order of validation;
   - `FrozenInstanceError` on assignment;
   - `parse_lines(io.StringIO(...))` equal to `parse_csv`, including a BOM;
   - `parse_csv` on `bad_amount.csv` raising `LedgerError(3, …)`.

   Import only `from ledger import …`. Covers AC 1–8. Test layer: `package-api`.
5. **Add one t1 CHANGELOG line** under `## Unreleased` in `CHANGELOG.md`, describing the `ledger` model and CSV parser. Repo gate rule 4 requires it. No test layer applies; the layout gate checks it.
6. **Implement `src/ledger/report.py`** following the Solution proposal. Append `monthly_report`, `RATES`, `CategoryTotal` and `MonthlyReport` to `__init__.py` without changing t1's exports. Covers AC 9–18. Test layer: `package-api`.
7. **Add `tests/test_ledger_report.py`.** It must contain:
   - the sample in ILS and in USD (AC 9, 10);
   - rounding once: one and three 0.05 ILS transactions in base EUR (AC 11);
   - two decimal places in `str` output, and negative zero (AC 12; hld §7);
   - top-N with 2, a value larger than the category count, and `None` (AC 13);
   - ties (AC 14);
   - `2026-05` and its `to_dict()` (AC 15);
   - `2026-02` (AC 16);
   - custom rates (AC 17);
   - every `ValueError` case, asserting it is not a `LedgerError` (AC 18), plus a currency missing from `rates`;
   - a non-empty `to_dict()`;
   - context isolation: set `getcontext().prec = 3` and `rounding = ROUND_DOWN` in a `localcontext()` within the test, then assert the same figures and that the caller's context is unchanged.

   Build inputs from `parse_csv` on `sample.csv` and from `Transaction` literals. Covers AC 9–18. Test layer: `package-api`.
8. **Add one t2 CHANGELOG line** describing the monthly report. Gate rule 4.
9. **Implement `src/ledger/cli.py` and `src/ledger/__main__.py`** following the Solution proposal. Exporting `main` from `__init__.py` is optional and append-only. Covers AC 19–24. Test layer: `package-api`.
10. **Add `tests/test_ledger_cli.py`.** A helper runs `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, cwd=REPO_ROOT)`. Cover:
    - the exact 13-line text output (AC 19);
    - JSON with `--base USD --top 1 --json`, checked through `json.loads` equality (AC 20);
    - `2026-05` output ending with the zero lines (AC 21);
    - the exit-2 matrix: no subcommand, `--month` missing, `--month 2026-13`, `--top 0`, `--base GBP`, a missing file, a directory, and a non-UTF-8 file written to `tmp_path` (AC 22). Each case asserts empty stdout, non-empty stderr, and `"Traceback"` absent from stderr;
    - `bad_amount.csv`, exit 3, with the exact stderr (AC 23);
    - `--help` (AC 24);
    - byte-identical output across two runs.

    Avoid `sys.path` manipulation and `conftest.py` (AC 25). Test layer: `package-api` (production path through the installed distribution).
11. **Add one t3 CHANGELOG line** describing `python -m ledger report`. Gate rule 4.

**Invariants the implement phase must cover:**
- **Authorization and tenancy:** not applicable. The tool is local and single-user, reads only the given path and does no network access.
- **Concurrency and idempotency:** pure functions with no shared state. The `decimal` context is isolated through `localcontext()`, and the output is deterministic (step 10).
- **Validation and error paths:** the parser reports only the first error. Caller errors (`ValueError`) are kept distinct from data errors (`LedgerError`). The CLI never lets a traceback escape for the listed cases.

**Dependencies:** none new. `pip install -e ".[test]"` installs the existing `pypdf`, `flask` and `pytest` from the index and does not assume a warm cache.

**Generated deliverables:** none. The fixtures are hand-written text. No binary is added, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1, 2, 3, 4, 5 | t1 — ledger: transaction model and validating CSV parser |
| 6, 7, 8 | t2 — ledger: monthly report in a base currency |
| 9, 10, 11 | t3 — ledger: `python -m ledger report` command line |

Every work item has steps. If t2 finds a figure the fixture cannot reproduce, `work-items.md` allows t2 to correct `sample.csv`, provided the t1 tests stay green.

## Verification and CI gate

- **Canonical gate, in order, from the repository root:** `pip install -e ".[test]"`, then `pytest`. It runs once locally on the committed SHA of each work item. CI's `test` job on Python 3.12 is authoritative at the pushed head.
- **Required layer:** `package-api` (`pytest`, production-path) is the only declared layer. It runs unprivileged in a pod, including the subprocess CLI tests, which need only `sys.executable` with the editable install.
- **What the gate must show:** `pytest` passes in full, both the existing suite and the new `tests/test_ledger_parser.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py`, with no skips added. Each work item must pass on its own tree: t1 without `report.py`, and t2 without `cli.py`.
- **Layout gate (`repo-gate`):** all source is under `src/` and all tests under `tests/`; every file is under 200 KB; each work item's diff adds a line under `## Unreleased` in `CHANGELOG.md`.
- **The `gate` job:** no `CI_FAIL` file may be created.
- **No CI change:** provider CI configuration needs no change, and `.factory/testing.md` needs no update because the layer does not change.
- **Python versions:** the code must avoid anything newer than 3.10. The local pod has Python 3.13 and CI has 3.12. Do not use `datetime.UTC`, `itertools.batched` or 3.11+ `fromisoformat` behaviour.

## Risks and scope guards

**Risks:**
- **Fixture drift breaks the AC figures.** Mitigation: use the verified row values in Research findings. t2's tests assert the figures against `sample.csv`.
- **The stdlib is lax** (`Decimal`, `fromisoformat`, `\d`). Mitigation: use explicit ASCII regexes before conversion, with parametrized negative tests.
- **Line numbers drift with multi-line quoted fields or blank lines.** Mitigation: derive the start line from the previous `line_num`, and test it.
- **Negative-zero output (`-0.00`).** Mitigation: normalise after quantizing, and test it.
- **The subprocess tests depend on the editable install and the working directory.** Mitigation: use `sys.executable` and an explicit `cwd`.
- **`argparse` would exit 0 or misbehave when no subcommand is given.** Mitigation: use `required=True` on the subparsers and test the exit code 2.

**Scope guards (the implement phase must NOT):**
- Modify `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/**`, `README.md`, `src/testbed_utils/**`, `src/guestbook/**`, existing tests or existing fixtures. The only exception is the single `CHANGELOG.md` line per work item.
- Add any third-party dependency, `conftest.py`, `sys.path` manipulation, `[project.scripts]` entry, linter or new CI job.
- Add features beyond the acceptance criteria: other formats, live rates, configuration, multi-month ranges, colour or tables in the output.
- Apply the claims glossary renames (`.factory/plugins/claims-dev/skills/glossary/SKILL.md`). It does not apply to this package (hld §8).
- Make a check green by deleting, skipping, `xfail`-ing or weakening it. A check that cannot pass is reported as blocked.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
