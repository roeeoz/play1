# Feature Specification — Hello world bash script in a dedicated folder

## 1. Feature Overview

- **What:** a bash script `hello.sh` in its own folder `hello-world/` at the repository root that prints "hello world".
- **Problem:** developers want a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Actor:** a developer working in the play1 repository.

> **Existing state.** `hello-world/hello.sh` is already on `main` (commit `65938b5`): mode `100755`, content `#!/bin/bash` / `echo "hello world"`, the only file in the folder. Running it prints `hello world` plus one newline and exits 0, and `tests/test_hello_sh.py` already checks the output, shebang, executable bit and folder contents. Per the developer's instruction (the story text and its criteria are the whole requirement; where silent, take the simplest reading), this story is delivered as a verification of that state: the script and folder are kept as they are (changed only if a criterion is found unmet), and the pull request carries the `CHANGELOG.md` line the repository gate requires. See assumptions A1–A3 in §8.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- `hello-world/hello.sh` exists, is executable, starts with `#!/bin/bash`, and prints exactly "hello world" to standard output with exit code 0.
- `hello-world/` contains no file other than `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (README etc.) inside `hello-world/` or added for this script. The repository-wide `CHANGELOG.md` line the gate requires is not counted as one (assumption A3).
- A regression or scope-boundary acceptance criterion beyond the story's four (the story does not state one; A4).

## 3. Functional Requirements

- **FR1** — Running `./hello-world/hello.sh` from the repository root prints "hello world" to standard output and exits with code 0. No input, no arguments.
- **FR2** — The script runs directly (shebang `#!/bin/bash` plus executable permission) without being invoked as `bash hello.sh`.
- **FR3** — The `hello-world` folder holds only `hello.sh`.
- **FR4** — Output is the lowercase string "hello world", no leading or trailing whitespace, no extra lines. The single newline that terminates the line is allowed and is the only character after the text (assumption A2).

## 4. User Experience & Behavior

- Flow: the developer runs `./hello-world/hello.sh` in a terminal and sees `hello world` on one line; the prompt returns with exit status 0.
- No visual style, interaction or error states are specified; the script takes no input.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Existing state:** `hello-world/hello.sh` and `tests/test_hello_sh.py` are already on `main` (see §1). The tests assert stdout is exactly `"hello world\n"`.
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 2 requires a new shell script to be executable and start with a shebang, which the story already requires. Rule 4 (`PLAY-G4`) blocks any pull request that does not add a line under `## Unreleased` in `CHANGELOG.md`. Every delivery must therefore touch `CHANGELOG.md`, and no exemption is possible.
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** `pytest` must pass and no `CI_FAIL` file may exist at the root.
- The story has no template-format story block (Harel story template); its criteria are Given/When/Then, cover the happy path, and include an edge case. The template's regression/scope-boundary scenario is not added, because the story does not state one (A4).

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. STRUCTURE decides how the script is written and tested, and whether the existing `tests/test_hello_sh.py` is kept, changed or reused.

## 8. Open Questions

No open product questions. The developer instructed that the story text and its acceptance criteria are the whole requirement and that silent points take the simplest reading, recorded here as assumptions:

- **A1 — Deliverable.** The script already exists on `main` and meets the criteria. The story is delivered as a verification pull request: `hello-world/hello.sh` stays as it is unless a criterion is found unmet, and the pull request adds the `CHANGELOG.md` line the gate requires, with the existing tests as evidence. *Risk:* the pull request contains no functional change; if the story was meant to change something else, that is not captured.
- **A2 — Trailing newline.** "No trailing whitespace and no additional lines" (Scenario 4) is read as allowing the one newline that terminates the single output line, so the output is exactly `hello world\n`. This matches the script and tests on `main`. *Risk:* a consumer that needs the output byte-exact with no newline would not be satisfied.
- **A3 — CHANGELOG.** The story's "documentation files" exclusion is read as covering documentation for the script/folder, not the root `CHANGELOG.md` line that gate `PLAY-G4` requires on every pull request (the gate cannot be waived). *Risk:* none to the product; the pull request touches one file outside `hello-world/`.
- **A4 — No extra criterion.** The Harel template's regression/scope-boundary scenario is not added; the four criteria are the story's, unchanged. *Risk:* scope creep outside `hello-world/` is guarded only by review and the existing test gate, not by a named criterion.
