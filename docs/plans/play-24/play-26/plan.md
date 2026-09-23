# Implementation plan — US-02 Number summary console script (testbed-num-summary)

| Field | Value |
| --- | --- |
| Work item | t1 — Add testbed-num-summary console script (numsummary module, pyproject entry, CLI tests) |
| Repo | `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`) — single repo, single PR |
| Tier | T2 (one work item, no dependencies) |
| Traces | R9–R14 · RK1, RK2 · spec AC1–AC7 · story US-02 Scenarios 1–6 · HLD §2–§6 |
| Inputs read | `docs/plans/play-24/play-26/{spec,hld,work-items}.md`; `docs/plans/play-24/play-25/plan.md` (US-01 precedent); `src/testbed_utils/{__init__,numutils,pdfutils}.py`; `tests/test_pdf_extract_cli.py`, `tests/test_numutils.py`; `pyproject.toml`; `.gitignore`; `README.md`; `.factory/testing.md`; `.github/workflows/ci.yml` |

## 1. Context

US-01 is merged on `main`: `src/testbed_utils/numutils.py` exposes `mean`, `median` and
`percentile`, re-exported from the package root, and `tests/test_numutils.py` already pins the
two downstream values this script relies on (`percentile([10, 20, 30], 90) == 28`,
`percentile([42], 90) == 42`). Package users still have no zero-code way to summarize a list of
numbers. This story adds a `testbed-num-summary` console script that reads whitespace- or
newline-separated numbers from a file path or from stdin and prints six fixed-order lines
(`count`, `min`, `max`, `mean`, `median`, `p90`). A supplied path must stay inside the current
working directory at invocation (RK2); empty input or a disallowed path yields exactly one
stderr line, nothing on stdout, and a non-zero exit.

## 2. Research findings

### 2.1 Change surface

| Path | Action | Why |
| --- | --- | --- |
| `src/testbed_utils/numsummary.py` | **create** | Whole CLI: argparse, containment check, text-only read, token parsing, formatting, `main()`. Must be its own module (see §2.3). |
| `pyproject.toml` | **edit** (1 line) | `testbed-num-summary = "testbed_utils.numsummary:main"` under `[project.scripts]`, after `pdf-extract`. `dependencies` and `optional-dependencies` unchanged (R13). |
| `tests/test_num_summary_cli.py` | **create** | AC coverage via the `run_main` harness pattern (§2.4). |
| `tests/fixtures/numbers.txt` | **create** | `1 2 3 4 5` + newline (AC1). |
| `tests/fixtures/single.txt` | **create** | `42` + newline (AC3). |
| `tests/fixtures/empty.txt` | **create** | a single newline — whitespace-only, so not a zero-byte file (AC4). |

**Not touched:** `src/testbed_utils/numutils.py`, `src/testbed_utils/__init__.py`,
`tests/test_numutils.py`, `.github/workflows/ci.yml`, `README.md`, `.factory/`, any dependency
list, `__version__`. No `CI_FAIL` exists at the root today (verified) and none may be created.
`git check-ignore` confirms `.gitignore` does not exclude `tests/fixtures/*.txt`.

### 2.2 Toolchain

- `pyproject.toml`: `requires-python >= 3.10`; runtime dep `pypdf` only; test extra `pytest>=8`; `testpaths = ["tests"]`, `addopts = "-q"`; setuptools `src/` layout, so tests import only the installed distribution (no `conftest.py`, no `sys.path` hacks).
- Gate (`.factory/testing.md`, `ci.yml`): `pip install -e ".[test]"` then `pytest` on Python 3.12 (job **test**); job **gate** fails iff `CI_FAIL` exists. No linter, formatter, type checker or coverage tool exists; install + pytest is the complete check. Layer id `package-api`, class production-path, run by the canonical gate.
- Local Python is 3.14; nothing planned uses anything newer than 3.9 (`Path.is_relative_to`, `int | float` in annotations under `from __future__ import annotations`).

### 2.3 Existing conventions to copy (and one constraint)

From `src/testbed_utils/pdfutils.py` (the only existing CLI):

