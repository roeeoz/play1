# Plan: SCRUM-5, monthly expense report from a CSV ledger

## Context

SCRUM-5 adds a new stdlib-only package, `ledger`, to `play1`. It is run as `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`. The package parses a UTF-8 CSV ledger strictly and stops at the first bad row with a line-numbered `LedgerError` (Scenarios 1–8). It builds a Decimal-exact monthly report in a base currency, converting at fixed rates and rounding each figure once, half to even (Scenarios 9–18). The command line prints byte-exact text or JSON and exits 0, 2 or 3 (Scenarios 19–25). The work lands in `play1` on the work branch `halo/feat/scrum-5-20261118-214209`, which was cut from `main` (`b7b5d0a`), and is delivered as three dependent work items: t1 → t2 → t3. `spec.md`, `hld.md` and `work-items.md` are in this folder (`stories/SCRUM-5/`), next to this file.

## Research findings

**Change surface: everything is new.** Neither `src/ledger/` nor any `tests/test_ledger_*.py` or `tests/fixtures/ledger/` exists yet (checked on the work branch; `python3 -c "import ledger"` → `ModuleNotFoundError`). No existing module is modified.

**Packaging**
- `pyproject.toml:24-25` sets `[tool.setuptools.packages.find] where = ["src"]`, so a new `src/ledger/` with an `__init__.py` is discovered without any change to the manifest.
- `pyproject.toml:9` sets `requires-python = ">=3.10"`. The code must therefore avoid 3.11+ APIs, for example `decimal.localcontext(prec=...)` keyword arguments (added in 3.11).
- `pyproject.toml:28-29` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- `pyproject.toml:13-17` holds the existing console scripts. None is added (spec §2).

**Package convention**
- `src/testbed_utils/__init__.py:1-28` and `src/guestbook/__init__.py:1-9` follow one pattern: a module docstring, explicit re-imports and an alphabetical `__all__`. `ledger/__init__.py` follows it.
- `src/testbed_utils/numsummary.py:1-17` shows the house CLI style: `argparse`, `from __future__ import annotations`, module-level message constants.

**Test conventions**
- pytest classes, grouped by behaviour, with no fixtures shared through a `conftest.py`. The suite has no `conftest.py` and no `sys.path` manipulation (`.factory/testing.md:17-22`).
- Subprocess tests compute `REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent` and call `subprocess.run(..., capture_output=True, text=True, timeout=10, cwd=...)` (`tests/test_qa_20261109_s1_a.py:6-15`). `tests/test_ledger_cli.py` reuses this shape with `[sys.executable, "-m", "ledger", ...]`.
- Existing fixtures live flat in `tests/fixtures/`. The new ones go under `tests/fixtures/ledger/` (spec §6).

**Canonical gate**
- `.factory/testing.md:3-9` and `.github/workflows/ci.yml:12-24` define the gate: `pip install -e ".[test]"`, then `pytest`, on Python 3.12.
- The only declared layer is `package-api` (production-path, `runBy: canonical-gate`, `.factory/testing.md:36-46`).
- No linter, formatter or type checker is configured.
- The CI `gate` job (`ci.yml:26-37`) fails only if a `CI_FAIL` file exists.

**Merge gate.** Rule 4 of `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:17-20` requires every PR to add a line under `## Unreleased` in `CHANGELOG.md`; otherwise it raises blocker `PLAY-G4`. `CHANGELOG.md:3-8` shows the precedent, one line per story. This conflicts with spec §2 / §6, "no changes to any existing file" (see Clarification outcomes).

**Local environment**
- The local interpreter is 3.13.18, while CI runs 3.12.
- The installed `testbed-utils` is an editable install pointing at another workspace (`pip show testbed-utils` → `delivery-c9650339…`). Re-run `pip install -e ".[test]"` from this checkout before running `pytest` locally (HLD §7).

**`.gitignore`.** No pattern matches `src/ledger/*.py`, `tests/fixtures/ledger/*.csv` or the empty `empty.csv`.

**External data.** None. Rates are constants (spec FR5).

