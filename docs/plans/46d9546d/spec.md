# Feature Specification Document (draft: waiting on one open question)

## 1. Feature Overview
- **Summary:** add a new top-level folder `hello-world/` to the repository. It contains one bash script, `hello.sh`, that a developer can run directly and that prints `hello world` (source: the story's description).
- **Problem statement:** a developer in this repository has no minimal, verified, runnable shell script to start from. The repository has no shell scripts today, and its existing hello feature is a Python one. The new script must not clutter existing directories (source: the story's user story and context).
- **Target users / actors:** a developer working in this repository who needs a minimal runnable shell script as a starting point.

## 2. Goals & Non-Goals
### Goals
- A dedicated `hello-world/` folder at the repository root holding only `hello.sh`.
- `hello.sh` runs directly (`./hello-world/hello.sh`), without being passed to bash, because it has the `#!/bin/bash` shebang and executable permission.
- Running it prints exactly the lowercase text `hello world` and exits with code 0.

### Non-Goals (from the story's out-of-scope list)
- Any additional scripts.
- CI/CD integration (no change to pipeline configuration).
- Documentation files.
- Any change to the repository's existing Python hello feature (its module, its `testbed-hello` command and its tests). It prints `Hello, world!`, a different text, and stays exactly as it is.

## 3. Functional Requirements
- **FR1:** The repository shall contain a top-level folder named `hello-world`.
- **FR2:** The `hello-world` folder shall contain exactly one file, `hello.sh`, and nothing else.
- **FR3:** The first line of `hello.sh` shall be the shebang `#!/bin/bash`.
- **FR4:** `hello.sh` shall have executable permission, and that permission shall be recorded in the repository so that a fresh clone keeps it.
- **FR5:** Running `hello.sh` shall write the lowercase text `hello world` to standard output, with no leading whitespace, no other characters and no additional lines. Whether one line break follows the text is **pending Q1**.
- **FR6:** Running `hello.sh` shall end with exit code 0.
- **Inputs:** none. The script takes no arguments and reads no input.
- **Outputs:** the text in FR5 on standard output, and exit code 0.

## 4. User Experience & Behavior
- **Main flow:** from the repository root, the developer runs `./hello-world/hello.sh`. The terminal shows `hello world` and the command ends successfully.
- **Direct execution:** the developer doesn't need to type `bash hello.sh`. The script runs as a command of its own.
- **Output format:** lowercase `hello world`, one space, no punctuation and no surrounding whitespace. Whether a line break follows the text is pending Q1.
- **Folder contents:** listing `hello-world/` shows only `hello.sh`.

## 5. Acceptance Criteria
1. **Script execution (happy path).** Given the repository contains `hello-world/hello.sh`, when a developer runs `./hello-world/hello.sh` from the repository root, then standard output is exactly `hello world` and the exit code is 0.
2. **Folder isolation (happy path).** Given the `hello-world` folder exists, when a developer lists its contents, then the only file present is `hello.sh`.
3. **Direct execution via shebang (happy path).** Given `hello.sh` has `#!/bin/bash` as its first line and is executable in a fresh clone, when a developer runs it without typing `bash`, then it runs successfully.
4. **Output exactness (edge case).** Given the script is run, when its output is captured, then the output is the lowercase string `hello world` with no leading or trailing spaces or tabs and no additional lines. Whether one line break is allowed after the text is **pending Q1**.

## 6. Dependencies & Constraints (product-level)
- This is the epic's only story. It has no pre-conditions, no blockers and no dependent stories (source: the story's context).
- Priority Must, size XS (≈1).
- The change must not affect the existing Python hello feature or any existing directory.

## 7. Technical Design (deferred to STRUCTURE)
These are left to the tech lead:
- how the script produces its output (depends on the answer to Q1);
- how the executable permission is recorded in the repository;
- line-ending handling;
- whether and where an automated check lives (depends on Q2).

One constraint follows from the product requirements: any automated check must sit outside `hello-world/` (FR2).

## 8. Open Questions
- **Q1 (blocking):** Does "no trailing whitespace and no additional lines" allow one line break after `hello world`, or must the output be exactly the 11 characters with nothing after them?
- **Q2:** May an automated check be added alongside the repository's existing tests, outside `hello-world/`? Working assumption: yes, because that is not CI/CD integration.
- **Q3:** Must the repository readme stay untouched? Working assumption: yes.
- **Q4:** The text of R1–R4 and RK1, which the story traces to, wasn't available to this intake, so coverage against them is unconfirmed.
