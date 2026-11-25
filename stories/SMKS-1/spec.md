# Feature Specification Document — Hello world bash script in a dedicated folder (SMKS-1)

> Status: READY_FOR_SPEC — the developer's answers of 2026-11-25 settle the intake's open questions (§6, §8).

## 1. Feature Overview

- **What is being built:** a minimal hello-world bash script, `hello.sh`, in its own dedicated folder `hello-world` at the repository root, that prints exactly `Hello, World!!` when run.
- **Problem:** developers in this repository have no verified, runnable starting point for shell scripting; today the repository holds only Python code (`src/`, `tests/`) and no shell scripts and no `hello-world` folder.
- **Target users:** internal developers working in this repository, who run the project's scripts inside shell substitutions such as `$(...)` (product memory "users-internal-devs-shell-substitution"), so any extra output breaks their commands.
- This is the only story of its epic (Priority: Must, Size: XS ≈1, traces to R1, R2, R3, R4 · steps 1–4 · RK1).

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly `Hello, World!!` to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals

- A developer can run `./hello-world/hello.sh` directly (no explicit `bash`) and get exactly `Hello, World!!` on standard output with exit code 0.
- The script sits alone in its own dedicated `hello-world` folder, without cluttering existing directories.
- The behavior is verified by automated tests in the repository's existing test location (`tests/`, run by `pytest`).

### Non-Goals

- Additional scripts.
- CI/CD integration (no change to `.github/workflows/ci.yml`).
- Documentation files (README, docs pages, a README inside `hello-world`). The single line the repository gate requires in `CHANGELOG.md` is not treated as a documentation file of this feature (§6).
- Argument handling: no `--help`, no flags and no refusal of unknown arguments — the developer chose to keep exactly to the story, as an exception to the standing `qa/` script rule (§6).
- Placing the script under `qa/`.

## 3. Functional Requirements

- **FR1 — Location:** a new folder `hello-world` at the repository root holds exactly one file, `hello.sh`, and nothing else (no README, no tests, no other files).
- **FR2 — Direct execution:** `hello.sh`'s first line is the shebang `#!/bin/bash` and the file is executable, so `./hello-world/hello.sh` runs without `bash hello.sh`.
- **FR3 — Output:** run with no arguments, the script prints the line `Hello, World!!` (capital H and W, a comma, one space, two exclamation marks) to standard output, prints nothing to standard error, and exits with code 0. The line is ended by a single newline, which shell substitution `$(...)` removes, so captured output is exactly `Hello, World!!`; there is no leading or trailing whitespace, no other character and no second line.
- **FR4 — Arguments:** the script defines no flags or argument behavior beyond what the story names. Behavior when arguments are passed is unspecified by the product.
- **FR5 — Tests:** automated tests covering the acceptance criteria live in `tests/` alongside the repository's existing tests and run under `pytest`.
- **FR6 — Changelog line:** the change adds one line describing it under `## Unreleased` in `CHANGELOG.md` at the repository root, creating the file with that heading (it does not exist today), as the repository gate requires.
- **Inputs:** none. **Outputs:** the `Hello, World!!` line on stdout.

## 4. User Experience & Behavior

- **Main flow:** from the repository root the developer runs `./hello-world/hello.sh` and sees `Hello, World!!`; `$(./hello-world/hello.sh)` yields exactly `Hello, World!!`.
- **Output format:** exactly `Hello, World!!` — capital H and W, a comma, one space, two exclamation marks — no leading or trailing whitespace, no additional lines, no banner or extra text — extra text would break the users' shell substitutions.
- **Listing the folder:** shows only `hello.sh`.
- No visual or interactive look-and-feel applies: this is a command-line script.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly `Hello, World!!` to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the string `Hello, World!!` with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Exception to the standing product rule "qa-script-standing-rule":** that rule puts every shipped script under `qa/` with `--help` and unknown-argument handling. For this story the developer chose (2026-11-25) to keep exactly to the story: `hello-world/hello.sh` at the root, no flags. The rule stays in force for other work; this story is a recorded exception.
- **Criterion 4 and the line ending:** read as allowing the single newline that ends the output line (the developer delegated this to the simplest reading); the captured output via `$(...)` is exactly `Hello, World!!`.
- **Repository gate (play1 layout gate, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 1 (tests under `tests/`) matches FR5; rule 2 (a new shell script is executable and starts with a shebang) matches FR2; rule 4 requires a line under `## Unreleased` in `CHANGELOG.md` — met by FR6, which sits outside `hello-world`, so FR1 still holds.
- **Test gate (`.factory/testing.md`):** `pytest` runs on every pull request; it must stay green with the new tests.
- No other product depends on this story.

## 7. Technical Design (deferred to STRUCTURE)

How the script is written and how its behavior is tested under `pytest` (for example, running the script as a subprocess from a test in `tests/`) are left to STRUCTURE.

## 8. Open Questions

- None blocking. Settled on 2026-11-25: location `hello-world/hello.sh` at the root with no argument handling (exception to the `qa/` rule); tests in `tests/`; a terminating newline is allowed; the gate's `CHANGELOG.md` line is added.