**Unknowns left after research**
- The `PLAY-G4` decision (open).
- Whether a figure that rounds to zero from a negative sum should print `-0.00`. The spec is silent; see Assumptions.

## Locked decisions and assumptions

**Locked decisions**

*Scope and dependencies*
- The package uses only the standard library. The only entry point is `python -m ledger`: no console script and no `pyproject.toml` edit (spec §2, §6).
- The story may add files only under `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`. It adds no `conftest.py` and no `.gitattributes` (spec §6).

*Parser*
- Module dependencies run one way, model ← parser ← report ← cli ← `__main__` (HLD §2).
- `csv.reader(strict=True)` reads the input. A row's line number is the previous `line_num + 1`. A leading `\ufeff` is stripped on the first line. Blank rows and all-empty rows are skipped but still counted (HLD §4 Parser).
- Rows are checked in this order: field count, empty id, duplicate id, date, amount, currency, category. The expected field count is `len(header)` (HLD §4).
- Amounts must fully match the ASCII regex `-?[0-9]+(\.[0-9]+)?`. More than two fractional digits is rejected, so `1.500` fails. Zero is rejected. The value is built with `Decimal(text)` (HLD §4).
- Header problems raise these errors (HLD §4):
  - a duplicate required column → `duplicate column 'id'`;
  - malformed quoting → `malformed CSV: <detail>`;
  - a decoding failure → `invalid UTF-8`.

*Error strings and output*
- Every reason string in spec Scenarios 5–7 and 23 is byte-exact, as is the 13-line text output in Scenario 19 (spec §7).

*Report*
- `RATES = {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}` (spec Scenario 10).
- Each amount is converted at full precision inside a local Decimal context. Each figure is quantized independently, once, with `ROUND_HALF_EVEN` (spec FR5, HLD §4 Report).
- Categories are ordered by absolute rounded total descending, then by name ascending. `top` slices only the categories list (HLD §4).
- `month` must match `^[0-9]{4}-(0[1-9]|1[0-2])$`. A bad `month`, a `base` outside `rates` or `top < 1` raises `ValueError` (HLD §4).

*Command line*
- `--base` uses argparse `choices`. `--month` and `--top` use `type=` validators.
- An open failure goes through `parser.error` (exit 2). A `LedgerError` prints `error: {FILE}:{line}: {reason}` and exits 3.
- Output is fully formatted before anything is written to stdout (HLD §3, §4 CLI).
- CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", ...]`, with `cwd` set to the repository root (spec Scenario 25, HLD §7).

*Fixtures*
- `sample.csv` holds the rows listed in HLD §6. t1 creates `sample.csv`, `bom_blank.csv` and `empty.csv`; t3 creates `bad_amount.csv` (HLD §6, work-items).

**Assumptions**

- **A1. `CHANGELOG.md` stays unchanged** unless the developer approves option (a). Evidence: spec §8 keeps "no changes to any existing file" by the developer's direction, and work-items.md names (a) as an approved-only exception. If wrong: each PR carries the `PLAY-G4` blocker until the decision lands. Applying (a) is a one-line addition per work item.
- **A2. The module file names** are `model.py`, `parser.py`, `report.py`, `cli.py` and `__main__.py`. Evidence: HLD §2 names only roles. The stdlib `parser` module was removed in 3.10, so a package-local `ledger.parser` does not collide. If wrong: rename only, with no behavioural effect.
- **A3. The report value is a frozen dataclass named `MonthlyReport`** with fields `month, base, count, income, expense, net, categories`, plus `to_dict()`. `CategoryTotal` is a frozen dataclass `(name, total, count)`. Evidence: spec FR4 names `CategoryTotal` but not the report type. If wrong: rename only.
- **A4. The `sample.csv` groceries rows** are two March ILS rows summing to `-760.50`, for example `-500.25` and `-260.25`. The April row is any valid row. Evidence: spec §8 accepts any rows that reproduce the figures. Checked by hand: USD income 12925/3.70 → `3493.24`, expense −3025.50/3.70 → `-817.70`, net 9899.50/3.70 → `2675.54`, salary → `3243.24`, freelance 250 USD → `250.00`.
- **A5. No negative-zero normalisation.** A negative exact sum that rounds to zero would render as `-0.00`. No acceptance criterion covers it, and adding normalisation is out of scope. If wrong: a one-line follow-up in `report.py`.
- **A6. `--month` validation in the CLI repeats the report's month regex** in `cli.py`. t3 must not modify `report.py` (work-items t3), and reaching into a private name is fragile. If wrong: t2 could export the validator instead. That is a t2 edit, made only while t2 is being built.
- **A7. The local Decimal context is `decimal.localcontext(decimal.Context(prec=50, rounding=ROUND_HALF_EVEN))`.** The positional `Context` form keeps Python 3.10 compatibility. Any precision of at least 28 satisfies the HLD.