- `argparse.ArgumentParser(description=...)`; positional argument; `args = parser.parse_args()`.
- Library function raises `ValueError(f"Cannot open '{path}': ...")`; `main()` catches `ValueError`, prints `Error: {exc}` to stderr, `sys.exit(1)`; success prints to stdout and returns.
- Module docstring one line; `from __future__ import annotations`; stdlib imports then package imports.

From `tests/test_pdf_extract_cli.py`:

- `run_main(args)` patches `sys.argv` with `patch("sys.argv", [prog] + args)`, wraps `main()` in `redirect_stdout`/`redirect_stderr`, converts `SystemExit` to an exit code (`None` → 0) and returns `(exit_code, stdout, stderr)`.
- `FIXTURES = pathlib.Path(__file__).parent / "fixtures"`; one `Test<Scenario>` class per behaviour group; plain asserts.

Constraint from `tests/test_numutils.py::TestDocstringExamples`: the set of public functions
defined in `numutils` must equal exactly `{mean, median, percentile}`, and every one must carry
a `>>>` example. Adding `main()` or any helper to `numutils.py` breaks the suite. The CLI
therefore lives in a new module, mirroring `pdfutils.py` owning its own `main()`.

### 2.4 Contracts

**Consumed (US-01, unchanged):**

| Name | Behaviour relied on |
| --- | --- |
| `mean(numbers)` | `sum / len` → float (`mean([1,2,3,4,5]) == 3.0`) |
| `median(numbers)` | middle element (raw type) or mean of the two middle values |
| `percentile(numbers, 90)` | linear interpolation between nearest ranks; `4.6`, `28.0`, `42.0` for the three AC inputs |

**Provided (CLI, user-facing):**

| Surface | Contract |
| --- | --- |
| Invocation | `testbed-num-summary [PATH]`; `--help` |
| Success stdout | exactly six lines `count: <v>`, `min: <v>`, `max: <v>`, `mean: <v>`, `median: <v>`, `p90: <v>`; stderr empty; exit 0 |
| Value format | integral values print with no decimal part (`3`, `28`, `42`); non-integral values print via Python's default `str()` (`4.6`, `1.5`); integer tokens parse as `int`, other numeric tokens as `float` |
| Empty input | stderr `Error: no numbers found in input`; stdout empty; exit 1 |
| Disallowed path | stderr `Error: path not allowed: '<path>' is outside the current directory`; stdout empty; exit 1; file never opened |
| Unreadable path inside cwd | stderr `Error: Cannot open '<path>': <os error>`; stdout empty; exit 1 |
| `--help` | argparse help on stdout whose description line is the one-line purpose summary; exit 0 |

Cross-repo contracts: none. Wiring: the one `[project.scripts]` line.

### 2.5 Resolved unknowns

| Question | Resolution | Basis |
| --- | --- | --- |
| Module placement | New `src/testbed_utils/numsummary.py`. | `TestDocstringExamples` forbids new public names in `numutils.py`; HLD §2/§6. |
| Numeric formatting (spec §8) | Integral-collapse: a `float` with `is_integer()` prints as `int`; otherwise `str()`. No rounding. | Only rule that yields `mean: 3`, `p90: 28`, `p90: 42` **and** `p90: 4.6` while keeping full precision; `:g` would truncate to 6 significant digits. Verified against all three AC inputs (§2.6). |
| Exit code (spec §8) | `1` for every error path. | Matches `pdf-extract`; spec leaves it unpinned. |
| Error wording | `Error:` prefix; empty-input message contains `no numbers found`; path message contains `not allowed`; the two never overlap. | AC4/AC5 need distinct wordings; `pdf-extract` convention. |
| Directory anchor | `Path.cwd().resolve()` at invocation; accept iff `resolved == cwd or resolved.is_relative_to(cwd)`. | Spec §6; resolving **both** sides is required on macOS where temp dirs sit under the `/var` → `/private/var` symlink (§2.6). |
| Symlink inside cwd pointing outside | Rejected (resolution follows the link). | HLD §6; work-item AC; verified. |
| Missing file / directory inside cwd | Passes containment, fails at open with `Cannot open` wording, exit 1. | `FileNotFoundError` / `IsADirectoryError` are `OSError`; verified. |
| Unparseable tokens | Skipped, not fatal; `nan`, `inf`, `-inf` also skipped (`math.isfinite`); a file with only such tokens is empty input. | Spec edge case "no parseable numbers → empty input"; keeps `min`/`max`/`median` ordering sound. |
| `--help` "one line" | The argparse description is ≤ 76 characters so it renders on one line at 80 columns; the test asserts the description after whitespace normalisation, not a single stdout line. | HLD's 97-char sample wraps (verified); argparse also prints usage/options, as `pdf-extract` does. |
| Fixture location | `tests/fixtures/` alongside the PDFs. | HLD §2; not ignored by `.gitignore` (verified). |

