# Plan — SCRUM-31 Monthly expense report from a CSV ledger

## Context

SCRUM-31 adds a new stdlib-only Python package `ledger` to the `play1` repository (work branch `halo/feat/scrum-31-20261119-030637`, target `main`). The package parses a UTF-8 CSV ledger into validated transactions (criteria 1–8), builds a monthly per-category report in ILS/USD/EUR at fixed rates, rounding once after summing (criteria 9–18), and exposes it as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]` with exit codes 0/2/3 (criteria 19–25). The approved requirement is `spec.md`, the design (rulings D1–D14) is `hld.md`, and the three-item breakdown t1 → t2 → t3 is `work-items.md`, all beside this file in `stories/SCRUM-31/`.

## Research findings

**Change surface (all new, except one line in `CHANGELOG.md`):**
- `src/ledger/` does not exist; `tests/test_ledger_*.py` and `tests/fixtures/ledger/` do not exist.
- `pyproject.toml:23-24` — `[tool.setuptools.packages.find] where = ["src"]` discovers a new `src/ledger/` with no manifest edit. `pyproject.toml:9` — `requires-python = ">=3.10"`. `pyproject.toml:26-28` — `testpaths = ["tests"]`, `addopts = "-q"`.
- `CHANGELOG.md:3` — `## Unreleased` heading; entries are `- <KEY>: <description>.` lines (`CHANGELOG.md:5-8`).

**Contracts touched:** in-package Python API only (`hld.md` §5): `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` (t1); `RATES`, `CategoryTotal`, `monthly_report`, report `to_dict()` (t2); the CLI argv, stdout/stderr text and exit codes (t3). No cross-repo contract, no network, no external data.

**Existing patterns to follow:**
- CLIs use `argparse` (`src/testbed_utils/numsummary.py:5`, `:76-80`) with `from __future__ import annotations` and module docstrings (`numsummary.py:1-3`).
- Subprocess-driven tests exist: `tests/test_hello_sh.py:2`, `:11` use `subprocess.run`. Class-grouped pytest tests (`tests/test_num_summary_cli.py:36`) with a module-level `FIXTURES = pathlib.Path(__file__).parent / "fixtures"` (`test_num_summary_cli.py:11`).

**Canonical gate:** `.factory/testing.md` — `pip install -e ".[test]"` then `pytest` from the repo root (CI job `test`, `.github/workflows/ci.yml:12-24`, Python 3.12). One declared layer, `package-api` (production-path, `runBy: canonical-gate`). No linter, formatter or type checker exists. The CI `gate` job only checks for a `CI_FAIL` file (`ci.yml:26-36`). The PR-layout gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rules 1–4: Python under `src/`, tests under `tests/`, no file > 200 KB, and PLAY-G4 — a line added under `## Unreleased` in `CHANGELOG.md`.

**Test rule:** no `conftest.py`, no `sys.path` manipulation; tests import `ledger` through the editable install only (`.factory/testing.md`, criterion 25).

**Verified behaviour:** the `USD` figures in criteria 10/20 follow from the ILS totals by linearity (12000/3.70 → 3243.24; 12925/3.70 → 3493.24; −3025.50/3.70 → −817.70; 9899.50/3.70 → 2675.54), so any currency mix in `sample.csv` that keeps the ILS totals of `hld.md` §4 satisfies both reports.

**Unknowns remaining:** none blocking. `.factory/memory/` does not exist.

## Locked decisions and assumptions

**Locked decisions**
- Package `ledger` under `src/`, stdlib only, Python ≥ 3.10; tests under `tests/` (spec §1, §6).
- Module split `parser.py` (t1), `report.py` (t2), `cli.py` + `__main__.py` (t3); dependencies cli → report → parser (`hld.md` §2).
- Entry point is `python -m ledger` via `__main__.py`; `pyproject.toml` is not edited (`hld.md` §2, §6 alternatives).
- Money is `decimal.Decimal` throughout; `RATES` = `ILS` → `Decimal("1")`, `USD` → `Decimal("3.70")`, `EUR` → `Decimal("4.00")`; round once per figure with `ROUND_HALF_EVEN` (criteria 10, 11).
- Exact error reasons and `str(LedgerError)` = `line {line}: {reason}` (criteria 5–7); CLI data-error stderr `error: {FILE}:{line}: {reason}\n` (criterion 23).
- Parser rulings D1–D6, report rulings D7–D11, CLI rulings D12–D14 (`hld.md` §6), including the duplicate-column reason `duplicate column '<name>'` (`hld.md` A5).
- Sample fixture contract (`hld.md` §4).
- Only one existing file changes: one line per work item under `## Unreleased` in `CHANGELOG.md` (spec A1, repo-gate PLAY-G4).

