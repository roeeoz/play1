# Feature Specification — Hello world bash script in a dedicated folder (DRAFT, not ready)

## 1. Feature Overview

- **What:** a bash script `hello.sh` in its own folder `hello-world/` at the repository root that prints "hello world".
- **Problem:** developers want a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Actor:** a developer working in the play1 repository.

> **Intake finding — the deliverable already exists on `main`.** `hello-world/hello.sh` is on `main` (commit `65938b5`, "WI-220A63-1: Add hello-world bash script in dedicated folder"), mode `100755`, content `#!/bin/bash` / `echo "hello world"`, and it is the only file in the folder. Running it prints `hello world` followed by one newline and exits 0. `tests/test_hello_sh.py` already checks the output, shebang, executable bit and folder contents. As written, every acceptance criterion below is already met (subject to Q2), so this story would produce no change. See §8, Q1.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- `hello-world/hello.sh` exists, is executable, starts with `#!/bin/bash`, and prints exactly "hello world" to standard output with exit code 0.
- `hello-world/` contains no file other than `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (README etc.). Whether the repository's mandatory `CHANGELOG.md` entry counts as one is open (Q3).

## 3. Functional Requirements

- **FR1** — Running `./hello-world/hello.sh` from the repository root prints "hello world" to standard output and exits with code 0. No input, no arguments.
- **FR2** — The script runs directly (shebang `#!/bin/bash` plus executable permission) without being invoked as `bash hello.sh`.
- **FR3** — The `hello-world` folder holds only `hello.sh`.
- **FR4** — Output is the lowercase string "hello world", no leading or trailing whitespace, no extra lines. Whether the single line terminator after it is allowed is open (Q2).

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
- The story has no template-format story block (Harel story template); its criteria are Given/When/Then, cover the happy path, and include an edge case. The template also asks for a regression or scope-boundary scenario, which is missing (Q4).

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. STRUCTURE decides how the script is written and tested, and whether the existing `tests/test_hello_sh.py` is kept, changed or reused.

## 8. Open Questions

- **Q1 (P0)** — The script already exists on `main` and already meets the criteria. What should this story deliver? (a) Close it as already done, with no pull request. (b) Treat it as a verification story: the pull request only adds the `CHANGELOG.md` line the gate needs, and the existing tests are the evidence. (c) Something else is meant to change, which you need to name. Recommendation: (a), because the "new folder" the context describes already exists and a change-free story has no honest pull request. Pick (b) if the platform needs a merged pull request to close the story.
- **Q2 (P0)** — Does "no trailing whitespace / no additional lines" allow the single newline that ends the line? Today the script outputs `hello world\n`, and the existing tests require exactly that. Recommendation: allow exactly one terminating newline, because that is standard for terminal output and is what `main` and its tests already do. Answer "no newline at all" only if a byte-exact consumer needs it, since that would change both the script and the tests.
- **Q3 (P0)** — The repository gate requires a `CHANGELOG.md` line on every pull request, but the story puts documentation files out of scope. Does the out-of-scope rule mean only documentation inside `hello-world/` (so the CHANGELOG line is allowed)? Recommendation: yes. `CHANGELOG.md` is at the root, outside the folder, and the gate cannot be waived. The other option is to change the gate in the repository first.
- **Q4 (P1)** — The Harel story template asks for at least one regression or scope-boundary scenario. Proposed addition: "Scenario 5 — Scope boundary: no other repository behaviour changes. Given the change is applied, When the existing test suite runs, Then all existing tests still pass, and no file outside `hello-world/` changes except the `CHANGELOG.md` entry." Do you accept it?
