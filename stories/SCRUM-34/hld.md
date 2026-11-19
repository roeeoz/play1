# High-Level Design — Monthly expense report from a CSV ledger (SCRUM-34)

## 1. System Overview

- **What:** a new stdlib-only package `ledger` in `src/ledger/` of play1. It parses a UTF-8 CSV ledger into validated `Transaction`s, builds a one-month report in a base currency (ILS/USD/EUR at fixed rates, exact `Decimal` arithmetic), and exposes it as `python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`.
- **Problem:** quick, deterministic monthly totals from the terminal. A malformed row must be named by its physical line, and no figure may be printed.
- **Responsibilities:** parsing and validation (t1), aggregation, conversion and rounding (t2), CLI, output formats and exit codes (t3).
- **Verified against the code:** `pyproject.toml` discovers packages under `src/` (`[tool.setuptools.packages.find] where = ["src"]`) and sets pytest `testpaths = ["tests"]`. CI (`.github/workflows/ci.yml`) runs `pip install -e ".[test]"` and `pytest` on Python 3.12. `requires-python = ">=3.10"`. There is no `conftest.py` and there are no `sys.path` hacks. None of `src/ledger/`, `tests/test_ledger_*.py` or `tests/fixtures/ledger/` exists. The spec's preconditions hold, so `pyproject.toml` needs no edit and `python -m ledger` needs no console-script entry.

## 2. Architecture Overview

Three layers, with one-way imports `cli → report → parser`:

| Module (new) | Owns | Ticket |
|---|---|---|
| `src/ledger/__init__.py` | the public re-exports (`Transaction`, `LedgerError`, `parse_lines`, `parse_csv`; t2 adds `monthly_report`, `Report`, `CategoryTotal`, `RATES`) | t1 creates it, t2 extends it |
| `src/ledger/parser.py` | `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` | t1 |
| `src/ledger/report.py` | `RATES`, `CategoryTotal`, `Report` (+ `to_dict`), `monthly_report` | t2 |
| `src/ledger/cli.py` + `src/ledger/__main__.py` | argparse front end, text/JSON rendering, exit codes | t3 |

- **External dependencies:** none. The package uses only the standard library (`csv`, `decimal`, `datetime`, `re`, `dataclasses`, `argparse`, `json`, `sys`). It makes no network access and reads no config or environment.
- **Existing code:** nothing existing is imported or changed. The existing CLIs (`src/testbed_utils/numsummary.py`, tested in-process by `tests/test_num_summary_cli.py`) are only a style reference. Per spec AC 25, the ledger CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", ...]` instead.
- **Repo gate:** the gate in `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` requires Python under `src/`, tests under `tests/`, files under 200 KB and a `CHANGELOG.md` line under `## Unreleased` (`PLAY-G4`, a blocker on every PR). See decision D8 for how three PRs share the single line the spec allows.

## 3. Data Flow Design

All processing is synchronous and in-process. There are no events.

1. The CLI parses argv. On a usage error, argparse prints to stderr and exits 2 (stdout stays empty).
2. `parse_csv(FILE)` opens the file with `encoding="utf-8-sig", newline=""` and delegates to `parse_lines`. That reads the header, then validates row by row and stops at the first `LedgerError`.
3. `monthly_report(transactions, month, base, top)` filters to the month, converts each amount at full precision, sums exactly, rounds each figure once, orders the categories and slices to the top N.
4. The CLI renders text or JSON into one string and writes it to stdout only once everything above has succeeded. Exit codes: 0 on success, 3 on a `LedgerError` with `error: {FILE}:{line}: {reason}` on stderr, 2 on an unopenable or undecodable FILE.

## 4. Component Breakdown

- **Parser** (`src/ledger/parser.py`, play1, t1). In: an iterable of text lines or a path. Out: `list[Transaction]` in file order, or `LedgerError(line, reason)`.
- **Report** (`src/ledger/report.py`, play1, t2). In: transactions, `month`, `base`, `top` and `rates`. Out: a frozen `Report`, or `ValueError` for caller errors.
- **CLI** (`src/ledger/cli.py`, `src/ledger/__main__.py`, play1, t3). In: argv. Out: stdout/stderr text and exit codes 0, 2 or 3.
- **Fixtures** (`tests/fixtures/ledger/`). t1 owns `sample.csv`, `bom_blank.csv` and `empty.csv`. t3 owns `bad_amount.csv`.
- **Tests:** `tests/test_ledger_parser.py` (t1), `tests/test_ledger_report.py` (t2) and `tests/test_ledger_cli.py` (t3).

