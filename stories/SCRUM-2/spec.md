# Feature Specification Document: 20261118-212149Z Hello world bash script in a dedicated folder

## 1. Feature Overview
- **What:** a minimal, runnable hello-world bash script, `hello.sh`, in its own folder `hello-world` at the repository root. Running it prints exactly `hello world`.
- **Problem:** developers in this repository want a checked, runnable starting point for shell scripting that doesn't clutter the existing directories.
- **Target users:** developers working in the play1 repository.
- **Current state of the target branch (`main`, `b7b5d0a`):** the deliverable is already there. It came from an earlier run of this same story (work item WI-220A63, 2026-10-27). `hello-world/hello.sh` contains `#!/bin/bash` and `echo "hello world"`, is tracked as executable (100755), and is the only file in the folder. `tests/test_hello_sh.py` already covers the behavior (6 tests, all passing), and CI runs it on every pull request.

## 2. Goals & Non-Goals
### Story context
This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- The repository has a `hello-world` folder that holds only `hello.sh`.
- `hello.sh` runs directly (`./hello-world/hello.sh`) through its `#!/bin/bash` shebang and executable bit, prints exactly `hello world`, and exits with code 0.
- The delivery shows, for each acceptance criterion, that the target branch meets it. Where `main` already does, no code change is needed.

### Non-Goals
- Additional scripts.
- CI/CD integration, including changes to `.github/workflows/`.
- Documentation files: no README in `hello-world/` and no CHANGELOG entry.
- Rebuilding or rewriting the existing script or tests when they already meet the criteria.

## 3. Functional Requirements
- **FR1: Folder.** A folder named `hello-world` exists at the repository root.
- **FR2: Isolation.** `hello.sh` is the only file in `hello-world`. Supporting files such as tests stay outside the folder.
- **FR3: Script identity.** The file is named `hello.sh`. Its first line is the shebang `#!/bin/bash`, and it has executable permission.
- **FR4: Behavior.**
  - Input: none. The script takes no arguments and reads no input.
  - Output: the single line `hello world` (lowercase) on standard output, ending with one newline (see Assumption A2). Nothing goes to standard error.
  - Exit: exit code 0.
- **FR5: Direct execution.** Running `./hello-world/hello.sh` from the repository root works without typing `bash` first.
- **Edge cases:**
  - Output exactness: no leading spaces, no trailing spaces, no extra lines.
  - Folder contents: any file added next to `hello.sh` breaks FR2.

## 4. User Experience & Behavior
- **Flow:** from the repository root, the developer runs `./hello-world/hello.sh`. The terminal shows one line, `hello world`, and the shell returns exit status 0.
- **Listing:** `ls hello-world` shows only `hello.sh`.
- **States:** none. The script is stateless and gives the same output on every run.
- **User-facing errors:** none are expected. The only way to fail is a missing executable bit, which shows as "permission denied", and FR3 rules that out.
- **Output format:** plain text, lowercase, one line, no decoration.

## 5. Acceptance Criteria
1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)
- **Depends on:** nothing. There are no pre-conditions and no blockers. This is the only story of the epic.
- **Repository rule:** the test gate in `.factory/testing.md` (`pip install -e ".[test]"`, then `pytest`) runs on every pull request and must stay green. The existing `tests/test_hello_sh.py` is part of that gate.
- **Delivery:** a person reviews and merges any pull request. The factory does not merge.
- **Scope constraint:** documentation and CI/CD are out of scope, so this story adds no CHANGELOG entry, even though earlier script stories did.

## 7. Technical Design (deferred to STRUCTURE)
The STRUCTURE stage decides how to show the criteria are met: through the existing tests and a recorded run on the work branch, and whether the delivery needs a code change at all. The only technical constraint the product imposes is that the output and the test asserting it must agree. If the reading of AC4 ever changes, the script and `tests/test_hello_sh.py` change in the same pull request.

## 8. Open Questions
- None block the work. The developer told us to take the simplest reading where the story is silent, and those readings are recorded as assumptions:
  - **A1:** the story is met by what is already on `main`. The delivery is evidence, not a rebuild.
  - **A2:** "exactly hello world" allows the one newline that ends the line.
  - **A3:** the existing tests are existing coverage. They are kept unchanged and are not new scope.
- The epic PRD and the trace IDs R1–R4 and RK1 were not checked against the epic material. The story text is treated as the whole requirement.
