# Implementation plan — SCRUM-34 Monthly expense report from a CSV ledger

## Context

SCRUM-34 adds a new standard-library-only package, `ledger`, to the play1 repository. The package parses a UTF-8 CSV ledger into validated `Transaction`s. It rejects the first bad row with its physical line number. It builds a one-month report in ILS, USD or EUR at fixed rates using exact `Decimal` arithmetic, rounding once and half to even. It exposes the report as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`, with exit codes 0, 2 and 3. The 27 acceptance criteria are in `spec.md` §5. The change lands on the work branch `halo/feat/scrum-34-20261119-042322`, cut from `main`, and merges into `main`. This file sits in `stories/SCRUM-34/` beside `spec.md` (the requirement), `hld.md` (the design, whose §4 fixes the sample fixture and §5 the edge cases) and `work-items.md` (t1 parser → t2 report → t3 CLI).

## Research findings

- **Packaging.** `pyproject.toml:23-24` discovers packages with `[tool.setuptools.packages.find] where = ["src"]`, so a new `src/ledger/` is picked up with no manifest edit. `pyproject.toml:9` sets `requires-python = ">=3.10"`. `python -m ledger` needs only `src/ledger/__main__.py`, not a `[project.scripts]` entry. `pyproject.toml:11` lists the runtime dependencies `pypdf` and `flask>=3`, which the install must download; `ledger` itself imports neither.
- **Tests.** `pyproject.toml:26-28` sets `testpaths = ["tests"]` and `addopts = "-q"`. `tests/` has no `__init__.py`, no `conftest.py` and no `sys.path` manipulation. Test module basenames must therefore be unique, and `test_ledger_parser.py`, `test_ledger_report.py` and `test_ledger_cli.py` are. Imports resolve only through the installed distribution.
- **Subprocess test style.** `tests/test_qa_s3_greeting.py:7-11` shows the house pattern: a module-level path resolved from `__file__`, `subprocess.run(..., capture_output=True, text=True, timeout=10)`, and a helper that returns `(returncode, stdout, stderr)`. `tests/test_num_summary_cli.py` drives `main()` in-process instead. AC 25 rules that style out for the ledger CLI.
- **Gate.** `.factory/testing.md` declares a single required layer, `package-api` (`pytest`, `runBy: canonical-gate`). `.github/workflows/ci.yml` runs it as `pip install -e ".[test]"` then `pytest`, on Python 3.12. The `gate` job only checks for a `CI_FAIL` marker. The repository has no linter, formatter or type checker.
- **PR gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` has four rules:
  - rule 1: Python source goes under `src/` and tests under `tests/`;
  - rule 3: no file in the diff is larger than 200 KB;
  - rule 4 (`PLAY-G4`, a blocker): every PR adds a line under `## Unreleased` in `CHANGELOG.md`.

  `CHANGELOG.md:3-8` holds `## Unreleased` with four `- KEY: …` bullets, and the new line follows that form.
- **Ignore rules.** `.gitignore` ignores none of `tests/fixtures/ledger/*.csv` or `src/ledger/*.py`.
- **Repository guidance.** There is no `AGENTS.md`, `CLAUDE.md` or `.factory/memory/`. The `claims-dev` glossary and reviewer cover only invoices code and do not apply.
- **What exists and what must be created.** None of `src/ledger/`, `tests/test_ledger_*.py` or `tests/fixtures/ledger/` exists. Everything is new except the one `CHANGELOG.md` line. No existing module is imported or changed.
- **Verified figures.** The hld §4 sample, computed with a 60-digit context and `ROUND_HALF_EVEN`, gives every figure the spec asserts:
  - March in ILS: income `12925.00`, expense `-3025.50`, net `9899.50`; categories salary 12000.00, rent -1500.00, freelance 925.00, groceries -760.50, software -444.00, travel -321.00.
  - March in USD: income `3493.24`, expense `-817.70`, net `2675.54`; salary `3243.24`, freelance `250.00`.
- **Stdlib behaviours the design relies on (facts):**
  - `csv.reader` yields `[]` for an empty line and `['   ']` for a whitespace-only one.
  - `reader.line_num` counts physical lines consumed, so the line a record starts on is the previous `line_num` + 1.
  - `Decimal()` accepts `1e2`, `NaN`, `1_000`, `.5` and non-ASCII digits, so the hld's regex must run first.
  - `argparse.add_subparsers(dest=..., required=True)` is needed for "no subcommand" to exit 2.
  - argparse `type=`/`choices=` failures exit 2. Subcommand `--help` prints to stdout and exits 0.
  - `UnicodeDecodeError` is a `ValueError` subclass and is raised lazily while the file is iterated.
