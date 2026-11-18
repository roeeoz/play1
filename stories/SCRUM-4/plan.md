# SCRUM-4 — Monthly expense report from a CSV ledger (implementation plan)

## Context

SCRUM-4 adds a new package to `roeeoz/play1`: `ledger`, which uses only the standard library. It parses a UTF-8 CSV ledger strictly and stops at the first bad row, giving the physical line and an exact reason. It builds a one-month report in ILS, USD or EUR at fixed rates, using `Decimal` arithmetic and rounding each figure once with `ROUND_HALF_EVEN`. It exposes the report as `python -m ledger report FILE --month YYYY-MM [--base …] [--top N] [--json]`, with exit codes 0, 2 and 3. Acceptance criteria are Scenarios 1–25 of `spec.md` §5: parser 1–8, report 9–18, command line 19–25. The work lands on `halo/feat/scrum-4-20261118-213242` and merges into `main`. `spec.md`, `hld.md` and `work-items.md` are next to this file in `stories/SCRUM-4/`. There are three dependent work items: t1 parser, t2 report, t3 CLI.

## Research findings

- **Packaging.**
  - `pyproject.toml:24` (`where = ["src"]`) finds any package under `src/`, so `src/ledger/` needs no manifest change.
  - `pyproject.toml:10` sets `requires-python = ">=3.10"`.
  - `pyproject.toml:27` sets `testpaths = ["tests"]`.
  - The runtime dependencies (`pyproject.toml:12`, `pypdf` and `flask>=3`) are unrelated, and `ledger` adds none.
- **Existing packages.** `src/testbed_utils/` and `src/guestbook/` exist. Nothing named `ledger` exists anywhere in `src/` or `tests/`, so every file this story touches is new.
- **Test conventions.**
  - Tests are flat `tests/test_*.py` files with no `conftest.py`, grouped in plain `class Test…`.
  - Subprocess tests locate the repo as `REPO_ROOT = Path(__file__).resolve().parent.parent` (`tests/test_hello_sh.py:5`) and call `subprocess.run(..., capture_output=True, text=True)`.
  - Fixtures live under `tests/fixtures/`. The existing `tests/fixtures/empty.txt` shows that a zero-byte fixture survives commits.
  - The in-process CLI style (`tests/test_hello_cli.py`, which patches `sys.argv`) is **not** allowed for t3, because Scenario 25 requires a subprocess.
- **Gate.** `.factory/testing.md` declares a single layer, `package-api`: `pytest`, production-path, required, `runBy: canonical-gate`. The CI `test` job runs `pip install -e ".[test]"` (`.github/workflows/ci.yml:22`) and then `pytest` (`:24`) on Python 3.12 (`:20`). There is no linter, formatter or type checker. The `gate` job only checks for a `CI_FAIL` marker.
- **PR layout gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` has four rules:
  - Rule 1: Python goes under `src/` and tests under `tests/`. This story complies.
  - Rule 3: every file is at most 200 KB. This story complies.
  - Rule 4 (`:17`): the PR must add a line under `## Unreleased` in `CHANGELOG.md`, or the gate raises blocker `PLAY-G4`. This **conflicts** with spec §2, which says no existing file changes, `CHANGELOG.md` named. See Clarification outcomes.
- **Contextual skill.** The `claims-dev` glossary covers invoice and claims naming. The ledger is not invoice code, so the glossary does not apply.
- **Editable-install behaviour (fact about setuptools ≥ 68 / PEP 660).** An editable install maps the top-level packages that exist at install time. A checkout that was installed before `src/ledger/` existed cannot import `ledger` until `pip install -e ".[test]"` is run again. CI installs fresh, so CI is not affected.
- **Verified arithmetic.** I recomputed every figure from the sample rows planned in step 3:
  - In ILS, income is 12925.00, expense −3025.50 and net 9899.50.
  - In USD, income is 3493.2432… → `3493.24`, expense −817.7027… → `-817.70`, net 2675.5405… → `2675.54`, and salary 3243.243… → `3243.24`. These match Scenarios 9, 10 and 20.
  - Scenario 11 holds: 0.05/4 = 0.0125 rounds to `0.01`, and 0.0375 rounds to `0.04`.
- **csv module behaviour relied on.**
  - `csv.reader.line_num` counts physical lines consumed, including lines inside a quoted multi-line field.
  - An empty line yields `[]`, and a whitespace-only line yields `['   ']`.
  - Opening with `newline=""` keeps quoted newlines intact.
