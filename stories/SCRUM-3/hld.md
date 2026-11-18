# SCRUM-3 High-Level Design: hello-world bash script

## 1. System Overview
- **What is being built:** nothing new at runtime. The required deliverable, `hello-world/hello.sh`, already exists on `main` (commit 65938b5) and meets FR1–FR5 and AC1–AC4.
- **Problem:** the story needs evidence that each acceptance criterion holds on the target branch. The existing tests come close, but in two places they are weaker than the criteria:
  - The folder isolation check ignores dotfiles, while AC2 says `hello.sh` is "the only file present".
  - The tests run the script by its absolute path, while AC1 and AC3 say it runs as `./hello-world/hello.sh` from the repository root.
- **Key responsibilities:**
  - Keep the script exactly as it is (spec assumption A1; PLAY-172 FR7).
  - Make the test suite check every criterion as the spec words it.
  - Let the repository's existing CI `pytest` gate, at the pull request's head commit, produce the delivery evidence.

## 2. Architecture Overview
- **Script component:** `hello-world/hello.sh`. It is read-only for this story.
- **Test component:** `tests/test_hello_sh.py`. This story owns it, and it is the only file the story changes.
- **CI gate:** `.github/workflows/ci.yml` runs `pytest` on each pull request with Python 3.12, and `testpaths = ["tests"]` includes the test file. It is consumed and not changed (CI/CD is a non-goal).
- **External dependencies:**
  - `/bin/bash` on the runner.
  - The executable bit stored in git as mode 100755.
  - Python's `subprocess` module, used by the tests.

## 3. Data Flow Design
- **Developer path (synchronous):**
  1. The developer runs `./hello-world/hello.sh` from the repository root.
  2. The kernel reads the shebang and runs `/bin/bash`.
  3. `echo` writes `hello world\n` to standard output.
  4. The script exits with 0.
- **Evidence path:**
  1. The pull request triggers CI.
  2. CI runs `pip install -e ".[test]"` and then `pytest`.
  3. `tests/test_hello_sh.py` runs the script, and the test that checks AC1/AC3 runs it from the repository root.
  4. The tests assert exit code, standard output, error output, shebang, executable bit and folder contents.
  5. A green run at the head commit is the evidence for AC1–AC4.
- There are no events and no asynchronous processing.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `hello-world/hello.sh` (existing, unchanged) | Print `hello world` and exit 0 | none / standard output `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` (hardened) | Check FR1–FR5 and AC1–AC4 exactly as the spec words them | the script file and folder / pass or fail results | play1 |
| CI `pytest` job (existing, unchanged) | Run the gate on the pull request's head commit | pull request / check status | play1 |

## 5. Interface Contracts
- **Script contract (fixed):**
  - It takes no arguments and reads no input.
  - Standard output is exactly `hello world\n`.
  - Error output is empty.
  - Exit code is 0.
  - Line 1 is `#!/bin/bash`.
  - Git stores it with mode 100755.
  - `hello-world/` holds exactly one entry, `hello.sh`, and no hidden files.
- There are no APIs, event schemas or cross-repository contracts.

## 6. Key Technical Decisions
- **Decision:** deliver through one test-only pull request in `play1`. It must not touch `hello-world/`.
- **Why:**
  - It answers the spec's open question about delivery mechanics.
  - It produces a CI run at the pull request's head commit, which `.factory/testing.md` names as the gate evidence.
  - It closes the two gaps between the tests and the acceptance criteria.
- **Alternatives considered:**
  - **Evidence only, with no pull request.** Rejected: it gives no head-commit CI run, and the factory requires a code-producing work item.
  - **Rewriting or reformatting the script.** Rejected: the spec's non-goals and PLAY-172 FR7 forbid it.
  - **Adding a `CHANGELOG.md` entry.** Left out: the spec excludes "other documentation for this story". It can be added on request.
  - **Adding a CI workflow step.** Rejected: CI/CD is a non-goal.
- **Trailing line break:** the tests keep the exact assertion `hello world\n`, as assumption A2 allows. They must not loosen it with strip-based comparisons.

## 7. Risks & Constraints
- **Accidental edits to the script.** Any edit to `hello-world/` breaks PLAY-172 and is out of scope. The ticket forbids it explicitly.
- **Executable bit.** Running the script directly depends on git's mode 100755 surviving checkout. This holds on the Linux CI runner. On a checkout where git ignores file modes (`core.fileMode=false`) or on Windows, it could differ, but that is not this story's environment.
- **Tests that depend on the working directory.** The root-relative test must set the repository root as its working directory explicitly, so it doesn't depend on where `pytest` was started.
- **Scale and performance:** not applicable. The script runs in milliseconds and has no failure path. Security exposure is nil: no input, no network, no secrets.
