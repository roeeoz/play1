# Implementation plan — US-02 Number summary console script (testbed-num-summary)

Work item: **t1** · Repo: `roeeoz/play1` (`971bf272-f661-4343-ba13-83764c3aec1f`) · Traces: R9–R14 · RK1, RK2 · Single PR

## 1. Context

US-01 is merged on `main`: `src/testbed_utils/numutils.py` exposes `mean`, `median` and `percentile`, and `tests/test_numutils.py` already asserts the two downstream values this script relies on (`percentile([10, 20, 30], 90) == 28`, `percentile([42], 90) == 42`). This story adds a `testbed-num-summary` console script that reads whitespace- or newline-separated numbers from a file path or from stdin and prints six fixed-order lines (`count`, `min`, `max`, `mean`, `median`, `p90`), so a package user can summarize a list of numbers without writing code or installing numpy. The supplied path must stay inside the current working directory at invocation, and empty input or a disallowed path must produce exactly one stderr line and a non-zero exit.

## 2. Approach

One work item (t1), one PR, four kinds of change:

- a new module `src/testbed_utils/numsummary.py` owning the whole CLI;
- one line in `pyproject.toml` `[project.scripts]`;
- a new test file `tests/test_num_summary_cli.py`;
- three text fixtures under `tests/fixtures/`.

The CLI must **not** live in `numutils.py`: `tests/test_numutils.py::TestDocstringExamples` asserts that module's public names are exactly `{mean, median, percentile}`, so any new public name there breaks the suite. `__init__.py`, `numutils.py`, `test_numutils.py`, CI, README and both dependency lists are untouched. Conventions are copied from the repo's one existing CLI, `pdf-extract` in `pdfutils.py` (argparse, `Error:` prefix on stderr, exit 1) and its harness in `tests/test_pdf_extract_cli.py` (patch `sys.argv`, capture stdout/stderr, normalise `SystemExit`). The repo has no linter, formatter or coverage tool (`.factory/testing.md`); the whole gate is `pip install -e ".[test]" && pytest` on Python 3.12.

Behavior pinned beyond the spec, all verified with a local prototype:

- **Formatting.** A float that is integral prints via `int()` (`3.0` → `3`); anything else via `str()` (`4.6` stays `4.6`). Integer tokens parse as `int`, other numeric tokens as `float`. `nan`, `inf` and non-numeric tokens are skipped; a file with only such tokens is empty input.
- **Containment.** Both the supplied path and the cwd are `.resolve()`d, then compared with `==` or `Path.is_relative_to` (Python 3.9+; repo requires 3.10+). Verified on macOS where `tmp_path` sits under the `/var` → `/private/var` symlink: `sub/../numbers.txt` accepted; `../x.txt`, `sub/../../x.txt`, `/etc/passwd` and an in-cwd symlink pointing outside all rejected; a missing file inside cwd passes the check and fails at open time.
- **Errors.** `Error:` prefix on stderr, exit 1, nothing on stdout, matching `pdf-extract`.
- **Help.** argparse output. The description must stay at or under 76 characters, otherwise argparse wraps it at its default width and it is no longer one line. The HLD's sample sentence is 97 characters and wraps; a shorter description is pinned below.

Order of work: module → pyproject line → fixtures → tests → local verification → PR. No sequencing constraints beyond that; t1 has no dependencies.

## 3. Steps

### Step 1 — Clone and branch (t1)

Clone `https://github.com/roeeoz/play1`, branch `feat/us-02-num-summary` from `main` (or the platform-assigned branch). Read `AGENTS.md`/`CLAUDE.md` and `.factory/memory/` if present. Confirm no `CI_FAIL` file exists at the repo root and do not create one.

### Step 2 — Create `src/testbed_utils/numsummary.py` (t1)

New file implementing this contract:

