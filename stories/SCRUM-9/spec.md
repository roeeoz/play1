# Feature Specification Document — Hello world bash script in a dedicated folder (DRAFT, NOT READY)

## 1. Feature Overview

- **Summary:** a hello-world bash script, `hello.sh`, in its own new folder `hello-world` at the repository root. It prints exactly "hello world" and exits 0.
- **Problem:** developers need a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target user:** a developer working in this repository.

> **Intake finding (blocks readiness):** the repository's target branch `main` already has this deliverable. `hello-world/hello.sh` was added in commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode `100755`, its contents are `#!/bin/bash` followed by `echo "hello world"`, and it is the only file in `hello-world/`. Running it prints `hello world\n` and exits 0. `tests/test_hello_sh.py` already checks all four scenarios (commits `a2ec96d` and `9a5bd0b`). Section 8 records the open question about what this story should change.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals

- A developer can run `./hello-world/hello.sh` directly, without `bash`, and see exactly `hello world`, with exit code 0.
- The `hello-world` folder holds only `hello.sh`.

### Non-Goals

- Additional scripts.
- CI/CD integration.
- Documentation files (README entries in the folder, etc.).

## 3. Functional Requirements

- **FR1:** the folder `hello-world/` exists at the repository root. Its only file is `hello.sh`.
- **FR2:** the first line of `hello.sh` is exactly `#!/bin/bash`.
- **FR3:** `hello.sh` has executable permissions, so `./hello-world/hello.sh` runs without `bash`.
- **FR4:** when run, it writes the lowercase text `hello world` to standard output, with no leading whitespace and no additional lines, and exits with code 0.
- **Inputs:** none. **Outputs:** the stdout text above and exit code 0.
- **Open edge case:** whether the output ends with a single newline. See Q2 in section 8.

## 4. User Experience & Behavior

- **Flow:** a developer at the repository root runs `./hello-world/hello.sh`. The terminal shows `hello world` and the shell reports exit status 0.
- **States:** the user sees no other states. There are no arguments, no prompts and no error messages.
- **Look and feel:** the output is plain lowercase text, `hello world`, with nothing else.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- Pre-conditions and blockers: none, per the story.
- The repository's merge gate (`pytest` plus the `gate` job in `.github/workflows/ci.yml`) runs on every pull request. `tests/test_hello_sh.py` already covers this script.
- A person merges the pull request after review. The factory does not merge.

## 7. Technical Design (deferred to STRUCTURE)

Deferred to the STRUCTURE stage.

## 8. Open Questions (if any remain)

- **Q1 (P0, blocking):** `main` already has the deliverable and its tests (see section 1). What should this story deliver? The options are (a) treat the story as already delivered and close it with verification evidence only, with no code change, or (b) name a concrete change the existing script lacks. I recommend (a): every acceptance criterion already holds on `main`, and anything else would expand the story's own scope.
- **Q2 (P1):** does "no trailing whitespace" in Scenario 4 allow the single newline that ends the line (`hello world\n`, which the current script prints and the existing test requires)? Or must the output be the 11 bytes `hello world` with no newline? I recommend allowing the newline: it is the standard way a line ends, and Scenario 4 already rules out "additional lines".
