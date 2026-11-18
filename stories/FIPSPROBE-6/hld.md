# HLD: FIPSPROBE-6, Hello-world bash script in a dedicated folder (verification)

## 1. System Overview
- **What:** a test linked to FIPSPROBE-6 that proves the story's acceptance criteria against `hello-world/hello.sh`. The script is already on `main`, added by commit `65938b5`.
- **Problem:** nothing in the repository links the script to this story. The existing executable check (`tests/test_hello_sh.py::test_executable_permission`) reads the file mode from the checkout, which RK1 says cannot be trusted.
- **Responsibilities:**
  - prove execution and output exactness (FR2, FR3);
  - prove the shebang and that the repository stores the file as executable (FR4, RK1);
  - prove the script's location (FR1);
  - run inside the existing pytest suite (FR5).

## 2. Architecture Overview
- **Component under test:** `hello-world/hello.sh`. It is read-only for this story.
- **New component:** `tests/test_fipsprobe_6_hello_sh.py`, a pytest module collected automatically through `testpaths = ["tests"]`.
- **External dependencies:**
  - `bash` at `/bin/bash`;
  - `git` on PATH with a `.git` directory present. In CI this holds: `actions/checkout@v4` on `ubuntu-latest`.
- **Untouched:**
  - `hello-world/`;
  - `tests/test_hello_sh.py`, owned by WI-220A63-1. FIPSPROBE-7 will edit its folder-contents check;
  - `.github/`, `pyproject.toml`, `src/`, and documentation.
  - `CHANGELOG.md` stays untouched unless the human resolves the `PLAY-G4` question in favour of a single line (see §7).

## 3. Data Flow Design
- **Sync only.** pytest runs the script as a subprocess, directly, with no `bash` prefix, from the repository root. It captures stdout, stderr and the exit code, then compares them with exact values.
- **Mode check:** pytest runs `git ls-files -s hello-world/hello.sh` from the repository root and reads the recorded mode, which must be `100755`.
- **Shebang check:** the first line of the file's bytes must be exactly `#!/bin/bash`.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| `hello-world/hello.sh` (existing) | Prints `hello world` and exits with 0 | none / stdout, exit code | roeeoz/play1 (unchanged) |
| `tests/test_fipsprobe_6_hello_sh.py` (new) | Story-linked proof of AC1–AC3 and RK1 | script, git index / pytest pass or fail | roeeoz/play1 |

## 5. Interface Contracts
- **Script contract:**
  - no arguments;
  - stdout is exactly `hello world\n`: one line, with no leading or trailing whitespace;
  - stderr is empty;
  - exit code is 0.
- **Repository contract:** the git index records `hello-world/hello.sh` at the repository root with mode `100755`, and its first line is `#!/bin/bash`.
- **Traceability contract:** the test file name and its module docstring carry the key `FIPSPROBE-6`.
- There are no cross-repository contracts.

## 6. Key Technical Decisions
- **A new story-keyed file rather than editing `tests/test_hello_sh.py`.**
  - This keeps the change within this story's ownership.
  - It avoids touching a file that FIPSPROBE-7 must edit.
  - The pull request diff shows plainly that it adds only the linked test.
  - Some assertions overlap with the existing file; that is accepted.
- **Link by file name and docstring, not a custom pytest marker.** A marker would have to be registered in `pyproject.toml`, which widens the diff. There is no existing convention for linking a test to a story key.
- **Read the executable bit from the git index (`git ls-files -s`), not from `st_mode`.**
  - `core.fileMode=false` and the `-rwxrwxrwx` checkout make `st_mode` unreliable (RK1).
  - Alternative considered: `git ls-tree HEAD`. The index is preferred because it also reflects staged state during development.
- **If git or `.git` is unavailable, the test fails with a clear message rather than skipping.** A skip would hide RK1. The suite only ever runs from a git checkout: CI does, and so do developers working from a clone.
- **Each subprocess has a timeout** (about 10 s), matching `tests/test_qa_s3_greeting.py`.
- **No folder-contents assertion.** Leaving it out avoids coupling to FIPSPROBE-7.

## 7. Risks & Constraints
- **The repository gate conflicts with the spec (blocking).** Rule 4 of the play1 layout gate (`PLAY-G4`, blocker) requires a line under `## Unreleased` in `CHANGELOG.md`. The spec's AC5 forbids a CHANGELOG change, and AC4 requires the checks to pass. A human must decide between them.
- **This is the first test that shells out to `git`.** It depends on `git` being on PATH and on the subprocess running from the repository root. Both hold on `ubuntu-latest`.
- **Overlap with the existing `test_hello_sh.py`.** The existing file also runs the script and checks its output, and both run quickly, so the overlap is harmless. Its weak `st_mode` check stays until its owner changes it, which is out of scope here.
- **Scaling, performance and security:** not applicable. The tests add a few subprocess calls, well within CI's 5-minute timeout.