- **No external data or cross-repo contracts.** The rates are product constants.
- **Remaining unknowns:**
  - The `CHANGELOG.md` / `PLAY-G4` conflict, raised as a question.
  - Everything else is settled by the design or by an assumption below.

## Locked decisions and assumptions

**Locked decisions**
- The public names are `parse_csv`, `parse_lines`, `Transaction`, `LedgerError` (`.line`, `.reason`), `RATES`, `monthly_report`, `CategoryTotal` and the report's `to_dict()`, all importable from `ledger` (spec §5, hld §5).
- Every reason string in Scenarios 5–7, character for character. `str(LedgerError)` is `line {line}: {reason}` (spec Scenario 5).
- `RATES = {"ILS": Decimal("1"), "USD": Decimal("3.70"), "EUR": Decimal("4.00")}` (Scenario 10).
- Money is `Decimal` everywhere, with no floats. Conversion is `amount × rates[cur] ÷ rates[base]` at full precision, then an exact sum, then one quantize to `0.01` with `ROUND_HALF_EVEN`. Negative zero becomes `0.00` (spec FR4, hld §6).
- Categories are ordered by absolute **rounded** total descending, then by name ascending. `top` cuts only the category list (Scenarios 13 and 14, hld §6).
- Amounts must match the ASCII grammar `[+-]?[0-9]+(\.[0-9]+)?`. More than 2 written decimals (including `1.500`) is an error, and so is zero (including `-0.00`). Dates get an ASCII `YYYY-MM-DD` pattern check, then a calendar check; `date.fromisoformat` is not used for validation. The month argument must fully match `YYYY-MM` with month 01–12 (hld §6).
- Header columns are matched by trimmed name. A duplicated name is `LedgerError(1, "duplicate column '<name>'")`. Missing columns are listed in canonical order. "expected N" is the header's column count (hld §6).
- Checks within a row run in this order: field count, id, date, amount, currency, category, duplicate id (hld §6).
- `parse_lines` strips a leading U+FEFF. `parse_csv` opens with `encoding="utf-8-sig", newline=""` and delegates. A decode failure becomes `LedgerError(line, "file is not valid UTF-8")` (Scenario 8, hld §6).
- The CLI uses `prog="python -m ledger"`, a subparser with `dest=` set, and argparse for usage errors (exit 2). A `LedgerError` prints `error: {FILE as typed}:{line}: {reason}\n` on stderr and exits 3. stdout is empty on both error paths (FR6, hld §6).
- CLI tests run `[sys.executable, "-m", "ledger", ...]` through `subprocess`, with no `sys.path` changes (Scenario 25).
- Only these paths are added: `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`. No existing file changes, `pyproject.toml` and `CHANGELOG.md` included (spec §2 and §6).

**Assumptions**

| # | Assumption | Evidence | If wrong |
|---|---|---|---|
| A1 | The modules are `src/ledger/model.py`, `parser.py`, `report.py`, `cli.py` and `__main__.py`. The report type is a frozen dataclass named `MonthlyReport`, also exported from `ledger`. | hld §2 proposes these names; the spec leaves the report type's name open. | Renaming is local. No contract depends on these names. |
| A2 | The header is the first record that is not blank. It is line 1 in every case the spec defines. | Scenario 7 always reports header errors on line 1. | Only an unspecified case changes: a file with blank lines before the header. |
| A3 | A blank record is `[]`, or a single field that is empty after stripping. A row such as `,,,,,` is **not** blank and fails with `empty id`. | FR1 says "blank and whitespace-only *lines*". | A comma-only row would be skipped instead of reported. |
| A4 | Header names are compared case-sensitively after trimming. | The spec lists lower-case names, and currency is case-sensitive too. | A header like `ID` would be accepted. |
| A5 | Within the header, the duplicate-column check runs before the missing-column check. | hld §6 lists both checks without an order. | Only the reason for a header with both problems changes. |
| A6 | To find the line that is not valid UTF-8, `parse_csv` re-reads the file as bytes after the decode error. It decodes physical lines one at a time and reports the first one that fails. | Text-mode decoding works in chunks, so the exception's offset is not the line number. | Only the line number for that error is affected. |
| A7 | The CLI calls `parse_csv(FILE)`. It maps an `OSError` (missing file, directory, no permission) to `parser.error(...)`, which exits 2. | hld §3 step 1 and §6. | None. Scenario 22 is met either way. |
| A8 | The report module exposes an internal month validator, which the CLI wraps as its argparse `type=`. This keeps one source for the month rule. | hld §6 says to use the same ASCII care for the month. | The CLI would duplicate one regex. |
| A9 | Arithmetic runs in `decimal.localcontext()`, with `prec=50` and `rounding=ROUND_HALF_EVEN` and the traps at their defaults. | hld §6 asks for a local context. 50 digits are far beyond what 2-place rounding needs. | Nothing observable changes. |

