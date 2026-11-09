# HLD — PLAY-165: QA script that prints "c" and exits successfully

Target repo: `roeeoz/play1` · Base/target branch: `qa-20261109-s6-base` · Epic: QA-20261109-S6 (Epic PRD, Confluence pageId 33980417)

## 1. System Overview
- **What:** a standalone bash script at `qa/20261109-s6/c.sh` that writes exactly `c\n` to stdout and exits 0, plus the one `CHANGELOG.md` line the repo gate requires.
- **Problem:** the epic checks that the delivery factory can carry one trivial story from spec to merge as a one-product-file change with every required check green (G3).
- **Responsibilities:** deterministic output, ignoring arguments (FR4), a gate-compliant file (executable, with a shebang), and traceability in the PR.

## 2. Architecture Overview
- **Components:**
  - A single leaf shell script.
  - It has no runtime dependencies beyond `bash` (`/usr/bin/bash` is available).
  - It has no coupling to the Python package (`src/`), its console scripts (`[project.scripts]`) or the tests (`tests/`, `testpaths = ["tests"]`).
- **Boundaries:**
  - `qa/20261109-s6/` is a new subdirectory and the first nested folder under `qa/`.
  - The existing `qa/s3-a.sh` and `qa/s3-hello.sh` are not touched.
- **Ownership:** one work item owns both `qa/20261109-s6/c.sh` (new) and the single appended line in `CHANGELOG.md`.
- **External dependencies:**
  - The existing CI in `.github/workflows/ci.yml`:
    - The `test` job runs pytest on Python 3.12.
    - The `gate` job fails only if a `CI_FAIL` file exists at the repo root.
  - The repo-gate rules:
    - Rule 2: a new shell script must be executable and start with a shebang.
    - Rule 3: no file over 200 KB.
    - Rule 4 (PLAY-G4): the PR must add a CHANGELOG line under `## Unreleased`.

## 3. Data Flow Design
- Synchronous only: `bash qa/20261109-s6/c.sh [any args]` → stdout `c\n` → exit 0.
- No input, state, files, environment variables, network or events.
- Delivery flow:
  1. The factory opens the PR.
  2. The `test` and `gate` jobs run.
  3. A human reviews and merges into `qa-20261109-s6-base`.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
| --- | --- | --- | --- |
| `qa/20261109-s6/c.sh` | Print exactly `c` plus a newline and exit 0, regardless of arguments | In: none (args ignored) / Out: stdout `c\n` (2 bytes, LF), empty stderr, exit 0 | roeeoz/play1 |
| `CHANGELOG.md` entry | Satisfy gate rule PLAY-G4 | One line appended at the end of `## Unreleased`, in the existing entry style | roeeoz/play1 |

## 5. Interface Contracts
- **CLI contract:**
  - Invocation: `bash qa/20261109-s6/c.sh` or `./qa/20261109-s6/c.sh`.
  - stdout is the bytes `0x63 0x0A`.
  - stderr is empty.
  - Exit code is 0.
  - Any arguments, including `--help`, produce identical results.
- **Repo contract:**
  - Git mode `100755`.
  - First line is a shebang.
  - LF line endings.
- No API, event or cross-repo contracts.

## 6. Key Technical Decisions
- **Shebang `#!/bin/bash`:** the spec calls it a "bash script" and makes a bash shebang the default.
  - Alternative: `#!/bin/sh`, consistent with `qa/s3-*.sh` and the PLAY-156 choice.
  - Rejected because the spec's own default wins. Either choice meets AC1, AC2 and gate rule 2.
- **Print with `printf`, not `echo`:** `printf` gives byte-exact output across shells, the same reason PLAY-156 gave.
- **No argument parsing:** the script never reads its arguments, so `--help` behaves the same as a bare run (FR4, Epic §7 decision).
- **No automated test:** a test would be an extra product file (spec non-goal; Epic §7). AC1, AC2 and AC5 are shown by manual runs recorded in the PR.
- **CHANGELOG line:**
  - Required by gate rule PLAY-G4, and the spec approves it as a deliberate departure from the Epic PRD's R4 and §8.
  - It can't be split into a separate PR, because the gate checks each PR on its own.
- **One work item:** the whole change is about 4 lines and can't usefully be split.

## 7. Risks & Constraints
- **Executable bit:** the file must be committed as `100755`, or gate rule 2 fails. Verify with `git ls-files -s qa/20261109-s6/c.sh`.
- **No CI check of the output:** CI stays green even if the script prints the wrong thing. The PR must include manual-run evidence of the exact bytes, empty stderr and exit 0, both with no arguments and with `--help`.
- **CHANGELOG merge conflict:** a parallel story appending to `## Unreleased` will conflict in `CHANGELOG.md`. Resolve by keeping both lines. Never rebase onto another branch.
- **Changed-files check (AC3):** the PR diff also contains the `stories/PLAY-165/` planning docs. The PR description must say these are not product files.
- **PRD mismatch:** the Epic PRD's R4 and §8 still forbid a CHANGELOG entry. The PR description acknowledges the spec's override.
- **Security and performance:**
  - No secrets or personal data in the script, the PR or the commits; the commit author is a noreply address.
  - No effect on coverage (G1) or on pytest runtime (G4).
- **Scaling:** not applicable.

## 8. Requirement coverage
| Requirement | Work item |
| --- | --- |
| FR1–FR4 / AC1–AC2 | t1 |
| FR5 / AC3 | t1 |
| FR6 / AC5 | t1 (no existing file touched, plus manual regression runs) |
| AC4 (required checks green) | t1 |
| FR7 / AC6 | t1 (PR description cites PLAY-165 and the QA-20261109-S6 Epic PRD) |
