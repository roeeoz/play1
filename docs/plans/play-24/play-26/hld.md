# HLD — US-02 `testbed-num-summary` console script

Target repo: `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`). Single repo, single PR.

## 1. System Overview
- **What**: a `testbed-num-summary` console script that reads whitespace/newline-separated numbers from a user-supplied file path or from stdin and prints six lines (`count`, `min`, `max`, `mean`, `median`, `p90`) to stdout.
- **Problem**: package users have no zero-code, dependency-free way to summarize a list of numbers.
- **Responsibilities**: argument parsing, path-containment check, text-only reading, token parsing, statistics via existing `numutils` helpers, pinned output formatting, one-line error reporting, `--help`.

## 2. Architecture Overview
- **New module** `src/testbed_utils/numsummary.py` owns the whole CLI (`main()` entry point plus private helpers). It must NOT live in `numutils.py`: `tests/test_numutils.py` asserts that module's public names are exactly `{mean, median, percentile}` and doctests every public function.
- **Consumes** `testbed_utils.numutils.mean/median/percentile` unchanged (US-01, merged).
- **Wiring**: one new line in `pyproject.toml` `[project.scripts]`: `testbed-num-summary = "testbed_utils.numsummary:main"`, sibling of the existing `pdf-extract` entry.
- **Tests**: new `tests/test_num_summary_cli.py` reusing the `run_main` harness pattern from `tests/test_pdf_extract_cli.py` (patch `sys.argv`, redirect stdout/stderr, normalise `SystemExit`), plus small text fixtures under `tests/fixtures/`.
- **External dependencies**: stdlib only (`argparse`, `sys`, `pathlib`). No runtime or test dependency changes. `__init__.py`, `numutils.py`, CI and README are not touched.

## 3. Data Flow Design
Synchronous, single process, no state persisted:
1. Parse argv (optional positional path; `--help`).
2. If a path is given: fully resolve it (symlinks followed, `..` collapsed) and fully resolve the cwd at invocation; reject unless the resolved path equals the cwd or lies beneath it. Otherwise open as text (never exec/import).
3. If no path: read all of stdin as text.
4. Split on whitespace, parse tokens to numbers.
5. If zero numbers: one line on stderr, nothing on stdout, exit 1.
6. Compute count, min, max, `mean()`, `median()`, `percentile(_, 90)`; print six fixed-order lines; exit 0.

## 4. Component Breakdown
| Component | Responsibility | Inputs → Outputs | Repo |
|---|---|---|---|
| `numsummary.py` (new) | CLI entry point, containment check, parsing, formatting, error reporting | argv/stdin/file text → stdout lines, stderr line, exit code | roeeoz/play1 |
| `numutils.py` (existing, consumed) | mean/median/percentile | list of numbers → number | roeeoz/play1 |
| `pyproject.toml` `[project.scripts]` (edited) | expose the script name | — | roeeoz/play1 |
| `tests/test_num_summary_cli.py` + `tests/fixtures/*.txt` (new) | AC coverage | fixtures / simulated stdin → assertions | roeeoz/play1 |

## 5. Interface Contracts
- **CLI**: `testbed-num-summary [PATH]`; `--help`.
- **Success stdout** (exactly six lines, this order): `count: <v>`, `min: <v>`, `max: <v>`, `mean: <v>`, `median: <v>`, `p90: <v>`; exit 0.
- **Value formatting (pinned)**: a value that is integral prints without a decimal part (`3`, `28`, `42`, `1`); a non-integral value prints with Python's default `repr`/`str` for floats (`4.6`). Integer tokens parse as `int`, other tokens as `float`.
- **Error stderr** (exactly one line, nothing on stdout, exit 1), following the `pdf-extract` convention of an `Error:` prefix:
  - no numbers found → e.g. `Error: no numbers found in input`
  - disallowed path → e.g. `Error: path not allowed: <path>` (wording must differ from the empty-input message)
  - unreadable/missing/directory path inside cwd → e.g. `Error: Cannot open '<path>': ...`
- **`--help`**: argparse output whose description is the one-line purpose summary (e.g. `Print count, min, max, mean, median and the 90th percentile of the numbers in a file or on stdin.`); exit 0.
- **Cross-repo contracts**: none.

## 6. Key Technical Decisions
- **Separate module, not `numutils.py`** — forced by the existing public-surface test; also mirrors `pdfutils.py` owning its own `main()`.
- **argparse + `Error:` prefix + exit 1** — reuse the `pdf-extract` convention rather than invent a second CLI style; the spec leaves exit codes unpinned.
- **Resolve both sides of the containment check** — verified necessary on macOS where pytest `tmp_path` is a symlinked `/var/folders/...` path; also covers symlinks inside cwd pointing outward (rejected). `Path.is_relative_to` is available for `requires-python >= 3.10`.
- **Integral-collapse formatting** over `:g` — `:g` silently truncates to 6 significant digits; integral-collapse satisfies every worked example and keeps full precision otherwise.
- **Unparseable tokens are skipped, not fatal** — the spec treats a file with "no parseable numbers" as empty input, implying filtering; `nan`/`inf` tokens are treated as unparseable so ordering of min/max/median is never broken.
- **`--help` reading** — the "one-line summary" is the argparse description line; the test asserts that line is present and exit is 0 rather than asserting a single stdout line (argparse emits usage/options too, as `pdf-extract` does).

## 7. Risks & Constraints
- **Existing suite breaks** if any public name is added to `numutils.py` — mitigated by the new-module decision.
- **Naïve printing fails AC1–AC3** (`3.0` vs `3`) — mitigated by the pinned formatter and exact-line tests.
- **Cross-platform containment** — tests must `monkeypatch.chdir(tmp_path)` and the implementation must resolve cwd too, or macOS and Linux CI diverge.
- **Empty fixture file** — commit `tests/fixtures/empty.txt` as whitespace-only (or create in `tmp_path`) so tooling does not drop a zero-byte file.
- **Line cap / coverage**: ~60–90 source lines, ~100–130 test lines, one pyproject line — well under 300. No coverage tool exists in the repo; nothing to add.
- Scale/performance: not a concern (small in-memory lists, per epic non-goals).