## Solution proposal

The solution is a small layered package, matching HLD §2. Each layer is a pure function over the one below it, and only the CLI performs I/O to stdout and stderr.

**`model.py`**
- `@dataclass(frozen=True) class Transaction` with `id: str`, `date: datetime.date`, `amount: Decimal`, `currency: str`, `category: str` and `memo: str`.
- `class LedgerError(Exception)` stores `line` and `reason`, and `__str__` returns `f"line {line}: {reason}"`. It calls `super().__init__(line, reason)` so pickling and `args` behave normally.
- Module constants `CURRENCIES = ("ILS", "USD", "EUR")` and `COLUMNS = ("id", "date", "amount", "currency", "category", "memo")`, in canonical order.

**`parser.py`**
- `parse_lines(lines)`:
  - Wraps the iterable in a generator that strips a leading `\ufeff` from the first item, then feeds `csv.reader(strict=True)`.
  - Drives the reader with an explicit `next()` loop. That way a `csv.Error` or a `UnicodeDecodeError` raised during iteration is caught and turned into a `LedgerError` with the row's start line (`reader.line_num + 1` before the read).
  - Skips blank rows.
  - Validates the first non-blank row as the header and builds a name → index map from the stripped names. Raises a missing-columns error, listed in `COLUMNS` order, or a duplicate-column error.
  - Validates each later row in the locked order. Small private helpers per field keep each reason string in one place.
  - Tracks seen ids with their line numbers to produce `duplicate id 't1' (first seen on line 2)`.
- `parse_csv(path)` does `open(path, encoding="utf-8-sig", newline="")` and returns `parse_lines(f)`. The BOM handling is therefore identical whether the BOM is decoded away or stripped by the generator.

**`report.py`**
- `RATES`, `CategoryTotal`, `MonthlyReport` and `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)`.
- The arguments are validated first (`ValueError`).
- Transactions are filtered by `(date.year, date.month)`.
- Inside the local context, each amount is converted as `amount * rates[cur] / rates[base]`. The exact values accumulate into income (positive), expense (negative) and per-category sums and counts.
- Each figure is then quantized with `Decimal("0.01")` and `ROUND_HALF_EVEN`, still inside the local context so the caller's global context cannot change the result.
- Categories are sorted with the key `(-abs(total), name)`, then sliced to `top`.
- `to_dict()` builds the keys in the locked order, with `str()` amounts.

**`cli.py` and `__main__.py`**
- `cli.py` provides `main(argv=None) -> int`:
  - It uses argparse with `add_subparsers(dest="command", required=True)` and a `report` subparser. `report` takes the positional `FILE`, `--month` (required, with a `type=` validator that raises `argparse.ArgumentTypeError`), `--base` (`choices`, default `ILS`), `--top` (`type=` positive int) and `--json`.
  - `FILE` is opened inside `try` with the same `utf-8-sig`/`newline=""` mode. On `OSError` it calls `parser.error(...)`, which exits 2.
  - `parse_lines` runs inside `try`. On `LedgerError` it writes `error: {args.file}:{e.line}: {e.reason}\n` to stderr and returns 3.
  - Otherwise it builds the report, formats the whole output string, writes it once and returns 0.
- `__main__.py` is `raise SystemExit(main())`.

