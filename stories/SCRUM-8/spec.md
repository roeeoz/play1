# Feature Specification Document — Hello world bash script in a dedicated folder
## 1. Feature Overview

- **What:** a minimal hello-world bash script, `hello-world/hello.sh`, alone in its own `hello-world` folder, that prints "hello world" when run directly.
- **Problem:** developers in this repository want a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Actor:** a developer working in the play1 repository.

> **Intake finding:** the deliverable already exists on the target branch `main`. `hello-world/hello.sh` was added by commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"); it is mode `100755`, its content is `#!/bin/bash` / `echo "hello world"`, it is the only file in `hello-world/`, and running `./hello-world/hello.sh` today prints `hello world` followed by one newline and exits 0. Per the developer's direction (the story text and its criteria are the whole requirement; take the simplest reading where they are silent), the story is done when `main` carries a `hello-world/hello.sh` meeting the four acceptance criteria — see assumption A1 in §8.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` from the repository root and see exactly "hello world", with exit code 0.
- The `hello-world` folder holds only `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (README, CHANGELOG entries in the folder, etc.).

## 3. Functional Requirements

- **FR1** — A folder `hello-world` exists at the repository root containing exactly one file, `hello.sh`.
- **FR2** — `hello.sh` starts with the shebang line `#!/bin/bash` and is executable, so it runs as `./hello-world/hello.sh` without `bash` in front.
- **FR3** — When run, it writes "hello world" (lowercase, single space) to standard output, nothing to other lines, and exits with code 0.
- **FR4** — Line termination: the output is the single line "hello world", ended by one standard newline (assumption A2 in §8); no leading/trailing spaces and no other lines.
- **FR5** — The change touches nothing outside `hello-world/`: no additional scripts, no CI/CD integration, no documentation files (the story's out-of-scope list; assumption A3 in §8).
- Inputs: none (no arguments, no environment). Outputs: the one line above on stdout; exit code 0.

## 4. User Experience & Behavior

- Flow: the developer clones the repo, runs `./hello-world/hello.sh` from the root, sees `hello world` in the terminal, and gets exit status 0.
- Listing `hello-world/` shows only `hello.sh`.
- No error states are in scope: the script takes no input and has nothing that can fail from the user's point of view.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- Pre-conditions and blockers: none stated by the story.
- The repository's CI (`.github/workflows/ci.yml`: pytest + a `CI_FAIL` gate) runs on every pull request; this story adds no CI integration of its own.
- A person reviews and merges the pull request; the factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

Deferred to the STRUCTURE stage. No technical constraint beyond the shebang, executable bit and output stated above.

## 8. Open Questions

No blocking questions remain. The developer directed that the story text and its acceptance criteria are the whole requirement and that silent points take the simplest reading, recorded here as assumptions:

- **A1 — Existing script.** `hello-world/hello.sh` already exists on `main` (commit `65938b5`) and meets the criteria. Simplest reading: the story's outcome is that the script exists as described; implementation verifies it and changes it only where a criterion is not met, with no new files. Risk: the work may produce no code change, so the pull request (if any) may be empty or verification-only.
- **A2 — Trailing newline.** Scenario 4's "no trailing whitespace and no additional lines" is read as allowing the single newline that ends the one output line (what `echo "hello world"` prints). Risk: a strict byte-for-byte check expecting 11 bytes without a newline would fail.
- **A3 — Scope boundary.** No acceptance criterion is added; the story's out-of-scope list (additional scripts, CI/CD integration, documentation files) is honoured as a constraint (FR5). Harel's Definition of Ready asks for a regression/scope-boundary scenario, which the story lacks; per the developer's direction the four criteria stand as written. Risk: scope creep is checked only by review, not by a criterion.
