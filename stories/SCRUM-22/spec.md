# Feature Specification Document — Hello world bash script in a dedicated folder (draft, not ready)

> **Status: PARTIALLY_READY.** Three blocking questions (§8) must be answered first. The biggest one: the deliverable already exists on `main`.

## 1. Feature Overview

- **What:** a minimal hello-world bash script, `hello-world/hello.sh`, in its own top-level folder of the play1 repository.
- **Problem:** developers want a verified, runnable starting point for shell scripting that does not clutter the existing directories (`qa/`, `src/`, `tests/`, `docs/`).
- **Target user:** a developer working in this repository.
- **Epic context:** this is the only story of its epic (traces to R1–R4, steps 1–4, risk RK1). Priority Must, size XS (≈1). No pre-conditions and no blockers are listed.

**Finding from the repository (must be resolved before build):** `main` already contains `hello-world/hello.sh` (commit `65938b5`, "WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode `100755`, its content is `#!/bin/bash` followed by `echo "hello world"`, it is the only file in `hello-world/`, and running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits 0. So, as they stand, Scenarios 1–3 are already met on the target branch. See Q1.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals

- A developer can run `./hello-world/hello.sh` from the repository root and see `hello world`, with exit code 0.
- The script runs directly through its shebang, without typing `bash`.
- The `hello-world` folder holds `hello.sh` and nothing else.

### Non-Goals

- Additional scripts.
- CI/CD integration (no new workflow job or test that runs the script in CI).
- Documentation files (no README in `hello-world/`). How this applies to the repository's required `CHANGELOG.md` line is open (Q3).
- Arguments, options, localisation or any output other than `hello world`.

## 3. Functional Requirements

- **FR1 — Location.** A folder named `hello-world` at the repository root contains exactly one file, `hello.sh`.
- **FR2 — Shebang.** The first line of `hello.sh` is exactly `#!/bin/bash`.
- **FR3 — Executable.** `hello.sh` has executable permission in the repository, so it keeps that permission in a fresh clone.
- **FR4 — Output.** The script takes no input. When run, it writes exactly the lowercase text `hello world` to standard output, with no leading or trailing spaces and no other lines. Whether one terminating newline is allowed is open (Q2).
- **FR5 — Exit status.** The script exits with code 0.
- **Edge cases:** if the script is run from a directory other than the repository root (for example `cd hello-world && ./hello.sh`), the output and exit code are the same. Nothing is written to standard error.

## 4. User Experience & Behavior

- **Flow:** the developer clones the repository, runs `./hello-world/hello.sh` from the root, and the terminal shows one line, `hello world`. Then the prompt returns.
- **States:** there is one state, success. The story defines no input and no error output.
- **Look and feel:** plain terminal text, all lowercase, nothing printed before or after it.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Already delivered on `main`:** `hello-world/hello.sh` exists there from commit `65938b5` (Q1).
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 2 says a new shell script must be executable and start with a shebang. The story already requires both. Rule 4 says every pull request must add a line under `## Unreleased` in `CHANGELOG.md`, or the gate blocks it (`PLAY-G4`). This runs on every pull request and cannot be waived, so it conflicts with "documentation files out of scope" unless the changelog line is treated as in scope (Q3).
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** the gate is `pip install -e ".[test]"` and `pytest`, plus the `CI_FAIL` marker check. Neither is affected by a bash script. The story puts CI integration out of scope, so the script is checked by hand against §5. The pull request's required checks must still be green.
- A person reviews and merges the pull request. The factory does not merge it.

## 7. Technical Design (deferred to STRUCTURE)

Nothing here needs design. How executable permission is recorded in git, and how the manual checks are written up as pull-request evidence, are left to STRUCTURE.

## 8. Open Questions

- **Q1 (P0) — What should this story change, given the script already exists on `main`?** Options:
  - (a) Treat the story as already delivered and close it, with no pull request.
  - (b) Deliver only verification evidence against §5, with no code change.
  - (c) Change something specific that the story does not yet name.

  I recommend (a): commit `65938b5` already meets Scenarios 1–3, and an empty or duplicate pull request has no value. I would pick (c) instead if this run is meant to rebuild the script from a clean `main`, for example as a pipeline exercise. In that case, say which base or which change you want.
- **Q2 (P0) — Does Scenario 4 allow one terminating newline after `hello world`?** The current script prints `hello world\n`. Read strictly, "no trailing whitespace" would fail it. I recommend allowing exactly one terminating newline, with nothing else before or after the text. That is the normal behaviour of a shell command, and a captured value (`$(./hello-world/hello.sh)`) equals `hello world` exactly. I would pick "no newline at all" only if a byte-exact comparison is what you need.
- **Q3 (P0) — Is the required `CHANGELOG.md` line in scope?** The repository gate blocks any pull request that does not add a line under `## Unreleased` in `CHANGELOG.md` (rule `PLAY-G4`), and that gate cannot be waived. I recommend treating that one line as in scope, and reading "documentation files" as files inside `hello-world/` such as a README. The changelog sits outside the folder, so Scenario 2 still holds. The only other option is to change the gate rule in the repository first. This question matters only if Q1's answer leads to a pull request.
