## Context

SCRUM-18 adds a new stdlib-only Python package `ledger` to `roeeoz/play1`. It parses a UTF-8 CSV ledger strictly, reporting the first bad row by physical line. It builds one month's income, expense, net and per-category totals in ILS, USD or EUR using exact `Decimal` arithmetic, rounded once with `ROUND_HALF_EVEN`. It exposes this through `python -m ledger report FILE --month YYYY-MM [--base …] [--top N] [--json]`, with exit codes 0, 2 and 3. Acceptance criteria 1–8 cover parsing (work item t1), 9–18 the report (t2), and 19–25 the command line (t3). Work lands on `halo/feat/scrum-18-20261118-234805`, which merges into `main`. `spec.md` (requirement and the 25 criteria), `hld.md` (design) and `work-items.md` (t1 → t2 → t3) sit beside this file in `stories/SCRUM-18/`.

## Research findings

- **Packaging needs no change.** The package is found automatically:
  - `pyproject.toml:23-24` discovers packages under `src/`.
  - `pyproject.toml:27` sets `testpaths = ["tests"]`, and `pyproject.toml:28` sets `addopts = "-q"`.
  - `pyproject.toml:10` sets `requires-python = ">=3.10"`, so the code must avoid 3.11+ APIs.
  - A `src/ledger/__main__.py` is enough for `python -m ledger`. No `[project.scripts]` entry is needed, and none is in scope.
- **What already exists.**
  - `src/` holds only `guestbook/` and `testbed_utils/`. `src/ledger/` and `tests/test_ledger_*.py` do not exist.
  - `import ledger` fails in this pod (`ModuleNotFoundError`), so no installed distribution has that name.
  - `tests/fixtures/` has no `ledger/` subdirectory. Every source, test and fixture file is new.
- **Conventions to follow.**
  - `src/testbed_utils/__init__.py:8-26` re-exports the public API through an explicit, sorted `__all__`.
  - The existing CLIs use `argparse` (`src/testbed_utils/numsummary.py:5,76-77`, `src/testbed_utils/hello.py:5,20`).
  - Existing CLI tests call `main()` in-process (`tests/test_num_summary_cli.py:18-31`). Criterion 25 asks for `subprocess` instead. That is a new style inside the existing pytest layer, not a new layer.
  - There is no `conftest.py` and no `tests/__init__.py`, so test basenames must be unique across `tests/`.
- **CHANGELOG contract.** `CHANGELOG.md:3` is `## Unreleased`, and entries take the form `- <KEY>: add \`<path>\`, …` (`CHANGELOG.md:5-8`). The repo gate's rule PLAY-G4 (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:17-20`) blocks any pull request that does not add a line there.
- **Other repo-gate rules.** Rules 1 and 3 (`SKILL.md:14,16`): Python under `src/`, tests under `tests/`, no file over 200 KB. All new files comply.
- **Canonical gate.**
  - `.factory/testing.md` declares one layer, `package-api` (`pytest`, production-path, `runBy: canonical-gate`).
  - `.github/workflows/ci.yml:12-24` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12.
  - `.github/workflows/ci.yml:26-37` is the `CI_FAIL` marker switch, not a quality check.
  - No linter, formatter or type checker is configured.
- **Fixture fidelity.** There is no `.gitattributes`, and `core.fileMode` is `true`. Editors may strip the BOM in `bom_blank.csv` or its whitespace-only line, and a zero-byte `empty.csv` must stay at zero bytes.
- **Fixture data checked against the criteria.** I ran the arithmetic with `Decimal` in this pod. The sample rows proposed in step 1 give every figure in criteria 9, 10, 16 and 20:
  - ILS: salary 12000.00, rent -1500.00, freelance 925.00, groceries -760.50 (2), software -444.00, travel -321.00.
  - USD: income 3493.24, expense -817.70, net 2675.54, salary 3243.24, freelance 250.00.
  - Criterion 11: one 0.05 ILS → EUR gives 0.01, and three give 0.04.
- **`csv.reader` behaviour the parser relies on.** A blank line yields `[]`, and a whitespace-only line yields a single whitespace field. `reader.line_num` counts physical lines consumed, so a record's start line is the previous `line_num` + 1 (hld §6).
- **External data:** none. Rates are constants and there is no network access.
- **Remaining unknowns:** none that block. The points the spec and HLD leave open are recorded as assumptions below.

## Locked decisions and assumptions

