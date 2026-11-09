# HLD — PLAY-172: `qa/20261109-s1/a.sh` prints "A"

## 1. System Overview
- **What:** a new terminal script, `qa/20261109-s1/a.sh`, in a new folder. It prints exactly one line, `A`, and exits 0. It comes with new pytest coverage and a CHANGELOG line.
- **Problem:** the epic tests that the factory delivers dependent stories in order. PLAY-173 (`b.sh`) needs a stable first script to call.
- **Responsibilities:** a deterministic output contract (path, stdout `A\n`, empty stderr, exit 0) and automated proof of it in the existing CI `test` job.

## 2. Architecture Overview
- **Script component:** `qa/20261109-s1/a.sh`. It is self-contained and depends on no sibling file or older `qa/` script (RK3).
- **Test component:** `tests/test_qa_20261109_s1_a.py`, a new file. The existing `pytest` config (`testpaths = ["tests"]`) picks it up automatically.
- **Changelog:** one new line under `## Unreleased` in `CHANGELOG.md`, which PR gate rule 4 requires.
- **External dependencies:** none. No new packages, no CI or `pyproject.toml` changes.
- **Owner:** all of it is in roeeoz/play1.

## 3. Data Flow
- A user or a test calls the script by path, from any working directory. `/bin/sh` runs it, it writes `A\n` to stdout and exits 0.
- Everything is synchronous. There are no events, no state and no input.
- In CI, pytest runs the script through `subprocess` with an absolute path, both from the repo root and with `cwd` set to a temporary directory, and asserts the stdout, stderr and exit code.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `qa/20261109-s1/a.sh` | Print `A` and succeed | none / stdout `A\n`, stderr empty, exit 0 | roeeoz/play1 |
| `tests/test_qa_20261109_s1_a.py` | Check the normal run, the run from another directory, the file's shape, and that `qa/s3-a.sh` output is unchanged | script paths / pytest pass or fail | roeeoz/play1 |
| `CHANGELOG.md` (one-line addition) | Record PLAY-172 under `## Unreleased` | — | roeeoz/play1 |

## 5. Interface Contracts
- **Contract consumed by PLAY-173 (fixed):**
  - the path is `qa/20261109-s1/a.sh`
  - it can be run directly (executable bit set, shebang on line 1)
  - stdout is exactly `A\n`, stderr is empty and the exit code is 0
  - it does not depend on its own location or on any sibling file, so PLAY-173 tests can copy it into a temporary directory
- There are no APIs, events or cross-repo contracts.

## 6. Key Technical Decisions
- **Interpreter `#!/bin/sh` (POSIX) with `printf 'A\n'`:** this matches `qa/s3-a.sh`, `qa/s3-hello.sh` and their shape tests. It gives the same result under dash and bash. Bash was considered (it appears in the PRD glossary) and rejected: it adds nothing and the folder's convention is sh.
- **Tests as pytest + subprocess:** this follows `tests/test_qa_s3_greeting.py`. The run from another directory uses `cwd=tmp_path`, a built-in fixture with no network or clock. `timeout=10` matches the existing tests.
- **Regression check for `qa/s3-a.sh`:** it lives in the new test file and asserts the script still prints `A\n` and exits 0. That turns scenario 3 into a real check without modifying any existing file.
- **Test file name** uses underscores (`test_qa_20261109_s1_a.py`), since a hyphenated name can't be a Python module.
- **One PR:** script, tests and CHANGELOG line together, about 60 lines, well inside G3. Gate rule 4 checks each PR on its own, so the CHANGELOG line can't be split off.

## 7. Risks & Constraints
- **Executable bit:** if the file is committed as 100644, direct execution fails. That breaks gate rule 2, the new test and PLAY-173. Mitigation: check `git ls-files -s` shows 100755, and assert the executable bit in the test.
- **Stray output:** any extra stdout or stderr (debug lines, `set -x`) breaks the PLAY-173 contract. The tests assert exact stdout and empty stderr.
- **CRLF line endings** would break the shebang. The test asserts the file contains no `\r`.
- **Merge order (RK1):** PLAY-173's PR opens only after this one merges to `main`.
- **G4:** the test job stays well under 60 s, and no new tests use the network, the clock or environment variables.
- **R6:** no existing file changes except one added line in `CHANGELOG.md`. `ci.yml`, `pyproject.toml`, `qa/s3-*.sh`, `hello-world/` and the existing tests stay as they are.
