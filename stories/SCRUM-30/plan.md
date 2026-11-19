# Implementation plan — SCRUM-30: Monthly expense report from a CSV ledger

## Context

SCRUM-30 adds a new stdlib-only Python package `ledger` to play1 (work branch `halo/feat/scrum-30-20261119-025733`, merging into `main`). The package parses and validates a UTF-8 CSV ledger (`parse_csv` / `parse_lines` → `list[Transaction]`, or `LedgerError(line, reason)` at the first bad row). It reports one calendar month by category in a base currency (`monthly_report`, fixed `RATES`, `Decimal`, rounded half-even once after summing). It exposes all of this as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]` with exit codes 0/2/3. The acceptance criteria are Scenarios 1–26 of `spec.md`. The design is `hld.md` and the three dependent work items (t1 parser → t2 report → t3 CLI) are in `work-items.md`. All three files sit beside this file in `stories/SCRUM-30/`.

## Research findings

**Packaging and discovery (facts).**
- `pyproject.toml:25-26` — `[tool.setuptools.packages.find] where = ["src"]`, so a new `src/ledger/` is discovered with no manifest edit. `requires-python = ">=3.10"` (`pyproject.toml:10`). Runtime deps `pypdf`, `flask>=3`; test extra `pytest>=8`.
- `pyproject.toml:15-19` — `[project.scripts]` exists for other tools. `python -m ledger` needs only `src/ledger/__main__.py`, so no entry is added.
- `pyproject.toml:28-30` — pytest `testpaths = ["tests"]`, `addopts = "-q"`. `tests/` has no `conftest.py`, no `__init__.py` and no `sys.path` manipulation. Tests import through the editable install.
- Existing packages `src/testbed_utils/` and `src/guestbook/` are unrelated and stay unchanged. `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/` do not exist.

**Patterns to follow (facts).**
- CLI shape: `src/testbed_utils/numsummary.py:76-98` uses argparse, `print(..., file=sys.stderr)` and `sys.exit(code)`. Do not copy its `is_within_cwd` path restriction (`numsummary.py:38-54`): the spec has no such restriction.
- Package re-exports: `src/testbed_utils/__init__.py:9-23` uses explicit `from … import …` plus `__all__`.
- Subprocess tests: `tests/test_hello_sh.py:1-15` resolves `REPO_ROOT = Path(__file__).resolve().parent.parent` and calls `subprocess.run(..., capture_output=True, text=True)`. `tests/test_ledger_cli.py` uses the same shape with `[sys.executable, "-m", "ledger", ...]` (FR17).
- `CHANGELOG.md:3` — `## Unreleased` followed by one `- KEY: …` bullet per story (`CHANGELOG.md:5-8`).

**Gate (facts).**
- `.factory/testing.md` declares `test-gate: pytest` and one required layer, `package-api` (production-path, `runBy: canonical-gate`).
- `.github/workflows/ci.yml` runs job `test` on Python 3.12: `pip install -e ".[test]"`, then `pytest`. Job `gate` fails only if `CI_FAIL` exists at the repository root. No linter, formatter or type checker is configured.
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` checks every PR: rule 1 puts Python source under `src/` and tests under `tests/`. Rule 3 caps files at 200 KB. Rule 4 (`PLAY-G4`, blocker) requires the PR to add a line under `## Unreleased` in `CHANGELOG.md`.
- `.factory/plugins/claims-dev/agents/reviewer.md` covers the invoices code only and does not apply here.
- The repository has no `.factory/memory/` and no `.factory/delivery-assets`. No `AGENTS.md` or `CLAUDE.md` exists.

**Contracts touched.** The new public import surface of `ledger` (hld §5), the CLI argv/stdout/stderr/exit-code contract (FR13–FR16), and `CHANGELOG.md`. No other system, schema, network endpoint or cross-repo value is involved.

**Verified numbers.** The fixture row set in hld §8 was computed with `decimal` (`ROUND_HALF_EVEN`, quantize `0.01`). It gives ILS income `12925.00`, expense `-3025.50`, net `9899.50`. It gives USD income `3493.24`, expense `-817.70`, net `2675.54`, salary `3243.24`. These match Scenarios 9 and 20. The two groceries rows used in the check were `-400.25` and `-360.25`; any pair summing to `-760.50` works.

**Remaining unknowns.** None block the plan. The unreadable-file stderr wording is free-form (hld §8).

## Locked decisions and assumptions

