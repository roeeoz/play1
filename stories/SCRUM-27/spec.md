# Feature Specification Document — Hello world bash script in a dedicated folder (draft, NOT READY)

## 1. Feature Overview

> **Status: in-progress intake draft — NOT READY.** See §8 for the blocking questions.

- **What is being built:** a minimal hello-world bash script, `hello.sh`, in a dedicated `hello-world` folder of the play1 repository, which prints exactly "hello world" when run directly.
- **Problem statement:** a developer wants a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target user:** a developer working in the play1 repository.

**Important finding from the repository (main at `b7b5d0a`):** this exact deliverable already exists.
- `hello-world/hello.sh` is present, mode `-rwxr-xr-x`, content `#!/bin/bash` / `echo "hello world"`; it is the only file in `hello-world/`.
- Running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits 0.
- `tests/test_hello_sh.py` already checks output, exit code, shebang, executable bit and folder isolation, and runs in the CI `pytest` gate.
- It was delivered by an earlier story ("20261027-180550Z Hello world bash script in a dedicated folder", commits `65938b5`, `a2ec96d`, `9a5bd0b`).

So what this story must change in the repository is not yet defined (see §8, Q1).

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` from the repository root and see exactly "hello world" on standard output, exit code 0.
- The script runs directly via its `#!/bin/bash` shebang and executable bit, without `bash hello.sh`.
- The `hello-world` folder contains only `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration (no change to `.github/workflows/ci.yml`).
- Documentation files (no README or docs in or for the folder).

## 3. Functional Requirements

- **FR1 — Location:** a folder `hello-world` at the repository root holds a file `hello.sh`. (Already true on main.)
- **FR2 — Isolation:** `hello.sh` is the only file in `hello-world`. (Already true on main.)
- **FR3 — Direct execution:** the first line of `hello.sh` is `#!/bin/bash` and the file is executable, so `./hello-world/hello.sh` runs without invoking `bash`. (Already true on main.)
- **FR4 — Output:** running the script writes exactly "hello world" (lowercase) to standard output, nothing to standard error, and exits 0. **Open:** whether the single trailing newline the script prints today counts as "no trailing whitespace" (Q2).
- **Inputs:** none (no arguments, no environment).
- **Edge cases:** output exactness (Scenario 4); nothing else is in scope.

## 4. User Experience & Behavior

- **Flow:** from the repository root the developer runs `./hello-world/hello.sh`; the terminal shows `hello world` and the shell prompt returns, `$?` is `0`.
- **Listing:** `ls hello-world` shows `hello.sh` only.
- No look-and-feel, interaction or performance qualities were requested beyond the exact output text.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Existing delivery:** the earlier story "20261027-180550Z Hello world bash script in a dedicated folder" already shipped `hello-world/hello.sh` and `tests/test_hello_sh.py` on main.
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** every pull request must add a line under `## Unreleased` in `CHANGELOG.md` (rule PLAY-G4, blocker); a new shell script must be executable and start with a shebang. The story's "no documentation files" exclusion is read as "no new doc files", so a CHANGELOG line is still required by any PR.
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** `pytest` must stay green; `tests/test_hello_sh.py` currently asserts the output is `"hello world\n"`.

## 7. Technical Design (deferred to STRUCTURE)

How the script and its checks are implemented is left to STRUCTURE. The only product-imposed constraints are the exact path, name, shebang, executable bit, folder contents and output in §3/§5.

## 8. Open Questions

**Blocking (P0)**

- **Q1 — What should this story change, given the script already exists on main?** `hello-world/hello.sh` already meets Scenarios 1–3 and is covered by `tests/test_hello_sh.py`. Options: (a) treat the story as already delivered — the PR only verifies it and adds a `CHANGELOG.md` line recording SCRUM-27 (the gate requires one); (b) close the story without a PR; (c) re-create it somewhere new (a different folder name). Recommendation: (a) — it is the only option that still ends in a reviewable PR that passes the repo gate without duplicating code; pick (b) if no PR is wanted, or (c) only if a different folder name is actually intended.
- **Q2 — Does "no trailing whitespace and no additional lines" (Scenario 4) allow the single newline that ends the line?** Today the script prints `hello world\n` and the existing test asserts exactly that. Options: (a) one terminating newline is allowed (the line is "hello world", nothing else); (b) no newline at all — the output is the 11 bytes `hello world`, which changes the script and the existing test. Recommendation: (a) — it is the standard shell behaviour, matches what is already shipped and tested, and keeps the terminal prompt on its own line; choose (b) only if a consumer compares raw bytes.

**Important (P1)**

- **Q3 — Is a `CHANGELOG.md` line acceptable despite "Out of scope: documentation files"?** The repository gate blocks any PR without one (PLAY-G4). Working assumption: yes — the exclusion covers new documentation files, not the mandatory changelog line.
