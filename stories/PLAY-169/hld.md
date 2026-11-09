# HLD — PLAY-169: test script `qa/20261109-s6/a.sh` prints "a" and exits successfully

Target repository: `roeeoz/play1`. Target branch: `qa-20261109-s6-base`.

## 1. System Overview
- **What is being built:** one standalone POSIX shell script, `qa/20261109-s6/a.sh`, that prints exactly one line, `a`, and exits with code 0. It comes with one `CHANGELOG.md` line under `## Unreleased`.
- **Problem statement:** the factory's single-story controls probe (epic QA-20261109-S6) needs a trivial, self-contained change. It shows that a one-story epic can go through define, structure, implement and approval and end in one mergeable pull request without breaking CI.
- **Key responsibilities:** produce the exact output, exit 0, and keep the change to the allowed files.

## 2. Architecture Overview
- **Components:** one shell script under `qa/`, outside the Python package. It is not packaged, not registered in `[project.scripts]`, and not collected by pytest (`testpaths = ["tests"]`).
- **Boundaries:** the script does not depend on or touch the package code, `tests/`, other `qa/` scripts or CI configuration.
- **Ownership:** one ticket owns the new file `qa/20261109-s6/a.sh` and the one appended line in `CHANGELOG.md`.
- **External dependencies:** only a POSIX `sh` and its `printf` builtin. No libraries and no network.

## 3. Data Flow Design
- The user runs `qa/20261109-s6/a.sh`. The script writes `a` and a newline to stdout and exits 0.
- Everything is synchronous. There are no events, no input and no state.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| `qa/20261109-s6/a.sh` | Print `a` and exit 0 | In: none. Out: stdout `a\n`, exit code 0, nothing on stderr | roeeoz/play1 |
| `CHANGELOG.md` (one line) | Record the change; satisfies merge gate rule PLAY-G4 | One bullet appended under `## Unreleased`, same style as the existing entries | roeeoz/play1 |

## 5. Interface Contracts
- **CLI contract:** the script is run directly as `qa/20261109-s6/a.sh` (or `sh qa/20261109-s6/a.sh`) with no arguments. stdout is exactly the bytes `a\n`. The exit status is 0.
- **No APIs, event schemas or cross-repo contracts.**

## 6. Key Technical Decisions
- **Copy the existing `qa/` scripts** (`qa/s3-a.sh`, `qa/s3-hello.sh`): a `#!/bin/sh` shebang, a one-line purpose comment, and `printf` rather than `echo` so the output bytes are the same in every shell. Do not copy the stale "called by qa/s3-b.sh" comment from `qa/s3-a.sh`.
- **Executable bit:** git mode `100755`, as the existing `qa/` scripts have. Merge gate rule 2 requires an executable file with a shebang.
- **Exit code:** a `printf` that succeeds returns 0. Whether to add an explicit `exit 0` is left to the implementer; either way the contract is exit status 0.
- **No new automated test:** the PO limited the scope, and the same choice was made for PLAY-156. The run-the-script check (acceptance criterion 1) is done by hand.
- **Alternatives rejected:** `echo` (its behavior differs between shells); a Python entry point (would change the package, which is out of scope).

## 7. Risks & Constraints
- **Lost executable bit:** if the file lands as mode 100644, gate rule 2 blocks it and running it directly fails. Check the mode in the git index.
- **Scope creep (risk RK1):** any extra product file fails acceptance criterion 2. That includes tests, a README entry, `c.sh`, or a fix to the stale comment in `s3-a.sh`.
- **CHANGELOG:** append only. Existing lines must not change.
- **CI:** minimal risk. pytest does not collect anything from `qa/`, and the `gate` job stays green unless a `CI_FAIL` file is added.
- **Scale, performance, security:** not relevant. The script has no input and handles no secrets or personal data.
