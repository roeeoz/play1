# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

- **What:** a minimal, runnable bash script `hello.sh` that prints "hello world", living alone in a dedicated top-level folder `hello-world`.
- **Problem:** developers in this repository want a verified, runnable starting point for shell scripting that does not clutter existing directories.
- **Target users:** developers working in the play1 repository.
- **Status found in the repository (intake finding):** the target branch `main` already contains this deliverable. `hello-world/hello.sh` was added by commit `65938b5` ("Add hello-world bash script in dedicated folder"); it is the only file in the folder, starts with `#!/bin/bash`, is executable (`-rwxr-xr-x`), and running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits 0. `tests/test_hello_sh.py` already checks output, exit code, shebang, executable bit and folder isolation. Per the developer's direction (the story text and its acceptance criteria are the whole requirement; where they are silent, take the simplest reading), this story's deliverable is that state: the `hello-world` folder and `hello.sh` meeting the four acceptance criteria. Assumption A1 (§8) covers what the delivery changes given that the repository already holds it.

## 2. Goals & Non-Goals
### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` directly and see exactly "hello world".
- The `hello-world` folder contains only `hello.sh`.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (README etc.). The one-line `CHANGELOG.md` entry the repository gate requires on every pull request is delivery mechanics, not documentation of the script (assumption A3, §8).
- Changing the existing script's content or behaviour when it already meets the criteria.

## 3. Functional Requirements

- **FR1** — A top-level folder named `hello-world` exists and contains exactly one file, `hello.sh`.
- **FR2** — `hello.sh` starts with the shebang line `#!/bin/bash` and has executable permissions, so it runs as `./hello-world/hello.sh` without `bash` in front.
- **FR3** — Running the script takes no input and writes exactly the lowercase text `hello world` to standard output, nothing else, and exits with code 0. The output is the single line `hello world` terminated by one newline (`hello world\n`); no leading or trailing spaces/tabs, no blank or extra lines (assumption A2, §8).
- **FR4** — If the repository already satisfies FR1–FR3 (it does on `main` today), the delivery leaves the folder and script as they are and only verifies them against the acceptance criteria (assumption A1, §8).

## 4. User Experience & Behavior

- **Flow:** the developer clones the repository, runs `./hello-world/hello.sh` from the repository root, and sees `hello world` in the terminal; the prompt returns with exit status 0.
- **Listing the folder** shows only `hello.sh`.
- No interactive behaviour, arguments, colours or error messages are specified.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Repository layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): a new shell script must be executable and start with a shebang (already met); and **every pull request must add a line under `## Unreleased` in `CHANGELOG.md`** (rule PLAY-G4, blocker). The gate cannot be waived; any pull request for this story carries that one line (assumption A3).
- **Test gate** (`.factory/testing.md`, `.github/workflows/ci.yml`): `pytest` runs on every pull request; `tests/test_hello_sh.py` already pins the output to `"hello world\n"`, consistent with assumption A2.
- No other product depends on this script.

## 7. Technical Design (deferred to STRUCTURE)

Deferred. The product imposes no technical constraint beyond §3 and §6.

## 8. Open Questions

No blocking questions remain. The developer directed that the story text and its acceptance criteria are the whole requirement and that silent points take the simplest reading, recorded here:

- **A1 — Already-delivered state.** `main` already contains `hello-world/hello.sh` meeting all four criteria (commit `65938b5`). Simplest reading: the story is satisfied by that state; the delivery verifies it and does not rewrite the script. *Risk:* a pull request from this story may contain no change to the script itself.
- **A2 — Final newline.** "No leading or trailing whitespace and no additional lines" is read as allowing the single newline that terminates the one output line (`hello world\n`), which is what `echo` prints and what `tests/test_hello_sh.py` expects. *Risk:* a consumer comparing raw bytes against the 11 characters `hello world` would see a mismatch.
- **A3 — Changelog line.** If a pull request is opened, it adds one line under `## Unreleased` in `CHANGELOG.md`, because gate PLAY-G4 requires it on every pull request; this is not treated as a "documentation file" for the script. *Risk:* none to the product; it is the only file outside `hello-world/` the delivery may touch.