```python
"""Console script: summarize the numbers in a file or on standard input."""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from testbed_utils.numutils import mean, median, percentile

# Keep under 77 characters so argparse prints it on one line at 80 columns.
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

Implementer notes:

- Containment is checked before any `open`; a rejected path is never read. Content is only ever read as text (`read_text`), never executed or imported.
- `UnicodeDecodeError` is a `ValueError` subclass, not an `OSError`, so it is caught explicitly to keep the `Cannot open` wording for binary files.
- The empty-input message must contain `no numbers found`; the path message must contain `not allowed`. The two wordings must not overlap.
- `int()` accepts underscores (`1_000` → 1000) and `float()` accepts `1e3`. Both are acceptable and need no test.
- Do not lengthen `_DESCRIPTION` past 76 characters.

### Step 3 — Edit `pyproject.toml` (t1)

Add exactly one line under `[project.scripts]`, after the existing `pdf-extract` entry:

```toml
testbed-num-summary = "testbed_utils.numsummary:main"
```

No other change to the file; `dependencies` and `optional-dependencies` stay as they are (R13).

### Step 4 — Add fixtures under `tests/fixtures/` (t1)

| File | Content |
| --- | --- |
| `tests/fixtures/numbers.txt` | `1 2 3 4 5` followed by a newline |
| `tests/fixtures/single.txt` | `42` followed by a newline |
| `tests/fixtures/empty.txt` | a single newline (whitespace-only, so it is not a zero-byte file that tooling might drop) |

Confirm with `git status` that `.gitignore` does not exclude them.

### Step 5 — Create `tests/test_num_summary_cli.py` (t1)

Copy the `run_main` harness from `tests/test_pdf_extract_cli.py` and extend it with a `stdin_text=""` parameter that patches `sys.stdin` with `io.StringIO(stdin_text)` alongside the `sys.argv` patch; it returns `(exit_code, stdout, stderr)`. Define `FIXTURES = Path(__file__).parent / "fixtures"`. Every file-based test first calls `monkeypatch.chdir(...)` so results do not depend on where pytest is launched from. Cases:

| Class | Case | Setup | Assertion |
| --- | --- | --- | --- |
| `TestFileInput` | AC1 happy path | `chdir(FIXTURES)`, arg `numbers.txt` | stdout `== "count: 5\nmin: 1\nmax: 5\nmean: 3\nmedian: 3\np90: 4.6\n"`, stderr `""`, exit 0 |
| `TestFileInput` | AC3 single number | `chdir(FIXTURES)`, arg `single.txt` | stdout `== "count: 1\nmin: 42\nmax: 42\nmean: 42\nmedian: 42\np90: 42\n"`, exit 0 |
| `TestFileInput` | AC4 empty file | `chdir(FIXTURES)`, arg `empty.txt` | exit 1, stdout `""`, stderr exactly one line containing `no numbers found` |
| `TestFileInput` | only junk tokens | `tmp_path` file containing `nan inf -inf abc 0x10` | same assertions as AC4 |
| `TestFileInput` | missing file | `chdir(tmp_path)`, arg `missing.txt` | exit 1, stdout `""`, stderr one line starting `Error: Cannot open` |
| `TestFileInput` | directory | `chdir(tmp_path)`, `sub/` created, arg `sub` | exit 1, stdout `""`, stderr one line starting `Error:` |
| `TestStdinInput` | AC2 happy path | no args, stdin `"10\n20\n30\n"` | stdout `== "count: 3\nmin: 10\nmax: 30\nmean: 20\nmedian: 20\np90: 28\n"`, exit 0 |
| `TestStdinInput` | empty stdin | no args, stdin `""` | exit 1, stdout `""`, one stderr line containing `no numbers found` |
| `TestStdinInput` | mixed tokens | stdin `"1 x 2\n"` | stdout contains `count: 2` and `mean: 1.5` (non-integral keeps default float form) |
| `TestStdinInput` | float tokens | stdin `"1.5 2.5"` | stdout contains `mean: 2` (integral float collapses) |
| `TestPathSafety` | AC6 `..` resolving inside cwd | `chdir(tmp_path)`, write `numbers.txt` (`1 2 3 4 5`) and create `sub/`, arg `sub/../numbers.txt` | AC1 output, exit 0 |
| `TestPathSafety` | AC5 rejected paths (parametrized) | `chdir(tmp_path)`, args `../x.txt`, `sub/../../x.txt`, `/etc/passwd` | exit 1, stdout `""`, one stderr line containing `not allowed` and not containing `no numbers` |
| `TestPathSafety` | escaping symlink | file with valid numbers in `tmp_path_factory.mktemp("outside")`, `tmp_path/link` symlinked to it via `os.symlink`, `chdir(tmp_path)`, arg `link` | rejected as above; the valid content proves nothing was read |
| `TestHelp` | AC7 help | arg `--help` | exit 0, stderr `""`, stdout contains `usage:`, and `" ".join(stdout.split())` contains `_DESCRIPTION` |

Use `pytest.mark.parametrize` for the rejected paths to keep the file near 120 lines. "Exactly one line" assertions use `stderr.count("\n") == 1` and `stderr.endswith("\n")`.

### Step 6 — Verify locally (t1)

From the repo root:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[test]"
pytest
printf "10\n20\n30\n" | testbed-num-summary
testbed-num-summary tests/fixtures/numbers.txt
testbed-num-summary /etc/passwd; echo "exit=$?"
testbed-num-summary --help
git diff --stat main
git status --short
```