**The sample fixture's content is fixed here**, because t2 and t3 assert figures from it. It holds the header `id,date,amount,currency,category,memo` and nine rows, in this order:

| id | date | amount | currency | category |
|---|---|---|---|---|
| t001 | 2026-02-27 | -99.99 | ILS | groceries |
| t002 | 2026-03-01 | 12000.00 | ILS | salary |
| t003 | 2026-03-02 | -1500.00 | ILS | rent |
| t004 | 2026-03-05 | -400.50 | ILS | groceries |
| t005 | 2026-03-09 | 250.00 | USD | freelance |
| t006 | 2026-03-12 | -120.00 | USD | software |
| t007 | 2026-03-18 | -360.00 | ILS | groceries |
| t008 | 2026-03-22 | -80.25 | EUR | travel |
| t009 | 2026-04-01 | -50.00 | ILS | rent |

- Memos are free text, and at least one is empty.
- These rows give every figure in spec AC 9, 10, 16 and 20. In ILS: income 12925.00, expense -3025.50, net 9899.50. In USD: income 3493.24, expense -817.70, net 2675.54, salary 3243.24, freelance 250.00. February: groceries -99.99 (1).

## 5. Interface Contracts

The public Python surface is fixed by the spec (§3, AC 1–18): `Transaction`, `LedgerError(line, reason)` with `str()` == `line {line}: {reason}`, `parse_lines`, `parse_csv`, `RATES`, `CategoryTotal(name, total, count)`, `Report` (`month, base, count, income, expense, net, categories`) with `to_dict()`, and `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`. All of them are importable from `ledger`.

The spec leaves the cases below open. They are settled here:

**Parser**
- **Header:** the header is the first non-blank row; leading blank lines are skipped but still counted. A file with no non-blank row raises `missing header` at line 1. A leading U+FEFF is stripped in `parse_lines` too, so it matches `parse_csv`. Header names are stripped and matched case-sensitively.
- **Duplicate required column:** a required column named twice in the header raises `duplicate column 'amount'` at the header's line.
- **Missing columns:** reported in canonical order and joined with `, `.
- **Line numbers:** a row's line is the physical line where its record **starts**. This matters for a quoted field that spans lines, since `csv.reader.line_num` reports the end line.
- **Blank rows:** a row is blank when it has no fields, or one field that is empty after stripping. `,,,,,` is not blank: it fails validation (`empty id`).
- **Validation order within a row:** field count (`expected {header field count} fields, got {n}`, where the header count includes extra columns), then `empty id`, `duplicate id`, date, amount, currency, `empty category`. The first failure is the one reported.
- **Amount:** accepted only if it matches ASCII `[+-]?[0-9]+(\.[0-9]+)?`. Anything else is `amount '{text}' is not a number`. That covers `NaN`, `Infinity`, `1e2`, `1,000`, `1_000`, `.5`, `5.`, non-ASCII digits and the empty string; `Decimal()` itself accepts most of these, as verified on Python 3.13.
  - More than two fractional digits *as written* (including `1.500`) is `has more than 2 decimal places`.
  - A value equal to zero (`0`, `-0`, `0.00`) is `amount must not be zero`.
  - The stored value is `Decimal(text)` unchanged, so `+5` becomes `Decimal("5")`.
- **Date:** must match ASCII `[0-9]{4}-[0-9]{2}-[0-9]{2}`, otherwise it is `is not YYYY-MM-DD`; `fromisoformat` on 3.11+ would accept `20260301`, so the pattern is checked first. If constructing the date then fails, it is `is not a calendar date`.
- **Currency:** an exact match of `ILS`, `USD` or `EUR`. An empty value gives `unknown currency ''`.
- **Category, memo and id:** kept exactly as written after stripping; grouping is case-sensitive.

