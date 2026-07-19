# Implementation Plan: testbed-utils CLI Entry Point with --json Support

## Context

The `testbed_utils` package exports six library functions but has no command-line interface; scripting users must write ad-hoc Python wrappers. This ticket adds a `testbed-utils` entry point that exposes all six functions as subcommands and adds a global `--json` flag that routes both success output and errors into machine-readable JSON envelopes, enabling `jq`-based pipelines. No library code changes; all new code is contained in three files.

## Approach

All work is in the `play1` repository. The implementation order is: (1) read existing files to resolve the two open unknowns, (2) edit `pyproject.toml` to wire the entry point, (3) create `src/testbed_utils/cli.py`, (4) create `tests/test_cli.py`, (5) install and run tests. Steps 2–4 have no mutual dependencies once the unknowns are resolved, but step 5 depends on all three. The chosen CLI framework is stdlib `argparse`; no new runtime dependency is introduced.

## Steps

### Step 0 — Read before writing

Before any file is created or edited, read:

- `pyproject.toml` — confirm whether `[project.scripts]` already exists, the package layout (src-layout `src/testbed_utils/` vs. flat `testbed_utils/`), and the Python version floor.
- `src/testbed_utils/__init__.py` (or `testbed_utils/__init__.py` if flat) — confirm `__all__` and the exact import names for the six functions.
- `src/testbed_utils/dateutils.py` — confirm signatures of `days_between`, `humanize_delta`, and `is_weekend`. Critical: verify whether `humanize_delta` accepts a `datetime.timedelta` object or raw integer seconds.
- `src/testbed_utils/textutils.py` — confirm signatures of `slugify`, `truncate` (especially the `suffix` parameter name and default), and `word_count`.
- Any existing test file — confirm class-based or function-based style to match.

### Step 1 — Edit `pyproject.toml`

**Work item:** t1 | **File:** `pyproject.toml`

Add the `[project.scripts]` table after the `[project]` section (insert it if absent; do not duplicate if present):

```toml
[project.scripts]
testbed-utils = "testbed_utils.cli:main"
```

No entry in `[project.dependencies]` is needed — `argparse` is stdlib. Adjust the import path (`testbed_utils.cli` vs `src.testbed_utils.cli`) based on what Step 0 reveals about the package layout.

### Step 2 — Create `src/testbed_utils/cli.py`

**Work item:** t1 | **File:** `src/testbed_utils/cli.py` (adjust path if flat-layout)

Implement the following components in order:

**2a. Imports**
```python
import argparse
import json
import sys
from datetime import date, timedelta

from testbed_utils import days_between, humanize_delta, is_weekend, slugify, truncate, word_count
```

**2b. `CustomParser` subclass**

Override `error(self, message)` to intercept argparse parse errors before `parse_args()` completes:
```python
class CustomParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._json_mode = "--json" in sys.argv

    def error(self, message):
        if self._json_mode:
            print(json.dumps({"error": message}))
            sys.exit(1)
        else:
            super().error(message)
```
Checking `sys.argv` at construction time is safe because `--json` is a global flag that must precede the subcommand name — its position in `sys.argv` is deterministic.

**2c. `_emit_error` helper**
```python
def _emit_error(msg, json_mode):
    if json_mode:
        print(json.dumps({"error": msg}))
    else:
        print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)
```

**2d. `_dispatch` function**

Perform per-subcommand argument coercion and library dispatch. Raise `ValueError` on bad inputs so `main()` catches them uniformly:

- `days-between`: `date.fromisoformat(args.start)`, `date.fromisoformat(args.end)` → `days_between(start, end)`
- `humanize-delta`: `timedelta(seconds=int(args.delta))` → `humanize_delta(delta)` *(adjust if Step 0 reveals `humanize_delta` takes raw int seconds instead of a `timedelta`)*
- `is-weekend`: `date.fromisoformat(args.day)` → `is_weekend(day)`
- `slugify`: `slugify(args.text)` (pass-through)
- `truncate`: `int(args.max_length)` → call `truncate(args.text, max_length)` or `truncate(args.text, max_length, args.suffix)` depending on whether `args.suffix is not None`; use `None` as sentinel to avoid overriding the library's own default
- `word-count`: `word_count(args.text)` (pass-through)

**2e. `main()` function**

Build the root `CustomParser` with `--json` (store_true), add `add_subparsers(dest='subcommand', required=True)`, register the six subparsers with their positional args:

- `days-between`: positionals `start`, `end`
- `humanize-delta`: positional `delta`
- `is-weekend`: positional `day`
- `slugify`: positional `text`
- `truncate`: positionals `text`, `max_length`; optional positional `suffix` with `nargs='?'`, `default=None`
- `word-count`: positional `text`

Then:
```python
args = parser.parse_args()
json_mode = args.json
try:
    result = _dispatch(args)
except Exception as e:
    _emit_error(str(e), json_mode)
if json_mode:
    print(json.dumps({"result": result}))
else:
    print(str(result))
```

