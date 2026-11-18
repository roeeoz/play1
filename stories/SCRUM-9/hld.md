# SCRUM-9 high-level design: hello-world bash script

## 1. System overview
- **What:** a standalone bash script, `hello-world/hello.sh`, at the repository root. It prints exactly `hello world` and exits 0.
- **Problem:** developers need a verified, runnable starting point for shell scripting, in its own folder.
- **Current state:** `main` (`b7b5d0a`) already has the deliverable, unchanged since commit `65938b5`.
  - The script is mode `100755` and 31 bytes.
  - Its contents are `#!/bin/bash` followed by `echo "hello world"`.
  - It is the only file in `hello-world/`.
  - `tests/test_hello_sh.py` checks all four scenarios.
  - The work branch differs from `main` only by `stories/SCRUM-9/*`.
- **Responsibility of this story:** keep the deliverable as it is and confirm it against acceptance criteria AC1–AC4 through the existing merge gate. Per assumption A1, no new script and no other file change.

## 2. Architecture overview
- **Components:**
  - The script `hello-world/hello.sh`.
  - Its test module `tests/test_hello_sh.py`, run by `pytest` (`testpaths = ["tests"]`).
  - The existing CI in `.github/workflows/ci.yml`: the `test` job and the `gate` job.
- **Boundaries:** the script has no inputs, no dependencies on other repo code, and nothing in the repo depends on it.
- **Ownership:** a single work item in `play1` owns `hello-world/` and `tests/test_hello_sh.py`. CI is consumed as it is, never modified (CI/CD is a non-goal).
- **External dependencies:** `/bin/bash` on the developer's machine and on the CI runner.

## 3. Data flow
- A developer at the repo root runs `./hello-world/hello.sh`.
- The kernel reads the shebang and runs `/bin/bash`.
- The script runs `echo` and writes `hello world\n` to stdout. It writes nothing to stderr and exits 0.
- Everything is synchronous, with no events, state or persistence.
- On the verification path, pytest runs the script as a subprocess and checks:
  - the exit code, stdout bytes and stderr;
  - the shebang line;
  - the user-executable bit;
  - that the folder holds only `hello.sh`.

## 4. Component breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` and exit 0 | None in / `hello world\n` on stdout, exit 0 | play1 |
| `tests/test_hello_sh.py` | Check FR1–FR4 and AC1–AC4 in the merge gate | The script / pytest pass or fail | play1 |
| CI (`ci.yml`), consumed only | Run pytest and the gate job on the pull request | Repo / gate status | play1 |

## 5. Interface contracts
- **CLI contract:** `./hello-world/hello.sh`, with no arguments.
  - stdout is exactly the 12 bytes `hello world\n`: lowercase, no leading whitespace, no extra lines.
  - stderr is empty and the exit code is 0.
- **File contract:**
  - Path `hello-world/hello.sh` with git mode `100755`.
  - Line 1 is exactly `#!/bin/bash`.
  - It is the only file in `hello-world/`.
- There are no APIs, event schemas or cross-repo contracts.

## 6. Key technical decisions
- **Keep the existing script and tests as they are.**
  - They already meet FR1–FR4 and AC1–AC4.
  - Rewriting them risks dropping the executable bit, the trailing newline, or folder isolation.
  - Alternative rejected: re-creating the script. It would duplicate or collide with the existing file for no gain.
- **The trailing newline stays (A2).** `echo` ends the single line with one newline, and `test_prints_hello_world` requires it.
- **Reuse the existing test layer and CI.** The required layer is `package-api` (pytest, canonical gate). No new harness and no CI change.
- **No documentation file inside `hello-world/`.** It would break AC2 and the folder-isolation test.

## 7. Risks and constraints
- **Lost executable bit.** Any edit to `hello.sh` must keep mode `100755`; `test_executable_permission` guards this.
- **Extra file in `hello-world/`.** Adding a README, `.gitkeep` or a test there breaks AC2. The folder test ignores dotfiles, so reviewers should also check for hidden files.
- **Newline semantics (A2).** A consumer that compares against the raw 11 bytes would see a mismatch. No such consumer exists.
- **Pull request with no code change.** The pipeline may expect a code diff. The default is a pull request with only the plan documents; the fallback is one `CHANGELOG.md` "Unreleased" line, outside `hello-world/`.
- **Scale, performance and security:** not relevant. The script takes no input and makes no network or filesystem writes.
