# Feature Specification Document — Hello world bash script in a dedicated folder (DRAFT, not ready)

## 1. Feature Overview

**Status: in-progress intake draft (NOT_READY).** Two blocking questions in §8 must be answered before this becomes the final specification.

- **What is being built:** a hello-world bash script, `hello.sh`, in its own folder `hello-world/` at the repository root. Running it prints exactly "hello world".
- **Problem statement:** a developer in this repository wants a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target users / actors:** a developer working in the play1 repository.

**Finding: the deliverable already exists on the target branch.** On `main` (b7b5d0a), which this story's work branch was cut from:
- `hello-world/hello.sh` is tracked with mode `100755` (executable). It was added in commit 65938b5, "WI-220A63-1: Add hello-world bash script in dedicated folder".
- Its content is `#!/bin/bash` followed by `echo "hello world"`. Running it prints `hello world` plus one terminating newline and exits with 0. This was verified locally.
- `hello-world/` contains only `hello.sh`.
- `tests/test_hello_sh.py` (commits a2ec96d and 9a5bd0b, from an earlier run of a story with the same title) already checks each scenario in §5. It covers the output and exit code, the absence of stderr output, the shebang line, the executable bit, and that the folder holds only this one file. CI's `test` job runs it on every pull request.

So the story's outcome is already met on `main`. The open question is what this story should still change (§8, Q1).

## 2. Goals & Non-Goals
### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` directly, without invoking bash explicitly, and gets exactly "hello world" on standard output with exit code 0.
- The `hello-world` folder holds only `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (for example a README in `hello-world/`).

## 3. Functional Requirements

- **FR1:** The repository has a folder `hello-world/` at its root, containing a file `hello.sh`.
- **FR2:** `hello.sh` starts with the shebang line `#!/bin/bash` and has executable permissions.
- **FR3:** Running `./hello-world/hello.sh` writes exactly `hello world` (lowercase) to standard output and exits with code 0. It needs no input or arguments.
- **FR4:** `hello-world/` contains no file other than `hello.sh`.
- **Edge case, output exactness:** no leading or trailing whitespace and no additional lines. Whether the single terminating newline counts as allowed is open (§8, Q2).

## 4. User Experience & Behavior

- **Flow:** from the repository root, the developer runs `./hello-world/hello.sh`. The terminal shows `hello world` and the command succeeds (exit code 0).
- **No other states:** the script takes no input and has no error path.
- **Look and feel:** the request names no qualities beyond the exact output text.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Repository gate:** the play1 layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) runs on every pull request.
  - Rule 2 requires a new shell script to be executable and to start with a shebang. The story already requires both.
  - Rule 4 requires every pull request to add a line under `## Unreleased` in `CHANGELOG.md`. Otherwise the gate raises blocker `PLAY-G4`.
  - The story lists "documentation files" as out of scope. I read that as files inside `hello-world/`, not the repository-wide changelog. If that reading holds, any pull request from this story must still add a changelog line. This rule cannot be waived per story.
- **Test gate:** `pytest` (`.factory/testing.md`, CI `test` job). `tests/test_hello_sh.py` already covers this behaviour, so any change to the script's output must keep that test passing, or update it.
- **Depends on:** nothing. Pre-conditions: none. Blockers: none.

## 7. Technical Design (deferred to STRUCTURE)

Deferred to STRUCTURE. The product imposes no technical constraint beyond §3 and the repository gates in §6.

## 8. Open Questions (if any remain)

- **Q1 (P0, blocking):** what should this story deliver, given that its whole outcome is already on `main`?
  - Already present: `hello-world/hello.sh`, executable with the `#!/bin/bash` shebang, printing "hello world" and exiting with 0, alone in its folder, and covered by `tests/test_hello_sh.py`.
  - Option (a): close the story as already delivered, with no pull request.
  - Option (b): open a verification-only pull request. Its only change would be the required `CHANGELOG.md` line, recording that SCRUM-33 is satisfied by the existing script.
  - Option (c): rewrite the script anyway. This gives the same observable result.
  - **Recommendation: (a).** Every acceptance criterion already holds and is enforced in CI, so a pull request would add no product change. I would pick (b) if you need a merged pull request for SCRUM-33's traceability.
- **Q2 (P0, blocking):** Scenario 4 says "no trailing whitespace and no additional lines". Does the single newline that ends the output line count as allowed?
  - The existing script prints `hello world\n`, and `tests/test_hello_sh.py` asserts exactly that.
  - **Recommendation: yes, allow it.** It terminates the one line rather than adding a line. It is how shell output is normally captured, and it keeps the existing script and test valid.
  - If you answer no, the script and its test must change to print `hello world` with no newline.