## Solution proposal

The design has three layers. Each depends only on the layer below it, and each matches one work item, so each change set builds and passes its tests alone.

1. **Model and parser (t1).**
   - `model.py` holds the `RATES` constant and two types:
     - `Transaction`, a `@dataclass(frozen=True)` with fields `id`, `date`, `amount`, `currency`, `category`, `memo`;
     - `LedgerError(Exception)`, which stores `line` and `reason`, with `__str__` returning `line {line}: {reason}`.
   - `parser.py` builds `parse_lines` on `csv.reader` over the given iterable:
     - It strips the BOM from the first line with a small generator.
     - Before each `next(reader)`, it records `start = reader.line_num + 1`. That gives the line where a record starts, multi-line records included.
     - It skips blank records (A3).
     - It treats the first record that is not blank as the header. It trims the names, checks for duplicates and missing columns, and builds a name → index map.
     - It validates each data row in the locked check order, one small helper per field. Each helper returns the parsed value or raises `LedgerError(start, reason)`.
     - It tracks ids in a dict `id → first line`.
   - `parse_csv` opens the path with `utf-8-sig` and `newline=""` and delegates to `parse_lines`. On `UnicodeDecodeError` it uses the byte rescan (A6).
2. **Report (t2).**
   - `report.py` defines `CategoryTotal(name, total, count)` and `MonthlyReport(month, base, count, income, expense, net, categories)`, both frozen. `to_dict()` turns every amount into `str(Decimal)`, which is already quantized.
   - `monthly_report` works in this order:
     1. It validates the month (`re.fullmatch`, ASCII), the base (`in rates`) and `top` (`None` or ≥ 1), raising `ValueError`.
     2. It filters by `(date.year, date.month)`.
     3. Inside a local context, it converts each amount, then accumulates income, expense and per-category sums and counts.
     4. It quantizes each figure once and normalizes −0 to `0.00`.
     5. It sorts by `(-abs(total), name)` and slices to `top`.
3. **Command line (t3).**
   - `cli.main(argv=None) -> int` builds the argparse parser:
     - `prog="python -m ledger"`;
     - `add_subparsers(dest="command", required=True)`;
     - a `report` subcommand with a positional `file`;
     - `--month`, required, using the month type (A8);
     - `--base` with `choices=("ILS", "USD", "EUR")` and default `ILS`;
     - `--top` with a type that accepts integers ≥ 1;
     - `--json`.
   - It parses and builds the whole report **before** writing anything, so a failure never leaves partial stdout.
   - It renders the 13-line layout (`categories: none` when the list is empty), or `json.dumps(report.to_dict())`.
   - It catches `LedgerError` and writes `error: {args.file}:{e.line}: {e.reason}\n` to stderr, then returns 3.
   - `__main__.py` is `raise SystemExit(main())`.

**Alternatives rejected:**
- A single module: it breaks the file-disjoint tickets (hld §6).
- A console script: it would change `pyproject.toml`.
- In-process CLI tests: Scenario 25 forbids them.
- `Decimal(str)` with exponent rejection, instead of a regex: it accepts `NaN`, `1e3` and non-ASCII digits, then needs blacklisting.
- `date.fromisoformat` alone: its behaviour differs between 3.10 and 3.11+, which accepts `20260301`.
- Opening FILE in the CLI and passing it to `parse_lines`: the UTF-8 error path in `parse_csv` would then need duplicating.

## Ordered implementation steps

**Work item t1: model and parser.** Test layer for all steps: `package-api` (pytest), `tests/test_ledger_parser.py`.

1. **Create `src/ledger/model.py`.**
   - Add `Transaction`, `LedgerError` and `RATES` as specified in Solution proposal 1.
   - Advances Scenarios 1, 5 and 10 (the `RATES` part).
   - Tests:
     - the dataclass is frozen (`FrozenInstanceError`);
     - `str(LedgerError(3, "x")) == "line 3: x"`;
     - the exact keys and values of `RATES`.