**Alternatives rejected**
- **Letting `parse_csv` own file opening in the CLI.** It would make an open failure indistinguishable from a data error, but HLD §3 needs exit 2 for the former.
- **Catching `ValueError` from `monthly_report` in the CLI** instead of using `type=` validators. Bad arguments would be detected only after the file is parsed, so a bad file plus a bad month would give exit 3 instead of the usage error.
- **Using `float` anywhere.** It breaks the exactness in Scenario 11.
- **Exposing a `ledger` console script.** Forbidden by spec §2.

## Ordered implementation steps

### Work item t1: model and parser

**1. Create the fixtures** under `tests/fixtures/ledger/`. Advances Scenarios 1, 3 and 7 and supports Scenarios 9–23. Covered by the `package-api` layer (pytest) in step 4.
- `sample.csv`: LF line endings, the header, then rows t001–t009 per HLD §6 and A4. Seven rows are dated 2026-03, one 2026-02-27 (groceries -99.99 ILS) and one 2026-04-01. Include at least one empty memo.
- `bom_blank.csv`:
  - Write it as bytes so it starts with `EF BB BF`.
  - Include a blank line and a whitespace-only line between rows.
  - One row has an empty memo. Another has a memo quoted because it contains a comma.
  - It has exactly two data rows.
- `empty.csv`: zero bytes.

**2. Create `src/ledger/model.py`**: `Transaction`, `LedgerError`, `CURRENCIES` and `COLUMNS`, as in the Solution proposal. Advances Scenarios 1 and 5. Covered by the `package-api` layer in step 4.

**3. Create `src/ledger/parser.py`** (`parse_lines`, `parse_csv`) and `src/ledger/__init__.py`. Advances Scenarios 1–8. Covered by the `package-api` layer in step 4.
- `__init__.py` has a docstring and re-exports `LedgerError`, `Transaction`, `parse_csv` and `parse_lines` in an alphabetical `__all__`.
- Error paths to cover:
  - each reason string in Scenario 5;
  - duplicate id (Scenario 6);
  - missing columns and missing header (Scenario 7);
  - duplicate column;
  - `malformed CSV: …`;
  - `invalid UTF-8`.
- Invariants:
  - Parsing stops at the first error.
  - Line numbers count blank lines and use the start line of a multi-line row.
  - Header names and every field are stripped.
  - Extra columns are ignored.

**4. Create `tests/test_ledger_parse.py`.** Covers Scenarios 1–8. Layer: `package-api`.
- **Sample fixture:** nine transactions in order; field types; `amount == Decimal("12000.00")` and `str(amount) == "12000.00"`; the dataclass is frozen (assigning raises `FrozenInstanceError`).
- **Header handling:** a reordered, space-padded header with an extra column, through `io.StringIO`.
- **`bom_blank.csv`:** its raw bytes start with `b"\xef\xbb\xbf"` and it contains a whitespace-only line. It parses to two rows with `""` and a comma-bearing memo.
- **Header-only input** returns `[]`.
- **Reason strings:** one parametrized case per Scenario 5 reason, plus `NaN`, `Infinity`, `+5`, `1e3`, `1_000`, a non-ASCII digit, `1.500`, `-0` and `0.00`. Each asserts `.line`, `.reason` and `str(err)`.
- **Field count:** `expected 6 fields, got 5`.
- **Duplicate id:** separated by a blank line, reported on the second row's line.
- **Header errors:** missing columns in canonical order; `empty.csv` → `(1, "missing header")`; duplicate column.
- **Broken input:** an unclosed quote, and invalid UTF-8 bytes written to `tmp_path` and read through `parse_csv`. Each raises `LedgerError` with an `int` line, never `csv.Error` or `UnicodeDecodeError`.
- **First error wins:** two bad rows report only the first.
- **Multi-line row:** a quoted memo spanning lines followed by a bad row reports the bad row's start line.
- **Entry-point parity:** `parse_lines(io.StringIO("\ufeff" + text)) == parse_csv(path)`.

### Work item t2: monthly report

