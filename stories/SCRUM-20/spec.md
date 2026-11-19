# Feature Specification Document — Hello world bash script in a dedicated folder (draft, NOT READY)

> **Status: NOT READY.** The repository's `main` branch (which this story's work branch was cut from) already contains everything this story asks for. See §8 for the blocking questions.

## 1. Feature Overview

- **What:** a minimal hello-world bash script, `hello-world/hello.sh`, alone in its own folder at the repository root, that prints exactly "hello world" when run.
- **Problem:** developers in this repository want a verified, runnable starting point for shell scripting that does not clutter existing directories (`qa/`, `src/`, `tests/`).
- **Actor:** a developer working in the play1 repository.

**Intake finding (verified in the checkout):** the requested artefact is already on `main`:
- `hello-world/hello.sh` exists, mode `100755`, with content `#!/bin/bash` / `echo "hello world"`. It was added by commit `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder") and is the only file in `hello-world/`.
- Running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits with code 0.
- `tests/test_hello_sh.py` already checks exit code 0, exact output (`"hello world\n"`), empty stderr, the shebang line, the executable bit and that the folder holds only `hello.sh`. It runs in the repository's `pytest` CI gate.

So as written, the story would produce an empty change. What this story should deliver is still open (§8, Q1).

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
- **FR4 — Output:** when run, the script writes exactly the lowercase string `hello world` to standard output, with no leading or trailing whitespace and no other lines. Whether the single line-terminating newline counts as "trailing whitespace" is open (§8, Q2).
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

- **Already delivered on `main`:** `hello-world/hello.sh` (commit `65938b5`) and `tests/test_hello_sh.py`. All four criteria above already hold on `main`, if the trailing newline is allowed (Q2).
- **Repository gates:** they run on every pull request whatever this ticket says:
  - The `play1 layout gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`), rule 2: a new shell script must be executable and start with a shebang. The story already requires both.
  - The same gate, rule 4 (PLAY-G4): every pull request must add a line under `## Unreleased` in `CHANGELOG.md`. A pull request from this story would have to touch `CHANGELOG.md`, although the story lists "documentation files" as out of scope (Q3).
  - The CI `test` job (`.github/workflows/ci.yml`, declared in `.factory/testing.md`): `pytest` must pass. It already runs `tests/test_hello_sh.py`.
- A person merges the pull request after review; the factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

Not designed here. The only constraints the product sets are FR1–FR5. How the change is verified, and where any verification lives outside `hello-world/` (which must stay single-file), is left to STRUCTURE.

## 8. Open Questions (if any remain)

- **Q1 (P0, blocking):** the deliverable already exists on `main`. See the scorecard question and the reply for the options and my recommendation.
- **Q2 (P0, blocking):** does Scenario 4's "no trailing whitespace" allow the single terminating newline (`hello world\n`), which the current script prints and the existing test expects?
- **Q3 (P1):** if a pull request goes out, the CHANGELOG line PLAY-G4 requires must be accepted as in scope. The gate gives no exemption.
