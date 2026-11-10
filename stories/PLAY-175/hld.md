# PLAY-175 — High-Level Design: `qa/20261110-s3/hello.sh` and its test

## 1. System Overview
- **What:** two new POSIX shell scripts in their own folder in roeeoz/play1:
  - a greeting script that prints exactly `hello s3\n` and exits 0;
  - a test script that runs it and passes (exit 0) only when the output and exit code are exactly right.
- **Problem:** the factory-QA runner must currently check output by eye. This epic is the smallest possible end-to-end run of the factory.
- **Responsibilities:**
  - The greeting script produces the output.
  - The test script decides pass or fail with its exit code.
  - One CHANGELOG line satisfies the repo gate.

## 2. Architecture Overview
- **Components:** `qa/20261110-s3/hello.sh` and `qa/20261110-s3/test_hello.sh`, plus one line under `## Unreleased` in `CHANGELOG.md`.
- **Boundary:** everything new lives under `qa/20261110-s3/`. Nothing else is touched:
  - the existing `qa/` scripts (`qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`);
  - `src/`, `tests/`, `pyproject.toml` and `.github/workflows/ci.yml`.
- **Ownership:** one ticket (t1) owns all three changes.
- **External dependencies:** none. The scripts need only `/bin/sh` and POSIX utilities. There is no network and no third-party code.

## 3. Data Flow Design
1. The user, or the test, runs `hello.sh` directly through its path.
2. `hello.sh` writes `hello s3\n` to stdout and exits 0.
3. `test_hello.sh` finds `hello.sh` relative to its own location, so it works from any current directory.
4. The test runs `hello.sh` directly, never as `sh hello.sh`, so a script that isn't executable fails.
5. The test captures stdout in memory, keeping trailing newlines, and records the exit code.
6. The test exits 0 only if the output is exactly `hello s3\n` and the exit code is 0. In every other case it exits non-zero.

Everything runs synchronously. There are no events and no persisted state.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `qa/20261110-s3/hello.sh` | Print the greeting | No input, no arguments read. Stdout is `hello s3\n`; exit code 0. | roeeoz/play1 |
| `qa/20261110-s3/test_hello.sh` | Check the greeting script | Input: the sibling `hello.sh`. Output: exit code 0 for pass, non-zero for fail; any message wording is free. | roeeoz/play1 |
| `CHANGELOG.md` (one line) | Satisfy gate rule 4 (`PLAY-G4`) | One line under `## Unreleased` that mentions PLAY-175, in the same style as the PLAY-172 entry | roeeoz/play1 |

## 5. Interface Contracts
- **CLI contract, `hello.sh`:** stdout is exactly the 9 bytes `hello s3\n`, with no other text, and the exit code is 0.
- **CLI contract, `test_hello.sh`:**
  - Exit 0 if and only if the contract above holds.
  - Exit non-zero if the text is wrong (including a missing or extra trailing newline), the exit code is non-zero, the script is missing, or the script is not executable.
- **File-mode contract:** both files are committed as executable (git mode `100755`), use LF line endings and start with a shebang (gate rule 2).
- There are no APIs, events or cross-repo contracts.

## 6. Key Technical Decisions
- **`#!/bin/sh` rather than bash:** this matches the existing `qa/` convention (`#!/bin/sh` with `printf`). A POSIX prototype passed every case, and the spec §7 leaves the choice to this stage. Either shebang would pass the gate.
- **Exact comparison in memory:** a naive `$(...)` strips trailing newlines and would accept wrong output. The test must keep trailing newlines, for example by adding a sentinel character after the output and stripping it again. Comparing in memory also avoids temp files, which would break FR6/AC9.
- **Locate relative to the test file:** the test finds `hello.sh` from its own path, not from the current directory (FR5).
- **Direct execution, no fallback:** the test never calls the interpreter explicitly, so a missing executable bit is a failure (FR4).
- **stderr is not checked:** the spec requires only stdout and the exit code.
- **Not wired into CI:** this is deferred to another epic (RK1, out of scope). The PR description reports a manual run instead (FR8).
- **Alternatives rejected:**
  - A pytest wrapper under `tests/`: the spec forbids extra files.
  - Temp-file diffs: they would write outside the folder.
  - Bash-only features: they bring no benefit here.

## 7. Risks & Constraints
- **Executable bit:** `core.fileMode=true` and there is no `.gitattributes`. A file committed as `100644` fails gate rule 2 and breaks direct execution. Verify the mode with `git ls-files -s qa/20261110-s3` before the PR.
- **Trailing-newline comparison:** if the capture is done naively, the test would pass broken output.
- **CRLF line endings** would break the shebang. Nothing checks the new files automatically, so the implementer must make sure they use LF.
- **RK1:** CI (pytest and the `CI_FAIL` gate) never runs the shell test. pytest only collects `test_*.py` under `tests/`, so the new files also can't break or slow CI. The only evidence is the manual run reported in the PR, including temporary checks of scenarios 3–5 that are never committed.
- **RK2:** `qa/s3-hello.sh` looks similar and is pinned by `tests/test_qa_s3_greeting.py`. Any edit to it makes CI red, and the PR diff must not touch it.
- **Running as root:** a file with no execute bit still fails to run as root, so scenario 5 holds.
- **Size and scale:** about 25 changed lines, far under the G3 limit of 300. The test runs in milliseconds, well inside G4's 60-second budget.