2. **Create `src/ledger/parser.py` with `parse_lines` and `parse_csv`.** Follow Solution proposal 1, A2–A6 and the locked check order.
   - Advances Scenarios 2–8 and the design's validation decisions.
   - Tests, one per item:
     - each Scenario 5 reason string, at its exact physical line;
     - first-bad-row-wins;
     - `+`-signed amounts are accepted and keep their value;
     - "not a number" for `NaN`, `Infinity`, `1e3`, `1_0`, `.5`, `١٢` and `abc`;
     - `1.500` and `-0.00`;
     - `20260301`;
     - `usd`;
     - whitespace-only id and category;
     - `expected 6 fields, got 5`, plus a 7-column header giving "expected 7";
     - a duplicate id across a blank line (Scenario 6);
     - missing columns in canonical order, and a duplicate column (Scenario 7);
     - a multi-line quoted memo reported at its starting line;
     - reordered, padded and extra columns (Scenario 2);
     - a header with no rows → `[]` (Scenario 4);
     - `parse_lines(io.StringIO(...))` equals `parse_csv` on the same bytes, including a BOM (Scenario 8);
     - a `tmp_path` file with an invalid UTF-8 byte on line 3 → `LedgerError(3, "file is not valid UTF-8")`.
3. **Create the fixtures under `tests/fixtures/ledger/`.**
   - `sample.csv` has a header and rows `t001`…`t009` in this order:
     - salary `12000.00` ILS;
     - rent `-1500.00` ILS;
     - freelance `250.00` USD;
     - groceries `-400.25` ILS;
     - groceries `-360.25` ILS;
     - software `-120.00` USD;
     - travel `-80.25` EUR, all of the above dated 2026-03;
     - groceries `-99.99` ILS on `2026-02-27`;
     - one row dated `2026-04-01`.
   - `bom_blank.csv` starts with the bytes `EF BB BF`. It has blank and whitespace-only lines, one empty memo and one quoted memo containing a comma.
   - `empty.csv` is zero bytes.
   - `bad_amount.csv` has a valid row on line 2 and `-2.505` on line 3.
   - Write the bytes deliberately, for example with Python `write_bytes`, so no editor drops the BOM.
   - Advances Scenarios 1, 3 and 7, and the `bad_amount.csv` criterion.
   - Tests:
     - Scenario 1, with types and exact `Decimal("12000.00")`;
     - Scenario 3;
     - `empty.csv` → `LedgerError(1, "missing header")`;
     - `bad_amount.csv` → `line 3: amount '-2.505' has more than 2 decimal places`;
     - a guard asserting that `bom_blank.csv` starts with `b"\xef\xbb\xbf"` and that `empty.csv` has size 0.
4. **Create `src/ledger/__init__.py`.** Export the parser API and the model names in `__all__`. Tests import only from `ledger`. Advances the public-API contract.

**Work item t2: monthly report.** Test layer for all steps: `package-api`, `tests/test_ledger_report.py`.

5. **Create `src/ledger/report.py`.** Include the month validator (A8), `CategoryTotal`, `MonthlyReport` with `to_dict()`, and `monthly_report`, as in Solution proposal 2.
   - Advances Scenarios 9–18.
   - Tests:
     - Scenarios 9, 10, 13 and 16 on the parsed sample;
     - Scenarios 11, 12, 14 and 17 on hand-built `Transaction`s;
     - Scenario 15, both the figures and `to_dict()`;
     - a non-empty `to_dict()` category shape;
     - Scenario 18, parametrized over all six bad months, plus an unknown base and `top=0`, each asserting `ValueError` and not `LedgerError`.
   - Invariant tests:
     - −0 normalization: a single `-0.01` ILS transaction reported in EUR (−0.0025 → `-0.00`) gives `expense`, `net` and the category total as `0.00`, never `-0.00`;
     - the result is unchanged under a caller `localcontext(prec=3, rounding=ROUND_DOWN)`;
     - no `float` instances appear anywhere in `to_dict()`.
6. **Extend `src/ledger/__init__.py`.** Add only the report exports: `monthly_report`, `CategoryTotal` and `MonthlyReport`. This is the handoff from t1. Covered by step 5's imports.

**Work item t3: command line.** Test layer for all steps: `package-api`, `tests/test_ledger_cli.py`.

7. **Create `src/ledger/cli.py` and `src/ledger/__main__.py`.** Follow Solution proposal 3 and A7. Advances Scenarios 19–24.
8. **Create `tests/test_ledger_cli.py`.**
   - Use a helper that runs `subprocess.run([sys.executable, "-m", "ledger", *args], cwd=REPO_ROOT, capture_output=True, text=True)` with relative fixture paths.
   - Tests:
     - Scenario 19, exact stdout equality with the 13 lines and empty stderr;
     - Scenario 20, `json.loads` equality and amounts as `str`;
     - Scenario 21, the last four lines;
     - Scenario 22, parametrized over no subcommand, missing `--month`, `--month 2026-13`, `--top 0`, `--base GBP`, a nonexistent path and a directory path, each asserting exit 2, empty stdout and non-empty stderr;
     - Scenario 23, exact stderr and exit 3;
     - a `tmp_path` file that is not valid UTF-8 → exit 3 with `error: {path}:{line}: file is not valid UTF-8`;
     - Scenario 24, `--help` exits 0 and `--month` appears in stdout;
     - usage text contains `python -m ledger`;
     - two runs give byte-identical stdout.
   - Advances Scenario 25.

