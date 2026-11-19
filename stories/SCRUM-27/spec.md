# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

- **What is being built:** a minimal hello-world bash script, `hello.sh`, in a dedicated `hello-world` folder of the play1 repository, which prints exactly "hello world" when run directly.
- **Problem statement:** a developer wants a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target user:** a developer working in the play1 repository.

**Important finding from the repository (main at `b7b5d0a`):** this exact deliverable already exists.
- `hello-world/hello.sh` is present, mode `-rwxr-xr-x`, content `#!/bin/bash` / `echo "hello world"`; it is the only file in `hello-world/`.
- Running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits 0.
- `tests/test_hello_sh.py` already checks output, exit code, shebang, executable bit and folder isolation, and runs in the CI `pytest` gate.
- It was delivered by an earlier story ("20261027-180550Z Hello world bash script in a dedicated folder", commits `65938b5`, `a2ec96d`, `9a5bd0b`).

**Assumption A1 (decided under the developer's instruction to take the simplest reading where the story is silent):** the story is treated as already met by what is on main. The delivery keeps `hello-world/hello.sh` as it is, confirms each acceptance criterion against it (the existing `tests/test_hello_sh.py` stays green), and adds the `CHANGELOG.md` line the repository gate requires for SCRUM-27. No second script or folder is created. *Risk:* if the story's author actually wanted a fresh or different artefact, this delivery adds no new code.

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
- **FR4 — Output:** running the script writes exactly "hello world" (lowercase) to standard output, nothing to standard error, and exits 0. **Assumption A2:** "no trailing whitespace and no additional lines" (Scenario 4) means the output is the one line `hello world`; the single newline that terminates that line (as `echo` prints it today, and as `tests/test_hello_sh.py` asserts) is allowed. No extra blank line, spaces or second line. *Risk:* a consumer comparing raw bytes against the 11 characters `hello world` would see one extra newline.
- **FR5 — Traceability:** the pull request records SCRUM-27 with one line under `## Unreleased` in `CHANGELOG.md`, as the repository gate requires of every pull request (Assumption A3).
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

No blocking questions remain. The developer directed that where the story is silent the simplest reading be taken and recorded; these assumptions stand in for the earlier questions:

- **A1 — Story already delivered on main** (see §1): the delivery verifies the existing script and adds the SCRUM-27 changelog line; no new script or folder. Risk: no new code if a fresh artefact was intended.
- **A2 — One terminating newline is allowed** in the output (see FR4). Risk: a byte-exact consumer would see `hello world\n`, not `hello world`.
- **A3 — The `CHANGELOG.md` line is not a "documentation file"**: the story's exclusion covers new documentation files only; the line is mandatory under the repository gate (PLAY-G4) and is not an exemption the story can grant. Risk: none to the product behaviour.
