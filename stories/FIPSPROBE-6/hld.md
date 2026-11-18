# HLD: FIPSPROBE-6, Hello-world bash script in a dedicated folder (verification)

## 1. System Overview
- **What:** a test linked to FIPSPROBE-6 that proves the story's acceptance criteria against `hello-world/hello.sh`. The script is already on `main`, added by commit `65938b5`. The pull request also adds one CHANGELOG line, as the repository gate requires.
- **Problem:** nothing in the repository links the script to this story. The existing executable check (`tests/test_hello_sh.py::test_executable_permission`) reads the file mode from the checkout, which RK1 says cannot be trusted.
- **Responsibilities:**
  - prove execution and output exactness (FR2, FR3);
  - prove the shebang and that the repository stores the file as executable (FR4, RK1);
  - prove the script's location (FR1);
  - run inside the existing pytest suite (FR5);
  - satisfy the play1 layout gate (`PLAY-G4`) with one line under `## Unreleased` in `CHANGELOG.md`.

## 2. Architecture Overview
- **Component under test:** `hello-world/hello.sh`. It is read-only for this story.
- **New component:** `tests/test_fipsprobe_6_hello_sh.py`, a pytest module collected automatically through `testpaths = ["tests"]`.
- **Changed file:** `CHANGELOG.md` gets exactly one added line under `## Unreleased`, describing the FIPSPROBE-6 test. Nothing else in the file changes.
- **External dependencies:**
  - `bash` at `/bin/bash`;
  - `git` on PATH with a `.git` directory present. In CI this holds: `actions/checkout@v4` on `ubuntu-latest`.
- **Untouched:**
  - `hello-world/`;
  - `tests/test_hello_sh.py`, owned by WI-220A63-1. FIPSPROBE-7 will edit its folder-contents check;
  - `.github/`, `pyproject.toml`, `src/`, README and any other documentation.

## 3. Data Flow Design
- **Sync only.** pytest runs the script as a subprocess, directly, with no `bash` prefix, from the repository root. It captures stdout, stderr and the exit code, then compares them with exact values.
- **Mode check:** pytest runs `git ls-files -s hello-world/hello.sh` from the repository root and reads the recorded mode, which must be `100755`.
- **Shebang check:** the first line of the file's bytes must be exactly `#!/bin/bash`.
- **Gate:** the `mr-gate` play1 layout gate finds the added `## Unreleased` line in the diff and passes rule `PLAY-G4`.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| `hello-world/hello.sh` (existing) | Prints `hello world` and exits with 0 | none / stdout, exit code | roeeoz/play1 (unchanged) |
| `tests/test_fipsprobe_6_hello_sh.py` (new) | Story-linked proof of AC1–AC3 and RK1 | script, git index / pytest pass or fail | roeeoz/play1 |
| `CHANGELOG.md` (one added line) | Records the change for the `PLAY-G4` gate | — / one line under `## Unreleased` | roeeoz/play1 |

## 5. Interface Contracts
- **Script contract:**
  - no arguments;
  - stdout is exactly `hello world\n`: one line, with no leading or trailing whitespace;
  - stderr is empty;
  - exit code is 0.
- **Repository contract:** the git index records `hello-world/hello.sh` at the repository root with mode `100755`, and its first line is `#!/bin/bash`.
- **Traceability contract:** the test file name, its module docstring and the CHANGELOG line all carry the key `FIPSPROBE-6`.
- **Gate contract:** the diff adds exactly one line under `## Unreleased` in `CHANGELOG.md` (rule `PLAY-G4`).
- There are no cross-repository contracts.

## 6. Key Technical Decisions
- **A new story-keyed file rather than editing `tests/test_hello_sh.py`.**
  - This keeps the change within this story's ownership.
  - It avoids touching a file that FIPSPROBE-7 must edit.
  - The pull request diff shows plainly what it adds.
  - Some assertions overlap with the existing file; that is accepted.
- **Link by file name and docstring, not a custom pytest marker.** A marker would have to be registered in `pyproject.toml`, which widens the diff.
- **Read the executable bit from the git index (`git ls-files -s`), not from `st_mode`.**
  - `core.fileMode=false` and the `-rwxrwxrwx` checkout make `st_mode` unreliable (RK1).
  - Alternative considered: `git ls-tree HEAD`. The index is preferred because it also reflects staged state during development.
- **If git or `.git` is unavailable, the test fails with a clear message rather than skipping.** A skip would hide RK1.
- **Each subprocess has a timeout** (about 10 s), matching `tests/test_qa_s3_greeting.py`.
- **No folder-contents assertion.** Leaving it out avoids coupling to FIPSPROBE-7.
- **One CHANGELOG line to satisfy `PLAY-G4` (developer decision, option b).** The developer chose this over asking for a waiver. AC5 is amended to allow exactly that one line. PLAY-175 set the precedent.

## 7. Risks & Constraints
- **Gate conflict resolved.** The added CHANGELOG line satisfies `PLAY-G4`, and the amended AC5 allows it. The remaining risk is that the line is misplaced: if it is not under `## Unreleased`, the gate still fails. The ticket's acceptance criteria pin its placement.
- **This is the first test that shells out to `git`.** It depends on `git` being on PATH and on the subprocess running from the repository root. Both hold on `ubuntu-latest`.
- **Overlap with the existing `test_hello_sh.py`.** The overlap is harmless. Its weak `st_mode` check stays until its owner changes it, which is out of scope here.
- **Scaling, performance and security:** not applicable. The tests add a few subprocess calls, well within CI's 5-minute timeout.
