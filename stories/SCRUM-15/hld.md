# High-Level Design — SCRUM-15: Hello world bash script in a dedicated folder

## 1. System Overview
- **What is being built:** a runnable `hello-world/hello.sh` that prints exactly `hello world` (one terminating newline) and exits 0, alone in its own top-level folder.
- **Current state:** already on `main` (commit `65938b5`, WI-220A63-1). Its git mode is `100755` and its content is `#!/bin/bash` followed by `echo "hello world"`. Running it gives 12 bytes of stdout and exit code 0. `git diff 65938b5 HEAD -- hello-world` is empty, because the two banner changes added later were both reverted.
- **Remaining work:** the change record that the repository gate requires (FR6). Nothing else is missing.

## 2. Architecture Overview
- **Single repo:** `play1` (`86d449d4-e5db-42c9-8d61-17b798bdd7e2`).
- **Components:**
  - `hello-world/hello.sh`: the deliverable. It already exists and stays unchanged.
  - `tests/test_hello_sh.py`: existing pytest coverage of acceptance criteria 1–4. It stays unchanged.
  - `CHANGELOG.md`: the repository change record. It gets one new line under `## Unreleased`.
  - `.github/workflows/ci.yml`: the existing CI `test` job, which runs `pytest` on every PR. It stays unchanged.
- **External dependencies:** `/bin/bash` on the developer machine and on the CI runner.

## 3. Data Flow Design
- Developer runs `./hello-world/hello.sh` → the kernel follows the shebang to `/bin/bash` → `echo` writes `hello world\n` to stdout → exit 0. The run is synchronous and has no inputs, state or events.
- Verification: a PR triggers the CI `test` job → `pytest` → `tests/test_hello_sh.py` runs the script with `subprocess` and checks its output, its stderr, the shebang, the execute bit and what the folder contains.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo | Change |
|---|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` and exit 0 | none / stdout `hello world\n`, exit 0 | play1 | none (FR1–FR5 already met) |
| `tests/test_hello_sh.py` | Automated check of acceptance criteria 1–4 | the script / pass or fail | play1 | none |
| `CHANGELOG.md` | Record the change for the repository gate (`PLAY-G4`) | — / one line under `## Unreleased` | play1 | add one line (FR6) |

## 5. Interface Contracts
- **CLI contract:** `./hello-world/hello.sh` takes no arguments and no environment. stdout is exactly `hello world\n`, stderr is empty, and the exit code is 0.
- **File contract:** `hello-world/` holds only `hello.sh`. Its first line is `#!/bin/bash` and git records it as `100755`.
- There are no APIs, event schemas or cross-repo contracts.

## 6. Key Technical Decisions
- **Reuse the existing script as the delivery (A1).** Rewriting it would produce the same file.
- **Reuse the existing tests.** Spec §6 says pytest doesn't run shell scripts. That is wrong: `tests/test_hello_sh.py` covers all four acceptance criteria and CI runs it. A new test or CI step would duplicate it, and CI/CD integration is out of scope.
- **The output check accepts one newline (A2).** This matches what the existing test asserts (`"hello world\n"`).
- **The `CHANGELOG.md` line is a change record, not documentation (A3).** The gate rule allows no exemption, so the line is required.
- **Alternatives rejected:** closing the story as already done, which leaves no traceable PR; adding a README, which is out of scope and would break the folder-isolation test.

## 7. Risks & Constraints
- **Folder isolation:** any new file in `hello-world/` breaks acceptance criterion 2 and fails `test_folder_contains_only_hello_sh`. This ticket must not add files there.
- **Other branches:** many `origin/halo/feat/*` branches change `hello-world/` or the test. They are not the base and must not be merged in.
- **A PR that only changes the changelog:** a reviewer may expect a change to the script. The PR description should explain where the script and tests came from (WI-220A63-1).
- **No scaling, performance or security concerns:** the script runs once, statically, and takes no input.
