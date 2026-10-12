# Implementation plan — Shared shell helper `scripts/lib/common.sh`

Work item: **dev-1** · Branch: `halo/feat/play-4`

## Solution proposal

Add a single sourced shell library `scripts/lib/common.sh` that defines a
`project_version` function. The function reads `pyproject.toml` from the
repository root and prints the `version = "…"` value. Because the file is a
library (sourced with `. scripts/lib/common.sh`), it carries no shebang line and
is not marked executable.

The version extraction uses `sed` against `pyproject.toml` line 7
(`version = "0.1.0"`). The function locates `pyproject.toml` relative to the
script's own location (`scripts/lib/`), navigating two levels up to reach the
repo root. This avoids depending on the caller's working directory.

A pytest test file `tests/test_common_sh.py` exercises the function by running
`bash -c ". scripts/lib/common.sh; project_version"` from the repo root, then
compares the output to the version parsed from `pyproject.toml` via Python's
`tomllib` (stdlib in 3.11+, available in the repo's ≥3.10 target via
`tomli` fallback or direct toml parsing). Since the repo requires ≥3.10 and
the CI runs 3.12, `tomllib` is available; the test can fall back to a simple
regex parse to avoid adding a dependency.

Key design decisions:

- **`sed` over `grep`/`awk`**: `sed` with a substitution extracts the quoted
  value in one pass, portable across macOS and Linux.
- **Relative path resolution**: `BASH_SOURCE[0]` locates the library file so
  `project_version` works regardless of the caller's `$PWD`.
- **No shebang, not executable**: AC-2 is satisfied by omitting the shebang and
  not setting the execute bit on the file.
- **Pytest for the shell test**: AC-3 specifies a test under `tests/` that runs
  the bash command; `subprocess.run` in pytest is the natural fit and matches
  the repo's existing test patterns.

## Research findings

### Repository structure

- **Layout**: setuptools `src/` layout, Python ≥3.10, single package
  `testbed_utils`.
- **Version source**: `pyproject.toml` line 7: `version = "0.1.0"` (standard
  PEP 621 `[project]` table).
- **Existing scripts**: none. No `scripts/` directory exists; `scripts/lib/`
  must be created.
- **Test gate**: `pytest` (documented in `.factory/testing.md` as `test-gate:
  pytest`). CI runs `pip install -e ".[test]"` then `pytest` on Python 3.12
  / ubuntu-latest.
- **CI**: `.github/workflows/ci.yml` with workflow-level `permissions:
  contents: read`. Two jobs: `test` (pytest) and `gate` (CI_FAIL marker check).
- **No linter, formatter, or type checker** is configured.

### Change surface

| Area | Files | Exists today? |
|---|---|---|
| Shell library | `scripts/lib/common.sh` | No — new file, new directories |
| Test | `tests/test_common_sh.py` | No — new file |

No existing code is modified. No upstream or downstream dependencies are
affected. No CI configuration changes are needed — pytest already discovers
`tests/test_*.py` files automatically.

### Resolved unknowns

- **`pyproject.toml` format**: confirmed standard PEP 621 with
  `version = "0.1.0"` on its own line inside `[project]`.
- **Shell portability**: `sed`, `dirname`, and `BASH_SOURCE` are available on
  both macOS (CI on ubuntu-latest) and the developer's macOS host.
- **Python version for `tomllib`**: CI runs 3.12, so `tomllib` (stdlib since
  3.11) is available for the test's reference parse. For the ≥3.10 floor, the
  test can use a simple regex instead to avoid a conditional import.

## Ordered implementation tasks

### Task 1 — Create `scripts/lib/common.sh` (AC-1, AC-2 → dev-1)

Create the directory tree `scripts/lib/` and the file `common.sh` containing:

1. A `project_version` function that:
   - Resolves the repo root via `$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)`.
   - Reads `pyproject.toml` at that root.
   - Extracts and prints the version string using
     `sed -n 's/^version = "\(.*\)"/\1/p'`.
2. No shebang line (first line is blank or directly the function definition).
3. File permissions: `644` (not executable).

**Files**: `scripts/lib/common.sh` (new).

**Invariants**: the function must print exactly the version string with no
trailing whitespace beyond a newline, and must exit 0.

### Task 2 — Add pytest for `project_version` (AC-3 → dev-1)

Create `tests/test_common_sh.py` with a test that:

1. Reads the version from `pyproject.toml` using Python (regex on the raw
   text, to avoid a stdlib-version dependency).
2. Runs `bash -c ". scripts/lib/common.sh; project_version"` via
   `subprocess.run`, with `cwd` set to the repo root.
3. Asserts the subprocess exits 0 and its stripped stdout equals the
   Python-parsed version.

**Files**: `tests/test_common_sh.py` (new).

**Covered by**: existing `package-api` test layer (`pytest`). No new layer is
needed — the new test file is auto-discovered by pytest's `testpaths = ["tests"]`
configuration.

### Task 3 — Validate from clean state

Run the repo gate (`pip install -e ".[test]" && pytest`) and confirm:

- All existing tests still pass (no regressions).
- `test_common_sh.py` passes.
- `scripts/lib/common.sh` is not executable (`stat` check or `ls -l`).

## Files and test layers

| File | Action | Test layer |
|---|---|---|
| `scripts/lib/common.sh` | Create | `package-api` (via `tests/test_common_sh.py`) |
| `tests/test_common_sh.py` | Create | `package-api` (pytest auto-discovery) |

No new test layer is introduced. The existing `package-api` layer (`pytest`)
covers the new test file.

## Verification gate

The change is done when `pytest` passes from a clean worktree at the committed
SHA:

```
pip install -e ".[test]"
pytest
```

All pre-existing tests must remain green. The new test
`tests/test_common_sh.py` must pass, confirming `project_version` output
matches `pyproject.toml`.

## Risks and scope guards

### Risks

- **`sed` portability**: GNU vs BSD `sed` — the pattern used
  (`sed -n 's/…/…/p'`) is POSIX-compatible and works on both. Low risk.
- **Version line format drift**: if `pyproject.toml` ever uses single quotes or
  inline comments after the version value, the `sed` pattern would fail. This is
  unlikely for standard PEP 621 files and out of scope for this ticket.

### Scope guards — the implement phase must NOT

- Add a shebang line or make `common.sh` executable.
- Modify any existing file (`pyproject.toml`, CI config, existing tests).
- Add Python dependencies (use stdlib or simple regex for version parsing in the
  test).
- Create additional shell functions beyond `project_version`.
- Refactor or create release scripts that source the library — only the library
  and its test are in scope.

## Clarification outcomes

No clarifications needed. All acceptance criteria are unambiguous and the
repository state supports them directly.
