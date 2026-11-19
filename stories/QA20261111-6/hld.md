# HLD — Monthly expense report from a CSV ledger (QA20261111-6)

## 1. System Overview

- **What:** a new stdlib-only package `ledger` under `src/ledger/` that parses a UTF-8 CSV ledger into immutable `Transaction`s (R1, R2), builds an exact Decimal monthly report in a chosen base currency (R3, R4), and exposes it as `python -m ledger report FILE --month YYYY-MM [--base] [--top] [--json]` (R5).
- **Problem:** spreadsheet float arithmetic and silently skipped rows give wrong totals; the developer wants exact totals, byte-stable output, and the physical line of the first bad row.
- **Responsibilities:** strict row validation that stops at the first bad row; month selection, currency conversion, one half-to-even rounding per figure; text/JSON rendering with exit codes 0 / 2 / 3.
- **Grounding (checked on `main` @ `0fe2628`, work branch @ `0a9e88c`):** `pyproject.toml` discovers packages with `[tool.setuptools.packages.find] where = ["src"]` and `testpaths = ["tests"]`, so `src/ledger/` is installed by the existing `pip install -e ".[test]"` with no manifest edit. `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/` do not exist. Existing CLIs (`src/testbed_utils/numsummary.py`, `hello.py`) use `argparse` and are console scripts; this story deliberately adds **no** console script (spec non-goal) and uses `__main__.py` instead. The code agrees with the spec's assumptions; no discrepancy found.

## 2. Architecture Overview

Three layers in one package, each owned by one work item, each depending only on the layer below:

| Module (new) | Owns | Owner |
|---|---|---|
| `src/ledger/parser.py` | `Transaction`, `LedgerError`, `parse_lines`, `parse_csv` | t1 |
| `src/ledger/report.py` | `RATES`, `CategoryTotal`, the report type with `to_dict()`, `monthly_report` | t2 |
| `src/ledger/cli.py` + `src/ledger/__main__.py` | argument parsing, rendering, exit codes | t3 |
| `src/ledger/__init__.py` | public re-exports | t1 creates; t2 adds report names (handoff) |

- `cli` → `report` → `parser`; `report` consumes only `Transaction` values, never files. No module imports upward.
- External dependencies: none (stdlib `csv`, `decimal`, `datetime`, `re`, `dataclasses`, `argparse`, `json`). No edit to `pyproject.toml` or any existing file.
- Tests: `tests/test_ledger_parser.py` (t1), `tests/test_ledger_report.py` (t2), `tests/test_ledger_cli.py` (t3, via `subprocess` on `[sys.executable, "-m", "ledger", ...]`). Fixtures under `tests/fixtures/ledger/` (t1).

## 3. Data Flow Design

All synchronous, single process, no I/O beyond reading one file and writing stdout/stderr.

1. `cli` parses argv (usage errors → exit 2 before any reading) → opens FILE via `parse_csv` (OSError / UnicodeDecodeError → exit 2).
2. `parse_csv` opens with `encoding="utf-8-sig", newline=""` and delegates to `parse_lines`, which streams rows through `csv.reader(strict=True)`, tracks the physical start line of each record, validates, and returns `list[Transaction]` in file order or raises `LedgerError(line, reason)` at the first bad row.
3. `monthly_report` validates its arguments (`ValueError`), filters by year-month, converts each amount exactly, sums exactly per figure, quantizes each figure once, orders categories, truncates to `top`.
4. `cli` renders the complete text (or `json.dumps(report.to_dict())`) into a string and writes it to stdout only after the report is built, so on any error stdout stays empty; `LedgerError` → stderr `error: {FILE}:{line}: {reason}`, exit 3.

## 4. Component Breakdown

All components are in `roeeoz/play1` (repoId `421a0585-bb05-4b9d-99da-3905671bbab3`).

**Parser (t1) — `src/ledger/parser.py`, `src/ledger/__init__.py`, fixtures.**
- In: iterable of text lines, or a path. Out: `list[Transaction]` (frozen dataclass: `id`, `date`, `amount`, `currency`, `category`, `memo`) or `LedgerError(line, reason)` with `str()` = `line {line}: {reason}`.
- Fixtures (`tests/fixtures/ledger/`):
  - `sample.csv` — header + 9 rows; verified to reproduce criteria 9, 10, 16, 19, 20:
    `t001 2026-02-27 -99.99 ILS groceries` · `t002 2026-03-01 12000.00 ILS salary` · `t003 2026-03-02 -1500.00 ILS rent` · `t004 2026-03-05 -460.25 ILS groceries` · `t005 2026-03-10 250.00 USD freelance` · `t006 2026-03-12 -111.00 EUR software` · `t007 2026-03-18 -300.25 ILS groceries` · `t008 2026-03-25 -321.00 ILS travel` · `t009 2026-04-01 -1500.00 ILS rent` (memos free text, at least one empty). In base USD: income 3493.24, expense -817.70, net 2675.54, salary 3243.24, freelance 250.00.
  - `bom_blank.csv` — UTF-8 BOM bytes, two valid rows separated by an empty line and a whitespace-only line, one empty memo, one quoted memo containing a comma.
  - `empty.csv` — zero bytes.
  - `bad_amount.csv` — header (line 1), one valid row (line 2), a row with amount `-2.505` (line 3).

