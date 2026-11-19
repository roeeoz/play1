# High-Level Design — SCRUM-30: Monthly expense report from a CSV ledger

## 1. System Overview

- **What:** a new stdlib-only package `ledger` in play1 (`src/ledger/`) that parses a UTF-8 CSV ledger into immutable `Transaction`s, totals one calendar month by category in a base currency (ILS/USD/EUR, fixed rates, `Decimal` end to end), and exposes it as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`.
- **Problem:** a bad row must never yield a wrong total; it must be pointed at by physical line with an exact reason (spec FR5).
- **Responsibilities:** parse + validate (R1, R2) → report + convert + round (R3, R4) → CLI formatting and exit codes (R5).
- **Grounding (play1 `main`, checked in this checkout):** `pyproject.toml` discovers packages with `[tool.setuptools.packages.find] where = ["src"]`, so `src/ledger/` is picked up with no manifest edit; `requires-python = ">=3.10"`; pytest `testpaths = ["tests"]`. Existing packages `src/testbed_utils/`, `src/guestbook/` are untouched. No `src/ledger/`, no `tests/test_ledger_*.py`, no `tests/fixtures/ledger/` exist today.

## 2. Architecture Overview

Three layers inside one package, each depending only on the one below:

| Layer | Module(s) | Owner ticket |
| --- | --- | --- |
| Model + parser | `src/ledger/__init__.py`, `src/ledger/parser.py` | t1 |
| Report | `src/ledger/report.py` (+ re-export in `__init__.py`, handoff from t1) | t2 |
| Command line | `src/ledger/cli.py`, `src/ledger/__main__.py` | t3 |

- **No external dependencies:** `csv`, `decimal`, `datetime`, `re`, `argparse`, `json`, `dataclasses` only; `pyproject.toml` is not touched (no `[project.scripts]` entry is needed for `python -m ledger`).
- **Boundaries:** the parser knows nothing of months or currencies' rates; the report takes `Transaction`s and never raises `LedgerError`; the CLI is the only place that touches `sys.argv`, stdout/stderr and exit codes.
- **Existing pattern followed:** `src/testbed_utils/numsummary.py` (argparse + `print(..., file=sys.stderr)` + `sys.exit`) for the CLI shape; unlike it, there is no cwd path restriction (not in the spec) and tests use `subprocess` (FR17), not in-process `main()`.

## 3. Data Flow Design

All synchronous, single process, read-only:

1. CLI parses argv (argparse). Usage problems → stderr message, exit 2, stdout empty.
2. CLI calls `parse_csv(FILE)` → opens with `encoding="utf-8-sig", newline=""` → `parse_lines` streams rows through `csv.reader`, tracking the physical start line of each record, validating each row in the fixed order of §6, and returns `list[Transaction]` in file order or raises `LedgerError(line, reason)` at the first bad row.
   - `OSError` (missing file, directory, permission) and `UnicodeDecodeError` (not UTF-8; may surface mid-iteration) → exit 2.
   - `LedgerError` → stderr `error: {FILE}:{line}: {reason}\n` exactly, exit 3.
3. CLI calls `monthly_report(transactions, month, base, top)` → filters by month, converts each amount at full precision, sums exactly, quantizes each figure once, sorts categories, truncates to top N.
4. CLI renders the report as the exact text format (FR14) or `json.dumps(report.to_dict())` (FR15), writes to stdout only after steps 2–3 succeed, exit 0.

## 4. Component Breakdown

| Component | Responsibility | Inputs → Outputs | Repo |
| --- | --- | --- | --- |
| Model + parser (t1) | `Transaction` (frozen dataclass), `LedgerError(line, reason)`, `parse_lines`, `parse_csv`; header matching, row tolerance, validation with exact reasons | iterable of lines / path → `list[Transaction]` or `LedgerError` | play1 |
| Report (t2) | `RATES`, `CategoryTotal`, report value with `to_dict()`, `monthly_report`; month filter, conversion, half-even rounding, ordering, top-N, caller `ValueError`s | `list[Transaction]`, month, base, top, rates → report | play1 |
| CLI (t3) | `report` subcommand, argument validation, text/JSON rendering, exit codes 0/2/3, `python -m ledger` entry | argv + FILE → stdout/stderr + exit code | play1 |
| Fixtures | `tests/fixtures/ledger/sample.csv`, `bom_blank.csv`, `empty.csv` (t1); `bad_amount.csv` (t3) | — | play1 |

## 5. Interface Contracts

The public surface is fixed by the spec (FR1–FR16) and is the contract between tickets; it is not restated beyond what the tickets need:

- **t1 → t2:** `from ledger import Transaction, LedgerError, parse_csv, parse_lines`. `Transaction` fields `id, date, amount, currency, category, memo`; `LedgerError` exposes `.line` and `.reason`, `str()` = `line {line}: {reason}`.
- **t2 → t3:** `from ledger import monthly_report, RATES, CategoryTotal`; report attributes `month, base, count, income, expense, net, categories` and `to_dict()` with key order `month, base, count, income, expense, net, categories` and category dicts `name, total, count` (amounts as two-place strings).
- **CLI contract (external):** argv per FR13; stdout text per FR14 (13 lines for the sample, `categories: none` for an empty month); JSON per FR15 (one object, followed by a newline); exit 0/2/3 per FR16; data-error stderr `error: {FILE}:{line}: {reason}\n` with FILE exactly as typed.
- No events, no network, no persisted state.

## 6. Key Technical Decisions

Settled here because the stdlib behaves in ways the spec does not mention (verified by running Python 3.13 in this workspace; the cases hold on 3.10–3.12 too, or the design avoids the version-dependent API):

- **Amount syntax is checked by an ASCII pattern before `Decimal()`.** `Decimal()` alone accepts `1_000`, Arabic-Indic digits (`'١٢'` → 12), surrounding spaces, `1.`, `.5`, `1e3`, `NaN`, `sNaN`, `Infinity`. Accepted: optional `+`/`-`, one or more ASCII digits, optionally `.` and one or more ASCII digits. Everything else → `amount '<text>' is not a number` (incl. `NaN`, `Infinity`, `1e3` per A3, `1_000`, `1.`, `.5`, non-ASCII digits, empty). A well-shaped amount with 3+ decimals → `amount '<text>' has more than 2 decimal places` (so `1.505`, `-2.505`, and also `1.500`). Value zero in any spelling (`0`, `-0.00`, `+0.0`) → `amount must not be zero`. The `Decimal` keeps the text's exponent (`12000.00` stays `Decimal("12000.00")`; a leading `+` is dropped by `Decimal`).
- **Date syntax by ASCII pattern `[0-9]{4}-[0-9]{2}-[0-9]{2}`**, then `datetime.date(y, m, d)` for the calendar check. Not `date.fromisoformat` alone: since 3.11 it accepts `20260301` and other ISO forms, so results would differ across supported versions. `\d` is not used (it matches full-width digits).
- **Physical line numbers:** the record's line is `csv.reader.line_num` before reading it + 1 (its first physical line), so blank lines count and a quoted multi-line memo reports its first line. The header is line 1.
- **Blank-line skipping:** a record is skipped when it is empty (`[]`) or a single whitespace-only field; a record like `,,,,,` is NOT blank and is validated (→ `empty id`).
- **Validation order per row (A2):** field count (`expected N fields, got M`, N = header field count, A5) → id → date → amount → currency → category → duplicate id. Memo is never invalid. Fields are trimmed before checks; header names trimmed and matched case-sensitively (A6); extra header columns ignored but still count toward N.
- **Header:** no record at all (zero bytes, BOM only, blank lines only — A7) → `LedgerError(1, "missing header")`; missing names → `LedgerError(1, "missing column(s): a, b")` in canonical order. Duplicate header names: the first occurrence wins (simplest reading; not specified).
- **Report arithmetic:** convert each in-month amount as `amount * rates[currency] / rates[base]` under a local decimal context with default precision (28) so a caller's global context cannot change results; sum exactly; quantize each figure once with `ROUND_HALF_EVEN` to `0.01`. A quantized negative zero (e.g. a converted `-0.0025`) is normalised to `0.00` so output never shows `-0.00`. Income = sum of positive converted amounts, expense = sum of negative ones, net = exact total quantized (not income + expense).
- **Report caller errors (`ValueError`):** month not matching ASCII `YYYY-MM` with month 01–12; base not a key of `rates`; `top` not `None` and < 1; an in-month transaction whose currency is not a key of a caller-supplied `rates` (`ValueError` naming the currency).
- **CLI:** argparse with a required `report` subcommand (no subcommand → exit 2; argparse returns `cmd=None` by default, so it must be made required or checked explicitly). `--month` validated at parse time (bad → exit 2), `--base` with `choices=["ILS","USD","EUR"]`, `--top` an integer ≥ 1. `OSError`/`UnicodeDecodeError` from reading FILE → exit 2 with `error: cannot read {FILE}: …` on stderr. Nothing is written to stdout before the report is complete. `--help` → stdout, exit 0 (argparse default).
- **CHANGELOG (A1, PLAY-G4):** exactly one story line under `## Unreleased`; t1 adds it, t2 and t3 revise that same line in place (never add a second) so every change set touches `CHANGELOG.md` while the story's net diff is one line.
- **Alternatives rejected:** `csv.DictReader` (loses field-count mismatch detail and line tracking is equivalent); floats anywhere (precision); `[project.scripts]` console entry (would modify `pyproject.toml`, out of scope).