**5. Create `src/ledger/report.py`**: `RATES`, `CategoryTotal`, `MonthlyReport` with `to_dict()`, and `monthly_report`. Advances Scenarios 9–18. Covered by the `package-api` layer in step 7.
- Validation order: `month`, then `base`, then `top`. Each raises `ValueError`. `top` is checked only when it is not `None`.
- Conversion and quantization run inside the local context (A7).

**6. Extend `src/ledger/__init__.py`** to re-export `CategoryTotal`, `MonthlyReport`, `RATES` and `monthly_report`, keeping `__all__` alphabetical. Advances Scenarios 9–18. Covered by the `package-api` layer in step 7.

**7. Create `tests/test_ledger_report.py`.** Covers Scenarios 9–18. Layer: `package-api`. It builds inputs from `parse_csv` on `sample.csv`, or from `Transaction` values constructed directly.
- **Sample report:**
  - Scenario 9: compare figures with both `==` and `str()`, so the scale is checked.
  - Scenario 10: USD figures, including the totals from Scenario 20.
  - Scenario 13: `top=2`, `top=99` and `top=None`.
  - Scenario 15: the empty month, including the exact `to_dict()`.
  - Scenario 16: February.
- **Rounding and formatting:**
  - Scenario 11: 0.05 ILS → EUR gives `0.01` once and `0.04` for three such transactions.
  - Global-context independence: run under `decimal.localcontext()` with `prec=4` and `rounding=ROUND_DOWN`, set via the `Context` object, and expect identical results.
  - Scenario 12: `5.00` / `-2.00` / `3.00`.
- **Ordering and rates:**
  - Scenario 14: a tie ordered by name.
  - Scenario 17: custom rates.
- **Argument errors** (Scenario 18), each asserting it is not a `LedgerError`:
  - the six bad months;
  - a bad `base`;
  - `top=0` and `top=-1`.
- **`to_dict()` key order:** `list(d) == [...]`.

### Work item t3: command line

**8. Create `tests/fixtures/ledger/bad_amount.csv`**: the header, a valid row on line 2 and the amount `-2.505` on line 3, with LF endings. Advances Scenario 23. Covered by the `package-api` layer in step 10.

**9. Create `src/ledger/cli.py` and `src/ledger/__main__.py`.** Advances Scenarios 19–24.
- Text format: the six `key: value` lines, then `categories:` with `  name: total (count)` lines, or `categories: none` when there are no categories. The lines are joined with `\n` plus a trailing `\n`.
- JSON format: `json.dumps(report.to_dict()) + "\n"`.
- `--help` on the subparser goes to stdout and exits 0 (argparse default). The help text for `--month` mentions `YYYY-MM`.
- Covered by the `package-api` layer in step 10.

**10. Create `tests/test_ledger_cli.py`.** Covers Scenarios 19–25. Layer: `package-api`.
- **Harness:** `REPO_ROOT` from `__file__`, and a `run(*args)` helper calling `subprocess.run([sys.executable, "-m", "ledger", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30)`.
- **Successful runs:**
  - Scenario 19: an exact 13-line stdout and empty stderr.
  - Scenario 20: `json.loads(stdout) ==` the expected object.
  - Scenario 21: stdout ends with the four lines.
  - Byte-identical stdout across two runs.
- **Usage errors (Scenario 22):** each case exits 2 with empty stdout and non-empty stderr. The cases are: no subcommand, `--month` missing, `--month 2026-13`, `--top 0`, `--base GBP`, a missing FILE and a directory as FILE.
- **Data errors:**
  - Scenario 23: an exact stderr string.
  - Invalid UTF-8 and an unclosed quote, written to `tmp_path`: exit 3, empty stdout, and stderr starting with `error: {path}:`.
- **Help (Scenario 24):** exit 0 and `--month` appears in stdout.

**Dependencies.** None are added. The package installs through the existing `pip install -e ".[test]"`.

**Generated deliverables.** None. The fixtures are hand-authored text, and `empty.csv` is zero bytes. No binary is 1 MiB or larger, so no `.factory/delivery-assets` entry is needed.