### 2.6 Verification done during research (Python 3.14, macOS, throwaway temp dir)

Prototype of the §3 functions, nothing written to the repo:

| Input | Output |
| --- | --- |
| `"1 2 3 4 5"` | `count: 5` `min: 1` `max: 5` `mean: 3` `median: 3` `p90: 4.6` |
| `"10\n20\n30\n"` | `count: 3` `min: 10` `max: 30` `mean: 20` `median: 20` `p90: 28` |
| `"42\n"` | `count: 1` `min: 42` `max: 42` `mean: 42` `median: 42` `p90: 42` |
| `"1.5 2.5"` | `mean: 2` (integral float collapses), `p90: 2.4` |
| `"1 x 2\n"` | `count: 2`, `mean: 1.5` |
| `"nan inf -inf abc 0x10"`, `"\n"` | empty input |

Containment with cwd = a `tempfile` dir (`/var/folders/...`, resolving to `/private/var/...`):
`numbers.txt`, `sub/../numbers.txt`, `missing.txt`, `sub`, `.` and the absolute cwd path →
accepted; `../x.txt`, `sub/../../x.txt`, `/etc/passwd`, and an in-cwd symlink to an outside
file → rejected. Opening `sub` raises `IsADirectoryError`; `missing.txt` raises
`FileNotFoundError`. A 76-character description prints on one line under argparse at the
default width; the HLD's 97-character sentence wraps onto two.

## 3. Solution proposal

**Approach.** One new stdlib-only module owns the CLI end to end, copying the `pdf-extract`
shape: small pure helpers (`parse_numbers`, `is_within_cwd`, `read_text`, `format_value`,
`summarize`) plus a thin `main()` that maps `ValueError` to one `Error:` line and exit 1. It
consumes `numutils` unchanged, is wired by one `pyproject.toml` line, and is tested through the
installed entry point's `main()` exactly like `tests/test_pdf_extract_cli.py`, with the harness
extended to patch `sys.stdin`.

**Key design decisions.**

1. **Separate module `numsummary.py`, not `numutils.py`** — forced by the public-surface test in `test_numutils.py`; also mirrors `pdfutils.py`.
2. **Containment check resolves both the path and the cwd**, compares with `==` or `Path.is_relative_to`, and runs **before** any open. Content is only read via `Path.read_text` — never executed or imported (R10).
3. **Integral-collapse formatting** (`float.is_integer()` → `int`, else `str()`), not `:g` and not rounding. Satisfies every worked example without losing precision.
4. **Token parsing: `int` first, then finite `float`, else skip.** `nan`/`inf` are skipped so ordering statistics stay meaningful; a junk-only file is empty input (R14).
5. **Errors follow `pdf-extract`:** `Error:` prefix on stderr, exit 1, nothing on stdout; wordings for empty input and disallowed path are distinct. Unreadable-but-contained paths reuse the `Cannot open '<path>': ...` wording. `UnicodeDecodeError` is caught explicitly (it is a `ValueError`, not an `OSError`) so binary files also get the `Cannot open` wording.
6. **Help description pinned at ≤ 76 characters** so argparse prints it on one line at 80 columns; the test normalises whitespace so a narrower terminal cannot break it.
7. **Tests always `monkeypatch.chdir`** into the fixture or `tmp_path` directory so containment results do not depend on where pytest is launched.

**Target module (contract for the implementer):**