**Locked decisions**
- Public API, exact reason strings, output format, JSON shape and exit codes are fixed by spec FR1–FR17 and Scenarios 1–26.
- Stdlib only. `Decimal` end to end. `pyproject.toml` is not modified (spec §2 Non-Goals; hld §2).
- Module layout is `src/ledger/{__init__,parser,report,cli,__main__}.py` (hld §2).
- Amounts and dates are validated by ASCII regex before `Decimal()` / `datetime.date()`. Do not use `date.fromisoformat` or `\d` (hld §6).
- A record's physical line is `reader.line_num` before the read + 1. A record is skipped as blank only when it is `[]` or a single whitespace-only field (hld §6).
- Per-row validation order: field count → id → date → amount → currency → category → duplicate id (spec A2; hld §6).
- Report arithmetic runs under a local decimal context (precision 28). Each figure is quantized once with `ROUND_HALF_EVEN`. A negative zero is normalised to `0.00`. Net is the exact total, quantized (hld §6).
- An in-month currency missing from a caller's `rates` raises `ValueError` (hld §6; t2 AC).
- CLI: required `report` subcommand, `--month` validated at parse time, `--base choices=["ILS","USD","EUR"]`, `--top` an int ≥ 1. `OSError` / `UnicodeDecodeError` exit 2. `LedgerError` exits 3 with `error: {FILE}:{line}: {reason}\n`. Nothing goes to stdout before the report is complete (hld §3, §6; spec A4).
- There is exactly one SCRUM-30 line under `## Unreleased` in `CHANGELOG.md`. t1 adds it; t2 and t3 revise it in place (spec A1; hld §6).
- Sample fixture rows follow hld §8.

**Assumptions**
- **P1.** CLI tests run with `cwd=REPO_ROOT` and pass the fixture path as the relative string `tests/fixtures/ledger/…`, so the "FILE as given" assertion compares against that exact string. *Evidence:* Scenarios 19 and 23 quote repository-relative paths, and `tests/test_hello_sh.py` already resolves `REPO_ROOT`. *If wrong:* pytest run from another cwd would fail to find the file. Fixing `cwd=` in `subprocess.run` makes this independent of the invoking cwd.
- **P2.** `python -m` puts the cwd on `sys.path`. The repository root holds no top-level `ledger` directory, so the installed `src/ledger` is what runs (FR17 holds). *If wrong:* a stray `ledger/` at the root would shadow it. Nothing creates one.
- **P3.** `json.dumps(report.to_dict())` with default separators and a trailing newline satisfies FR15. Scenario 20 compares parsed JSON, not bytes.
- **P4.** argparse's own `type=` callables (raising `argparse.ArgumentTypeError`) give exit 2 with stderr for `--month 2026-13`, `--top 0` and `--top abc`. This is standard argparse behaviour on 3.10–3.13.

## Solution proposal

**Approach.** Build one new package in three layers, each depending only on the one below. Add nothing to the existing code.

1. **`parser.py` (t1).** Defines `Transaction` (`@dataclass(frozen=True)`), `LedgerError(Exception)` with `.line`, `.reason` and `__str__` → `line {line}: {reason}`, and the two entry points.
   - `parse_lines` drives `csv.reader` directly rather than `DictReader`, so it keeps the field count and line tracking.
   - It reads the header, trims the names, maps each canonical name to its first column index, and reports missing names in canonical order.
   - It then iterates the records, recording `start_line = reader.line_num + 1` before each `next()`, and skips truly blank records.
   - Each row is validated with small private helpers, one per field: `_amount` uses the regex `^[+-]?[0-9]+(\.[0-9]+)?$`, then checks decimals, then zero. `_date` uses the regex `^[0-9]{4}-[0-9]{2}-[0-9]{2}$`, then `datetime.date(...)`.
   - A `dict[id → line]` catches duplicates.
   - `parse_csv` opens with `encoding="utf-8-sig", newline=""` and delegates to `parse_lines`. Detecting the BOM-only case needs no extra code: `utf-8-sig` strips it and an all-blank stream then has no header record.
   - The BOM in `parse_lines` input from `io.StringIO`: `parse_lines` also strips a leading `﻿` from the first header cell. Equivalence with `parse_csv` (Scenario 8) is tested on BOM-free text, so this is defensive only. Keep it a one-line `lstrip` on the first header name.
