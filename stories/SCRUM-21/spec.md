# Feature Specification Document — Hello world bash script in a dedicated folder (draft, NOT READY)

## 1. Feature Overview

> **Intake status: NOT READY.** The repository already contains what this story
> asks for (see §6 and §8). What this story should change has to be settled
> before the specification can be final.

- **What is being built:** a minimal bash script, `hello-world/hello.sh`, in its
  own folder, that prints exactly `hello world` to standard output when run directly.
- **Problem statement:** a developer in this repository wants a verified, runnable
  starting point for shell scripting that doesn't clutter existing directories.
- **Target users / actors:** a developer working in the `play1` repository.
- **User story:** As a developer, I want a hello-world bash script in its own
  dedicated folder in the repository, so that I have a verified, runnable starting
  point for shell scripting without cluttering existing directories.
- **Traceability:** R1, R2, R3, R4 · steps 1–4 · RK1. Priority: Must. Size: XS (≈1).
  Pre-conditions: none. Blockers: none listed in the story (one found at intake, see §8).

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
  *Undecided:* whether the standard terminating newline that ends the one
  line (`hello world\n`) is allowed, or the output must be the 11 bytes
  `hello world` with no newline at all (see §8, Q2).

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

How to deliver this is left to the STRUCTURE stage. The product adds one
constraint: the delivered state must keep the existing `pytest` suite green,
including `tests/test_hello_sh.py`, or change that test in step with any
output change agreed under Q2.

## 8. Open Questions (if any remain)

- **Q1 (P0, blocking) — What should this story change, given that the deliverable
  already exists on `main`?** Options:
  (a) Close the story as already delivered by commit `65938b5`, with no pull request.
  (b) Deliver a verification-only pull request that keeps the script as it is and
  adds the required `CHANGELOG.md` line tracing to SCRUM-21.
  (c) Something the current story doesn't say, such as a different folder or
  script name, or different content.
  *Recommendation: (a).* All four criteria are already met and tested, and an
  empty change has no product value. (b) only makes sense if you need a
  SCRUM-21 pull request for traceability.
- **Q2 (P0, blocking) — Does "no trailing whitespace" in Scenario 4 allow the
  newline that ends the line?** Options:
  (a) `hello world` followed by one newline, which is what the script prints
  today and what `tests/test_hello_sh.py` asserts.
  (b) Exactly the 11 bytes `hello world` with no newline.
  *Recommendation: (a).* It is standard terminal output, it matches the existing
  script and test, and (b) leaves the shell prompt on the same line as the output.
  I'd only switch to (b) if a consumer compares raw bytes.
