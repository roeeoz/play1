# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

- **Summary:** a hello-world bash script, `hello.sh`, in its own new folder `hello-world` at the repository root. It prints exactly "hello world" and exits 0.
- **Problem:** developers need a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target user:** a developer working in this repository.

> **Intake finding:** the target branch `main` already has this deliverable. `hello-world/hello.sh` was added in commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode `100755`, its contents are `#!/bin/bash` followed by `echo "hello world"`, and it is the only file in `hello-world/`. Running it prints `hello world\n` and exits 0. `tests/test_hello_sh.py` already checks all four scenarios (commits `a2ec96d` and `9a5bd0b`).
>
> **Assumption A1 (simplest reading, per the developer's direction):** the story is done when the acceptance criteria below hold on the work branch. If they already hold, the story needs no new script and no other file change: the work is to confirm each criterion against the real script and give that as evidence. The story does not ask for anything beyond its criteria, so nothing more is added.

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
- **Edge case, output exactness (Assumption A2):** the output is the single line `hello world` ended by one newline (`hello world\n`). The criteria are silent on the newline, and the simplest reading counts the newline as the end of the line, not as trailing whitespace or an additional line. The existing script prints this and the existing test requires it.
- **Edge case, existing deliverable (Assumption A1):** if `main` already meets FR1–FR4, the story keeps it as it is and adds nothing.

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

Deferred to the STRUCTURE stage. The product imposes only what the functional requirements say: the script path `hello-world/hello.sh`, the `#!/bin/bash` shebang, executable permissions, and the exact output.

## 8. Open Questions (if any remain)

No blocking questions remain. The developer directed that the story text and its criteria are the whole requirement, and that the simplest reading applies where they are silent. That settled the two earlier questions as assumptions:

- **A1 — the deliverable already exists on `main`.** The story is satisfied by confirming the four criteria. No new or changed files are required. *Risk:* if the epic expected a visible change, the pull request may contain only evidence. A reviewer who expected new code should raise it there.
- **A2 — one ending newline is allowed.** The output is `hello world\n`. *Risk:* a consumer that compares the raw bytes against the 11-byte string `hello world` would see a mismatch. Nothing in the story or the epic names such a consumer.
