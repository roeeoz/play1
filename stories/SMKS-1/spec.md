# Feature Specification Document — Hello world bash script in a dedicated folder (SMKS-1)

> Status: in-progress ticket draft (NOT_READY) — open blocking questions in §8.

## 1. Feature Overview

- **What is being built:** a minimal hello-world bash script, `hello.sh`, in its own dedicated folder `hello-world`, that prints "hello world" when run.
- **Problem:** developers in this repository have no verified, runnable starting point for shell scripting; today the repository holds only Python code (`src/`, `tests/`) and no shell scripts or `hello-world`/`qa` folder.
- **Target users:** internal developers working in this repository, who run the project's scripts inside shell substitutions such as `$(qa/script.sh)` (product memory "users-internal-devs-shell-substitution"), so any extra output breaks their commands.
- This is the only story of its epic (Priority: Must, Size: XS ≈1, traces to R1, R2, R3, R4 · steps 1–4 · RK1).

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals

- A developer can run `hello.sh` directly (no explicit `bash`) and get exactly "hello world" on standard output with exit code 0.
- The script sits alone in its own dedicated `hello-world` folder, without cluttering existing directories.

### Non-Goals

- Additional scripts.
- CI/CD integration.
- Documentation files (subject to the open question on the repository's changelog rule, §8 Q2).

## 3. Functional Requirements

- **FR1 — Location:** a new folder named `hello-world` holds one file, `hello.sh`, and nothing else. Where the folder sits (repository root, as the story implies with `./hello-world/hello.sh`, or under `qa/` as the standing rule requires) is open — §8 Q1.
- **FR2 — Direct execution:** `hello.sh` starts with the shebang line `#!/bin/bash` and is executable, so it runs without `bash hello.sh`.
- **FR3 — Output:** run with no arguments, the script prints exactly the lowercase string "hello world" to standard output, nothing to standard error, and exits with code 0. Whether a single terminating newline counts as allowed is open — §8 Q3.
- **FR4 — Arguments (pending §8 Q1):** the product's standing rule says every script answers `--help` with exactly one summary line on stdout and exit code 0, and refuses any other unknown argument with a short one-line error on stderr, nothing on stdout, and exit code 2. The story says nothing about arguments; whether this rule applies here is open.
- **Inputs:** none required. **Outputs:** the "hello world" line on stdout.

## 4. User Experience & Behavior

- **Main flow:** the developer runs `./hello-world/hello.sh` (path pending §8 Q1) from the repository root and sees `hello world`; `$(./hello-world/hello.sh)` yields exactly `hello world`.
- **Output format:** lowercase, no leading or trailing whitespace, no additional lines, no banner or extra text — any extra text breaks the users' shell substitutions.
- **Listing the folder:** shows only `hello.sh`.
- No visual or interactive look-and-feel applies: this is a command-line script.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Standing product rule "qa-script-standing-rule":** every script the project ships lives under `qa/`, prints only to stdout on success, answers `--help` with one summary line (exit 0) and refuses unknown arguments (one-line stderr error, exit 2). The story's `hello-world` folder at the root and its silence on arguments collide with it — §8 Q1.
- **Repository gate (play1 layout gate, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 2 (a new shell script is executable and starts with a shebang) matches the story. Rule 4 requires every pull request to add a line under `## Unreleased` in `CHANGELOG.md` (creating the file if absent — it does not exist today); a pull request that does not touch it gets blocker `PLAY-G4`. The story puts documentation files out of scope — §8 Q2.
- **Test gate (`.factory/testing.md`):** `pytest` runs on every pull request; adding the script must keep it green.
- No other product depends on this story.

## 7. Technical Design (deferred to STRUCTURE)

How the script is written, how its behavior is tested within the repository's `pytest` gate, and how argument handling is implemented (if Q1 keeps it) are left to STRUCTURE.

## 8. Open Questions

- **Q1 (P0) — Location and arguments vs. the standing qa/ rule.** See the scorecard question; working assumption until answered: none — blocking.
- **Q2 (P0) — CHANGELOG.md line vs. "no documentation files".** The repository gate blocks any pull request that does not add a line to `CHANGELOG.md`.
- **Q3 (P0) — Terminating newline.** Does "no trailing whitespace and no additional lines" allow the single newline that ends the line?