```python
"""Console script: summarize the numbers in a file or on standard input."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from testbed_utils.numutils import mean, median, percentile

# Keep at or under 76 characters so argparse prints it on one line at 80 columns.
_DESCRIPTION = (
    "Print count, min, max, mean, median and p90 of numbers from a file or stdin."
)


def _parse_number(token: str) -> int | float | None:
    """Return *token* as an int or finite float, or None if it is not a plain number."""
    try:
        return int(token)
    except ValueError:
        pass
    try:
        value = float(token)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def parse_numbers(text: str) -> list[int | float]:
    """Return every whitespace-separated numeric token in *text*, skipping the rest."""
    return [v for v in map(_parse_number, text.split()) if v is not None]


def is_within_cwd(path: str) -> bool:
    """True if *path*, fully resolved, is the current working directory or beneath it."""
    cwd = Path.cwd().resolve()
    resolved = Path(path).resolve()
    return resolved == cwd or resolved.is_relative_to(cwd)


def read_text(path: str | None) -> str:
    """Read the input as text: stdin when *path* is None, else a file inside the cwd."""
    if path is None:
        return sys.stdin.read()
    if not is_within_cwd(path):
        raise ValueError(f"path not allowed: '{path}' is outside the current directory")
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise ValueError(f"Cannot open '{path}': {exc}") from exc


def format_value(value: int | float) -> str:
    """Print integral values without a decimal part; otherwise Python's default."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def summarize(numbers: list[int | float]) -> list[tuple[str, int | float]]:
    """Return the six statistics in output order."""
    return [
        ("count", len(numbers)),
        ("min", min(numbers)),
        ("max", max(numbers)),
        ("mean", mean(numbers)),
        ("median", median(numbers)),
        ("p90", percentile(numbers, 90)),
    ]


def main() -> None:
    parser = argparse.ArgumentParser(prog="testbed-num-summary", description=_DESCRIPTION)
    parser.add_argument(
        "path",
        nargs="?",
        help="Text file of whitespace-separated numbers (default: read stdin).",
    )
    args = parser.parse_args()

    try:
        numbers = parse_numbers(read_text(args.path))
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if not numbers:
        print("Error: no numbers found in input", file=sys.stderr)
        sys.exit(1)

    for name, value in summarize(numbers):
        print(f"{name}: {format_value(value)}")
```

**Target `pyproject.toml` fragment after edit:**

```toml
[project.scripts]
pdf-extract = "testbed_utils.pdfutils:main"
testbed-num-summary = "testbed_utils.numsummary:main"
```

**Test harness (extends the `pdf-extract` one):**

```python
def run_main(args, stdin_text=""):
    stdout_buf, stderr_buf, exit_code = io.StringIO(), io.StringIO(), 0
    with patch("sys.argv", ["testbed-num-summary"] + args), patch("sys.stdin", io.StringIO(stdin_text)):
        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                main()
            except SystemExit as exc:
                exit_code = exc.code if exc.code is not None else 0
    return exit_code, stdout_buf.getvalue(), stderr_buf.getvalue()
```

## 4. Ordered implementation tasks

All tasks belong to work item **t1**. Order: module → pyproject → fixtures → tests → verify → PR.

| # | Task | Files | Satisfies |
| --- | --- | --- | --- |
| 1 | Work on the platform-assigned branch from `main`. Re-read `.factory/testing.md`. Confirm no `CI_FAIL` at root; never create one. | — | scope guard |
| 2 | Create `src/testbed_utils/numsummary.py` exactly per §3. Do not lengthen `_DESCRIPTION` past 76 characters. | `src/testbed_utils/numsummary.py` | AC1–AC7 · R9, R10, R11, R12, R14 |
| 3 | Add the one `[project.scripts]` line per §3; no other change to the file. | `pyproject.toml` | R9, R13 · work-item AC "registered console script" |
| 4 | Create the three fixtures per §2.1 (`numbers.txt`, `single.txt`, whitespace-only `empty.txt`). `git status` must show them as untracked additions, not ignored. | `tests/fixtures/*.txt` | AC1, AC3, AC4 |
| 5 | Create `tests/test_num_summary_cli.py` per §5, using the §3 harness, `FIXTURES = Path(__file__).parent / "fixtures"`, `monkeypatch.chdir` in every file-based test, `pytest.mark.parametrize` for the rejected paths. | `tests/test_num_summary_cli.py` | AC1–AC7 · R8-style three-case coverage · G4 determinism |
| 6 | Run the §6 gate block locally and tick every expected outcome. | — | test gate |
| 7 | One commit, `Add testbed-num-summary console script (US-02)`. PR title the same. PR body: work item t1, US-02, R9–R14, RK1/RK2; the touched files; the pytest summary line; the pinned decisions (integral-collapse formatting, token skipping incl. `nan`/`inf`, exit 1, cwd anchor with both sides resolved, ≤ 76-char help description); note the unenforced coverage gate (§7). Do not merge — the human approval gate decides. End commit message and PR body with the session's attribution lines. | — | traceability |

