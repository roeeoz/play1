# HLD — SCRUM-23 Monthly expense report from a CSV ledger

## 1. System Overview

- **What:** a new stdlib-only Python package `ledger` (`src/ledger/`) that parses a UTF-8 CSV ledger into immutable transactions, builds a one-month per-category report in a base currency (ILS/USD/EUR at fixed rates) and exposes it as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`.
- **Problem:** get a deterministic monthly summary from the terminal; never print a wrong total — a bad row is reported by its physical line number (exit 3).
- **Responsibilities:** parsing + validation (R1, R2), report arithmetic (R3, R4), command line (R5). Library surface (`parse_csv`, `parse_lines`, `LedgerError`, `Transaction`, `monthly_report`, `RATES`, `CategoryTotal`, report `to_dict()`) is part of the product because the spec's ACs name it.
- **Verified against the code (`main` @ `8c059d9`):** no `src/ledger/` and no `tests/test_ledger_*.py` exist; `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets `testpaths = ["tests"]`, so the new package needs no manifest change. The spec's repository-fit claims (§6) hold.

## 2. Architecture Overview

Three layers inside one package, each depending only on the one below:

| Layer | Module(s) | Depends on |
|---|---|---|
| Model + parser | `src/ledger/__init__.py`, `src/ledger/model.py` (Transaction, LedgerError, constants), `src/ledger/parser.py` (parse_lines, parse_csv) | stdlib `csv`, `decimal`, `datetime`, `dataclasses` |
| Report | `src/ledger/report.py` (RATES, CategoryTotal, report type, monthly_report) | model |
| CLI | `src/ledger/cli.py` (argparse, formatting, exit codes), `src/ledger/__main__.py` | parser, report |

- Module names inside `src/ledger/` are a suggestion; the binding boundary is the package `ledger` and its public names re-exported from `ledger/__init__.py`.
- **Follows existing patterns:** argparse CLIs in `src/testbed_utils/numsummary.py:76` and `src/testbed_utils/hello.py:21` (stderr messages, `sys.exit`). Unlike those, this CLI is reached via `python -m ledger` (a `__main__.py`), not a `[project.scripts]` entry — so `pyproject.toml` stays untouched.
- **External dependencies:** none (stdlib only; `pytest>=8` test extra already present).
- **Ownership:** all in repo `play1`; one work item per layer, strictly sequential (t1 → t2 → t3), matching the spec's delivery shape.

## 3. Data Flow Design

All synchronous, single process, no I/O beyond reading one file and writing stdout/stderr.

1. `python -m ledger report FILE --month M [--base B] [--top N] [--json]` → argparse validates usage (month shape, base choice, top ≥ 1). Usage error → exit 2, stdout empty.
2. `parse_csv(FILE)` opens with `encoding="utf-8-sig", newline=""` (OSError → exit 2) → `parse_lines` → `csv.reader`, tracking the physical line number (header = 1, blank lines count) → validates each row → `list[Transaction]` or raises `LedgerError(line, reason)` at the first bad row → CLI prints `error: {FILE}:{line}: {reason}` to stderr, exit 3, stdout empty.
3. `monthly_report(txs, M, base=B, top=N)` → filter by month → convert each amount exactly (`amount × rates[cur] ÷ rates[base]`, full Decimal precision) → sum exact per figure / per category → quantize each figure once to `0.01` with `ROUND_HALF_EVEN` → order categories by |total| desc, name asc → apply top-N to the category list only.
4. CLI renders the 13-line text format (AC 19/21) or `json.dumps(report.to_dict())` (AC 20), exit 0.
- Output is fully deterministic: no clock, no locale, no environment input.

## 4. Component Breakdown

- **Model & parser** (repo `play1`, t1) — In: an iterable of text lines or a path. Out: `list[Transaction]` in file order, or `LedgerError(line, reason)`. Owns every validation reason text of AC 5–7 and the fixtures `sample.csv`, `bom_blank.csv`, `empty.csv`, `bad_amount.csv`.
- **Report** (repo `play1`, t2) — In: transactions, month, base, top, rates. Out: an immutable report (`month`, `base`, `count`, `income`, `expense`, `net`, `categories: list[CategoryTotal(name, total, count)]`) with `to_dict()`; `ValueError` on caller errors.
- **CLI** (repo `play1`, t3) — In: argv + the file. Out: stdout text/JSON, stderr message, exit code 0/2/3. The terminal entry point of this story (`python -m ledger`); it is the composition root and owns the assembled-path tests (AC 25).

## 5. Interface Contracts

The spec fixes these (no cross-repo contracts exist):