**Report (t2) — `src/ledger/report.py`.**
- In: transactions, `month`, `base="ILS"`, `top=None`, `rates=RATES`. Out: immutable report (`month`, `base`, `count`, `income`, `expense`, `net`, `categories: list[CategoryTotal(name, total, count)]`) with `to_dict()`; or `ValueError`.

**CLI (t3) — `src/ledger/cli.py`, `src/ledger/__main__.py`.**
- In: argv. Out: text or JSON on stdout + exit 0; stderr message + exit 2 (usage / unreadable file) or exit 3 (`LedgerError`).

## 5. Interface Contracts

No cross-repo contracts, APIs or events. The contracts are the package's public surface, fixed by the spec (FR2–FR8) plus these settled cases the spec leaves open:

**Parser input rules (t1).**
- Leading U+FEFF on the first line is stripped by `parse_lines` too, so `parse_lines` and `parse_csv` behave identically (FR3).
- The header is the first non-blank line. Column names are trimmed and matched case-sensitively; extra columns are ignored. A column name that appears twice in the header → `LedgerError(header line, "duplicate column 'id'")`. No non-blank line at all (zero bytes, or only blank lines) → `LedgerError(1, "missing header")`.
- A "blank" line is one whose record is empty or a single whitespace-only field; it is skipped but counted. A row of only commas is not blank (it fails as `empty id`).
- `line` is the physical line where the record **starts** (header = 1 when the file has no leading blank lines). A quoted field spanning lines is one record; `csv.reader.line_num` reports the record's end line, so the parser tracks the start line itself.
- Malformed CSV quoting (unterminated quote, text after a closing quote) or a field over the csv module's 131072-char limit → `LedgerError(start line, "malformed CSV: {csv module message}")` (reading with `strict=True`).
- Per-row check order, first failure wins: field count (`expected {header count} fields, got {n}`) → `empty id` → duplicate id → date → amount → currency → `empty category`.
- **Date:** must match `[0-9]{4}-[0-9]{2}-[0-9]{2}` (ASCII) else `date '{text}' is not YYYY-MM-DD` (`date.fromisoformat` alone is not used: on 3.11+ it accepts `20260301`); then a real calendar date else `date '{text}' is not a calendar date`.
- **Amount:** must match `[+-]?[0-9]+(\.[0-9]+)?` (ASCII digits) else `amount '{text}' is not a number` — this refuses `NaN`, `Infinity`, `1e3`, `1_000`, `1,000`, `.5`, `5.`, non-ASCII digits and empty, all of which `Decimal()` would otherwise accept or mis-handle; then more than two fractional digits (textually: `1.500` too) → `amount '{text}' has more than 2 decimal places`; then a zero value incl. `0`, `-0.00`, `+0.0` → `amount must not be zero`. A leading `+` is accepted. The kept value is `Decimal(text)` (so `12000.00` stays `Decimal("12000.00")`).
- **Currency:** exactly `ILS`, `USD` or `EUR` after trimming, else `unknown currency '{text}'`.
- `{text}` in reasons is the trimmed field value. Category names are kept exactly (case-sensitive grouping).
- `parse_csv`: an `OSError` or `UnicodeDecodeError` from opening/decoding propagates unchanged (not a `LedgerError`).

**Report rules (t2).**
- `month` must fully match `[0-9]{4}-(0[1-9]|1[0-2])` and be a `str`, else `ValueError`. `base` not a key of `rates` → `ValueError`. `top` must be `None` or an `int` (not `bool`) ≥ 1, else `ValueError`. A transaction currency missing from `rates`, or a non-positive rate for the base or a used currency → `ValueError`. Never `LedgerError`.
- Conversion `amount × rates[currency] ÷ rates[base]`, performed in a local Decimal context (prec 28, `ROUND_HALF_EVEN`) so the caller's global context cannot change results. Rates may be `Decimal` or `int`.
- `income` = exact sum of positive converted amounts; `expense` = of negative ones; `net` = of all; each category total = of its amounts; each quantized once to `0.01` with `ROUND_HALF_EVEN`. A figure that rounds to zero is reported as `0.00`, never `-0.00` (e.g. one −0.01 ILS transaction in base EUR).
- Category order: absolute **reported** (rounded) total descending, then name ascending; `top` truncates only `categories`.
- `to_dict()` key order `month, base, count, income, expense, net, categories[{name, total, count}]`, amounts as `str` with two decimals.