## 5. Test plan (layer: `package-api` — pytest under `tests/`, production-path)

Only fixture files, `tmp_path`, `monkeypatch.chdir` and a patched `sys.stdin` are used; no real
terminal, network or clock (G4). "Exactly one stderr line" is asserted as
`stderr.count("\n") == 1 and stderr.endswith("\n")`.

| Class | Test | Setup | Assertion | AC / req |
| --- | --- | --- | --- | --- |
| `TestFileInput` | `test_summary_from_file` | `chdir(FIXTURES)`, arg `numbers.txt` | stdout `== "count: 5\nmin: 1\nmax: 5\nmean: 3\nmedian: 3\np90: 4.6\n"`, stderr `""`, exit 0 | AC1 · R9, R11 |
| `TestFileInput` | `test_single_number` | `chdir(FIXTURES)`, arg `single.txt` | stdout `== "count: 1\nmin: 42\nmax: 42\nmean: 42\nmedian: 42\np90: 42\n"`, exit 0 | AC3 · R11 |
| `TestFileInput` | `test_empty_file` | `chdir(FIXTURES)`, arg `empty.txt` | exit 1, stdout `""`, one stderr line containing `no numbers found` | AC4 · R14 |
| `TestFileInput` | `test_only_junk_tokens` | `chdir(tmp_path)`, file `nan inf -inf abc 0x10` | same as `test_empty_file` | AC4 (edge "no parseable numbers") · R14 |
| `TestFileInput` | `test_missing_file` | `chdir(tmp_path)`, arg `missing.txt` | exit 1, stdout `""`, one stderr line starting `Error: Cannot open` | work-item AC (unreadable path inside cwd) |
| `TestFileInput` | `test_directory_path` | `chdir(tmp_path)`, `sub/` created, arg `sub` | exit 1, stdout `""`, one stderr line starting `Error:` | work-item AC (unreadable path inside cwd) |
| `TestStdinInput` | `test_summary_from_stdin` | no args, `stdin_text="10\n20\n30\n"` | stdout `== "count: 3\nmin: 10\nmax: 30\nmean: 20\nmedian: 20\np90: 28\n"`, exit 0 | AC2 · R9, R11 |
| `TestStdinInput` | `test_empty_stdin` | no args, `stdin_text=""` | exit 1, stdout `""`, one stderr line containing `no numbers found` | AC4 · R14 |
| `TestStdinInput` | `test_mixed_tokens_skipped` | `stdin_text="1 x 2\n"` | stdout contains `count: 2\n` and `mean: 1.5\n` | work-item AC (token skipping, default float form) |
| `TestStdinInput` | `test_integral_float_collapses` | `stdin_text="1.5 2.5"` | stdout contains `mean: 2\n` | work-item AC (value formatting) |
| `TestPathSafety` | `test_dotdot_inside_cwd_accepted` | `chdir(tmp_path)`, write `numbers.txt` = `1 2 3 4 5`, mkdir `sub`, arg `sub/../numbers.txt` | AC1 stdout, exit 0 | AC6 · R10 |
| `TestPathSafety` | `test_escaping_path_rejected[...]` (parametrized: `../x.txt`, `sub/../../x.txt`, `/etc/passwd`) | `chdir(tmp_path)` | exit 1, stdout `""`, one stderr line containing `not allowed` and not `no numbers` | AC5 · R10, RK2 |
| `TestPathSafety` | `test_escaping_symlink_rejected` | outside file with `1 2 3` in `tmp_path_factory.mktemp("outside")`, `os.symlink` to `tmp_path/link`, `chdir(tmp_path)`, arg `link` | rejected as above — valid content proves nothing was read | AC5 · R10, RK2 |
| `TestHelp` | `test_help` | arg `--help` | exit 0, stderr `""`, `usage:` in stdout, `_DESCRIPTION` in `" ".join(stdout.split())` | AC7 · R12 |