**Locked decisions**
- Public names and contracts: `Transaction`, `LedgerError(line, reason)` with `str(error) == f"line {line}: {reason}"`, `parse_csv`, `parse_lines`, `RATES`, `CategoryTotal(name, total, count)`, `monthly_report(transactions, month, base="ILS", top=None, rates=RATES)` and `to_dict()`. Source: spec §5 criteria 1–18, hld §5.
- Every error reason, the text layout, the JSON shape and the exit codes 0/2/3 are taken exactly as spec §5 criteria 5–7 and 19–23 spell them.
- Module layout: `src/ledger/__init__.py`, a parser module (proposed name `src/ledger/_parse.py`), `src/ledger/report.py`, `src/ledger/cli.py` and `src/ledger/__main__.py`. Source: hld §2.
- Layer boundaries: only the parser raises `LedgerError`, the report raises only `ValueError`, and only the CLI maps errors to exit codes. Source: hld §2.
- Row checks run in this order: field count, empty id, date, amount (number, then decimal places, then zero), currency, empty category, duplicate id. A row is reported at its start line. Source: hld §6, spec A3.
- Dates and amounts pass a strict ASCII regex before the stdlib converts them. The `csv.reader` is used directly; `DictReader` is not. Source: hld §6.
- Money is converted as `amount × rates[currency] ÷ rates[base]` inside a local Decimal context. Each figure is quantized once to `0.01` with `ROUND_HALF_EVEN`, and negative zero becomes `0.00`. Source: spec FR4, hld §6.
- The CLI uses `argparse` with a required subparser. `OSError` and `UnicodeDecodeError` exit 2, and FILE is echoed as typed. Source: hld §6, work item t3.
- CLI tests use `subprocess` with `[sys.executable, "-m", "ledger", …]` and no `sys.path` manipulation. Source: criterion 25.
- Stdlib only. No existing file changes except one SCRUM-18 line per work item under `## Unreleased` in `CHANGELOG.md`. Source: spec §2, A1, work-items t1–t3.

**Assumptions**
- *The header is the first record of the input, at line 1.* Blank lines before the header are not supported: a blank first line gives `missing column(s): …` at line 1. Header names are trimmed and compared case-sensitively.
  - Evidence: criterion 7 fixes both header errors at line 1.
  - If wrong: only an input that opens with blank lines behaves differently, and no criterion covers that.
- *A record is blank if it has no fields, or all its fields strip to `""`.*
  - Evidence: criterion 3, and a whitespace-only line is one field to `csv.reader`.
  - If wrong: a row of only commas would be skipped instead of raising `empty id`. To avoid that, the implementer treats only `[]` and a single whitespace-only field as blank.
- *The amount pattern is `[+-]?[0-9]+(\.[0-9]+)?`.* `.5` and `5.` are therefore "not a number". Decimal places are counted from the text, so `1.500` is rejected.
  - Evidence: hld §6 says "optional sign, ASCII digits, optional fraction".
  - If wrong: rarely used forms are rejected that a reader might accept. No criterion covers them.
- *Categories are sorted on their rounded totals: `(-abs(total), name)`.*
  - Evidence: criterion 14 compares the totals the report shows.
  - If wrong: two categories whose exact totals differ below a cent could swap places.
- *The report type is a frozen dataclass named `MonthlyReport`.* Its `categories` is a `list` (criterion 9 says "the list"). The HLD leaves the name to the implementer.
  - If wrong: only the name changes. It is exported, and no criterion names it.
- *The local Decimal context uses `prec=50` and `ROUND_HALF_EVEN`.* That is ample for these sums, and the caller's global context is never used.
  - If wrong: nothing observable at ledger scale.

## Solution proposal

Build a three-layer package that follows hld §2, in the order the work items require. Each layer depends only on the layer below it.

1. **Parser (`src/ledger/_parse.py`).**
   - `Transaction` is a `@dataclass(frozen=True)`. `LedgerError(Exception)` stores `line` and `reason`, and its `__str__` returns `line {line}: {reason}`.
   - `parse_lines(lines)`:
     - Wraps the iterable in a generator that strips a leading `﻿` from the first line only.
     - Feeds that generator to `csv.reader`.
     - Records `start = reader.line_num + 1` before each `next()`, so multi-line quoted rows and skipped blank lines are both counted correctly.
     - Maps the header with a first-occurrence-wins name → index dict.
     - Runs the per-row checks in the locked order.
     - Keeps an `id → first line` dict to detect duplicates.
   - `parse_csv(path)` opens the file with `encoding="utf-8-sig", newline=""` and returns `parse_lines(f)` inside the `with` block.
   - Calendar validation uses `datetime.date(int(y), int(m), int(d))` after the regex. `date.fromisoformat` is not used, because it is looser on 3.11+ and differs across versions.