- **Remaining unknowns.** No product unknown remains (spec §8, hld §5). One assumption, the order of the two header checks, is listed below.

## Locked decisions and assumptions

**Locked decisions**
- **Public surface (spec §3, AC 1–18; hld §5).** The public names are `Transaction`, `LedgerError(line, reason)` (whose `str()` is `line {line}: {reason}`), `parse_lines`, `parse_csv`, `RATES`, `CategoryTotal(name, total, count)`, `Report` with `to_dict()`, and `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`. All are importable from `ledger`.
- **Messages, formats and exit codes.** Every error reason, output line and exit code is fixed verbatim by spec AC 5–7, 19–24 and 26, and by hld §5.
- **Module layout (hld §2).** `src/ledger/parser.py` (t1), `src/ledger/report.py` (t2), and `src/ledger/cli.py` plus `src/ledger/__main__.py` (t3). Imports run one way: `cli → report → parser`.
- **Sample fixture content (hld §4, D7).** Fixed row for row.
- **Parsing rules (hld §5, D1, D2).** Use `csv.reader`, not `DictReader`. Validate amount and date text with ASCII-only regexes before `Decimal`/`date`. Check each row in this order: field count, empty id, duplicate id, date, amount, currency, empty category. A record's line is the line where it starts.
- **Arithmetic (D3; hld §5).** Use a local context of precision 60 with `ROUND_HALF_EVEN`. Quantize each figure to `0.01` once. Never report `-0.00`. Order categories by the absolute value of the rounded total, descending, then by name.
- **Errors (D4, D5).** The library raises `LedgerError` for data errors and `ValueError` for caller errors. argparse owns every usage error (exit 2). An unopenable or undecodable FILE exits 2. The CLI buffers its output and writes to stdout only on success.
- **Subprocess CLI tests (AC 25, D6).**
- **CHANGELOG (spec FR16/AC 27, hld D8).** t1 adds one `## Unreleased` line. t2 and t3 rewrite that same line in place.
- **Stdlib only, Python 3.10+, no network, configuration or environment reads (spec §2, hld §7).**

**Assumptions**
- **A1 — Header check order.** When a header has both a duplicated and a missing required column, `duplicate column '<name>'` is reported first. Evidence: hld §5 lists the duplicate check before the missing-column check, and no scenario combines them. If wrong, the change is a two-line swap in `parser.py` and its test.
- **A2 — `LedgerError` derives from `Exception`, not `ValueError`.** Evidence: spec FR10/AC 18 say caller errors are "never `LedgerError`", and the CLI must tell exit 3 apart from a `UnicodeDecodeError` (a `ValueError`, exit 2). If wrong, the CLI's `except` order would misroute decode errors.
- **A3 — CHANGELOG wording.** The line reads `- SCRUM-34: add the \`ledger\` package …` and grows per work item. Evidence: the `CHANGELOG.md:5-8` style. If wrong, only the wording changes.
- **A4 — The test install has network access.** `pip install -e ".[test]"` downloads `pypdf`, `flask` and `pytest`. Evidence: `pyproject.toml:11,20`. If the pod is offline, the local run is reported blocked and the provider CI run stays authoritative.

## Solution proposal

Build three small modules layered `cli → report → parser`. Each is a pure function core, and only the CLI deals with I/O and exit codes. This mirrors hld §2 and adds nothing beyond the three work items.

- **Parser (`src/ledger/parser.py`).**
  - `Transaction` is a `@dataclass(frozen=True)` with the six typed fields.
  - `LedgerError(Exception)` stores `line` and `reason` and formats `line {line}: {reason}`.
  - `parse_lines` strips a leading `﻿` from the first item of the iterable. It feeds the lines to `csv.reader` and records each record's start line as the previous `reader.line_num` + 1.
  - It skips blank records, where blank means no fields or one field that is empty after stripping. The first non-blank record is the header. It strips the header names and checks for a duplicated required column, then for missing columns (reported in canonical order).
  - It builds a name→index map, then validates each row in the locked order. A `seen` dict maps each id to its first line, for the duplicate message.
  - Module-level compiled patterns check amounts and dates: `[+-]?[0-9]+(\.[0-9]+)?` and `[0-9]{4}-[0-9]{2}-[0-9]{2}`, applied with `re.fullmatch` so a trailing `\n` cannot slip through `$`.
  - The decimal-places check counts the fractional digits as written. The zero check runs on the `Decimal`. The date is built from the three integer groups inside `try/except ValueError` and is never parsed with `fromisoformat`.
  - `parse_csv` opens the path with `encoding="utf-8-sig", newline=""` and returns `parse_lines(f)`.
