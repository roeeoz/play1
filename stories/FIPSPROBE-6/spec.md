# Feature Specification Document

## 1. Feature Overview
- **Summary:** Deliver "Hello-world bash script in a dedicated folder" as a verification pull request. `hello-world/hello.sh` is already on `main`: it was added by commit `65938b5`, starts with `#!/bin/bash` and is stored in git as executable. This story adds one test, linked to this story, which proves the story's acceptance criteria hold against that script.
- **Problem statement:** Developers need a runnable starting point for shell scripting. The script exists, but nothing links it to this story. Without a deliverable tied to the story, nothing traces the story's acceptance criteria to proof in the repository.
- **Target users / actors:** Developers who clone the repository and run `./hello-world/hello.sh`. Reviewers who check that this story is done.

## 2. Goals & Non-Goals
### Story context
In: the `hello-world` folder and `hello.sh`, which already exist on `main` at the repository root, and a test linked to this story that checks them. Out: other scripts, CI, documentation (including a CHANGELOG entry), and any change to `hello.sh` itself.

### Goals
- Show, through a test linked to this story, that `./hello-world/hello.sh` prints exactly `hello world` as one line and exits with code 0.
- Show that `hello.sh` starts with `#!/bin/bash` and is stored as executable in the repository, so it runs without `bash` (R5, and the mitigation for RK1).
- Keep the `hello-world` folder at the repository root (R1). This confirms the PRD's open assumption.

### Non-Goals
- Re-implementing, moving or editing `hello-world/hello.sh`.
- `greet.sh` and anything else covered by "Greet a person by name". That includes updating the existing check that the folder holds only `hello.sh`.
- A CHANGELOG entry, a README or other documentation.
- CI changes.
- Other shells, such as zsh or sh.

## 3. Functional Requirements
- **FR1:** The repository keeps `hello-world/hello.sh` at its root, unchanged from `main` (R1).
- **FR2:** Running `./hello-world/hello.sh` prints exactly `hello world` and exits with code 0 (R2).
- **FR3:** The output is exactly one line, `hello world`, with no surrounding whitespace.
- **FR4:** `hello.sh` starts with `#!/bin/bash` and is executable in the repository, so it runs without invoking `bash` (R5, RK1).
- **FR5:** The pull request adds a test linked to this story by its key, FIPSPROBE-6. The test checks FR2–FR4 and runs in the repository's existing test suite.
- **Inputs:** none. The script takes no arguments.
- **Outputs:** `hello world` on standard output, then exit code 0.
- **Edge cases:** the output must have no extra lines or whitespace. The executable bit must be checked in the repository itself, not on a checkout that may not keep file modes.

## 4. User Experience & Behavior
- **Flow:** a developer clones the repository and runs `./hello-world/hello.sh` from the root. The terminal shows the single line `hello world` and the command exits with code 0.
- **Reviewer flow:** the reviewer opens the pull request and sees that it adds only the linked test, and that the repository's required checks are green.
- **Output format:** exactly one line, `hello world`, with no leading or trailing whitespace and nothing on standard error.

## 5. Acceptance Criteria
1. Scenario 1 — Happy path: script execution. Given the repository holds `hello-world/hello.sh`, When a developer runs `./hello-world/hello.sh`, Then it prints exactly "hello world" and exits with code 0.
2. Scenario 2 — Happy path: direct execution. Given `hello.sh` starts with `#!/bin/bash` and is executable, When it is run without `bash`, Then it runs.
3. Scenario 3 — Edge case: output exactness. Given the script runs, When its output is captured, Then it is exactly one line, "hello world", with no surrounding whitespace.
4. Scenario 4 — Happy path: traceable verification. Given the story's pull request, When a reviewer opens it, Then it adds a test linked to FIPSPROBE-6 that checks criteria 1–3 against `hello-world/hello.sh`, And the repository's required checks pass on it.
5. Scenario 5 — Scope boundary: nothing else changes. Given the story's pull request, When its changed files are reviewed, Then `hello-world/hello.sh` is unchanged and still at the repository root, And there is no CHANGELOG, documentation or CI change.

## 6. Dependencies & Constraints (product-level)
- Depends on what is already on `main`: `hello-world/hello.sh` from commit `65938b5`, and the existing test suite.
- "Greet a person by name" depends on this story. It will add `greet.sh` and must update the existing check that the folder holds only `hello.sh`. This story leaves that check unchanged.
- The pull request is reviewed and merged by a person. The factory never merges it.

## 7. Technical Design (deferred to STRUCTURE)
STRUCTURE decides where the test lives and how it is named, how it links to FIPSPROBE-6, and whether it adds to or reuses the existing checks. The one product-level constraint is that it must read the executable bit from the repository itself (RK1).

## 8. Open Questions
None. The deliverable (option b, no CHANGELOG) and the folder location (repository root) were confirmed by the developer.