**Dependencies:** none new. In a checkout, re-run `pip install -e ".[test]"` after `src/ledger/` first exists, before `pytest`. That install needs package-index access for `pypdf`, `flask` and `pytest`; no warm cache is assumed.

**Generated deliverables:** none. The fixtures are hand-written sources, and no binary is larger than 1 MiB.

**Invariants:**
- Authorization and tenancy: not applicable. This is a local, single-user CLI that reads only the given path and makes no network calls.
- Concurrency and idempotency: not applicable beyond output being deterministic, which the step 8 test covers.
- Validation and error paths: covered by steps 2, 5 and 8.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1–4 | t1 | ledger: transaction model, fixed rates and CSV parser with line-exact validation |
| 5–6 | t2 | ledger: monthly report with fixed-rate conversion, single half-even rounding, ordering and top-N |
| 7–8 | t3 | ledger: `python -m ledger report` command line with exact text/JSON output and exit codes 0/2/3 |

Every work item has at least one step.

## Verification and CI gate

- **Canonical gate, in order, from the repo root:** `pip install -e ".[test]"`, then `pytest`. Run it once locally on the committed SHA of each work item. The CI `test` job on Python 3.12 is the authoritative run, as `.factory/testing.md` says (`runBy: canonical-gate`).
- **Required layer:** `package-api` (pytest, production-path). It runs in a pod as long as the pod has package-index access for the install.
- **Expected results:**
  - After t1, the existing tests plus `tests/test_ledger_parser.py` pass.
  - After t2, `tests/test_ledger_report.py` also passes.
  - After t3, `tests/test_ledger_cli.py` also passes, run through the installed package with no `sys.path` changes.
  - Failures: 0. Nothing skipped or xfailed among the new tests.
- **CI configuration:** no change needed. `.github/workflows/ci.yml` already runs the gate on `pull_request`.
- **Python 3.10:** CI runs only 3.12. Python 3.10 compatibility is ensured by design: no `match`, no 3.11+ APIs, an explicit `prog` and `dest=`. It is not executed by any layer, and this is a stated gap rather than a new pipeline.
- **`.factory/delivery-assets`:** no obligations, since there are no large binaries.
- **PR layout gate:** rules 1–3 pass. Rule 4 (`PLAY-G4`) fails by design under the spec as written; see Clarification outcomes.

## Risks and scope guards

**Risks**
- **`PLAY-G4` blocks each PR**, because `CHANGELOG.md` is untouched. A human must waive it knowingly, or the scope must be amended. This is raised as a question.
- **A stale editable install** gives `ModuleNotFoundError: ledger` in a pod that was installed before the package existed. Mitigation: re-run the install (see Dependencies).
- **Fixture bytes:** the BOM or the zero-byte file could be lost on commit. Mitigation: the step 3 byte guard test.
- **Version drift between 3.10 and 3.12:** dates, argparse `prog` and subparsers. Mitigation: ASCII regexes before any stdlib parsing, plus explicit `prog` and `dest`.

**Do NOT**
- Edit any existing file: `CHANGELOG.md`, `pyproject.toml`, `README.md`, `.github/workflows/ci.yml`, `.factory/*`, existing tests and fixtures, `src/testbed_utils/`, `src/guestbook/`. Do not add a `.gitattributes` or a `conftest.py`.
- Add a console script or any third-party dependency, or use `float` anywhere.
- Add file formats, live rates, currencies, configuration or multi-month ranges.
- Touch `sys.path` in tests, or test the CLI in-process.
- Delete, skip, xfail or weaken any check to get green. A failing gate, `PLAY-G4` included, is reported as blocked.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

One question is open in `plan-questions.json`. It is about the `CHANGELOG.md` conflict: spec §2 forbids touching existing files, but repo-gate rule 4 raises blocker `PLAY-G4` on any PR that doesn't touch `CHANGELOG.md`. Until it is answered, the plan follows the approved spec: `CHANGELOG.md` stays untouched, and the expected `PLAY-G4` finding is left for a human reviewer to waive.
