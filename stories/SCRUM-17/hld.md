# HLD — SCRUM-17: Monthly expense report from a CSV ledger

## 1. System overview
- **What:** a stdlib-only Python package `ledger` in play1 (`src/ledger/`). It parses and validates a CSV ledger and builds a deterministic monthly report in a base currency (ILS, USD or EUR). It is available as a library (`parse_csv`, `parse_lines`, `monthly_report`) and as a command line (`python -m ledger report FILE --month YYYY-MM [--base] [--top N] [--json]`).
- **Problem:** quick, trustworthy monthly totals from the terminal. A malformed row fails loudly with its line number and a reason, instead of producing a wrong total.
- **Responsibilities:**
  - parse and validate rows (R1, R2);
  - aggregate one month with exact `Decimal` arithmetic (R3, R4);
  - provide text/JSON output with exit codes 0, 2 and 3 (R5).

## 2. Architecture overview
The package has three layers inside one repository (play1, base `main`). Each layer depends only on the layers below it.

| Layer | Module (implementer may refine names) | Ticket |
|---|---|---|
| Model + parser | `src/ledger/__init__.py`, `src/ledger/parser.py` (or `model.py` + `parser.py`) | t1 |
| Report | `src/ledger/report.py` | t2 |
| CLI | `src/ledger/cli.py`, `src/ledger/__main__.py` | t3 |

- No external dependencies: stdlib only (`csv`, `decimal`, `datetime`, `re`, `dataclasses`, `argparse`, `json`). `pyproject.toml` is unchanged; setuptools finds the new package under `src/` automatically.
- `src/ledger/__init__.py` is created by t1. t2 takes it over to re-export the report API, and t3 does not change it.
- **Composition root:** `python -m ledger` goes to `__main__.py`, which calls the CLI. The CLI calls `parse_csv`, then `monthly_report`, then a formatter. This story owns that terminal wiring (AC19–25), and t3 delivers it.

## 3. Data flow
Everything is synchronous and in-process:
1. FILE path → `parse_csv` (opens with `utf-8-sig`, `newline=""`) → `parse_lines`.
2. `csv.reader` → header resolution (by name, trimmed) → per-row validation → `list[Transaction]` in file order. Parsing stops at the first `LedgerError(line, reason)`.
3. `monthly_report(transactions, month, base, top, rates)`:
   - filter by month;
   - convert each amount as `amount × rates[cur] ÷ rates[base]` at full precision;
   - sum exactly per figure and per category;
   - quantize each figure once to `0.01` with `ROUND_HALF_EVEN`;
   - normalise `-0.00` to `0.00`;
   - order categories by (−|rounded total|, name), then apply top-N.
4. The CLI prints either the text lines or `json.dumps(report.to_dict())`.
   - On `LedgerError` it prints `error: {FILE}:{line}: {reason}` to stderr and exits 3.
   - On a usage problem (argparse, or a file that cannot be opened or decoded) it exits 2.
   - Nothing is ever written to stdout on an error path.

## 4. Component breakdown

| Component | Responsibility | In → Out | Repo |
|---|---|---|---|
| Transaction / LedgerError | Immutable row value; data error carrying `line` and `reason`, `str()` = `line {line}: {reason}` | — | play1 |
| Parser | Header resolution, row validation, BOM and blank-line handling, physical line numbers | lines / path → list of transactions or LedgerError | play1 |
| Report | Month filter, conversion, exact sums, single rounding, ordering, top-N, `to_dict()`; ValueError for caller errors | transactions, month, base, top, rates → report | play1 |
| CLI | argparse surface, text/JSON rendering, exit-code mapping | argv → stdout/stderr + exit code | play1 |

## 5. Interface contracts
- **Library API:** the API named in spec FR2–FR13 and AC1–18, which is fixed by the spec. That covers `parse_lines`, `parse_csv`, `Transaction` fields, `LedgerError(line, reason)` with `.line` and `.reason`, `RATES`, `CategoryTotal(name, total, count)`, `monthly_report(...)`, `report.to_dict()`, and `ValueError` for caller errors.
- **CLI contract:** AC19–24.
  - Exact text output lines; `categories: none` when the month has no categories.
  - The JSON object equals `to_dict()`, with amounts as two-place strings.
  - stderr for a data error is exactly `error: {FILE}:{line}: {reason}\n`, where FILE is the path as typed.
- **Exact error reasons:** AC5–7, byte for byte.
- There are no events and no cross-repo contracts.

## 6. Key technical decisions
- **argparse for usage errors.** argparse already exits 2: `choices` handles `--base`; `type=` validators handle `--month` and `--top`; required subparsers handle a missing subcommand. A FILE that cannot be opened or decoded goes through `parser.error`, which also exits 2. `prog="ledger"` is set explicitly so usage text is the same on every Python version (3.10 through 3.14).
- **Strict lexical validation before stdlib conversion.**
  - Dates must match an ASCII `[0-9]{4}-[0-9]{2}-[0-9]{2}` before calendar conversion, because `fromisoformat` on 3.11+ also accepts `20260301`.
  - Amounts must match a plain signed decimal, `[+-]?digits[.digits]`, otherwise the reason is "is not a number". That rejects NaN, Infinity, `1E+2`, `1_000` and `.5`.
  - If more than 2 digits are written after the point, the reason is "has more than 2 decimal places", so `1.500` is rejected too. A value equal to zero (including `-0.00`) gives "must not be zero".
- **Line numbers.** The reported line is the physical line where the record starts: the header is line 1, and blank and whitespace-only lines count. A quoted field that spans lines is reported at its start line.
- **Field-count reason** uses the header's actual column count: `expected {header_len} fields, got {n}`.
- **`parse_lines` strips a leading `\ufeff`** from the first header cell, so it behaves exactly like `parse_csv` (AC8).
- **Rounding.** Exact sums use the default `Decimal` context (precision 28) and the global context is never changed. Each figure is quantized independently. Negative zero is normalised to `0.00` (A4, extended to every figure).
- **Tie-break** compares the rounded absolute totals, i.e. what the user sees, then the name ascending.
- **CLI tests run the real entry point**: `subprocess` with `[sys.executable, "-m", "ledger", ...]` and cwd at the repo root, with no `sys.path` changes (AC25).
- **Alternatives considered:**
  - A `ledger` console script: rejected, because it would change `pyproject.toml` (AC26).
  - Using `Decimal()` alone for amount parsing: rejected, because it is too permissive.
  - In-process CLI tests like those for numsummary: rejected by AC25.

## 7. Risks and constraints
- **PLAY-G4:** every PR adds a `- SCRUM-17: …` line under `## Unreleased`. The three PRs touch the same spot, so each one is rebased onto `main` after the previous one merges.
- **Stale local install:** the site-packages `.pth` points at another workspace. Run `pip install -e ".[test]"` in this checkout before running local tests. CI installs fresh and is not affected.
- **Exact strings:** the CLI builds its error line from `err.line` and `err.reason`, not from `str(err)`.
- **Python spread:** `requires-python >=3.10` and CI runs 3.12. Avoid the 3.11+ `fromisoformat` leniency and 3.14 argparse features (`suggest_on_error`, `color`).
- **Glossary reviewer:** the claims glossary may flag "net" (there it means "before tax"). The spec fixes the names, so they stay.
- **Scale:** ledgers are single-user and processed in memory with linear passes. There is no network access and no persistent state, so there is no security surface beyond reading a local file.