- **Report (`src/ledger/report.py`).**
  - `RATES` holds `Decimal` values. `CategoryTotal` and `Report` are frozen dataclasses, and `categories` is a list.
  - `monthly_report` first validates its arguments, raising `ValueError`: `month` must fullmatch `[0-9]{4}-(0[1-9]|1[0-2])`, `base` must be in `rates`, and `top` must be `None` or an `int` ≥ 1. A `bool` is rejected because it is not a meaningful count.
  - It then filters on `t.date.strftime("%Y-%m") == month`, or compares year and month.
  - Inside `decimal.localcontext(Context(prec=60, rounding=ROUND_HALF_EVEN))` it converts each amount as `amount * rates[cur] / rates[base]`. A currency missing from `rates` raises `ValueError` naming it.
  - It accumulates exact income, expense and per-category sums and counts, then quantizes each to `Decimal("0.01")` once.
  - It normalizes negative zero by adding `Decimal("0")` inside the context, or by an equivalent `copy_abs` when `is_zero()`.
  - It sorts categories by `(-abs(total), name)` and slices `[:top]`. `to_dict()` emits the locked key order, with `str()` of each two-place amount.
- **CLI (`src/ledger/cli.py`, `src/ledger/__main__.py`).**
  - `build_parser()` defines prog `python -m ledger` and a required `report` subparser with:
    - positional `file`;
    - `--month`, required, with a `type=` validator that uses the report's month pattern and raises `argparse.ArgumentTypeError`;
    - `--base`, with `choices=["ILS","USD","EUR"]` and default `ILS`;
    - `--top`, with a `type=` that requires an int ≥ 1;
    - `--json` as `store_true`.
  - `main(argv=None) -> int`:
    - parses the arguments;
    - calls `parse_csv` inside `try`, mapping `OSError` and `UnicodeDecodeError` to `parser.error(...)` (exit 2, stderr only);
    - catches `LedgerError` and writes `error: {args.file}:{e.line}: {e.reason}\n` to stderr, returning 3;
    - builds the report and renders the whole text or JSON into one string, then writes it to stdout once and returns 0.
  - `__main__.py` is `sys.exit(main())`.
  - The text renderer produces the six headline lines, then `categories:` followed by two-space-indented `name: total (count)` lines, or `categories: none` when the list is empty. JSON is `json.dumps(report.to_dict())` plus `\n`.

**Alternatives rejected**
- **`csv.DictReader`.** It hides the raw field count and the start lines (D1).
- **Relying on `Decimal()`/`fromisoformat` alone.** They accept spellings the spec rejects (D2).
- **Rounding each conversion.** It breaks AC 11 (D3).
- **Validating `--month` only in `monthly_report` and mapping `ValueError` to exit 2 in the CLI.** argparse `type=` gives exit 2 and the standard message for free (D5).
- **Opening FILE with `argparse.FileType`.** It cannot report a decode error, which happens during iteration, and it would leave the file open on usage errors. Opening inside `main` keeps one error path.
- **In-process CLI tests.** AC 25 forbids them.

## Ordered implementation steps

**t1 — parser**
1. Create `tests/fixtures/ledger/sample.csv` with header `id,date,amount,currency,category,memo` and rows `t001`…`t009` exactly as in hld §4, with free-text memos, at least one of them empty. Advances AC 1; consumed by t2 and t3.
2. Create `tests/fixtures/ledger/bom_blank.csv` and `tests/fixtures/ledger/empty.csv` (AC 3, AC 7).
   - `bom_blank.csv` starts with the UTF-8 BOM bytes and has blank and whitespace-only lines between two valid rows. One row has an empty memo, the other a `"quoted, memo"`.
   - `empty.csv` is zero bytes.
   - Write both as raw bytes so the BOM survives editors.
