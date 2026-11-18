# Feature Specification Document — Hello world bash script in a dedicated folder (DRAFT, NOT READY)

## 1. Feature Overview

> **Status: NOT READY.** The intake found that the deliverable this story describes
> already exists on the target branch `main`, and that two of the story's rules
> collide with what the repository and its gate require. See §8 before building.

- **What is being built:** a minimal, runnable hello-world bash script `hello.sh`
  in its own top-level folder `hello-world/`, which prints exactly `hello world`.
- **Problem statement:** developers in this repository want a verified, runnable
  starting point for shell scripting that does not clutter existing directories
  (existing shell scripts live under `qa/`).
- **Target users:** a developer working in the play1 repository.

**Intake finding — already delivered.** `main` already contains
`hello-world/hello.sh` (mode `100755`, the folder's only file), added by commit
`65938b5` "WI-220A63-1: Add hello-world bash script in dedicated folder". Its
content is `#!/bin/bash` followed by `echo "hello world"`. Run from the repo root
it prints `hello world` followed by one newline character and exits 0. It is not
yet listed in `CHANGELOG.md`.

## 2. Goals & Non-Goals

### Story context

This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

### Goals
- A developer can run `./hello-world/hello.sh` from the repository root, without
  invoking `bash` explicitly, and see exactly `hello world`, exit code 0.
- The script sits alone in a dedicated `hello-world/` folder.

### Non-Goals
- Additional scripts.
- CI/CD integration.
- Documentation files (README or similar). Whether the `CHANGELOG.md` line the
  repository gate requires counts as such is open (§8, Q3).

## 3. Functional Requirements

- **FR1 — Location:** a folder `hello-world/` at the repository root containing
  exactly one file, `hello.sh`.
- **FR2 — Shebang:** the first line of `hello.sh` is `#!/bin/bash`.
- **FR3 — Executable:** `hello.sh` has executable permissions, so it runs as
  `./hello-world/hello.sh` without `bash` in front of it.
- **FR4 — Output:** running the script writes the lowercase string `hello world`
  to standard output, nothing else, and exits with code 0. Whether a single
  terminating newline is allowed is open (§8, Q2).
- **Inputs:** none (no arguments, no environment required).
- **Edge cases:** none beyond output exactness; argument handling is not specified
  and not requested.

## 4. User Experience & Behavior

- **Flow:** the developer runs `./hello-world/hello.sh` from the repository root;
  the terminal shows `hello world`; the shell reports exit status 0.
- **Output format:** exactly the lowercase string `hello world`, no leading or
  trailing whitespace, no additional lines (newline handling: §8, Q2).
- No interactive behavior, no error messages, no visual styling requested.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Existing artifact:** `hello-world/hello.sh` already exists on `main`
  (commit `65938b5`, WI-220A63-1) and meets FR1–FR3 today (§8, Q1).
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):**
  rule 2 (a new shell script is executable and starts with a shebang) matches
  the story; rule 4 blocks any pull request that does not add a line under
  `## Unreleased` in `CHANGELOG.md` (blocker `PLAY-G4`). No exemption is possible.
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** `pytest`
  plus the `CI_FAIL` marker check; neither runs shell scripts. CI integration is
  out of scope per the story.
- Size XS (≈1), priority Must, no blockers or pre-conditions in the story.

## 7. Technical Design (deferred to STRUCTURE)

Nothing to design at product level. How the output's exactness is achieved and
verified is for STRUCTURE once Q2 is settled.

## 8. Open Questions

- **Q1 (P0) — The deliverable already exists on `main`.** What should this story
  change? (a) Nothing in the script: accept the existing `hello-world/hello.sh`
  as the delivery, with the pull request adding only the `CHANGELOG.md` line;
  (b) close the story as already done, with no pull request; (c) something
  else — say what. Recommendation: (a), because it records the existing script
  against this story and passes the gate; pick (b) if no PR is expected.
- **Q2 (P0) — Trailing newline.** The existing script prints `hello world` plus
  one newline. Scenario 4 says "no trailing whitespace and no additional lines".
  (a) A single terminating newline is allowed; (b) no newline at all.
  Recommendation: (a), because it is standard terminal output and the existing
  script already does it; choose (b) if the output will be compared byte-for-byte.
- **Q3 (P0) — `CHANGELOG.md` vs "documentation files out of scope".** The gate
  blocks any PR without a `CHANGELOG.md` line. Accept that one line as in scope?
  Recommendation: yes, because without it no PR can pass the gate; otherwise the
  only path is (b) in Q1.
