# High-Level Design: SCRUM-1, hello-world bash script

## 1. System Overview
- **What it is:** a standalone `hello-world/hello.sh` in `play1`. It prints exactly `hello world` and exits 0.
- **Where it stands:** the target branch `main` (`b7b5d0a`) already contains the deliverable.
  - Commit `65938b5` added the script.
  - Commit `a2ec96d` added `tests/test_hello_sh.py`.
  - The work branch differs from `main` only by the story documents.
- **What this story does:** it confirms each acceptance criterion with evidence from the repository's own gate. It also tightens that gate where it reads the spec more loosely than the spec is written. The script and its folder stay as they are, as assumption A1 and the non-goals require.

## 2. Architecture Overview
- **Deliverable component:** `hello-world/hello.sh`. It already exists, and nothing in it changes.
- **Verification component:** `tests/test_hello_sh.py`, collected by `pytest` through `testpaths = ["tests"]`. This is the only file that changes.
- **Gate:** the existing `.github/workflows/ci.yml` `test` job runs `pytest` on Python 3.12 for every pull request. It is used as it is and not changed.
- **External dependencies:** `/bin/bash` on the machine that runs the script. This story adds none.

## 3. Data Flow
- The developer or the test runs `./hello-world/hello.sh` directly. The kernel resolves the shebang to `/bin/bash`, the script writes `hello world\n` to stdout and exits 0.
- The test captures stdout, stderr and the exit code synchronously with a subprocess, then asserts on them. It also inspects the folder listing, the file's mode, and the mode git stores in its index.
- There are no async flows, events, persisted data or state.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` (unchanged) | Prints `hello world` and exits 0 | No input. Stdout `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` (tightened) | Turns every acceptance criterion into a check that can fail | Repo files and git index in, `pytest` pass/fail out | play1 |

## 5. Interface Contracts
- **Command-line contract:** `./hello-world/hello.sh` from the repository root.
  - Takes no arguments.
  - Stdout is exactly `hello world\n`; under A2 the single newline is allowed.
  - Stderr is empty and the exit code is 0.
- **Repository contract:**
  - `hello-world/` contains exactly one entry, `hello.sh`, with no hidden files.
  - The first line of `hello.sh` is `#!/bin/bash`.
  - Git stores `hello.sh` as `100755`.
- There are no cross-repo or API contracts.

## 6. Key Technical Decisions
- **Confirm, don't rewrite.** The content on `main` is correct. Rewriting it would add churn and risk merge conflicts, given the history of probe and re-add commits.
- **Close gaps in the test only.** The only change is in `tests/`, which keeps `hello-world/` isolated (AC2).
  - Count hidden entries, so AC2's "only file present" is checked literally.
  - Check the mode git stores (`100755`), so a lost execute bit fails the test no matter how the file system of the checkout behaves.
- **Evidence is the CI run at the pull request's head.** Per `.factory/testing.md`, the authoritative result is CI at the head commit. A local run is only a pre-check.
- **Alternatives rejected:**
  - Recreating the folder: violates A1 and adds churn.
  - A README or CHANGELOG entry: a non-goal.
  - A new CI job: a non-goal.
  - A pull request with no code change: the factory needs a code-producing work item.

## 7. Risks & Constraints
- **Execute bit:** `hello.sh` must keep mode `100755`. It is not edited, and the new check in the test guards it.
- **Output exactness:** the test keeps asserting the exact `hello world\n`. A `printf` with no newline, or any extra banner line, fails.
- **Hidden-file strictness:** the folder has no hidden entries today, so the stricter check passes. Any future dotfile in `hello-world/` would fail it, which is the intended reading of AC2.
- **Unrelated gate:** the `gate` job fails if a `CI_FAIL` file exists at the repository root. That has nothing to do with this story.
- **Scale and security:** neither applies. The script is static, takes no input and has no side effects.