**Report**
- **`month`:** must match ASCII `[0-9]{4}-(0[1-9]|1[0-2])`, otherwise `ValueError`.
- **`base`:** must be a key of `rates`, otherwise `ValueError`.
- **`top`:** `None` or an int ≥ 1, otherwise `ValueError`.
- **Missing rate:** a transaction in the month whose currency has no entry in `rates` raises `ValueError` naming that currency.
- **Arithmetic:** done inside a local decimal context (precision 60, `ROUND_HALF_EVEN`) that does not depend on the caller's thread context. Each figure is quantized to `0.01` once.
- **Negative zero:** a figure that rounds to zero is reported as `0.00`, never `-0.00`.
- **Category order:** by the absolute value of the *rounded* total, descending, then by name ascending. `categories` is a list.
- **`to_dict()`:** key order `month, base, count, income, expense, net, categories`; each category dict is `{name, total, count}`; amounts are two-place strings.

**CLI** (prog `python -m ledger`, subcommand `report`)
- **Usage errors:** handled by argparse and exit 2: a missing subcommand, `--month` failing the pattern above, `--base` outside `ILS|USD|EUR`, and `--top` not an int ≥ 1.
- **Unreadable FILE:** a FILE that cannot be opened (`OSError`: missing, a directory, permission) or is not valid UTF-8 exits 2 with an argparse-style `error:` message on stderr. Nothing goes to stdout.
- **Data errors:** `LedgerError` exits 3 with stderr exactly `error: {FILE}:{line}: {reason}\n`, where FILE is the path as given.
- **Text output:** spec AC 19 and 21. The last line is `categories: none` when the report has no categories, and the output ends with a newline.
- **JSON output:** `json.dumps(report.to_dict())` on one line plus a newline. The default `ensure_ascii` keeps the output ASCII-only.
- **Help:** `report --help` exits 0 and documents `--month`.

## 6. Key Technical Decisions

- **D1 — `csv.reader`, not `DictReader`:** we need the raw field count (for field-count errors) and physical line tracking.
- **D2 — Validate amount text with a regex before `Decimal()`:** `Decimal` accepts exponents, `NaN`/`Infinity`, underscores, Unicode digits, `.5` and `5.` (all verified), and the spec rejects them.
- **D3 — Convert, then sum, then round once:** exact sums use a fixed local context of 60 digits, so rounding does not depend on global state. The alternative, rounding each conversion, breaks spec AC 11.
- **D4 — Errors as values at the boundary:** the library raises (`LedgerError` for data, `ValueError` for callers). Only the CLI maps errors to exit codes, and it buffers all output, so stdout stays empty on any error.
- **D5 — argparse does all usage validation** through `type=`/`choices=`/`required=`. That gives exit 2 and the standard message format for free.
- **D6 — Subprocess CLI tests (spec AC 25):** these exercise the real installed `-m` entry point, unlike the in-process `main()` style of `tests/test_num_summary_cli.py`.
- **D7 — Fixed sample content (§4):** t2 and t3 assert numbers that t1's fixture must produce.
- **D8 — One CHANGELOG line across three PRs:** the repo gate (`PLAY-G4`) blocks any PR that does not touch `CHANGELOG.md`, while spec FR16/AC 27 allows the story exactly one added line.
  - t1 adds the line under `## Unreleased`.
  - t2 and t3 each *rewrite that same line in place*, extending its description, so each PR still touches `CHANGELOG.md` and the story's net change stays one added line.

## 7. Risks & Constraints

- **Python versions:** the code must run on 3.10 (`requires-python`) and 3.12 (CI). Use no 3.11+-only APIs; dates are validated by pattern, not by `fromisoformat` leniency.
- **Huge amounts:** amounts with more than about 55 significant digits would overflow the precision-60 context on quantize (`InvalidOperation`). This is out of scope for personal ledgers and accepted as a limit.
- **Text output and stdout encoding:** non-ASCII category names in text mode rely on the stdout encoding (UTF-8 on CI). JSON output is ASCII-only.
- **Scale:** the parser holds the whole month's transactions in memory as a list, which is fine for personal ledgers. It uses no network, no config and no environment variables.
- **Gate:** every PR must touch `CHANGELOG.md` (D8), keep Python under `src/` and tests under `tests/`, and add no shell scripts.

## 8. Assumptions

- **A1 — The CHANGELOG mechanism (D8).** Risk if wrong: if the platform merges the three work items as one PR, the line is simply written once in its final form, which still satisfies AC 27.
- **A2 — The cases §5 settles beyond the spec** are unobservable by the spec's scenarios and chosen to be strict and deterministic: the duplicate-column error, the starting-line rule, the extra amount rejections, the validation order, negative-zero normalisation, and an undecodable file exiting 2. Risk: low. Changing any of them later is a local edit to one module.