2. **Report (`src/ledger/report.py`).**
   - `RATES` is the constant mapping. `CategoryTotal` and `MonthlyReport` are frozen dataclasses, and `MonthlyReport.to_dict()` emits amounts as `str(Decimal)`.
   - `monthly_report` first validates its arguments, each failure raising `ValueError`:
     - `month` must fully match the ASCII pattern `[0-9]{4}-(0[1-9]|1[0-2])`.
     - `base` must be in `rates`.
     - `top` must be `None` or at least 1.
   - It then filters on `(t.date.year, t.date.month)` and converts each amount inside `decimal.localcontext()`.
   - It accumulates exact positive, negative, overall and per-category sums, and passes each through one helper that quantizes to `Decimal("0.01")` with `ROUND_HALF_EVEN` and maps negative zero to `Decimal("0.00")`.
   - It sorts categories by `(-abs(total), name)` and slices to `top`.
3. **CLI (`src/ledger/cli.py`, `src/ledger/__main__.py`).**
   - `main(argv=None) -> int` builds an `argparse` parser with `add_subparsers(dest="command", required=True)`. That `required` form works on 3.10.
   - The `report` subparser takes:
     - a positional `file`;
     - a required `--month` with a `type` callable that raises `argparse.ArgumentTypeError` on a bad month;
     - `--base`, with `choices=("ILS", "USD", "EUR")` and default `ILS`;
     - `--top`, with a `type` callable that accepts integers of at least 1;
     - `--json` as `store_true`.
   - Parsing and reporting run in one `try` block. The whole read is covered because the file is decoded lazily while parsing:
     - `OSError` or `UnicodeDecodeError` → `parser.error(...)`, which exits 2 and writes only to stderr.
     - `LedgerError` → `error: {args.file}:{e.line}: {e.reason}\n` on stderr, return 3.
   - The text renderer builds the 13-line layout, or `categories: none` for an empty month. JSON output is `json.dumps(report.to_dict())` followed by a newline.
   - `__main__.py` calls `raise SystemExit(main())`.
   - Output is complete before anything is printed, so a failure never leaves partial stdout.

**Alternatives rejected**
- `csv.DictReader`: it cannot report start lines, and it lets the last duplicate column win (hld §6).
- `float`: it loses exactness.
- Rounding each transaction: it breaks criterion 11.
- A `[project.scripts]` console entry: it is out of scope and would change `pyproject.toml`.
- Driving `main()` in-process in the CLI tests: criterion 25 forbids it.

## Ordered implementation steps

1. **Create the parser fixtures.** Write these with byte-exact tooling (e.g. a Python one-off), not an editor, and do not commit the tooling. Covers criteria 1, 3 and 7.
   - `tests/fixtures/ledger/sample.csv`. Header `id,date,amount,currency,category,memo`, then:
     - `t001,2026-02-27,-99.99,ILS,groceries,…`
     - `t002,2026-03-01,12000.00,ILS,salary,…`
     - `t003,2026-03-02,-1500.00,ILS,rent,` (empty memo)
     - `t004,2026-03-05,-400.50,ILS,groceries,"…, …"` (quoted memo)
     - `t005,2026-03-09,250.00,USD,freelance,…`
     - `t006,2026-03-12,-111.00,EUR,software,…`
     - `t007,2026-03-18,-360.00,ILS,groceries,`
     - `t008,2026-03-25,-321.00,ILS,travel,…`
     - `t009,2026-04-01,-50.00,ILS,groceries,…`

     Any other rows must keep the verified totals.
   - `tests/fixtures/ledger/bom_blank.csv`: starts with `EF BB BF`, has a blank line and a whitespace-only line between two rows, one row with an empty memo, and one row with a quoted memo containing a comma.
   - `tests/fixtures/ledger/empty.csv`: zero bytes.
