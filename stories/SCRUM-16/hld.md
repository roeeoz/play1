# High-Level Design: SCRUM-16, hello-world bash script

## 1. System Overview
- **What:** a runnable bash script, `hello-world/hello.sh`, that prints `hello world`. It is the only file in its own top-level folder.
- **Current state:** `main` already has it, added in commit `65938b5`. All four acceptance criteria are met:
  - git stores the file as `100755`
  - the first line is `#!/bin/bash`
  - it outputs exactly `hello world\n` and exits 0
  - the folder holds no other file
- `tests/test_hello_sh.py` (commits `a2ec96d` and `9a5bd0b`) pins each criterion.
- **What this story delivers:** a pull request that checks the existing script against the criteria and meets the repository's pull-request gates. Per spec FR4, A1 and A3, the only file it changes is `CHANGELOG.md`.

## 2. Architecture Overview
- **Script component:** `hello-world/hello.sh`. It is already delivered, and this story makes no change to it.
- **Test component:** `tests/test_hello_sh.py`, run by `pytest` in the CI `test` job (`.github/workflows/ci.yml`, Python 3.12). Already delivered, no change.
- **Changelog:** `CHANGELOG.md`, `## Unreleased` section. It needs one new line to meet gate PLAY-G4.
- **External dependencies:** none. The script uses only `/bin/bash` and the `echo` builtin.
- **Unrelated, do not touch:** `src/testbed_utils/hello.py` (the `testbed-hello` console script) and the `slugify` test that uses the string "hello-world".

## 3. Data Flow Design
- A developer runs `./hello-world/hello.sh`. The kernel reads the shebang and starts `/bin/bash`. `echo` writes `hello world\n` to stdout, and the process exits 0.
- Everything is synchronous. There is no input, state, persistence or event.
- In CI, `pytest` runs the script as a subprocess with no `bash` prefix and checks stdout, stderr, the exit code, the shebang, the executable bit and that the folder contains only `hello.sh`.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` | none / stdout `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` | Pin AC1 to AC4 | the script / pass or fail | play1 |
| `CHANGELOG.md` entry | Meet gate PLAY-G4 | none / one line under `## Unreleased` | play1 |

## 5. Interface Contracts
- **Command-line contract:** `./hello-world/hello.sh` takes no arguments. stdout is exactly `hello world\n`, stderr is empty, and the exit code is 0.
- **File contract:** `hello-world/` contains only `hello.sh`, including hidden files. Git stores the file as `100755`, the first line is `#!/bin/bash`, and line endings are LF.
- There are no APIs, events or contracts with other repositories.

## 6. Key Technical Decisions
- **Keep the existing script as it is.** Rewriting it, even with the same content, could lose the executable bit or change the line endings. The alternative was to re-create the script; it was rejected because nothing would improve and it could break AC3 and gate rule 2.
- **Keep `echo`, which ends the line with a newline (spec A2).** The existing test expects that output. Using `printf 'hello world'` was rejected because it contradicts A2 and would fail the test.
- **Reuse the existing pytest coverage.** No new test harness or CI change, since the spec puts CI/CD out of scope.
- **The changelog line follows the existing entry style:** `- <KEY>: … \`<path>\` …`.

## 7. Risks & Constraints
- **Gate PLAY-G4 is a blocker.** A pull request without the `CHANGELOG.md` line fails it.
- **Executable bit and line endings.** Any edit to `hello.sh` risks dropping mode `100755` or bringing in CRLF line endings. There is no `.gitattributes` to protect against this.
- **Folder test skips dotfiles.** A stray hidden file in `hello-world/` would pass the test but break AC2, so the pull request must not add one.
- **Only CI counts.** The pytest layer passes only in the CI run at the pull request's head commit. A local run is just a pre-push check.
- **Scale and security:** not applicable. The script is a trivial local one with no input.
