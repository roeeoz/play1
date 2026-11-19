# Feature Specification Document — Hello world bash script in a dedicated folder

> **Status: READY.** The developer ruled that the story text and its acceptance criteria are the whole requirement, and that where they are silent the simplest reading applies and is recorded as an assumption (§8, A1–A3).

## 1. Feature Overview

- **What:** a minimal hello-world bash script, `hello-world/hello.sh`, alone in its own folder at the repository root, that prints exactly "hello world" when run.
- **Problem:** developers in this repository want a verified, runnable starting point for shell scripting that does not clutter existing directories (`qa/`, `src/`, `tests/`).
- **Actor:** a developer working in the play1 repository.

**Intake finding (verified in the checkout):** the requested artefact is already on `main`:
- `hello-world/hello.sh` exists, mode `100755`, with content `#!/bin/bash` / `echo "hello world"`. It was added by commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder") and is the only file in `hello-world/`.
- Running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits with code 0.
- `tests/test_hello_sh.py` already checks exit code 0, exact output (`"hello world\n"`), empty stderr, the shebang line, the executable bit and that the folder holds only `hello.sh`. It runs in the repository's `pytest` CI gate.

So the story's outcome already holds on `main`. Under the simplest reading (§8, A1), the story is met by keeping that script exactly as it is: no new script, and no change inside `hello-world/`.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals

- A developer can run `./hello-world/hello.sh` directly (no explicit `bash`) and get exactly "hello world" on standard output, with exit code 0.
- The `hello-world` folder holds only `hello.sh`.

### Non-Goals

- Additional scripts.
- CI/CD integration.
- Documentation files (README or similar) in or about the folder.

## 3. Functional Requirements

- **FR1 — Location:** a folder named `hello-world` at the repository root contains a file named `hello.sh`, and nothing else.
- **FR2 — Shebang:** the first line of `hello.sh` is exactly `#!/bin/bash`.
- **FR3 — Executable:** `hello.sh` has the executable permission, so it runs as `./hello-world/hello.sh` without `bash hello.sh`.
- **FR4 — Output:** when run, the script writes exactly the lowercase string `hello world` to standard output, with no leading or trailing whitespace and no other lines. The single newline that ends the line is allowed: the output is `hello world\n` (§8, A2).
- **FR5 — Exit status:** the script exits with code 0.
- **Inputs:** none (no arguments, no environment variables, no stdin).

## 4. User Experience & Behavior

- **Flow:** the developer runs `./hello-world/hello.sh` from the repository root and sees `hello world` in the terminal. The script prompts for nothing and writes nothing to standard error.
- **Listing:** listing `hello-world/` shows only `hello.sh`.
- No visual style, sound or other sensory quality was requested.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Already delivered on `main`:** `hello-world/hello.sh` (commit `65938b5`) and `tests/test_hello_sh.py`. All four criteria above already hold on `main`, given A2.
- **Repository gates:** they run on every pull request whatever this ticket says:
  - The `play1 layout gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`), rule 2: a new shell script must be executable and start with a shebang. The story already requires both.
  - The same gate, rule 4 (PLAY-G4): every pull request must add a line under `## Unreleased` in `CHANGELOG.md`. Any pull request from this story carries that line (§8, A3). The gate allows no exemption.
  - The CI `test` job (`.github/workflows/ci.yml`, declared in `.factory/testing.md`): `pytest` must pass. It already runs `tests/test_hello_sh.py`.
- A person merges the pull request after review; the factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. The only constraints the product sets are FR1–FR5. How the change is verified, and where any verification lives outside `hello-world/` (which must stay single-file), is left to STRUCTURE.

## 8. Open Questions (if any remain)

No blocking questions remain. The developer told us to take the simplest reading wherever the story is silent. These are the assumptions that follow, each with its risk:

- **A1: what is delivered.** The existing `hello-world/hello.sh` on `main` is the deliverable, and it is kept exactly as it is. Nothing is added to or changed in `hello-world/`, and no second script is written. *Risk:* if the epic meant a different or fresh script, this story delivers no new behaviour, and that would only come to light at review.
- **A2: the terminating newline.** In Scenario 4, "no trailing whitespace" allows the one newline that ends the line, so the output is `hello world\n`. That is what `echo` prints and what `tests/test_hello_sh.py` asserts. *Risk:* a consumer that compares raw bytes against `hello world` with no newline would fail.
- **A3: the CHANGELOG line.** If the story produces a pull request, that pull request adds one line under `## Unreleased` in `CHANGELOG.md`, because gate PLAY-G4 requires it. This line is not a "documentation file" in the sense the story excludes, and it sits outside `hello-world/`, which still holds only `hello.sh`. *Risk:* none to the product. The line exists only to satisfy the gate.
