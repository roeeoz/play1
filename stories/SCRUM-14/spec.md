# Feature Specification Document — Hello world bash script in a dedicated folder (draft, NOT READY)

## 1. Feature Overview

> **Status: NOT READY.** The repository already holds what this story asks for. `hello-world/hello.sh` is on `main` (commit `65938b5`, "WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode 100755, starts with `#!/bin/bash`, prints `hello world` and exits 0, and it is the only file in `hello-world/`. Until the open questions in §8 are answered, it is unclear what this story is supposed to change.

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
- Documentation files. The repository gate's required `CHANGELOG.md` line is an open question, see §8 Q3.

## 3. Functional Requirements

- **FR1 (location):** a folder `hello-world` at the repository root contains a file `hello.sh`.
- **FR2 (isolation):** `hello.sh` is the only file in `hello-world`.
- **FR3 (direct execution):** the first line of `hello.sh` is `#!/bin/bash`, and the file has executable permissions, so `./hello-world/hello.sh` runs without `bash`.
- **FR4 (output):** when run, the script writes exactly the lowercase string `hello world` to standard output, with no other lines, and exits with code 0. Whether a single terminating newline is allowed is open, see §8 Q2.
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
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 2 says a new shell script must be executable and start with a shebang, which the story already requires. Rule 4 says every pull request must add a line under `## Unreleased` in `CHANGELOG.md`; without it there is a blocker (`PLAY-G4`). This collides with "documentation files" being out of scope (see Q3).
- **Test gate (`.factory/testing.md`):** `pytest` runs on every pull request through `.github/workflows/ci.yml`. The story adds no CI integration.
- A person merges the pull request after review. The factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. The STRUCTURE stage decides how the script is written and whether and how its behaviour is checked, within the scope settled in §8.

## 8. Open Questions

- **Q1 (P0): the deliverable already exists.** `hello-world/hello.sh` is already on `main` and appears to meet all four acceptance criteria. What should this story deliver?
  - (a) Close it as already delivered, with no pull request.
  - (b) A pull request that only records the existing script in `CHANGELOG.md`.
  - (c) Re-create or replace the script anyway.
  - *Recommendation:* (a). Any pull request would change no product behaviour. (b) is the fallback only if a pull request is mandatory for traceability.
- **Q2 (P0): trailing newline.** Scenario 4 says "no trailing whitespace and no additional lines". The current script prints `hello world` followed by one terminating newline. Does a single terminating newline count as exact output?
  - *Recommendation:* yes. It is standard terminal behaviour, it adds no extra line, and command substitution strips it. Answer "no" if the bytes must be exactly `hello world` with no newline.
- **Q3 (P0): CHANGELOG line versus "documentation files out of scope".** The repository gate blocks any pull request that does not add a line to `CHANGELOG.md` (rule `PLAY-G4`). No exemption is possible. Is that one line allowed?
  - *Recommendation:* yes. It sits outside `hello-world/`, so folder isolation still holds. The only alternative is to change the gate rule in the repository first.
