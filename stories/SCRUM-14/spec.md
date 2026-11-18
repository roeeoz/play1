# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

> **Note:** `hello-world/hello.sh` is already on `main` (commit `65938b5`, "WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode 100755, starts with `#!/bin/bash`, prints `hello world` and exits 0, and it is the only file in `hello-world/`. The developer ruled that the story text and its acceptance criteria are the whole requirement and that silent points take the simplest reading, recorded as assumptions (§8). So this story delivers the product the criteria describe: `hello-world/hello.sh` exists and behaves as specified on the target branch. Where the current file already does that, it stays as it is.

- **What is being built:** a minimal, runnable hello-world bash script, `hello.sh`, in its own folder `hello-world` at the root of the play1 repository.
- **Problem:** developers in this repository want a verified, runnable starting point for shell scripting that doesn't clutter existing directories.
- **Target user:** a developer working in the play1 repository.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` from the repository root, without typing `bash`, and get exactly `hello world` with exit code 0.
- The `hello-world` folder holds `hello.sh` and nothing else.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (no README or other docs in or for `hello-world/`). The single `CHANGELOG.md` line the repository gate requires on every pull request is not counted as a documentation file of this feature (assumption A3, §8).

## 3. Functional Requirements

- **FR1 (location):** a folder `hello-world` at the repository root contains a file `hello.sh`.
- **FR2 (isolation):** `hello.sh` is the only file in `hello-world`.
- **FR3 (direct execution):** the first line of `hello.sh` is `#!/bin/bash`, and the file has executable permissions, so `./hello-world/hello.sh` runs without `bash`.
- **FR4 (output):** when run, the script writes exactly the lowercase string `hello world` to standard output, with no other lines, and exits with code 0. A single terminating newline after `hello world` is the normal end of that one line, not trailing whitespace or an additional line (assumption A2, §8).
- **FR5 (existing script):** the script already on `main` is kept when it meets FR1–FR4; the story does not re-create or rewrite it for its own sake (assumption A1, §8).
- **Input:** none. The script takes no arguments and reads no input.

## 4. User Experience & Behavior

- **Flow:** from the repository root, the developer runs `./hello-world/hello.sh`. The terminal shows `hello world`, and `$?` is `0`.
- **Look and feel:** plain terminal text. No colour, no banner, no extra lines.
- **Listing the folder:** `ls hello-world` shows only `hello.sh`.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Existing deliverable:** `hello-world/hello.sh` already exists on `main` (commit `65938b5`). Today it contains `#!/bin/bash` followed by `echo "hello world"`. Running it prints `hello world\n` and exits 0. It is the only file in the folder, with mode 100755.
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 2 says a new shell script must be executable and start with a shebang, which the story already requires. Rule 4 says every pull request must add a line under `## Unreleased` in `CHANGELOG.md`; without it there is a blocker (`PLAY-G4`). No exemption is possible, so any pull request for this story carries that one line (assumption A3).
- **Test gate (`.factory/testing.md`):** `pytest` runs on every pull request through `.github/workflows/ci.yml`. The story adds no CI integration.
- A person merges the pull request after review. The factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. The STRUCTURE stage decides how the script is written and whether and how its behaviour is checked, within the assumptions recorded in §8.

## 8. Open Questions

No blocking questions remain. The developer directed that the story text and its acceptance criteria are the whole requirement, and that where they are silent the simplest reading is taken and recorded as an assumption:

- **A1 — the deliverable already exists.** `hello-world/hello.sh` is already on `main` and meets the four criteria. Simplest reading: the story is done when the target branch holds the script as specified. The existing file is kept, not rewritten. If the platform still opens a pull request, it changes nothing inside `hello-world/` and carries only what the repository gate requires (A3). *Risk:* the pull request shows no product change; reviewers should read it as confirming delivery of the criteria, not as new behaviour.
- **A2 — trailing newline.** Scenario 4's "no trailing whitespace and no additional lines" is read as: the single output line is `hello world`, ended by one newline, which `echo` writes and command substitution strips. *Risk:* a byte-exact check that rejects any newline would fail. That would need the story changed.
- **A3 — `CHANGELOG.md` line.** The repository gate (`PLAY-G4`) requires one line under `## Unreleased` in `CHANGELOG.md` on every pull request, with no exemption possible. That line sits outside `hello-world/` and is not counted as a documentation file of this feature. *Risk:* low; folder isolation (Scenario 2) still holds.