3. Create `src/ledger/parser.py` with `Transaction`, `LedgerError`, `parse_lines` and `parse_csv`, as in the Solution proposal (AC 1–8, 26; hld §5). Invariants: stop at the first error, never return a partial list, and use no 3.11+ API.
4. Create `src/ledger/__init__.py`, re-exporting `Transaction`, `LedgerError`, `parse_lines` and `parse_csv` with `__all__` (AC 8).
5. Create `tests/test_ledger_parser.py` (layer `package-api`, `pytest`). Most cases build their input inline with `io.StringIO`. It covers:
   - AC 1: the sample's types, order and `Decimal("12000.00")`;
   - AC 2: reordered header, extra column, stripped fields;
   - AC 3: `bom_blank.csv`;
   - AC 4: header only;
   - AC 5: one parametrized case per reason, each asserting `line`, `reason` and `str()`, plus a test that parsing stops at the first bad row;
   - AC 6: duplicate id across a blank line, giving `(first seen on line 2)` at line 4;
   - AC 7: missing columns in canonical order, `empty.csv`, and blank-only input;
   - AC 8: `parse_lines` on a `StringIO` with a BOM, and on a list of strings, equals `parse_csv`;
   - AC 26 and the work-item t1 AC 8 spellings: `+5`, `1e2`, `"1,000"`, `1_000`, `.5`, `5.`, `١٢`, the empty string, `1.500`, `0`, `-0`, `0.00`;
   - the work-item t1 AC 9 hld cases: validation order, field count taken from a header with extra columns, `,,,,,` → `empty id`, `duplicate column 'amount'`, `20260301`, and a multi-line quoted memo reporting its start line.
6. Add one line under `## Unreleased` in `CHANGELOG.md`, after `CHANGELOG.md:8`: `- SCRUM-34: add the \`ledger\` package with a validated CSV ledger parser.` (`PLAY-G4`, AC 27).

**t2 — report**

7. Create `src/ledger/report.py` with `RATES`, `CategoryTotal`, `Report` (with `to_dict()`) and `monthly_report`, as in the Solution proposal (AC 9–18). It imports `Transaction` from `ledger.parser` only for typing. Invariants: never return a `LedgerError`, stay independent of the caller's decimal context, and never report `-0.00`.
8. Extend `src/ledger/__init__.py` with `monthly_report`, `Report`, `CategoryTotal` and `RATES` (AC 9).
9. Create `tests/test_ledger_report.py` (layer `package-api`). It loads `sample.csv` through `parse_csv` and builds synthetic `Transaction`s for edge cases. It covers:
   - AC 9: the full ILS March report, including category order;
   - AC 10: USD;
   - AC 11: one and three 0.05 ILS amounts in EUR;
   - AC 12: `str()` gives two places;
   - AC 13: `top=2`, a `top` larger than the category count, and `None`;
   - AC 14: a tie broken by name;
   - AC 15: the `2026-05` `to_dict()`, including the key order;
   - AC 16: `2026-02`;
   - AC 17: custom rates;
   - AC 18: each bad `month`, an unknown `base`, `top=0`, and a missing rate, all `ValueError`, with a check that `LedgerError` is not raised;
   - the hld cases: a run under `localcontext(prec=3, rounding=ROUND_DOWN)` gives identical figures, and an amount pair that nets to a negative sub-cent value reports `0.00` rather than `-0.00`.
10. Rewrite the SCRUM-34 line in `CHANGELOG.md` in place to also mention the monthly report, without adding a line (D8).

**t3 — CLI**

11. Create `tests/fixtures/ledger/bad_amount.csv`: line 1 the header, line 2 a valid row, line 3 a row with amount `-2.505` (AC 23).
12. Create `src/ledger/cli.py` with `build_parser()` and `main(argv=None) -> int`, and `src/ledger/__main__.py` calling `sys.exit(main())`, as in the Solution proposal (AC 19–24). Invariants:
    - stdout stays empty on any non-zero exit;
    - nothing goes to stderr on success;
    - FILE is echoed exactly as given;
    - output is byte-identical across runs;
    - the file handle is closed by a `with` in `parse_csv`.
13. Create `tests/test_ledger_cli.py` (layer `package-api`). A helper calls `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, timeout=10, cwd=REPO_ROOT)`, with `REPO_ROOT` resolved from `__file__`, and does no `sys.path` work. It covers:
    - AC 19: the exact thirteen-line stdout, using the relative path `tests/fixtures/ledger/sample.csv`;
    - AC 20: `json.loads` equality and a single output line;
    - AC 21: the empty month;
    - AC 22, parametrized: no subcommand, missing `--month`, `--month 2026-13`, `--top 0`, `--base GBP`, a missing file, a directory (`tmp_path`), and a non-UTF-8 file (`tmp_path` written with `b"\xff\xfe..."`). Each asserts exit 2, empty stdout and non-empty stderr;
    - AC 23: exact stderr for a relative path, plus a second variant with an absolute path to prove it is echoed as given;
    - AC 24: `report --help`;
    - work-item t3 AC 7: two identical runs produce equal bytes.