- **Library (public, `import ledger`):** `parse_lines(lines)`, `parse_csv(path)`, `Transaction` (frozen dataclass: `id`, `date`, `amount`, `currency`, `category`, `memo`), `LedgerError` (`.line`, `.reason`, `str()` = `line {line}: {reason}`), `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`, `RATES` (`ILS→Decimal("1")`, `USD→Decimal("3.70")`, `EUR→Decimal("4.00")`), `CategoryTotal(name, total, count)`, report `.to_dict()`.
- **Error reason texts:** exactly those of AC 5–7 (templates per A3 of the spec).
- **`to_dict()` shape:** `{"month", "base", "count", "income", "expense", "net", "categories": [{"name", "total", "count"}]}`, amounts as two-place strings, keys in that order.
- **CLI:** text format of AC 19 / AC 21 (`categories: none` for an empty list); JSON of AC 20; exit codes 0 / 2 / 3; data-error stderr `error: {FILE}:{line}: {reason}\n` with FILE as given.
- **Fixtures** (`tests/fixtures/ledger/`): `sample.csv` (9 rows `t001`…`t009`; 7 in 2026-03, one 2026-02-27 groceries -99.99, one 2026-04-01) must reproduce the ILS figures of AC 9 and the USD figures of AC 10/20. Because conversion is linear, the USD figures follow from the ILS ones divided by 3.70 (e.g. 12000/3.70 → 3243.24; 12925/3.70 → 3493.24; -3025.50/3.70 → -817.70; 9899.50/3.70 → 2675.54) whatever the row currencies, provided per-row amounts convert to the stated ILS totals; freelance must be a 250.00 USD row (= 925.00 ILS) per spec §7.

## 6. Key Technical Decisions

- **`decimal.Decimal` end to end; round once.** Conversion and summing use exact/full-precision Decimal (default context precision 28 is ample for ledger magnitudes); each figure is quantized independently, so they need not add up (AC 11). Alternative — round per row — rejected by the spec.
- **Amount validation.** A non-decimal or non-finite amount (NaN, Infinity) gives "is not a number"; a finite amount with more than two fractional digits gives "has more than 2 decimal places"; the parsed value keeps the text's scale (`12000.00` stays `Decimal("12000.00")`). Exponent notation is accepted only if it passes those same rules (simplest reading, A3).
- **Physical line numbers** come from counting input lines as consumed, not from csv row indexes, so blank lines and quoted fields with embedded newlines still map to the right line (the line where the row starts).
- **`python -m ledger` via `__main__.py`**, no console script — keeps `pyproject.toml` unchanged (spec: only `CHANGELOG.md` may change).
- **argparse for usage errors** (it already exits 2 with stderr output); semantic checks (`--month` shape/range, `--top ≥ 1`, unopenable FILE) are mapped to exit 2 the same way. `--base` uses `choices=` for ILS/USD/EUR.
- **Three sequential PRs**, one per layer, as the spec's delivery shape prescribes; each adds its own `CHANGELOG.md` line (gate PLAY-G4).

## 7. Risks & Constraints

- **Repository gates every PR is held to:** CI `test` job (`.github/workflows/ci.yml`: `pip install -e ".[test]"` then `pytest`, Python 3.12, 5-min timeout); `.factory/testing.md` declares `pytest` as the only (production-path) layer — tests must import `ledger` through the installed package, no `conftest.py`/`sys.path` hacks; repo-gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rules 1–4 (code in `src/`, tests in `tests/`, files < 200 KB, a `CHANGELOG.md` line under `## Unreleased` — PLAY-G4). No linter/formatter exists. `requires-python = ">=3.10"`: code must not use 3.11+-only syntax.
- **CHANGELOG.md is the one shared file** across the three PRs; they are strictly sequential, each appends its own line (no concurrent edit).
- **RK1 — fixture arithmetic:** a sample whose rows don't reproduce AC 9/10/20 exactly makes t2/t3 unpassable. Mitigation: t1 owns the fixture and its AC; t2/t3 consume it unchanged, and t1's tests assert the row data while t2 asserts the figures.
- **RK2 — rounding/precision drift:** float leakage or premature rounding. Mitigation: AC 11/12 tests in t2; JSON emits strings.
- **Editable install & `-m` (AC 25):** CI does a fresh `pip install -e`, so `python -m ledger` resolves through the installed `src/` layout; a developer with an older editable install may need to reinstall locally. No `sys.path` manipulation allowed.
- **Scale/security:** single-user local file, linear time, whole list in memory (acceptable for personal ledgers); no network, no secrets, no shell. Error messages echo field text from the user's own file only.

## 8. Assumptions

Spec assumptions A1–A3 carry over unchanged. Engineering assumptions added here (none blocking):

- **E1 — Field-count reason uses the header's field count** (`expected {header_len} fields, got {n}`), including extra non-required columns; AC 5's "6" is the instance for a six-column header. *Risk:* low.
- **E2 — Check order within a row** follows the AC 5 list order (field count first, then date, amount, currency, category, id, duplicate id); the first failing check gives the reason. *Risk:* low — only visible for rows with several faults.
- **E3 — Missing header vs. blank-only file:** a file with no non-blank line (zero bytes, or only blank lines) yields `LedgerError(1, "missing header")`. *Risk:* low.
- **E4 — Month validation is shared semantics:** the CLI rejects a bad `--month` with exit 2 using the same `YYYY-MM`, 01–12 rule as `monthly_report`'s `ValueError`. *Risk:* none.
- **E5 — A file that cannot be decoded as UTF-8** is treated as a usage error (exit 2, like an unopenable file), since it carries no line-level reason. *Risk:* low; the spec is silent.