Expected: full suite green including `tests/test_numutils.py`; the two summary runs print the AC2 and AC1 lines exactly; the `/etc/passwd` run prints one `Error: path not allowed ...` line and `exit=1`; help shows the description on one line; the diff touches exactly `pyproject.toml`, the new module, the new test file and three fixtures, under 300 changed lines; no `CI_FAIL` file.

### Step 7 — Commit and open the PR (t1)

One commit: `Add testbed-num-summary console script (US-02)`. PR title matches. PR body references work item t1, story US-02, requirements R9–R14 and risks RK1/RK2; lists the touched files; pastes the pytest summary line; and records the pinned decisions from §2 (integral-collapse formatting, token skipping including `nan`/`inf`, exit code 1, cwd anchor with both sides resolved, 76-character help description). End the commit message and PR body with the session's attribution lines. Do not merge; the human approval gate decides.

## 4. Verification

- **AC1, AC2, AC3** (R9, R11): `TestFileInput` AC1/AC3 and `TestStdinInput` AC2 assert whole-stdout equality against the six exact lines, which also proves the `3` vs `3.0` formatting rule, exit 0 and empty stderr.
- **AC4** (R14): `empty.txt`, junk-token and empty-stdin cases assert one stderr line containing `no numbers found`, nothing on stdout, exit 1.
- **AC5** (R10, RK2): three parametrized rejected paths plus the escaping symlink assert one stderr line containing `not allowed`, nothing on stdout, exit 1. The symlink target holds valid numbers, so a leak would print a summary instead of an error.
- **AC6 (spec)** : `sub/../numbers.txt` is accepted and produces the AC1 output.
- **AC7 / story Scenario 6** (R12): `TestHelp` asserts exit 0, `usage:` present and the description present after whitespace normalisation, keeping the test stable across terminal widths.
- **R13**: `git diff main -- pyproject.toml` shows only the one `[project.scripts]` line; no dependency list changes.
- **Existing suite**: `numutils.py` and `__init__.py` are untouched, so `TestDocstringExamples` in `test_numutils.py` stays green and acts as the canary for the module-placement decision.
- **Determinism (G4)**: all tests use fixture files, `tmp_path`, `monkeypatch.chdir` and a patched `sys.stdin`; no real terminal, network or clock.
- **Final acceptance check**: run the Step 6 command block and confirm each expected outcome before opening the PR.

## 5. Risks & open points

- **Help wrapping.** The HLD's sample description (97 characters) wraps under argparse's default width, so a literal "one line" check would fail. Resolved by the 76-character `_DESCRIPTION` and the whitespace-normalised assertion. Reviewers should not lengthen the description without re-checking `--help` output.
- **Test cwd dependence.** Passing absolute fixture paths only works when pytest runs from the repo root (the fixture would otherwise resolve outside cwd and be rejected). Resolved by `monkeypatch.chdir` in every file-based test.
- **macOS versus Linux CI.** Resolving both sides of the containment check handles the macOS `/var` → `/private/var` symlink, verified locally; Linux CI has no such symlink and passes trivially. `os.symlink` is available on both.
- **Stdin blocking.** Running with no path on an interactive terminal waits for EOF. Standard CLI behavior; not tested.
- **Diff size.** Estimated ~90 module lines, ~120 test lines, 3 fixture lines, 1 pyproject line, roughly 215 changed lines. Parametrization of the rejected-path cases keeps headroom under the 300-line cap.
- **Coverage gate unenforced.** The epic's ≥90% target has no `pytest-cov` in the repo; adding one is outside this story, as it was for US-01. Flag in the PR body, do not fix.
- **Numeric formatting latitude.** Spec leaves precision open; this plan pins integral-collapse plus Python default `str()` for non-integral values (no rounding). Adjustable before merge if the PO wants fixed decimals.
- **Local Python.** The prototype ran on Python 3.14; CI runs 3.12 and nothing used is newer than 3.9, so no divergence is expected.
- **Scope lock.** Only the six named statistics; no arbitrary percentile flag, no rounding option, no change to `numutils.py`, `__init__.py`, CI or README.
