# HLD — SCRUM-31 Monthly expense report from a CSV ledger

## 1. System Overview

- **What:** a new stdlib-only package `src/ledger/` that parses a UTF-8 CSV ledger into validated transactions, builds a monthly per-category report in ILS/USD/EUR at fixed rates, and exposes it as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`.
- **Problem:** no deterministic terminal summary of a ledger; a malformed row must stop the run with its line and reason instead of producing a wrong total.
- **Responsibilities:** parse + validate (spec FR1/FR2), aggregate + convert + round once (FR3–FR5), CLI with exit codes 0/2/3 (FR6).

## 2. Architecture Overview

Three layers inside one new package, each owned by one work item, built in order t1 → t2 → t3:

| Layer | Module (new) | Owner |
|---|---|---|
| Model + parser (`Transaction`, `LedgerError`, `parse_lines`, `parse_csv`) | `src/ledger/__init__.py`, `src/ledger/parser.py` | t1 |
| Report (`RATES`, `CategoryTotal`, report object with `to_dict()`, `monthly_report`) | `src/ledger/report.py` | t2 |
| CLI (`report` subcommand, rendering, exit codes) | `src/ledger/cli.py`, `src/ledger/__main__.py` | t3 |

- Dependencies point one way: cli → report → parser. The report never reads files; the parser never knows about months or currencies' rates (only the allowed currency set ILS/USD/EUR).
- Existing system fit (verified in the checkout): `pyproject.toml` has `[tool.setuptools.packages.find] where = ["src"]`, so `src/ledger/` is installed by the existing `pip install -e ".[test]"` with no manifest edit; `testpaths = ["tests"]`; `requires-python = ">=3.10"` while CI (`.github/workflows/ci.yml`, job `test`) runs 3.12 — code must stay 3.10-compatible. Sibling packages `src/testbed_utils/` and `src/guestbook/` are untouched. The existing CLIs (`src/testbed_utils/numsummary.py`, `hello.py`) use `argparse` and are registered as console scripts; this story deliberately uses `python -m ledger` via `__main__.py` instead (spec criterion 25), so `pyproject.toml` is not edited.
- No external dependencies, no network, no persistent state.

## 3. Data Flow Design

All synchronous, single process:

1. `python -m ledger report FILE ...` → `src/ledger/__main__.py` → CLI parses argv (argparse; usage errors exit 2).
2. CLI calls `parse_csv(FILE)` → opens `utf-8-sig`, `newline=""` → `parse_lines` → `csv.reader` → header resolution → per-row validation → `list[Transaction]` in file order, or `LedgerError(line, reason)` on the first bad row.
3. CLI calls `monthly_report(transactions, month, base, RATES, top)` → filter by `date` year-month → convert each amount `amount × rates[cur] ÷ rates[base]` exactly → sum per category / income / expense / net → quantize each figure once to `0.01` `ROUND_HALF_EVEN` → sort categories → truncate to `top`.
4. CLI renders text (7 header lines + indented category lines, or `categories: none`) or `json.dumps(report.to_dict())`, one trailing newline, exit 0. `LedgerError` → stderr `error: {FILE}:{line}: {reason}`, exit 3. Open/decode failure → stderr message, exit 2. Nothing on stdout on any error (output is rendered fully before writing).

## 4. Component Breakdown

**Parser (t1, repo play1)** — in: an iterable of text lines or a path; out: `list[Transaction]` or `LedgerError`. Settles every row-level case below (§6, D1–D6). Fixtures `tests/fixtures/ledger/sample.csv`, `bom_blank.csv`, `empty.csv`.

**Report (t2, repo play1)** — in: transactions, month, base, rates, top; out: an immutable report (`month`, `base`, `count`, `income`, `expense`, `net`, `categories`) with `to_dict()`; `ValueError` on bad arguments. Settles D7–D11.

**CLI (t3, repo play1)** — in: argv; out: stdout text/JSON, stderr diagnostics, exit 0/2/3. Fixture `tests/fixtures/ledger/bad_amount.csv`. Settles D12–D14.

**Sample fixture contract** (t1 creates it, t2/t3 assert against it): header + nine rows `t001`…`t009`; seven dated in 2026-03, one 2026-02-27 (groceries, −99.99 ILS), one 2026-04-01. Its March rows must yield, in ILS: salary 12000.00 (1, the row's amount text is `12000.00` ILS), rent −1500.00 (1), freelance 925.00 (1, written as `250.00` USD so the USD report shows exactly 250.00), groceries −760.50 (2), software −444.00 (1), travel −321.00 (1); so in USD income 3493.24, expense −817.70, net 2675.54, salary 3243.24. (A currency mix is encouraged — e.g. software −120.00 USD, travel −80.25 EUR — as long as the ILS totals above hold.)

## 5. Interface Contracts

All in-package Python interfaces; no cross-repo contract. Public names re-exported from `ledger` (`src/ledger/__init__.py`): `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` (t1); `RATES`, `CategoryTotal`, `monthly_report` (t2).

- `Transaction` — frozen dataclass `(id: str, date: datetime.date, amount: Decimal, currency: str, category: str, memo: str)`.
- `LedgerError(line, reason)` — exception with `.line: int`, `.reason: str`, `str()` = `line {line}: {reason}`.
- `monthly_report(transactions, month, base="ILS", rates=RATES, top=None)` → report; `CategoryTotal(name, total, count)`; `report.to_dict()` → `{"month","base","count","income","expense","net","categories":[{"name","total","count"}]}` with every amount a string with exactly two places, keys in that order.
- CLI: `python -m ledger report FILE --month YYYY-MM [--base {ILS,USD,EUR}] [--top N] [--json]`; exits 0 / 2 / 3; stderr on data error exactly `error: {FILE}:{line}: {reason}\n`.

## 6. Key Technical Decisions

Cases the spec leaves open, settled here after running the stdlib (Python 3.13 locally; behaviour identical on 3.10–3.12 for these calls). Each is carried as an acceptance criterion by its owning ticket.

**Parser (t1)**
- **D1 Amount grammar.** `Decimal()` alone is too lax: it accepts `1_000`, `1e2`, ` 5`, Arabic-Indic digits `١٢`, `.5`, `5.`, `sNaN`. The amount (after trimming) must match ASCII `[+-]?[0-9]+(\.[0-9]+)?`; anything else, incl. `NaN`/`Infinity`/`1e2`/`1_000`/`.5`/`5.` → `amount '<text>' is not a number`. Then more than two digits after the point → `amount '<text>' has more than 2 decimal places` (textual: `1.500` is refused). Then a value equal to zero (`0`, `-0.00`) → `amount must not be zero`. The `Decimal` keeps the text's exponent (`12000.00` stays `Decimal("12000.00")`).
- **D2 Date grammar.** `date.fromisoformat` accepts `20260301` on 3.11+, so the date must first match ASCII `[0-9]{4}-[0-9]{2}-[0-9]{2}` (else `is not YYYY-MM-DD`), then be a real date (else `is not a calendar date`).
- **D3 Check order per row:** field count, then id, date, amount, currency, category (memo is free text), then duplicate id. So a row with several faults reports the first in this order.
- **D4 Lines and blanks.** `csv.reader.line_num` is the line where a record *ends*; a record's physical line is the line after the previous record ended (a quoted memo spanning lines reports its first line). A blank record is `[]` or a single whitespace-only field; it is skipped but counts. The header is the first non-blank record; no non-blank record → `LedgerError(1, "missing header")`. A leading BOM (`\ufeff`) is stripped from the first line in `parse_lines` too (`csv.reader` over `io.StringIO` keeps it — verified), so both entry points behave the same.
- **D5 Header.** Header names are trimmed and matched case-sensitively; extra columns are ignored but count toward the expected field count (`expected {n} fields, got {m}` uses the header's count). A required name appearing twice → `LedgerError(header_line, "duplicate column '<name>'")` (refusing beats silently picking one column — the spec's "never a wrong total").
- **D6 Decode errors.** `parse_csv` lets `UnicodeDecodeError` / `OSError` propagate unchanged (they are not row errors); the CLI maps them (D13).

**Report (t2)**
- **D7 Precision context.** Conversion and summing run in a local decimal context (precision 28, `ROUND_HALF_EVEN`) so a caller's altered global context cannot change results; quantize once per figure.
- **D8 Negative zero.** A figure that quantizes to `-0.00` (e.g. −0.01 ILS in EUR) is reported as `0.00`.
- **D9 Sorting** uses the rounded totals' absolute value descending, ties by name ascending (Python string order, case-sensitive; `Food` and `food` are distinct categories). Income = sum of converted positive amounts, expense = sum of converted negative amounts, net = sum of all; each rounded independently.
- **D10 Arguments.** `month` must match ASCII `[0-9]{4}-(0[1-9]|1[0-2])` (non-str → `ValueError`); `base` must be a key of `rates`; `top` must be `None` or an `int` ≥ 1 (bool and float refused). A transaction in the requested month whose currency is not a key of `rates` → `ValueError` naming the currency. Rate values are used as given (callers pass Decimals).
- **D11 Immutability.** Report and `CategoryTotal` are frozen; `categories` is a tuple or list — tests compare by content.

**CLI (t3)**
- **D12 argparse.** `prog="python -m ledger"`; subcommand required (none → exit 2); `--month` validated by an argparse `type` reusing the report's month rule; `--base` `choices` ILS/USD/EUR default ILS; `--top` an int ≥ 1 type. argparse's own messages on stderr (spec A3).
- **D13 File errors.** `OSError` (missing, directory, permission) and `UnicodeDecodeError` on FILE → exit 2, a one-line `python -m ledger report: error: cannot read '<FILE>': <detail>` style message on stderr, nothing on stdout.
- **D14 Output.** Whole output built before writing; each line ends `\n`; JSON is `json.dumps(report.to_dict())` (default separators) + `\n`; `--top` truncates the category lines in text as in JSON. Exit 3 on `LedgerError`.

**Alternatives rejected:** console script entry in `pyproject.toml` (edits an existing file, spec forbids); `float` anywhere (precision); per-row rounding (criterion 11).

## 7. Risks & Constraints

- **PR gate PLAY-G4:** every PR must add a line under `## Unreleased` in `CHANGELOG.md`. Tickets run sequentially, so each appends its own line after the previous one's (ownership hands off t1 → t2 → t3); a rebase conflict on that file is trivial.
- **Test gate (`.factory/testing.md`):** tests import `ledger` only through the editable install — no `conftest.py`, no `sys.path` edits; CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", ...]` (criterion 25), with `cwd` the repo root or absolute fixture paths.
- **Python version:** `requires-python >= 3.10`; avoid 3.11+-only APIs (e.g. no reliance on `fromisoformat`'s extended formats, which D2 sidesteps anyway).
- **Scale:** the whole file is read into memory as a list; acceptable for personal ledgers (spec's user). No performance target is specified.
- **Security:** reads one local file the user names; no network, no eval, no writes.
- **Fixture coupling:** t2/t3 expected numbers depend on t1's `sample.csv`; §4 fixes its contract.

## 8. Assumptions

- **A1–A3** as in the spec (CHANGELOG line per PR; size; argparse messages).
- **A4** D1–D14 above are design rulings where the spec is silent ("simplest reading", ruled by the developer); none contradicts a criterion. Risk: low — a reviewer preferring a different ruling changes one validation branch.
- **A5** The duplicate-column reason text `duplicate column '<name>'` is new wording not in the spec. Risk: low.