2. **Add the model.** In `src/ledger/_parse.py`, add `Transaction` and `LedgerError`. Covers criteria 1 and 5. Test layer: pytest `package-api`, in `tests/test_ledger_parse.py`.
3. **Add `parse_lines` and `parse_csv`.** In the same module, add the BOM strip, start-line tracking, blank-record skip, header mapping (missing columns listed in canonical order; empty input gives `missing header`), the per-row checks in the locked order with exact reasons, and duplicate-id detection. Covers criteria 1–8. Test layer: pytest `package-api`.
4. **Export the parser API.** Create `src/ledger/__init__.py` with a docstring and an `__all__` listing `LedgerError`, `Transaction`, `parse_csv` and `parse_lines`. Covers the work item t1 public API. Test layer: pytest, which imports `from ledger import …`.
5. **Write the parser tests.** Write `tests/test_ledger_parse.py`. Covers criteria 1–8. Test layer: pytest `package-api`. It must cover:
   - the sample file, value by value (exact `Decimal("12000.00")`, frozen-ness via `dataclasses.FrozenInstanceError`);
   - header reordering, stripping and extra columns, including a duplicate column where the first occurrence wins;
   - a byte-level check that `bom_blank.csv` starts with the BOM and contains a whitespace-only line, plus its parsed result;
   - header-only input;
   - each reason in criterion 5, parametrized, including `NaN`, `Infinity`, `1e2`, `1_000`, `0.00` and `-0`;
   - a multi-line quoted row reported at its start line, and blank lines counted in line numbers;
   - the duplicate id with a blank line between the two rows;
   - both header errors, including `empty.csv` (asserting it is 0 bytes);
   - `parse_lines(io.StringIO(...))`, with and without a BOM, matching `parse_csv` on the same text.
6. **Add the t1 CHANGELOG line.** Add one line under `## Unreleased` in `CHANGELOG.md`, e.g. `- SCRUM-18: add the \`ledger\` package's CSV parser (\`parse_csv\`, \`parse_lines\`).`. Covers PLAY-G4. Test layer: none; the repo gate checks it.
7. **Add the report module.** Create `src/ledger/report.py` with `RATES`, `CategoryTotal`, `MonthlyReport.to_dict()`, `monthly_report`, the argument validation, the local Decimal context, the round-once helper with the negative-zero fix, the ordering and the `top` slice. Covers criteria 9–18. Test layer: pytest `package-api`.
8. **Export the report API.** Extend `src/ledger/__init__.py` imports and `__all__` with `CategoryTotal`, `MonthlyReport`, `RATES` and `monthly_report`. Covers the t2 public API. Test layer: pytest.
9. **Write the report tests.** Write `tests/test_ledger_report.py`, using `parse_csv` on `sample.csv` and building `Transaction` values directly where needed. Covers criteria 9–18. Test layer: pytest `package-api`. It must cover:
   - the March report in ILS (criterion 9) and in USD (criterion 10);
   - the 0.05 ILS → EUR cases for one and three transactions;
   - 5 ILS / -2 ILS formatting through `str`;
   - a no-negative-zero case (e.g. +0.01 and -0.01 → net `0.00`);
   - `top` set to 2, to a large value and to `None`;
   - a tie case;
   - the empty month, comparing `to_dict()` exactly;
   - February only;
   - custom `rates`;
   - each bad `month`, `base` and `top` raising `ValueError`, asserting it is not a `LedgerError`;
   - one run under a modified global `decimal.getcontext()` (e.g. `prec=3`, `ROUND_DOWN`, restored afterwards) that still gives the same figures.
10. **Add the t2 CHANGELOG line.** Add one SCRUM-18 line under `## Unreleased` in `CHANGELOG.md` for `monthly_report`. Covers PLAY-G4.
11. **Create the CLI fixture.** Create `tests/fixtures/ledger/bad_amount.csv`: line 1 the header, line 2 a valid row, line 3 a row with amount `-2.505`. Covers criterion 23.
12. **Add the CLI.** Create `src/ledger/cli.py` (`main`, the parser, the renderers, the error mapping) and `src/ledger/__main__.py`. Change `src/ledger/__init__.py` only if an export is needed; none is planned. Covers criteria 19–24. Test layer: pytest `package-api`, through a subprocess.
13. **Write the CLI tests.** Write `tests/test_ledger_cli.py` with a helper that runs `subprocess.run([sys.executable, "-m", "ledger", *args], cwd=REPO_ROOT, capture_output=True, text=True)`, with `REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent` and relative FILE strings. Covers criteria 19–25. Test layer: pytest `package-api`. It must cover:
    - the exact 13-line stdout and empty stderr;
    - JSON with `--base USD --top 1`, parsed with `json.loads`;
    - the empty month ending with `categories: none`;
    - each usage error from criterion 22, plus a non-UTF-8 file written to `tmp_path`, each giving exit 2, empty stdout and non-empty stderr;
    - the exact stderr and exit 3 for `bad_amount.csv`;
    - `report --help` giving exit 0 with `--month` in stdout;
    - identical output from two runs (determinism).
