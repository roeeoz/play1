# HLD — PLAY-163: `qa/pe-greet.sh` prints "hello pe" and exits 0

Target repo: `roeeoz/play1` · Base branch: `qa-20261108-s4-base`

## 1. System overview
- **What is built:** one standalone POSIX shell script, `qa/pe-greet.sh`, in the existing `qa/` directory. It prints exactly `hello pe\n` to stdout and exits 0. One line is also added under `## Unreleased` in `CHANGELOG.md`.
- **Why:** this is a one-story, one-file epic that tests the full factory lifecycle against play1 (goal G3: a small change that can be merged).
- **Responsibilities:** deterministic output, exit code 0, runnable directly, and nothing else changes.

## 2. Architecture overview
- **No runtime architecture:** there is no service, no module and no Python change. The script is a leaf artifact that nothing imports or calls.
- **Fit with the existing system:** it follows the same three-line shape as its neighbours (`qa/s3-hello.sh`, `qa/s4-greet.sh`): a `#!/bin/sh` shebang, a one-line `#` purpose comment, then a single fixed `printf`. LF line endings, committed as mode 100755.
- **External dependencies:** only `/bin/sh` and its built-in `printf`.

## 3. Data flow
- The user runs `qa/pe-greet.sh [any args]`. The kernel reads the shebang and runs `/bin/sh`, which prints `hello pe\n` to stdout. The script exits 0.
- The flow is synchronous. There are no events, no input, no state and no files read or written.

## 4. Components
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `qa/pe-greet.sh` | Print the fixed greeting and exit 0 | In: none (arguments ignored). Out: stdout `hello pe\n`, empty stderr, exit 0 | roeeoz/play1 |
| `CHANGELOG.md` entry | Satisfy merge-gate rule 4 (PLAY-G4) | One line under `## Unreleased`, following the house style `- <KEY>: add `<path>`, <description>.` | roeeoz/play1 |

## 5. Interface contracts
- **CLI contract:** for any arguments (including `--help` or `x y`), stdout is exactly the bytes `hello pe\n`, stderr is empty and the exit code is 0.
- **Cross-repo contracts:** none. There are no APIs and no events.

## 6. Key technical decisions
- **`printf` with a fixed string instead of `echo`:** this avoids differences in how shells handle `echo` and matches the neighbouring scripts.
- **`#!/bin/sh` instead of bash:** the spec requires it (FR4), and it matches the directory convention.
- **Purpose comment on line 2:** kept to match the neighbours' convention. It doesn't affect the output.
- **No argument parsing:** arguments are ignored without any code, which meets FR3.
- **No pytest test:** the spec excludes tests (FR6/AC4), even though `tests/test_qa_s3_greeting.py` provides a pattern. Verification is a manual run plus code review (RK2).
- **Changelog line:** included because merge-gate rule 4 (PLAY-G4) blocks any PR that doesn't touch `CHANGELOG.md`. The approved spec puts it in scope (FR5).

## 7. Risks & constraints
- **Executable bit not committed:** this would break FR4/AC1 and gate rule 2. Check that `git ls-files -s qa/pe-greet.sh` shows 100755.
- **Stray output:** a CRLF ending, a trailing space, `set -x` or an `echo` variant would break FR1. Use a fixed `printf` and LF line endings.
- **Scope creep (RK1):** adding `--help`, a test or docs would break FR3, FR6 and AC4.
- **Changelog:** a missing entry fails the gate (PLAY-G4). More than one line, or an edit outside `## Unreleased`, breaks FR5.
- **Stale epic reference:** the epic names `qa/s3-a.sh`, which is not on the base branch. Regression checks use `qa/s3-hello.sh` and `qa/s4-greet.sh`.
- **Plan-folder docs** (`stories/PLAY-163/*`) appear in the PR diff. AC4 is read as applying to product files.
- **Scale, performance and security:** not applicable beyond the rule that the script, the changelog line and commit messages contain no secrets or personal data. There are no new dependencies and no licensing concerns.
