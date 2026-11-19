# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

> **Status: specification.** The developer ruled that the story text and its acceptance criteria are the whole requirement and that, where they are silent, the simplest reading applies and is recorded as an assumption. Assumptions A1–A3 (section 8) settle the three earlier intake questions.

- **What:** a bash script `hello.sh` in a new, dedicated top-level folder `hello-world/`. Run directly, it prints "hello world" and exits 0.
- **Problem:** a developer in this repository wants a minimal, verified, runnable shell-script starting point that doesn't clutter existing folders (for example `qa/`, which already holds other QA scripts).
- **Actor:** a developer working in this repository.

**Finding from the repository:** the target branch `main` **already contains** `hello-world/hello.sh`. It was added by commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode `100755`, its content is `#!/bin/bash` + `echo "hello world"`, it is the only file in the folder, and it prints `hello world\n` with exit code 0. The story as written is therefore already delivered on `main`. Per assumption A1, this story verifies the existing script against the four criteria and leaves `hello-world/` unchanged; it changes the script only if verification shows a criterion is not met.

## 2. Goals & Non-Goals
### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` from the repository root without calling `bash` explicitly. It prints "hello world" and exits with code 0.
- The `hello-world/` folder holds only `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration, such as a new workflow job or a test that runs the script in CI.
- Documentation files, such as a README in the folder. The one line the repository gate requires in the root `CHANGELOG.md` is not a documentation file in this sense (assumption A3).
- Rewriting, renaming or moving the existing `hello-world/hello.sh` when it already meets the criteria (assumption A1).

## 3. Functional Requirements

- **FR1 — Location:** a folder `hello-world/` at the repository root contains a file `hello.sh`.
- **FR2 — Isolation:** `hello.sh` is the only file in `hello-world/`.
- **FR3 — Direct execution:** the first line of `hello.sh` is `#!/bin/bash` and the file is executable, so `./hello-world/hello.sh` runs without `bash` in front of it.
- **FR4 — Output:** standard output is exactly the lowercase string `hello world`, with no leading or trailing whitespace and no additional lines. One terminating newline (`hello world\n`, the normal output of `echo`) is a single line with no additional lines and satisfies this (assumption A2).
- **FR5 — Exit status:** the script exits with code 0.
- **Inputs:** none. The script takes no arguments and reads no input.
- **Edge cases:** output exactness (FR4) is the only edge case the story names.

## 4. User Experience & Behavior

- **Flow:** from the repository root the developer runs `./hello-world/hello.sh`. The terminal shows `hello world`, and `echo $?` shows `0`.
- **Listing:** `ls -A hello-world` shows only `hello.sh`.
- The story names no visual style, no interaction affordances and no error messages.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **The play1 layout gate**, which runs on every pull request (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):
  - rule 2: a new shell script must be executable and start with a shebang. The story already requires this.
  - rule 4: every pull request must add a line under `## Unreleased` in the root `CHANGELOG.md`. A pull request that doesn't do this is blocked (`PLAY-G4`). The pull request adds that one line (assumption A3); it sits outside `hello-world/`, so the folder still holds only `hello.sh`.
- **Test gate:** `pytest`, via `.factory/testing.md` and the `test` job in `.github/workflows/ci.yml`. The story asks for no CI integration, so no test is added.
- **Existing state:** `hello-world/hello.sh` already exists on `main` (see section 1 and assumption A1).

## 7. Technical Design (deferred to STRUCTURE)

Deferred to STRUCTURE. The product imposes no technical constraint beyond those listed in section 6.

## 8. Open Questions

No blocking questions remain. The developer instructed that, where the story is silent, the simplest reading applies; these assumptions record those readings and their risk:

- **A1 — Deliverable given the existing script.** The script already exists on `main` and meets all four criteria, so the story verifies it and leaves `hello-world/` unchanged; the pull request carries only the required CHANGELOG line. *Risk:* if the intent was a fresh or different script, the pull request will look empty of functional change.
- **A2 — Trailing newline.** "Exactly `hello world` … no additional lines" is met by `hello world` followed by one newline, as `echo` prints. *Risk:* a byte-exact comparison expecting 11 bytes with no newline would fail; that would need the script changed to `printf 'hello world'`.
- **A3 — CHANGELOG line.** "Documentation files out of scope" excludes new documentation files (such as a README in `hello-world/`), not the one `CHANGELOG.md` line the play1 layout gate (rule 4) requires on every pull request. *Risk:* none to the folder-isolation criterion, since the line is outside `hello-world/`.