Coverage shape per G1: every behaviour group has a happy path, a boundary and an error case.

## 6. Test gate — what it must show

Run from the repo root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
pytest
pytest tests/test_num_summary_cli.py -v
printf "10\n20\n30\n" | testbed-num-summary
testbed-num-summary tests/fixtures/numbers.txt
testbed-num-summary /etc/passwd; echo "exit=$?"
testbed-num-summary --help
git diff --stat main
git diff main -- pyproject.toml
git status --short
test ! -e CI_FAIL && echo "no CI_FAIL"
```

Expected:

- `pytest` — whole suite green, including `tests/test_numutils.py` (its public-surface test is the canary for the module-placement decision) and `tests/test_pdf_extract_cli.py`.
- `pytest tests/test_num_summary_cli.py -v` — 16 tests pass (14 rows above, the rejected-path row expanding to 3).
- The stdin run prints the AC2 six lines exactly; the file run prints the AC1 six lines exactly.
- The `/etc/passwd` run prints one `Error: path not allowed ...` line to stderr and `exit=1`.
- `--help` shows the description on one line and exits 0.
- `git diff --stat main` lists exactly six paths: `pyproject.toml`, `src/testbed_utils/numsummary.py`, `tests/test_num_summary_cli.py`, three `tests/fixtures/*.txt`; roughly 90 + 130 + 3 + 1 ≈ 225 changed lines, under the 300 cap.
- `git diff main -- pyproject.toml` shows only the one `[project.scripts]` line (proves R13).
- No `CI_FAIL` file.

CI's **test** job repeats install + pytest on Python 3.12 (Linux, no `/var` symlink, so containment passes trivially there); the **gate** job stays green while `CI_FAIL` is absent.

## 7. Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **Public-surface test breaks** if any name is added to `numutils.py`. | CLI lives in `numsummary.py`; `numutils.py` untouched. |
| **Naïve printing fails AC1–AC3** (`3.0` vs `3`). | `format_value` integral-collapse; whole-stdout equality tests. |
| **macOS vs Linux containment divergence** (`tmp_path` under `/var` → `/private/var`). | Both sides `.resolve()`d, verified locally in §2.6; tests `monkeypatch.chdir` so behaviour is cwd-independent. |
| **Help wrapping.** argparse width follows the terminal (or `COLUMNS`); a narrow terminal wraps even a short description. | Description ≤ 76 characters for the 80-column default; test asserts after whitespace normalisation. Reviewers must not lengthen `_DESCRIPTION`. |
| **Fixture dropped as empty.** | `empty.txt` holds one newline; `git status` check in task 4. |
| **Stdin blocking** on an interactive terminal with no path. | Standard CLI behaviour; not tested; help text says stdin is the default. |
| **Coverage gate unenforced.** Epic targets ≥ 90 % but no `pytest-cov` exists; adding one edits dependency lists. | Out of scope; flagged in the PR body, not fixed (same call as US-01). |
| **Numeric precision latitude** (spec §8). | Pinned to integral-collapse + default `str()`, no rounding; adjustable before merge if the PO wants fixed decimals. |
| **Python drift** (local 3.14, CI 3.12, floor 3.10). | Nothing newer than 3.9 is used. |
| **Scope lock.** | Only the six paths in §2.1 change. No extra statistics, no arbitrary-percentile or rounding flags, no `__init__.py` re-export of CLI helpers, no CI/README/dependency edits, no `CI_FAIL`, no merge without the human approval gate. |

## 8. Open points for the developer

None blocking. Both spec §8 questions (numeric formatting, exit codes) are closed in §2.5 at no
cost, following the HLD. No `plan-questions.json` is written.