2. **`report.py` (t2).** Defines `RATES`, `CategoryTotal` (frozen dataclass `name, total, count`) and `MonthlyReport` (frozen dataclass with `to_dict()`). The report class name is not fixed by the spec; it is re-exported as well.
   - `monthly_report` validates its arguments first: month regex `^[0-9]{4}-(0[1-9]|1[0-2])$`, `base in rates`, `top is None or top >= 1`.
   - It then filters on `(t.date.year, t.date.month)`.
   - Inside `decimal.localcontext(decimal.Context(prec=28))` it converts each amount and accumulates income, expense, total and per-category sum and count.
   - It quantizes each figure once with a `_q` helper that also maps `-0.00` → `0.00`.
   - It sorts by `(-abs(total), name)` on the quantized totals and slices to `top`.
   - The hld does not say whether ties are compared on quantized or exact totals. Use the quantized value, so two categories that print equal sort by name, which is what Scenario 14 observes.
3. **`cli.py` + `__main__.py` (t3).** `main(argv=None) -> int` builds the parser: `prog="python -m ledger"`, `add_subparsers(dest="cmd", required=True)`, and a `report` subparser with `file`, `--month` (type `_month`), `--base` (choices, default `ILS`), `--top` (type `_positive_int`) and `--json`.
   - It runs `parse_csv` → `monthly_report` and renders text or JSON into one string, then writes it to stdout once.
   - It maps `LedgerError` → stderr `error: {args.file}:{e.line}: {e.reason}` and code 3, and `OSError` / `UnicodeDecodeError` → stderr `error: cannot read {file}: {e}` and code 2.
   - `__main__.py` calls `sys.exit(main())`.

**Design decisions.**
- The month regex lives in `report.py` (`ValueError`). The CLI reuses it in its argparse type through a small shared helper. Do not duplicate the pattern: import a private `_check_month` from `report.py`, or the compiled pattern.
- `UnicodeDecodeError` can surface mid-iteration, so the CLI wraps the whole `parse_csv` call. `parse_csv` returns a list, so the file is fully read and closed before the report.

**Alternatives rejected.**
- `csv.DictReader`: hides the field-count mismatch.
- Bare `Decimal(text)`: accepts `NaN`, `1e3`, `1_000` and non-ASCII digits.
- `date.fromisoformat`: behaves differently across Python versions.
- `[project.scripts]` entry: would modify `pyproject.toml`.
- In-process `main()` tests like `tests/test_num_summary_cli.py`: FR17 requires subprocess.
- Floats anywhere: lose precision.

## Ordered implementation steps

1. **Fixtures (t1).** Create `tests/fixtures/ledger/`:
   - `sample.csv` — header plus rows `t001`…`t009` per hld §8, including one quoted or empty memo for realism.
   - `bom_blank.csv` — starts with a UTF-8 BOM, has blank and whitespace-only lines, two valid rows, one empty memo and one quoted memo containing a comma.
   - `empty.csv` — zero bytes; make sure no editor adds a newline.

   Advances Scenarios 1, 3, 7, and 9/10/16/20 downstream. Layer: `package-api` (pytest), through step 3.
2. **Model and parser (t1).** Create `src/ledger/parser.py` (`Transaction`, `LedgerError`, `parse_lines`, `parse_csv`, private validators) and `src/ledger/__init__.py` (re-export the four names, with `__all__`). Cover header matching, extra columns, trimming, blank-record skip, the line tracking rule, the validation order and the exact FR5 reason strings, including `expected {N} fields, got {M}` with N = header field count. Advances Scenarios 1–8. Layer: `package-api`.
3. **Parser tests (t1).** Create `tests/test_ledger_parser.py`. Cover:
   - Scenario 1 on `sample.csv`: types, file order, `Decimal("12000.00")` exponent kept, `FrozenInstanceError` on assignment.
   - Scenario 2 via `io.StringIO`: reordered header, padded fields, extra column.
   - Scenario 3 on `bom_blank.csv`, and Scenario 4 (header only → `[]`).
   - One parametrized test for every FR5 case: `.line`, `.reason` and `str()`. Include `NaN`, `Infinity`, `1e3`, `1_000`, `'١٢'`, empty amount, `-0.00`, `1.500`, `20260301`, a leading `+` accepted, `,,,,,` → `empty id`, a multiply-broken row reporting by A2 order, and stop-at-first-bad-row.
   - Scenario 6, with a blank line between the duplicate rows.
   - Scenario 7: missing columns; `empty.csv`; a BOM-only file and a blank-lines-only file, written to `tmp_path`.
   - Scenario 8: `parse_lines(io.StringIO(text)) == parse_csv(path)`; patch `open` or inspect via a `tmp_path` UTF-8-BOM file to show `utf-8-sig`.
   - A quoted multi-line memo reporting its first line.

   Layer: `package-api`.
