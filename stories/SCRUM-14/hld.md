# HLD — SCRUM-14: Hello world bash script in a dedicated folder

## 1. System Overview
- **What:** a runnable bash script, `hello-world/hello.sh`, at the root of play1. It prints exactly `hello world` and exits 0.
- **Current state:** the script is already on `main` (commit `65938b5`).
  - Its mode is 100755, line 1 is `#!/bin/bash`, line 2 is `echo "hello world"`, and line endings are LF.
  - It is the only file in `hello-world/`.
  - `tests/test_hello_sh.py` already checks every acceptance criterion (6 tests, all passing).
- **Responsibility of this story:** make sure the target branch holds the script as specified (it already does), and meet the repository gate. Every PR must add a line under `## Unreleased` in `CHANGELOG.md`, or the gate raises `PLAY-G4`.

## 2. Architecture Overview
- **Script (`hello-world/hello.sh`):** an existing artifact that stays unchanged (FR5, A1). It has no runtime dependencies beyond `/bin/bash`.
- **Tests (`tests/test_hello_sh.py`):** existing pytest checks for output, exit code, stderr, shebang, the executable bit and folder isolation. pytest already collects them through `testpaths = ["tests"]`.
- **Changelog (`CHANGELOG.md`):** the only file this story changes. It gets one SCRUM-14 line under `## Unreleased`.
- **CI (`.github/workflows/ci.yml`):** existing `pytest` job and gate. No change, since CI integration is a non-goal.

## 3. Data Flow Design
- The developer runs `./hello-world/hello.sh` from the repository root.
- The kernel reads the shebang and runs `/bin/bash`.
- `echo` writes `hello world\n` to stdout, and the script exits 0.
- Everything is synchronous. There is no input, state, network or events.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` | none / stdout `hello world\n`, exit 0 | play1 (unchanged) |
| `tests/test_hello_sh.py` | Check acceptance criteria 1–4 | script / pass or fail | play1 (unchanged) |
| `CHANGELOG.md` | Record the story for the gate | n/a / one new line under `## Unreleased` | play1 (changed) |

## 5. Interface Contracts
- **CLI contract:**
  - Invocation is `./hello-world/hello.sh`, with no arguments.
  - stdout is exactly `hello world` followed by one newline (A2).
  - stderr is empty and the exit code is 0.
- **Filesystem contract:** `hello-world/` contains only `hello.sh`, with git mode 100755.
- **Changelog contract:** one line under `## Unreleased`, in the existing `- <KEY>: ...` format.
- There are no cross-repo contracts.

## 6. Key Technical Decisions
- **Keep the existing script rather than rewrite it (FR5).** Rewriting would add risk and no value.
- **Keep `echo` and its trailing newline (A2).** The existing byte-exact test expects `hello world\n`. Switching to `printf` without a newline would break it.
- **Reuse the existing tests.** They already cover every criterion, so no new test layer or CI is needed.
- **Alternative considered:** a PR with no changes at all. It was rejected because the gate rule `PLAY-G4` makes the changelog line mandatory.

## 7. Risks & Constraints
- **Leaving out the changelog line:** the gate raises `PLAY-G4`.
- **Adding any file to `hello-world/` (for example a README):** breaks criterion 2 and `test_folder_contains_only_hello_sh`.
- **Changing the script's mode or line endings:** breaks direct execution (criterion 3).
- **A changelog-only PR:** reviewers must read it as confirming delivery, not as new behaviour (A1).
- **`CI_FAIL`:** do not create this file at the repository root.
- Scale, performance and security concerns are negligible: a static script with no input.
