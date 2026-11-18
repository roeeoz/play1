# Feature Specification Document — Hello world bash script in a dedicated folder (DRAFT, not ready)

## 1. Feature Overview

- **What:** a minimal, runnable bash script `hello.sh` that prints "hello world", living alone in a dedicated top-level folder `hello-world`.
- **Problem:** developers in this repository want a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target users:** developers working in the play1 repository.
- **Status found in the repository (intake finding):** the target branch `main` already contains this deliverable. `hello-world/hello.sh` was added by commit `65938b5` ("Add hello-world bash script in dedicated folder"); it is the only file in the folder, starts with `#!/bin/bash`, is executable (`-rwxr-xr-x`), and running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits 0. `tests/test_hello_sh.py` already checks output, exit code, shebang, executable bit and folder isolation. What this story must still change is therefore open (see §8, Q1).

## 2. Goals & Non-Goals
### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` directly and see exactly "hello world".
- The `hello-world` folder contains only `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (README etc.) — subject to the repository's mandatory changelog rule, see §6 and Q3.

## 3. Functional Requirements

- **FR1** — A top-level folder named `hello-world` exists and contains exactly one file, `hello.sh`.
- **FR2** — `hello.sh` starts with the shebang line `#!/bin/bash` and has executable permissions, so it runs as `./hello-world/hello.sh` without `bash` in front.
- **FR3** — Running the script takes no input and writes exactly the lowercase text `hello world` to standard output, nothing else, and exits with code 0. Whether the single line-terminating newline after the text is allowed is open (Q2).

## 4. User Experience & Behavior

- **Flow:** the developer clones the repository, runs `./hello-world/hello.sh` from the repository root, and sees `hello world` in the terminal; the prompt returns with exit status 0.
- **Listing the folder** shows only `hello.sh`.
- No interactive behaviour, arguments, colours or error messages are specified.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Repository layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): a new shell script must be executable and start with a shebang (already met); and **every pull request must add a line under `## Unreleased` in `CHANGELOG.md`** (rule PLAY-G4, blocker). This collides with "Out of scope: documentation files" if `CHANGELOG.md` counts as one (Q3). The gate cannot be waived for this story.
- **Test gate** (`.factory/testing.md`, `.github/workflows/ci.yml`): `pytest` runs on every pull request; `tests/test_hello_sh.py` currently pins the output to `"hello world\n"`, so a change to the newline rule (Q2) changes that test too.
- No other product depends on this script.

## 7. Technical Design (deferred to STRUCTURE)

Deferred. The product imposes no technical constraint beyond §3 and §6.

## 8. Open Questions

- **Q1 (P0)** — The deliverable already exists on `main` (commit `65938b5`) and meets all four criteria as written (modulo Q2). What should this story deliver? (a) Close it as already done, with no pull request; (b) a pull request that only records the story in `CHANGELOG.md`; (c) something else that is missing. Recommended: (a).
- **Q2 (P0)** — Does "no trailing whitespace and no additional lines" allow the single newline that ends the line (`hello world\n`, as today), or must the output be the 11 bytes `hello world` with no newline at all? Recommended: allow the single newline.
- **Q3 (P0, only if a pull request is made)** — The repository gate requires every pull request to add a `CHANGELOG.md` line; confirm that this entry is in scope despite "no documentation files". Recommended: yes.
