# HLD — QA20261110-2 "QA-20261110-S4 hello.sh prints hello s4"

Target repo: roeeoz/play1 · base branch: `qa-20261110-s4-base` · requirements document: Epic PRD "סקריפט hello s4 (בדיקת שפיות של QA)"

## 1. System Overview
- **What is built:** a CLI script `qa/20261110-s4/hello.sh` that prints exactly `hello s4` and exits 0, and a self-contained shell test `qa/20261110-s4/test_hello.sh` that runs it and reports PASS/FAIL through its message and exit code. `CHANGELOG.md` also gets one line under `## Unreleased`, which play1's PR gate rule 4 requires.
- **Problem:** play1 has no script for the QA sanity check, so a developer would have to write one by hand.
- **Responsibilities:** deterministic output (FR1, FR2), deterministic verification from any directory (FR3–FR5), and a change limited to its agreed scope (FR6, FR7).

## 2. Architecture Overview
- Two standalone POSIX `sh` scripts with no dependencies. They live next to each other in the existing folder `qa/20261110-s4/`, which already holds `BASE_MARKER.txt`. That file is untouched.
- **Boundary:** `test_hello.sh` only *executes* `hello.sh` and never sources it. The contract between them is stdout plus the exit code.
- **External dependencies:** none. No network, no clock, no third-party code, and no new package dependencies.
- **Not touched:** `src/`, `tests/`, `.github/workflows/ci.yml`, `pyproject.toml` and `BASE_MARKER.txt`. The pytest CI is reused as it is.

## 3. Data Flow
1. Developer → `hello.sh` → stdout `hello s4\n`, exit 0. This is synchronous.
2. Developer (from any directory) → `test_hello.sh` → resolves its own directory → runs the `hello.sh` in that directory → captures stdout and exit status separately → compares the output byte-exactly with `hello s4\n` → prints a PASS or FAIL message and exits 0 or non-zero.
- There are no events and no async processing.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| `qa/20261110-s4/hello.sh` | Prints the line `hello s4` and nothing else, then exits 0 | In: none (arguments ignored, no stdin). Out: stdout `hello s4\n`, empty stderr, exit 0 | roeeoz/play1 |
| `qa/20261110-s4/test_hello.sh` | Verifies `hello.sh` by its own location | In: none. Out: a human-readable PASS/FAIL line; exit 0 on pass, non-zero on fail | roeeoz/play1 |
| `CHANGELOG.md` (one line) | Gate rule 4 traceability | One added line under `## Unreleased` naming QA20261110-2 | roeeoz/play1 |

## 5. Interface Contracts
- **hello.sh contract:** stdout is exactly the bytes `hello s4` followed by one LF, stderr is empty, and the exit code is 0, whatever the working directory.
- **test_hello.sh contract:** exit 0 if and only if the sibling `hello.sh` exits 0 *and* its stdout is exactly `hello s4\n`. Otherwise it exits non-zero and prints a failure message that says what was wrong (the exit code or the output that came back).
- **No cross-repo contracts.**

## 6. Key Technical Decisions
- **Shell:** `#!/bin/sh`, POSIX only. This matches the earlier `qa/` scripts (`qa/s3-hello.sh`, `qa/20261109-s1/a.sh`), and the PRD's "bash script" wording is satisfied because sh is a strict subset. The alternative, `#!/bin/bash`, works just as well but is less consistent with the other `qa/` scripts.
- **Locating the script:** the test resolves its own directory from `$0` and does not depend on the current directory or `CDPATH` (FR5).
- **Exact-output check:** `$(...)` strips trailing newlines, so the comparison must keep them (for example a sentinel or a byte comparison). That way `hello s4\n\n` and `hello s4` without a newline both fail. Exit status is captured separately from the output (FR4).
- **Scenario 3 without leaving a modified file:** copy both scripts to a temporary directory, change the copy of `hello.sh`, and run the copied `test_hello.sh`, which then expects a non-zero exit. This is done by hand during verification, so the scripts carry no test-only override variable. Alternatives considered: a `HELLO_SH` override variable (rejected because it adds surface the spec didn't ask for) and editing the real file and reverting it (rejected because it is error-prone).
- **Gate compliance:** both files are git mode 100755, start with a shebang, use LF only and are under 1 KB.
- **No pytest wrapper and no CI change:** both are out of scope (RK1, Non-Goals).

## 7. Risks & Constraints
- **RK1 (accepted):** CI runs only pytest on `tests/`, so a broken `hello.sh` could still merge green. Mitigation: the implementer runs scenarios 1–4 by hand and records the results in the PR description.
- **Gate rule 2:** a missing executable bit or shebang blocks the PR. The implementer verifies with `git ls-files -s` that both files are 100755.
- **Gate rule 4:** a missing CHANGELOG line causes a `PLAY-G4` blocker. Changing any other CHANGELOG line breaks FR6 and FR7.
- **Line endings:** CRLF would break the shebang, so the files must contain no CR characters.
- **Scale and performance:** not applicable. The test runs in milliseconds, far under the 60 s G4 budget.
- **Security:** no secrets, no personal data, no network, no external input.