**Assumptions**
- **P1** The CHANGELOG line uses the story key `SCRUM-31` in the existing `- KEY: description.` form. Evidence: `CHANGELOG.md:5-8`. If wrong: wording edit only.
- **P2** `__init__.py` re-exports via explicit imports plus `__all__`. Evidence: `hld.md` §5 lists the public names. If wrong: cosmetic.
- **P3** The report class is a frozen dataclass named `MonthlyReport`; `categories` is a tuple of `CategoryTotal`. Evidence: no source names it; `hld.md` D11 allows tuple or list and tests compare by content. If wrong: a rename inside t2.
- **P4** Unopenable FILE is reported through `parser.error(...)`, giving argparse's `usage:` + `python -m ledger report: error: cannot read '<FILE>': <detail>` and exit 2. Evidence: `hld.md` D13, spec A3. If wrong: message text only; criterion 22 checks exit code and empty stdout.

## Solution proposal

Build the package in three layers matching the work items, each self-contained and green on its own.

**Parser (`src/ledger/parser.py`).** `parse_lines(lines)` wraps the iterable so the first line's leading `\ufeff` is stripped (D4), feeds it to `csv.reader`, and tracks each record's physical start line as `previous_reader.line_num + 1`, where `previous_reader.line_num` is read before each `next()` (D4: a multi-line quoted record reports its first line). Blank records (`[]` or one whitespace-only field) are skipped but counted. The first non-blank record is the header: names trimmed, required names checked in canonical order (`missing column(s): …`), a required name twice → `duplicate column '<name>'`. Each data row is validated in D3 order (field count against the header's count, id, date, amount, currency, category, duplicate id) with `re.fullmatch` on ASCII-class patterns: date `[0-9]{4}-[0-9]{2}-[0-9]{2}` then `datetime.date(int, int, int)` for the calendar check; amount `[+-]?[0-9]+(\.[0-9]+)?` then fractional-digit count ≤ 2 then non-zero, constructing `Decimal(text)` so the exponent is preserved. `fullmatch` avoids `$` accepting a trailing newline; `[0-9]` (not `\d`) refuses non-ASCII digits. `Transaction` is a `@dataclass(frozen=True)`. `LedgerError(Exception)` stores `line`, `reason` and passes `f"line {line}: {reason}"` to `super().__init__`. `parse_csv(path)` opens with `encoding="utf-8-sig", newline=""` and delegates; `OSError`/`UnicodeDecodeError` propagate (D6).

**Report (`src/ledger/report.py`).** `monthly_report` validates arguments first (`ValueError`, D10): `month` a `str` fully matching `[0-9]{4}-(0[1-9]|1[0-2])`; `base in rates`; `top is None` or (`type(top) is int` and `top >= 1`). It filters by `(t.date.year, t.date.month)`, raises `ValueError` naming any filtered transaction's currency missing from `rates`, and inside `decimal.localcontext()` set to precision 28 with `ROUND_HALF_EVEN` (D7) accumulates exact `amount * rates[cur] / rates[base]` sums for income (positive), expense (negative), net and per category (sum, count). Each figure is quantized once with `Decimal("0.01")`, and a zero result is normalised to `Decimal("0.00")` (D8). Categories sort by `(-abs(total), name)` on the rounded totals (D9), then slice `[:top]`. `to_dict()` returns keys in the order `month, base, count, income, expense, net, categories` with amounts as `str`.

**CLI (`src/ledger/cli.py`, `src/ledger/__main__.py`).** `main(argv=None) -> int` builds `argparse.ArgumentParser(prog="python -m ledger")` with required subparsers and a `report` subcommand: positional `file`; `--month` required with a `type` that reuses the report's month validation (exposed as a small helper in `report.py`); `--base` `choices=["ILS", "USD", "EUR"]` default `ILS`; `--top` a `type` accepting ints ≥ 1; `--json` flag. It calls `parse_csv`, mapping `OSError`/`UnicodeDecodeError` to `report_parser.error(...)` (exit 2) and `LedgerError` to stderr `error: {args.file}:{e.line}: {e.reason}\n` with return 3. Output is built as one string (text: seven labelled lines plus `  name: total (count)` lines or `categories: none`; JSON: `json.dumps(report.to_dict()) + "\n"`) and written once, return 0. `__main__.py` calls `sys.exit(main())`.

**Alternatives rejected:** a console script in `pyproject.toml` (edits an existing file; spec non-goal); `float` anywhere (precision); per-row rounding (criterion 11); `Decimal()` / `date.fromisoformat()` alone as validators (too lax, `hld.md` D1/D2); argparse `FileType` for FILE (opens without `utf-8-sig`/`newline=""` and leaks a handle).

## Ordered implementation steps

**t1 — model and parser**
1. Create `tests/fixtures/ledger/sample.csv` (header + `t001`…`t009` per `hld.md` §4, with a currency mix such as freelance `250.00` USD, software `-120.00` USD, travel `-80.25` EUR, salary `12000.00` ILS), `tests/fixtures/ledger/bom_blank.csv` (BOM, blank and whitespace-only lines, an empty memo, a quoted memo containing a comma; two rows) and a zero-byte `tests/fixtures/ledger/empty.csv`. Criteria 1, 3, 7. Layer: `package-api`.
2. Create `src/ledger/parser.py` with `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` as in the solution proposal. Criteria 1–8. Layer: `package-api`.
3. Create `src/ledger/__init__.py` with a module docstring re-exporting the four names. Criterion 1, 8.
4. Create `tests/test_ledger_parser.py`: sample happy path (types, order, `Decimal("12000.00")` exponent preserved, frozen → `dataclasses.FrozenInstanceError`); free header order, trimming, extra columns; BOM/blank/quoted memo; header-only → `[]`; `empty.csv` and blank-only → `LedgerError(1, "missing header")`; missing columns in canonical order; duplicate column; every exact reason from criterion 5 and the extra D1/D2 inputs (`20260301`, `NaN`, `Infinity`, `1e2`, `1_000`, `.5`, `5.`, `١٢`, `1.500`, `-0.00`, `usd`); duplicate id across a blank line; physical line numbers with blanks and a multi-line quoted memo; D3 check order on a multi-fault row; parsing stops at the first bad row; `parse_lines(io.StringIO(...))` (with and without BOM) equals `parse_csv` on the same text written to `tmp_path`; `parse_csv` on a missing path raises `OSError` and on invalid UTF-8 raises `UnicodeDecodeError`. Most cases build inline text through `io.StringIO`. Criteria 1–8. Layer: `package-api`.
5. Append `- SCRUM-31: add the \`ledger\` package's transaction model and validating CSV parser.` under `## Unreleased` in `CHANGELOG.md` after the last existing entry. PLAY-G4. Layer: repo-gate (PR review), no pytest.

**t2 — monthly report**
6. Create `src/ledger/report.py` with `RATES`, `CategoryTotal` (frozen dataclass `name, total, count`), `MonthlyReport` (frozen dataclass with `to_dict()`), the month-validation helper and `monthly_report` as in the solution proposal. Criteria 9–18. Layer: `package-api`.
7. Extend `src/ledger/__init__.py` to re-export `RATES`, `CategoryTotal`, `monthly_report`. Criterion 9.
8. Create `tests/test_ledger_report.py`: sample March ILS (all figures and category order); USD (salary `3243.24`, freelance `250.00`, base `USD`); 0.05 ILS in EUR once → `0.01`, three → `0.04`; 5 and −2 ILS → `"5.00"`, `"-2.00"`, `"3.00"`; `-0.01` ILS in EUR → `str(expense) == "0.00"` and net `0.00` (D8); `top=2`, `top=100`, `top=None`; tie ordering by name; `2026-05` zero report and exact `to_dict()`; `2026-02` groceries −99.99; custom `rates` 10 USD → `20.00`; a lowered global decimal context (`localcontext` with `prec=3` around the call) does not change results; `ValueError` for each bad month, a non-str month, base not in rates, `top` 0 / −1 / `True` / `1.0`, and a month transaction whose currency is missing from `rates`; `pytest.raises(ValueError)` never catches a `LedgerError` (assert the type is not `LedgerError`). Transactions are built from `parse_csv(FIXTURES/"ledger"/"sample.csv")` or directly as `Transaction(...)`. Criteria 9–18. Layer: `package-api`.
9. Append the t2 line under `## Unreleased` in `CHANGELOG.md` after t1's. PLAY-G4.

**t3 — command line**
10. Create `tests/fixtures/ledger/bad_amount.csv` whose physical line 3 carries amount `-2.505` (lines 1–2 header and a valid row). Criterion 23.
11. Create `src/ledger/cli.py` (`main`, argparse setup, text/JSON rendering, exit-code mapping) and `src/ledger/__main__.py`. Criteria 19–24. Layer: `package-api`.
12. Create `tests/test_ledger_cli.py` with one helper running `subprocess.run([sys.executable, "-m", "ledger", *args], capture_output=True, text=True, cwd=REPO_ROOT)` where `REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent`. Cases: criterion 19 exact stdout and empty stderr; criterion 20 `json.loads(stdout)` equality; `--top 1` truncates text lines; criterion 21 tail lines; criterion 22 each usage case (no subcommand, missing `--month`, `--month 2026-13`, `--top 0`, `--top x`, `--base GBP`, missing file, a directory, an invalid-UTF-8 file in `tmp_path`) → exit 2, stdout `""`, stderr non-empty; criterion 23 exact stderr using the relative path as typed; criterion 24 `--help` exit 0 with `--month` in stdout; two runs byte-identical. No `sys.path` edits, no `conftest.py`. Criteria 19–25. Layer: `package-api`.
13. Append the t3 line under `## Unreleased` in `CHANGELOG.md` after t2's. PLAY-G4.

**Invariants every step keeps:** no authorization/tenancy surface (local file read only); no concurrency or shared state (pure functions, immutable results); validation and error paths are the bulk of the tests above. Dependencies: none beyond the stdlib and the existing `pytest>=8` test extra installed by `pip install -e ".[test]"` — no cache assumed. No generated deliverables; fixtures are hand-written text well under 200 KB; nothing for `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–5 | t1 — ledger package: Transaction model and validating CSV parser |
| 6–9 | t2 — ledger: monthly report by category with fixed-rate conversion |
| 10–13 | t3 — ledger: `python -m ledger report` command line (text/JSON, exit codes 0/2/3) |

Every work item has steps; no gap.

## Verification and CI gate

- Canonical gate, from the repo root, in order: `pip install -e ".[test]"` then `pytest` (`.factory/testing.md`; CI job `test`, Python 3.12). Run once locally on the committed SHA of each work item; the provider CI run at the exact head is authoritative for the `package-api` layer.
- Required layer: `package-api` (production-path) — runs unprivileged in a pod. No other layer exists; none is added.
- The gate must show: the full suite passing, including the new `tests/test_ledger_parser.py` (after t1), `tests/test_ledger_report.py` (after t2) and `tests/test_ledger_cli.py` (after t3), with every pre-existing test still passing and none skipped or deselected.
- Compatibility: no 3.11+-only API (no `datetime.UTC`, no `tomllib`, no extended `fromisoformat`, no `except*`); CI runs 3.12 only, so 3.10 compatibility is enforced by review, not by a layer.
- PR-layout gate (repo-gate): source under `src/`, tests under `tests/`, no file > 200 KB, one new line under `## Unreleased` in `CHANGELOG.md` per PR.
- No provider CI change is needed; `.factory/delivery-assets` does not apply.

## Risks and scope guards

**Risks**
- *Fixture arithmetic drift* — t2/t3 expected numbers depend on `sample.csv`. Mitigation: t1's tests assert the fixture's March ILS sums per category, so a wrong fixture fails in t1.
- *Line-number tracking with `csv.reader`* — `line_num` is the end line of a record. Mitigation: track the start line as previous `line_num + 1`; test with blank lines and a multi-line quoted memo.
- *BOM via `parse_lines`* — `csv.reader` over `io.StringIO` keeps `\ufeff`. Mitigation: strip it from the first line explicitly; test parity between entry points.
- *Argparse writing to stdout on error* — it writes usage errors to stderr; only `--help` uses stdout. Tests assert empty stdout on every exit-2 case.
- *Negative zero and global decimal context* — covered by D7/D8 and explicit tests.
- *CHANGELOG conflicts between sequential PRs* — trivial; append after the previous item's line.

**Scope guards — the implement phase must NOT:**
- Edit `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/`, `README.md`, `src/testbed_utils/`, `src/guestbook/` or any existing test or fixture; the only existing-file change is one `CHANGELOG.md` line per work item.
- Add a `conftest.py`, any `sys.path` manipulation, a third-party dependency, a linter/formatter configuration or a new test framework.
- Use `float`, live/fetched exchange rates, network access, file writes or persistent configuration; add other file formats or charts.
- Reorder or reword the exact error reasons, output labels or exit codes from the spec.
- Make any failing check green by deleting, skipping, `xfail`-ing or weakening a test; a blocked check is reported as blocked.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