14. **Add the t3 CHANGELOG line.** Add one SCRUM-18 line under `## Unreleased` in `CHANGELOG.md` for `python -m ledger report`. Covers PLAY-G4.

**Cross-cutting checks**
- Authorization, tenancy and concurrency do not apply: the work is one local process with no shared state.
- Validation and error paths are the core of steps 3, 7 and 12.
- Dependencies are acquired only by `pip install -e ".[test]"` (pytest). Re-run it after `src/ledger/` first appears, so that a pod with an older editable install sees the new package.
- No generated deliverables and no binaries; all fixtures are under 1 KB.

## Work-item mapping

| Step(s) | Work item | Title |
|---|---|---|
| 1–6 | t1 | ledger: Transaction model, LedgerError and strict CSV parser (parse_csv / parse_lines) |
| 7–10 | t2 | ledger: monthly_report with fixed-rate conversion, round-once totals, ordering, top-N and to_dict |
| 11–14 | t3 | ledger: `python -m ledger report` command line with text/JSON output and exit codes 0/2/3 |

Each work item is self-contained. Its tests pass on top of the previous items alone, and each adds its own `CHANGELOG.md` line.

## Verification and CI gate

- **Canonical gate.** From the repo root, run `pip install -e ".[test]"` and then `pytest`, once, locally on the committed SHA. This is the `test` job in `.github/workflows/ci.yml:12-24`, on Python 3.12.
- **Test layer.** The only declared layer is `package-api` (`pytest`). It runs unprivileged in a pod, and the provider run at the exact head is authoritative (`.factory/testing.md`).
- **Provider CI.** No CI change is needed. `CI_FAIL` must not be created.
- **What the gate must show.** `pytest` passes with these results:
  - Every existing test passes unchanged.
  - `tests/test_ledger_parse.py` covers criteria 1–8, `tests/test_ledger_report.py` covers 9–18, and `tests/test_ledger_cli.py` covers 19–25.
  - No test is skipped or xfailed.
- **Repo-gate obligations.**
  - Each pull request diff touches `CHANGELOG.md` under `## Unreleased` (PLAY-G4).
  - All Python is under `src/` or `tests/`, and no file is over 200 KB.
- **Factory obligations.** No `.factory/delivery-assets` entry is needed, because no binary of 1 MiB or more is added. `.factory/testing.md` is unchanged.

## Risks and scope guards

**Risks and mitigations**
- **Fixture bytes silently stripped.** An editor could drop the BOM, the whitespace-only line or the zero-byte file. Mitigation: write the fixtures byte-exact, and have the step 5 tests assert the raw bytes.
- **Start-line errors on multi-line rows.** Mitigation: step 3 records `line_num + 1` before each read, and step 5 tests a multi-line row.
- **3.11+-only APIs slipping in.** For example, `date.fromisoformat` would accept loose formats on 3.11+. Mitigation: use regex plus `datetime.date(...)`, `add_subparsers(required=True)`, and no 3.11+ stdlib features. CI runs on 3.12 only, so review must check the 3.10 floor.
- **Partial stdout before an error.** Mitigation: parse and build the report completely before writing anything to stdout.
- **Caller's Decimal context leaking in.** Mitigation: do all the arithmetic inside `decimal.localcontext()`, tested in step 9.
- **Stale editable install in a pod.** Mitigation: re-run `pip install -e ".[test]"` before `pytest`.

**The implement phase must NOT:**
- edit any existing file other than adding SCRUM-18 lines under `## Unreleased` in `CHANGELOG.md`. In particular, leave `pyproject.toml`, `README.md`, `.github/workflows/ci.yml`, `.factory/**`, `src/testbed_utils/**`, `src/guestbook/**` and the existing tests and fixtures untouched;
- add a `[project.scripts]` entry, a `conftest.py`, `tests/__init__.py`, `sys.path` manipulation or any third-party dependency;
- add a `.gitattributes`, a linter or other tooling;
- add features beyond the criteria: no other formats, no live rates, no config files, no colour, no multi-month reports;
- skip, delete, xfail or weaken any test or gate check to get a green run. A check that cannot pass is reported as blocked;
- edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