`json.dumps` correctly serializes Python `True`/`False` to JSON `true`/`false` and `int`/`float` to JSON numbers without any manual type checks.

### Step 3 — Create `tests/test_cli.py`

**Work item:** t1 | **File:** `tests/test_cli.py`

Class-based pytest suite (match existing test file style confirmed in Step 0). All tests invoke the real installed entry point via:
```python
def run(*args):
    return subprocess.run(["testbed-utils", *args], capture_output=True, text=True)
```

Four test classes:

**`TestPlainText`** — one method per subcommand, correct args:
- Assert `returncode == 0`, expected value in `stdout.strip()`, `stderr == ""`
- `days-between 2024-01-01 2024-03-01` → stdout `"60"`
- `humanize-delta 3600` → stdout non-empty
- `is-weekend 2024-01-06` → stdout `"True"` (Saturday)
- `slugify "Hello World"` → stdout non-empty
- `truncate "Hello World" 5` → stdout non-empty, `returncode == 0`
- `word-count "one two three"` → stdout `"3"`

**`TestJsonOutput`** — one method per subcommand with `--json` prefix:
- Assert `returncode == 0`, `json.loads(stdout)["result"]` equals expected value with correct Python type
- `days-between`: `result == 60` and `isinstance(result, int)`
- `humanize-delta`: `isinstance(result, str)`
- `is-weekend 2024-01-06`: `result is True`
- `is-weekend 2024-01-08`: `result is False` (Monday)
- `slugify`: `isinstance(result, str)`
- `truncate`: `isinstance(result, str)`
- `word-count`: `result == 3` and `isinstance(result, int)`

**`TestErrors`** — error paths:
- Wrong arg count with `--json`: `returncode == 1`, `json.loads(stdout)["error"]` is non-empty string
- Wrong arg count without `--json`: `returncode == 1`, `stdout == ""`, `stderr` non-empty
- Invalid date with `--json`: `returncode == 1`, `json.loads(stdout)["error"]` is non-empty string
- Invalid delta (non-integer) with `--json`: `returncode == 1`, `json.loads(stdout)["error"]` is non-empty string

**`TestHelp`**:
- `testbed-utils --help`: `returncode == 0`
- `testbed-utils days-between --help`: `returncode == 0`

### Step 4 — Install and verify

```bash
pip install -e .
testbed-utils --help
pytest tests/test_cli.py -v
pytest  # full suite, confirm existing tests still pass
```

Confirm no `CI_FAIL` file is present after the test run.

## Verification

| Acceptance Criterion | How Verified |
|---|---|
| AC1: entry point on PATH after `pip install -e .` | `which testbed-utils` succeeds; `TestPlainText` tests invoke it |
| AC2: six subcommands, correct output, exit 0 | `TestPlainText` — one test per subcommand |
| AC3: `--json` writes valid JSON; `jq .result` works | `TestJsonOutput` — `json.loads(stdout)` on every subcommand |
| AC4: native JSON types (number/string/boolean) | `TestJsonOutput` — `isinstance` assertions on each result |
| AC5: `--json` errors → `{"error": ...}` on stdout, exit 1 | `TestErrors` — wrong arg count and invalid input under `--json` |
| AC6: plain errors → stderr, empty stdout, exit 1 | `TestErrors` — `stdout == ""` and `stderr != ""` assertions |
| AC7: `--help` exits 0 | `TestHelp` |
| AC8: all existing tests pass; no `CI_FAIL` | Full `pytest` run in Step 4 |
| AC9: both output modes and error path tested per subcommand | `TestPlainText`, `TestJsonOutput`, `TestErrors` classes |

## Risks & Open Points

**Must verify before writing code (repo not checked out at plan time):**

1. **`pyproject.toml` structure** — if a `[project.scripts]` section already exists, the edit must extend it rather than create a new table. If the layout is flat (not src-layout), the module path in the entry point and the import path in `cli.py` must be adjusted accordingly.

2. **`humanize_delta` argument type** — the spec example shows `humanize-delta 3600` producing `"1 hour"`, which implies the function accepts either raw integer seconds or a `timedelta`. The coercion layer in `_dispatch` wraps the int in `timedelta(seconds=int(arg))`; if the function actually takes raw seconds, remove the `timedelta` wrapper.

**Design decisions confirmed by approved HLD (no reviewer action needed):**

- `CustomParser.error()` checks `'--json' in sys.argv` — safe because `--json` is a global pre-subcommand flag at a deterministic position.
- `truncate` suffix uses `nargs='?'` with `default=None` sentinel — avoids overriding the library's built-in default if it differs from `"..."`.
- `bool` subclass of `int` is not a problem — `json.dumps` serializes `True`/`False` to `true`/`false` natively.
- No new runtime dependency — argparse is stdlib; `pyproject.toml` `[project.dependencies]` is unchanged.
