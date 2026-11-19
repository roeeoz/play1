# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

> **Intake status: READY.** The repository already contains what this story asks
> for (see §6). Per the developer's instruction to take the simplest reading where
> the story is silent, this story's delivery keeps that script as it is and
> verifies it against the four criteria (assumptions A1–A2 in §8).

- **What is being built:** a minimal bash script, `hello-world/hello.sh`, in its
  own folder, that prints exactly `hello world` to standard output when run directly.
- **Problem statement:** a developer in this repository wants a verified, runnable
  starting point for shell scripting that doesn't clutter existing directories.
- **Target users / actors:** a developer working in the `play1` repository.
- **User story:** As a developer, I want a hello-world bash script in its own
  dedicated folder in the repository, so that I have a verified, runnable starting
  point for shell scripting without cluttering existing directories.
- **Traceability:** R1, R2, R3, R4 · steps 1–4 · RK1. Priority: Must. Size: XS (≈1).
  Pre-conditions: none. Blockers: none.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- The repository has a `hello-world` folder whose only file is `hello.sh`.
- `hello.sh` starts with `#!/bin/bash`, is executable, and can be run directly
  (`./hello-world/hello.sh`) without typing `bash`.
- Running it prints exactly `hello world` and exits with code 0.

### Non-Goals
- Additional scripts.
- CI/CD integration (changes to `.github/workflows/ci.yml`).
- Documentation files (README or similar inside or about the folder).

## 3. Functional Requirements

- **FR1 — Dedicated folder.** A folder `hello-world/` at the repository root
  holds exactly one file, `hello.sh`.
- **FR2 — Shebang.** The first line of `hello.sh` is exactly `#!/bin/bash`.
- **FR3 — Direct execution.** `hello.sh` has executable permission, so
  `./hello-world/hello.sh` runs it without an explicit `bash`.
- **FR4 — Output.** When run, the script writes the lowercase string
  `hello world` to standard output and exits with code 0. Inputs: none
  (no arguments or environment are read).
- **FR5 — Output exactness (edge case).** The output has no leading
  whitespace, no extra lines, and nothing else on standard output.
  The single newline that terminates that one line (`hello world\n`) is
  allowed: it is not "trailing whitespace" or an "additional line"
  (assumption A2, §8).
- **FR6 — Delivery against the existing state.** `hello-world/hello.sh` already
  exists on `main` and meets FR1–FR5. The script, its folder and its content are
  kept unchanged; the story is delivered as a verification of that state
  (assumption A1, §8).

## 4. User Experience & Behavior

- **Flow:** the developer opens a terminal at the repository root, runs
  `./hello-world/hello.sh`, and sees `hello world` on one line; the shell prompt
  returns and `echo $?` shows `0`.
- **Listing the folder:** `ls hello-world` shows only `hello.sh`.
- **States:** none. The script has no options, no input and no error path the
  developer can trigger. The only failure a developer could see is
  "Permission denied" if the executable bit is missing, which FR3 rules out.
- **Look and feel:** plain text, lowercase, no colour, no banner, no extra lines.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **The deliverable already exists on `main`.** `hello-world/hello.sh` is
  tracked with mode `100755`, contains `#!/bin/bash` and `echo "hello world"`,
  and is the only file in `hello-world/`. It was added by commit `65938b5`
  ("WI-220A63-1: Add hello-world bash script in dedicated folder"). Running it
  today prints `hello world\n` and exits 0. `tests/test_hello_sh.py` already
  checks the output, the shebang, the executable bit and that the folder holds
  only `hello.sh`. On the current tree, criteria 1–3 are already met, and
  criterion 4 is met if a terminating newline is allowed.
- **Repository gates every pull request must pass** (they cannot be waived):
  - `play1 layout gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):
    a new shell script must be executable with a shebang. **Rule 4:** the pull
    request must add a line under `## Unreleased` in `CHANGELOG.md`, or the gate
    blocks it (`PLAY-G4`). Updating that line isn't adding a "documentation file",
    so it doesn't conflict with the story's non-goal.
  - Test gate (`.factory/testing.md`, the `test` job in `.github/workflows/ci.yml`):
    `pytest` must pass, including the existing `tests/test_hello_sh.py`. That test
    expects the output to be exactly `hello world\n`.
- A person merges the pull request after review. The factory doesn't merge.

## 7. Technical Design (deferred to STRUCTURE)

How to deliver this is left to the STRUCTURE stage. The product adds two
constraints: the script must stay as it is on `main` (A1), and the delivered
state must keep the existing `pytest` suite green, including
`tests/test_hello_sh.py`, which already expects `hello world\n` (A2). Any pull
request also has to meet the layout gate's `CHANGELOG.md` rule (§6).

## 8. Open Questions (if any remain)

No open product questions. The developer instructed: "The story text and its
acceptance criteria are the whole requirement. Where they are silent, take the
simplest reading, record it as an assumption in the spec, and proceed." The two
points the story is silent on are recorded as assumptions:

- **A1 — The deliverable already exists; nothing in it changes.** The story asks
  for a script that `main` already has (commit `65938b5`), and it asks for no
  change to it. Simplest reading: the script, its folder and its content stay
  exactly as they are, and the story is delivered by verifying the four criteria
  against them. If a pull request is opened, its only change is the line under
  `## Unreleased` in `CHANGELOG.md` tracing SCRUM-21 that the layout gate
  requires (`PLAY-G4`); that is an entry in an existing file, not a new
  documentation file. *Risk:* the change has no user-visible effect; if the
  intent was a different folder, name or content, this story does not deliver it.
  Closing the story with no pull request remains the human's option.
- **A2 — The terminating newline is allowed.** In Scenario 4, "no leading or
  trailing whitespace and no additional lines" is read as: the one output line is
  `hello world`, ended by the standard single newline (`hello world\n`), which is
  what the script prints and the existing test asserts. *Risk:* a consumer that
  compares raw bytes against the 11 bytes `hello world` would see a mismatch.