## 7. Risks & Constraints

- **Gates every change set must pass:** `.factory/testing.md` / `.github/workflows/ci.yml` — `pip install -e ".[test]"` then `pytest` on Python 3.12 (no linter/formatter configured); `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` — source under `src/`, tests under `tests/`, no file > 200 KB, and a `CHANGELOG.md` `## Unreleased` touch (PLAY-G4). The existing suite must pass unchanged (Scenario 26).
- **Editable-install staleness (local only):** setuptools editable installs map top-level packages at install time; a developer with an older `pip install -e .` must reinstall before `import ledger` works. CI installs fresh, so the gate is unaffected. Tests must not add `sys.path` hacks or a `conftest.py` to work around it (FR17).
- **Scale:** the whole file is held as a `list[Transaction]` (the spec's return type); fine for personal/small-team ledgers. No streaming report is required.
- **Security:** read-only; FILE is opened as given (no shell, no eval); output is plain text/JSON. No path restriction is specified, so none is added.
- **Determinism:** output depends only on file + arguments (fixed rates, explicit rounding, local decimal context, stable sort with name tie-break).
- **RK1/RK2 (spec):** wrong totals from bad rows — mitigated by fail-fast validation; rounding drift — mitigated by single half-even rounding after summing (Scenario 11).

## 8. Assumptions

- Spec assumptions A1–A8 are adopted as written.
- **Sample fixture (A8) content**, authored in t1 and constrained by Scenarios 1, 9, 10, 16, 20: nine rows `t001`…`t009`; March 2026: salary `12000.00 ILS`, rent `-1500.00 ILS`, freelance `250.00 USD` (= 925.00 ILS), groceries two ILS rows summing `-760.50`, software `-120.00 USD` (= -444.00 ILS), travel `-321.00 ILS`; `2026-02-27` groceries `-99.99 ILS`; one `2026-04-01` row. Checked: in USD this gives income 3493.24, expense -817.70, net 2675.54, salary 3243.24, freelance 250.00 (matches Scenario 20). The implementer may choose different rows if every scenario number still holds.
- Not specified and decided here (low risk): duplicate header names → first wins; amounts like `1.` / `.5` / `1.500` handled as in §6; unreadable-file stderr wording is free-form (spec only requires "a message").
- Not verified: the epic PRD/backlog named by the spec were unavailable to intake and to this turn; the story is designed as published.