**CLI rules (t3).**
- `prog` is `python -m ledger`; subcommand `report` is required; `FILE` positional; `--month` required; `--base` choices `ILS USD EUR` default `ILS`; `--top` an int ≥ 1. Month is validated by the same rule as the report. Any of these failing, or FILE unopenable/undecodable (missing, directory, permission, invalid UTF-8) → argparse-style usage error on stderr, exit 2, empty stdout.
- Text: lines `month: …`, `base: …`, `transactions: N`, `income: …`, `expense: …`, `net: …`, then `categories:` followed by `  {name}: {total} ({count})` per category, or the single line `categories: none` when the list is empty (empty month). Every line ends with `\n`.
- JSON: `json.dumps(report.to_dict())` (default ASCII escaping) plus `\n`.
- `LedgerError` → stderr exactly `error: {FILE as given}:{line}: {reason}\n`, exit 3. `--help` → stdout, exit 0.

## 6. Key Technical Decisions

- **Explicit grammars before `Decimal`/`date`.** Probed on Python 3.12: `Decimal()` accepts `NaN`, `Infinity`, `1e3`, `1_000`, `.5`, `5.` and Arabic-Indic `٣`; `re` `\d` also matches `٣`; `date.fromisoformat("20260301")` succeeds. So validation uses ASCII-only regexes first. Alternative (try `Decimal()` and inspect) rejected: more special cases, same result.
- **`csv.reader(strict=True)` over raw lines, own start-line counter.** `line_num` points at a record's last physical line (probe: a 2-line quoted field at lines 4–5 reports 5); non-strict mode silently accepts an unterminated quote at EOF. Alternative `DictReader` rejected: it cannot report the field-count mismatch the spec requires and hides duplicate headers.
- **Round once at the end, local Decimal context.** Matches criteria 11 (0.0125 → 0.01; 0.0375 → 0.04). Normalizing `-0.00` → `0.00` avoids a signed zero in output (probe: `Decimal("-0.0025").quantize(Decimal("0.01"))` is `-0.00`).
- **Build output fully before writing.** Guarantees "stdout empty on error".
- **`__main__.py` instead of a console script.** Spec forbids editing `pyproject.toml`; `python -m ledger` works from the editable install.
- **Library raises, CLI maps.** Parser/report never print or exit; only `cli` decides exit codes.
- **Assumptions (non-blocking, spec silent):** duplicate header column refused; malformed CSV quoting surfaces as a `LedgerError` with reason `malformed CSV: …`; invalid UTF-8 and unopenable files are usage errors (exit 2), consistent with "unreadable FILE"; no path restriction to the cwd (unlike `numsummary.read_text`) since the spec names none. Risk if wrong: one extra reason string or exit code to change in a single module.

## 7. Risks & Constraints

- **Gates (every PR):** CI `test` job — `pip install -e ".[test]"` then `pytest` on Python 3.12 (`.github/workflows/ci.yml`, `.factory/testing.md`); `gate` job green (no `CI_FAIL`); repo-gate skill (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): Python under `src/`, tests under `tests/`, no file > 200 KB, new shell scripts executable with shebang (none planned). No linter/formatter is configured. Code must stay valid on Python ≥ 3.10 (`requires-python`) — no 3.11+-only syntax or stdlib APIs.
- **Fixture fidelity:** `bom_blank.csv` needs real BOM bytes and whitespace-only lines; `empty.csv` must be zero bytes. Editors/formatters may strip them — tests assert the bytes (BOM present, size 0) so a stripped fixture fails loudly.
- **Non-ASCII output:** text output prints category names as-is; on a non-UTF-8 stdout locale a non-ASCII category may fail to encode. JSON uses ASCII escaping. Accepted: the spec's fixtures are ASCII and CI runs UTF-8.
- **Scale:** whole month held in memory as a list (O(rows)); fine for personal/small-team ledgers. Decimal prec 28 leaves ≥ 20 fractional digits for amounts below 10⁸, far beyond the 2-place rounding.
- **Security:** reads one user-named local file, no network, no eval, no writes; csv field-size limit bounds a single field.
- **Glossary skill:** the claims glossary's "net amount = before tax" is for invoice code; this ledger's `net` = income + expense per the spec.
- **Name clash:** the top-level import name `ledger` is new in this distribution; a separately installed third-party `ledger` package in the same environment would shadow or be shadowed. CI's fresh environment has none.