14. Rewrite the SCRUM-34 line in `CHANGELOG.md` in place to also mention `python -m ledger report`, without adding a line (D8, AC 27).

**Dependencies.** No new dependency is added. The existing `pip install -e ".[test]"` makes `ledger` importable, so no generated deliverable or binary is involved, and `.factory/delivery-assets` does not apply.

**Authorization and concurrency.** These invariants do not apply. The package is a local, single-process, read-only tool with no tenancy, state or shared resources.

## Work-item mapping

| Step(s) | Work item | Title |
|---|---|---|
| 1–6 | t1 | ledger package: Transaction model and CSV parser (parse_lines / parse_csv) |
| 7–10 | t2 | ledger monthly report: fixed-rate conversion, exact sums, category totals, to_dict |
| 11–14 | t3 | ledger CLI: python -m ledger report with text/JSON output and exit codes 0/2/3 |

Every work item has steps. Each work item's steps leave the tree building and `pytest` green on their own: t2 and t3 only add modules on top of the earlier ones.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`, `.github/workflows/ci.yml`): `pip install -e ".[test]"`, then `pytest` from the repository root on Python 3.12. Run it once locally on the committed SHA. The provider CI run at the exact head is authoritative.
- **Required layer:** `package-api` (`pytest`, production-path). It can run in a pod if the install can reach the package index (A4). No other layer exists, and none is added.
- **What the gate must show:**
  - `pytest` exits 0 with the whole existing suite still passing;
  - `tests/test_ledger_parser.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py` are collected and pass, with at least one test per acceptance criterion in AC 1–26;
  - the CI `gate` job is green (no `CI_FAIL` file).
- **AC 27 and `PLAY-G4`** are checked by inspecting the diff, not by a test. `git diff --stat main...HEAD -- . ':!stories'` must list only new files under `src/ledger/`, `tests/` and `tests/fixtures/ledger/`, plus `CHANGELOG.md` with exactly one added line.
- **Python 3.10 compatibility.** CI runs only 3.12. Keep 3.10 compatibility by construction: no `match`-dependent semantics beyond 3.10, no `fromisoformat` leniency, no `ExceptionGroup`, no 3.11+ `typing` features. This is noted as a review item, not a new CI layer.
- **No CI configuration change is needed.** CI is not a deliverable.

## Risks and scope guards

**Risks**
- **CSV line accounting.** Off-by-one errors with blank lines, a BOM or a multi-line quoted field. Mitigation: explicit start-line tracking and dedicated tests (AC 5, AC 6, the multi-line memo).
- **Regex anchoring.** `re.match` with `$` accepts a trailing newline, and `\d` accepts Unicode digits. Mitigation: use `re.fullmatch` and the explicit `[0-9]`, with tests for `١٢`.
- **argparse on 3.10.** Required subparsers need `dest`, or the error path raises `TypeError`. Mitigation: set `dest="command", required=True`, and test the "no subcommand" case.
- **Decode errors surface during iteration, not at `open`.** Mitigation: the CLI's `try` wraps the whole `parse_csv` call. `LedgerError` is not a `ValueError` (A2).
- **CHANGELOG sequencing (hld A1).** If the work items ship as one PR, the line is written once in its final form, which still satisfies AC 27.
- **Very large amounts (hld §7).** Above about 55 significant digits, quantize raises `InvalidOperation`. This is accepted and untested.

**Scope guards — the implement phase must NOT:**
- edit `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/**`, `README.md`, any existing `src/` or `tests/` file, or anything in `stories/SCRUM-34/` other than this plan;
- add a console script, a `conftest.py`, `sys.path` manipulation, a third-party dependency, a config file or an environment-variable read;
- add a second `CHANGELOG.md` line, or touch the existing bullets;
- support other file formats, live rates, extra currencies or multi-month ranges;
- refactor `testbed_utils` or reuse its CLI style;
- delete, skip, `xfail` or weaken any existing or new test to get green. A failing required check is reported blocked, not silenced.

## Clarification outcomes

None. The spec's two intake questions were settled on 2026-11-19 (spec §8), and hld §5 resolves every remaining edge case. A1 to A4 are stated assumptions, not blockers.