4. **CHANGELOG (t1).** Add one bullet under `## Unreleased` in `CHANGELOG.md` after the PLAY-175 bullet, e.g. `- SCRUM-30: add the \`ledger\` package with a validated CSV ledger parser.` Advances Scenario 26 and PLAY-G4. Layer: the repo-gate review. pytest does not cover it.
5. **Report (t2).** Create `src/ledger/report.py` (`RATES`, `CategoryTotal`, `MonthlyReport` + `to_dict()`, `monthly_report`, `_q`, the month validator). `to_dict()` key order is `month, base, count, income, expense, net, categories`; category dicts are `name, total, count`; amounts are `str()` of the quantized `Decimal`. Extend `src/ledger/__init__.py` with the re-exports `monthly_report`, `RATES`, `CategoryTotal` and `MonthlyReport`, and extend `__all__`. Advances Scenarios 9–18. Layer: `package-api`.
6. **Report tests (t2).** Create `tests/test_ledger_report.py`. Cover:
   - Scenarios 9, 10, 13, 15 and 16 over `parse_csv("…/sample.csv")`, located via `Path(__file__).parent / "fixtures" / "ledger"`.
   - Scenarios 11, 12, 14 and 17 over hand-built `Transaction`s.
   - Scenario 18: parametrized bad months; bad base; `top=0` and `top=-1`; a currency missing from `rates`. Assert the error is `ValueError` and not `LedgerError`.
   - A negative-zero case renders `0.00`.
   - Global-context independence: run under `decimal.localcontext(prec=5, rounding=ROUND_DOWN)` and assert identical results.

   Layer: `package-api`.
7. **CHANGELOG revise (t2).** Edit the SCRUM-30 bullet in place to mention the monthly report. Do not add a second bullet. Advances Scenario 26 and PLAY-G4.
8. **CLI (t3).** Create `src/ledger/cli.py` (`main(argv=None) -> int`, argparse config, text/JSON rendering, error mapping) and `src/ledger/__main__.py`.
   - Text output: the seven header lines, then `categories:` followed by `  {name}: {total} ({count})` lines, or `categories: none`. Every line is newline-terminated.
   - JSON output: `json.dumps(report.to_dict())` + `\n`.
   - Build the full output string, then write it once. stderr stays empty on success.

   Advances Scenarios 19–24. Layer: `package-api` via subprocess.
9. **Bad-amount fixture and CLI tests (t3).** Create `tests/fixtures/ledger/bad_amount.csv`: header, a valid line 2, line 3 with amount `-2.505`. Create `tests/test_ledger_cli.py` using a `run(*args)` helper: `subprocess.run([sys.executable, "-m", "ledger", *args], cwd=REPO_ROOT, capture_output=True, text=True)`. Cover:
   - Scenario 19: exact stdout equality and empty stderr.
   - Scenario 20: `json.loads` equality.
   - Scenario 21: stdout ends with the four lines.
   - Scenario 22, parametrized over: no subcommand, missing `--month`, `--month 2026-13`, `--top 0`, `--top abc`, `--base GBP`, a missing file, a directory, and a non-UTF-8 file written to `tmp_path` (`b"\xff\xfe..."` after a valid header). Each case asserts returncode 2, `stdout == ""` and `stderr != ""`.
   - Scenario 23: exact stderr.
   - A header error exercising line 1 through the CLI, via a `tmp_path` file.
   - Scenario 24.
   - Determinism: run twice and compare bytes.
   - Default base ILS.

   No `sys.path` edits and no `conftest.py` (Scenario 25). Layer: `package-api`.
10. **CHANGELOG final revise (t3).** Edit the SCRUM-30 bullet in place to describe the finished feature, e.g. `- SCRUM-30: add the \`ledger\` package and \`python -m ledger report\`, a monthly expense report from a CSV ledger.` Confirm `git diff main -- ':!src/ledger' ':!tests/test_ledger_*' ':!tests/fixtures/ledger' ':!stories'` shows only that one `CHANGELOG.md` line. Advances Scenario 26.

**Implicit invariants.**
- Authz and tenancy: none, since the tool is a local read-only CLI.
- Concurrency and idempotency: the code is pure and deterministic. The stable sort has a name tie-break and the decimal context is local.
- Validation and error paths: covered by steps 3, 6 and 9.