**Authorisation and concurrency.** Not applicable: this is a single-process local CLI with no shared state. The only invariants are the validation and error paths listed above.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1, 2, 3, 4 | t1 | ledger: transaction model and strict CSV parser with line-numbered errors |
| 5, 6, 7 | t2 | ledger: monthly report with fixed-rate Decimal conversion and half-even rounding |
| 8, 9, 10 | t3 | ledger: python -m ledger report command line with text/JSON output and exit codes |

Every work item has steps. If the developer approves option (a), each work item also adds one line under `## Unreleased` in `CHANGELOG.md`, describing that work item's addition.

## Verification and CI gate

**Canonical gate.** From the repository root, run `pip install -e ".[test]"` and then `pytest`, once, on the committed SHA of each work item (`.factory/testing.md:3-9`). Locally, the editable install must be redone first because the current one points at another workspace.

**Test layer.** `package-api` is the only declared layer and is required. It runs in a pod without privileges. It is authoritative when observed in the provider's `test` job on Python 3.12 at the exact head SHA.

**What the gate must show for each work item**
- `pytest` exits 0, with the new `tests/test_ledger_*.py` for that work item collected and passing.
- Every pre-existing test still passes.
- No test is skipped or marked `xfail` in the new files.
- The CI `gate` job stays green, because no `CI_FAIL` file is added.
- For t3, the subprocess tests pass in CI, which proves that `python -m ledger` resolves through the installed package.

**No other configuration is needed.** The change requires no provider CI change and no `.factory/testing.md` change. `.factory/delivery-assets` is not needed, because there are no large binaries.

**Merge gate.** The mr-gate rule `PLAY-G4` will report a blocker on each PR unless option (a) is approved. Report it as blocked; never work around it.

## Risks and scope guards

**Risks**

- **Fixture bytes get altered by editors or tools.** This covers the BOM, the whitespace-only line, LF endings and a zero-byte file. Mitigation: write fixtures programmatically or verify them with `xxd`. Tests assert the BOM bytes and the presence of the whitespace-only line, so drift fails loudly.
- **Python version drift** (3.10 floor, 3.12 CI, 3.13 local) affects `localcontext` keyword arguments, `date.fromisoformat` leniency and argparse messages. Mitigation:
  - Run the regex checks before `fromisoformat` and `Decimal`.
  - Use the positional `Context` form.
  - Assert exact stderr only where the spec fixes it (Scenario 23). For usage errors, assert only exit 2, empty stdout and non-empty stderr.
- **Subprocess stdout encoding.** All outputs on the sample are ASCII, and `text=True` with LF endings is consistent on Linux CI. No env override is needed.
- **`PLAY-G4` blocker** on every PR (A1). This is a human decision and is surfaced through the question.

**Scope guards: the implement phase must NOT**
- Edit any existing file: `pyproject.toml`, `CHANGELOG.md` (unless (a) is approved), `.github/`, `README.md`, `.factory/`, existing `src/` or `tests/` files.
- Add a console script, a `conftest.py`, a `.gitattributes`, `sys.path` tweaks or any third-party dependency.
- Use `float` for money, fetch rates, or round before summing.
- Add `__main__.py` or `cli.py` in t1 or t2, or modify the t1 modules or fixtures in t2 or t3. The one exception is t2's re-export edit to `__init__.py`.
- Normalise `-0.00` (A5), accept `+`, exponents or a lenient date format, or add other file formats or configuration.
- Make any check pass by deleting, skipping, marking `xfail` or loosening an assertion. A failing required check is reported blocked.

## Clarification outcomes

One question was raised through the plan conversation and is awaiting the developer's answer. The plan proceeds on assumption A1 meanwhile.

- **The `PLAY-G4` CHANGELOG rule versus "no changes to any existing file" (spec §2, §6, §8).** The options are:
  - (a) Amend the scope so each work item's PR adds one line under `## Unreleased` in `CHANGELOG.md`.
  - (b) Change `PLAY-G4` first, as a separate change.
  - (c) Keep the scope and accept a blocked mr-gate on every PR.

  Recommended: (a). It is the smallest change, it matches every earlier story (`CHANGELOG.md:5-8`), and it is the only option that lets this story's PRs pass the gate without a separate change.
