# HLD — PLAY-156: `qa/s3-a.sh` prints "A"

## 1. System Overview
- **What:** a new standalone shell script, `qa/s3-a.sh`, in roeeoz/play1. It prints exactly one line, `A`, and exits 0.
- **Problem:** epic PLAY-155 tests whether the factory can deliver two stories where the second depends on the first. PLAY-157 (`qa/s3-b.sh`) will call this script, so this one has to exist first.
- **Responsibilities:** a fixed path, exact output, exit code 0, and the ability to run it directly (as a user or from another script). It must not break anything that exists today.

## 2. Architecture Overview
- **Component:** one file in `qa/`, next to `qa/s3-hello.sh`. `qa/` is outside `src/`, so the script isn't part of the Python package: it isn't a console script, and G1/G2 don't apply.
- **Release record:** `CHANGELOG.md` gets one line under `## Unreleased`. The repo's mr-gate (rule 4, `PLAY-G4`) requires it.
- **External dependencies:** only a POSIX `/bin/sh` and the `printf` builtin. Nothing new is added.
- **Ownership:** PLAY-156 creates and owns `qa/s3-a.sh`. Once this PR merges, PLAY-157 may only call it and must not change it.

## 3. Data Flow Design
- The developer runs `qa/s3-a.sh` from the repo root → the kernel follows the shebang to `/bin/sh` → the script writes `A\n` to stdout → it exits 0.
- Everything is synchronous. There is no input, no state, no files, no network and no environment variables.
- Later (PLAY-157): `qa/s3-b.sh` runs `qa/s3-a.sh` by path, its stdout passes straight through, and then B prints its own line.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| `qa/s3-a.sh` | Prints `A` and exits 0 | In: nothing. Out: stdout `A\n`, empty stderr, exit 0 | roeeoz/play1 |
| `CHANGELOG.md` entry | Release record the gate requires | One `- PLAY-156: …` line under `## Unreleased` | roeeoz/play1 |

## 5. Interface Contracts
- **The script's contract (PLAY-157 relies on it):**
  - Path: `qa/s3-a.sh`, relative to the repo root.
  - Stored in git as mode `100755`.
  - Starts with a shebang.
  - stdout is exactly the 2 bytes `A\n`: no trailing spaces, no CR, nothing else.
  - stderr is empty and the exit code is 0.
- Arguments are ignored and there's no `--help` handling (out of scope per Q1).
- There are no APIs, events, or cross-repo contracts.

## 6. Key Technical Decisions
- **Copy the sibling script.** It uses `#!/bin/sh` (POSIX), a one-line purpose comment and a single `printf 'A\n'`, just like `qa/s3-hello.sh`. Alternative: `#!/bin/bash` (as in `hello-world/hello.sh`). Rejected, because consistency within `qa/` and POSIX portability matter more.
- **Use `printf`, not `echo`.** `echo` behaves differently across shells, so `printf` is the reliable way to get exact bytes.
- **No new test.** The PO decided this (Q1). This departs from the PLAY-114 precedent, which added a pytest test. The acceptance criteria are shown in the PR description instead.
- **One PR.** The change is under 10 lines in 2 files, and the CHANGELOG line can't go in a separate PR because the gate checks each PR.

## 7. Risks & Constraints
- **Executable bit.** If the file is committed as `100644`, gate rule 2 fails and PLAY-157 can't run it directly. Check `git ls-files -s qa/s3-a.sh`.
- **No CI coverage of output.** CI passes even if the script prints the wrong thing. The PR description has to show the manual run.
- **Missing CHANGELOG line.** Without it, `PLAY-G4` blocks the merge.
- **Order (RK1).** PLAY-157's PR opens only after this one merges to `main`.
- **Regression (R3).** Existing `pytest` and `gate` jobs must stay green. No test globs `qa/`, so adding a file there can't break any of them. No `CI_FAIL` file may be added.
- **Traceability (R7) and secrets (R4).** The PR cites PLAY-156 and the Epic PRD (Confluence pageId 33292289). No secrets go in the code or commits.
- **Scale and performance:** not relevant. The script runs instantly and doesn't affect the CI time budget (G4).