**Dependency acquisition.** `pip install -e ".[test]"` from PyPI, as CI does. No new dependency.

**Generated deliverables.** None. No binaries; all fixtures are small text files, well under 200 KB.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1, 2, 3, 4 | t1 | ledger: Transaction model and validated CSV parser |
| 5, 6, 7 | t2 | ledger: monthly report with fixed-rate conversion and half-even rounding |
| 8, 9, 10 | t3 | ledger: `python -m ledger report` command line with text/JSON output and exit codes |

Every work item has steps. Each work item's steps build and pass `pytest` on their own: t2 only consumes t1's API, and t3 only consumes t1 and t2.

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"`, then `pytest`, from the repository root. Run it once locally on the committed SHA. The provider CI (`.github/workflows/ci.yml` job `test`, Python 3.12) is authoritative for the `package-api` layer (`runBy: canonical-gate`).
- **Local reinstall:** an existing older editable install will not map the new top-level `ledger` package. Re-run `pip install -e ".[test]"` before `pytest` (hld §7). Never work around this with `sys.path` or `conftest.py`.
- **Layers:** `package-api` is the only declared and required layer, and it runs unprivileged in a pod. The CLI tests in that layer exercise the real `python -m ledger` entry point through subprocess. No other layer exists or is invented.
- **CI job `gate`:** green as long as no `CI_FAIL` file is created.
- **CI configuration:** none is needed. The existing workflow already runs the new tests.
- **`.factory/testing.md`:** no update needed, because the layer and command are unchanged. **`.factory/delivery-assets`:** not applicable, since no binary of 1 MiB or more is added.
- **Repo-gate (`repo-gate/SKILL.md`):** source is under `src/` and tests are under `tests/` (rule 1). No shell script is added (rule 2). All files are under 200 KB (rule 3). The `CHANGELOG.md` `## Unreleased` line is touched in every change set (rule 4 / `PLAY-G4`).
- **Done means:**
  - `pytest` passes with zero failures and zero skips among the new tests.
  - All Scenarios 1–25 are asserted by `tests/test_ledger_parser.py`, `tests/test_ledger_report.py` and `tests/test_ledger_cli.py`.
  - The pre-existing tests pass unchanged.
  - The story's net diff against `main`, outside `src/ledger/`, `tests/test_ledger_*.py`, `tests/fixtures/ledger/` and `stories/SCRUM-30/`, is exactly one added line in `CHANGELOG.md` (Scenario 26).

## Risks and scope guards

**Risks**
- *Editor-added bytes in fixtures.* `empty.csv` could gain a newline, or `bom_blank.csv` could lose its BOM. Mitigation: write both with explicit bytes, and add a test that asserts `empty.csv` has size 0 and that `bom_blank.csv` starts with `b"\xef\xbb\xbf"`.
- *argparse exit 2 for a missing subcommand.* This depends on `required=True` with `dest` set. Python 3.10's error message for a missing `dest` is buggy, which is why `dest="cmd"` is set. The Scenario 22 test covers it.
- *Line-number drift on quoted multi-line fields.* Mitigated by the `line_num + 1` rule and a dedicated test.
- *Negative-zero output (`-0.00`).* Mitigated by normalising in `_q`, with a test.
- *`.gitignore` patterns* (`*.spec`, `lib/`, `build/`, …) do not match any planned path. `*.csv` is not ignored, so the fixtures are committed.

**Scope guards (the implement phase must NOT)**
- Modify any existing file other than the single SCRUM-30 bullet under `## Unreleased` in `CHANGELOG.md`. In particular, leave `pyproject.toml`, `src/testbed_utils/`, `src/guestbook/`, existing tests, `.factory/` and `.github/` untouched.
- Add a second CHANGELOG bullet in t2 or t3. Revise the existing one in place.
- Add any third-party dependency, `[project.scripts]` entry, `conftest.py`, `tests/__init__.py` or `sys.path` manipulation.
- Use floats, fetched exchange rates, or currencies beyond ILS/USD/EUR.
- Add a path restriction like `numsummary.is_within_cwd`, or other features: multi-month ranges, other formats, config files, writing ledgers.
- Edit `spec.md`, `hld.md` or `work-items.md`.
- Make a failing check green by deleting, skipping, `xfail`-ing or weakening a test. A blocked check is reported as blocked.

## Clarification outcomes

None. No question was needed. The spec and hld settle every point, and the remaining gaps are stated as assumptions P1–P4.
