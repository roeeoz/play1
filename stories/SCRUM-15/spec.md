# Feature Specification Document — Hello world bash script in a dedicated folder

## 1. Feature Overview

> **Status: READY.** The developer directed that the story text and its acceptance
> criteria are the whole requirement, and that where they are silent the simplest
> reading is taken and recorded as an assumption. Those assumptions are listed in
> §8 (A1–A3), each with its risk.

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
- Documentation files (README or similar) — inside `hello-world/` or anywhere
  else. The single `CHANGELOG.md` line the repository gate requires is a
  repository change record, not documentation of the script (§8, A3).

## 3. Functional Requirements

- **FR1 — Location:** a folder `hello-world/` at the repository root containing
  exactly one file, `hello.sh`.
- **FR2 — Shebang:** the first line of `hello.sh` is `#!/bin/bash`.
- **FR3 — Executable:** `hello.sh` has executable permissions, so it runs as
  `./hello-world/hello.sh` without `bash` in front of it.
- **FR4 — Output:** running the script writes the lowercase string `hello world`
  to standard output, nothing else, and exits with code 0. The single line is
  terminated by one newline, as a normal terminal line is; no other character,
  space or line is printed (§8, A2).
- **FR5 — Existing script:** `hello-world/hello.sh` already on `main` satisfies
  FR1–FR4; it is kept as the story's delivery and not rewritten (§8, A1).
- **FR6 — Change record:** the pull request adds one line under `## Unreleased`
  in `CHANGELOG.md` naming the hello-world script, as the repository gate
  requires (§8, A3).
- **Inputs:** none (no arguments, no environment required).
- **Edge cases:** none beyond output exactness; argument handling is not specified
  and not requested.

## 4. User Experience & Behavior

- **Flow:** the developer runs `./hello-world/hello.sh` from the repository root;
  the terminal shows `hello world`; the shell reports exit status 0.
- **Output format:** exactly the lowercase string `hello world`, no leading or
  trailing whitespace, no additional lines; the line ends with one newline, so
  the shell prompt returns on the next line (§8, A2).
- No interactive behavior, no error messages, no visual styling requested.

## 5. Acceptance Criteria

1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## 6. Dependencies & Constraints (product-level)

- **Existing artifact:** `hello-world/hello.sh` already exists on `main`
  (commit `65938b5`, WI-220A63-1) and meets FR1–FR4 today (§8, A1).
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):**
  rule 2 (a new shell script is executable and starts with a shebang) matches
  the story; rule 4 blocks any pull request that does not add a line under
  `## Unreleased` in `CHANGELOG.md` (blocker `PLAY-G4`). No exemption is possible.
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** `pytest`
  plus the `CI_FAIL` marker check; neither runs shell scripts. CI integration is
  out of scope per the story.
- Size XS (≈1), priority Must, no blockers or pre-conditions in the story.

## 7. Technical Design (deferred to STRUCTURE)

Nothing to design at product level. How the acceptance criteria are verified
(e.g. capturing the output and comparing it to `hello world` plus one newline)
is for STRUCTURE.

## 8. Assumptions & Open Questions

No open product questions remain. Per the developer's direction ("take the
simplest reading, record it as an assumption, and proceed"), these assumptions
stand in for the points the story is silent on:

- **A1 — The existing script is the delivery.** `hello-world/hello.sh` already on
  `main` meets every acceptance criterion, so the story changes nothing in it;
  the pull request records it against this story. *Risk:* if the story was meant
  to produce a new or different script, the PR will look like it changes nothing
  in `hello-world/`.
- **A2 — One terminating newline is allowed.** "No trailing whitespace and no
  additional lines" is read as: the output is the single line `hello world`,
  ended by its one newline (what `echo` prints). *Risk:* a byte-for-byte check
  expecting exactly 11 bytes with no newline would fail.
- **A3 — The `CHANGELOG.md` line is in scope.** The repository gate (rule 4,
  blocker `PLAY-G4`) blocks any pull request without a line under
  `## Unreleased`, and allows no exemption. That line is read as a change record,
  not one of the "documentation files" the story excludes. *Risk:* if the
  developer counts it as documentation, the story cannot be delivered by pull
  request at all, and the only alternative is closing it as already done.
