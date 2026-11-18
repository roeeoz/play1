# Feature Specification Document: SCRUM-1, Hello world bash script in a dedicated folder

## 1. Feature Overview
- **Summary:** A minimal bash script, `hello.sh`, kept alone in a dedicated `hello-world` folder at the repository root. When run directly, it prints exactly "hello world" and exits successfully.
- **Problem statement:** Developers in this repository want a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target users / actors:** A developer working in this repository.
- **Current state of the target branch (`main`, `b7b5d0a`):** The deliverable is already there. Commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder") added it. `hello-world/hello.sh` contains `#!/bin/bash` and `echo "hello world"`, git stores it as `100755`, and it is the only file in `hello-world/`. Running it prints `hello world` plus a newline and exits with 0. `tests/test_hello_sh.py`, which CI runs through `pytest`, already checks the output, exit code, empty stderr, shebang, executable bit and the folder's contents.

## 2. Goals & Non-Goals
### Story context
This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- The target branch has a `hello-world` folder that contains only `hello.sh`.
- `hello.sh` runs directly (`./hello-world/hello.sh`) through its `#!/bin/bash` shebang and executable permission.
- Running it prints exactly "hello world" to standard output and exits with code 0.
- The story is done when every acceptance criterion below is shown to hold on the target branch. Because `main` already meets them, done may mean confirming them with evidence and making no change to the script.

### Non-Goals
- Additional scripts (inside or outside `hello-world/`).
- CI/CD integration (new or changed pipelines).
- Documentation files (README, CHANGELOG entries, docs).
- Any other file inside `hello-world/`.
- Rewriting the existing script when it already meets the criteria.

## 3. Functional Requirements
- **FR1: Folder.** A folder named `hello-world` exists at the repository root, and its only entry is `hello.sh`.
- **FR2: Script identity.** The script is named `hello.sh`, and its first line is the shebang `#!/bin/bash`.
- **FR3: Direct execution.** `hello.sh` has executable permission, so a developer can run `./hello-world/hello.sh` without typing `bash`.
- **FR4: Output.** When run, the script writes exactly the lowercase text `hello world` to standard output as one line, with no leading or trailing spaces or tabs and no other lines. The single line ending after it is allowed (see Assumption A2).
- **FR5: Exit status.** The script exits with code 0.
- **Inputs:** none. The script takes no arguments and reads no input.
- **Edge cases:** Output exactness (FR4) is the only user-facing edge case the story names.

## 4. User Experience & Behavior
- **Key flow:** The developer clones or opens the repository, runs `./hello-world/hello.sh` from the repository root, and sees `hello world` in the terminal. The command returns success (exit code 0).
- **Listing flow:** The developer lists `hello-world/` and sees only `hello.sh`.
- **Output format:** One line, lowercase `hello world`, nothing before it and nothing after it except the terminal's normal line ending.
- **States / errors:** The story defines no error states or messages.

## 5. Acceptance Criteria
1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)
- This is the only story of its epic. No sibling stories, and no preconditions or blockers.
- Folder isolation (criterion 2) means nothing else may be added inside `hello-world/`. Any supporting artifact must live elsewhere. The existing test, for example, lives in `tests/`.
- The repository's own gate (`pytest`, run in CI) applies to any pull request. The existing `tests/test_hello_sh.py` already encodes these criteria and must keep passing.
- A person reviews and merges any pull request; the factory never merges.
- `hello-world/hello.sh` has a history of probe commits that were changed and then reverted. Any work must be checked against the exact content currently on `main`.

## 7. Technical Design (deferred to STRUCTURE)
STRUCTURE decides how to deliver this story when the target branch already meets every criterion: either confirmation only with evidence, or the smallest change that still keeps the script and its folder exactly as the criteria describe. It also decides how that evidence is shown. This spec does not resolve either question.

## 8. Open Questions
- None blocking. Two assumptions were made on the developer's instruction to take the simplest reading wherever the story is silent:
  - **A1:** The story is satisfied by the existing script on `main`. "A new folder" describes the outcome, not a requirement to recreate a folder that already exists.
  - **A2:** In criterion 4, "no trailing whitespace and no additional lines" allows the single final line ending that standard command-line output (`echo`) produces. The script prints `hello world\n`, which is what the existing test expects.
