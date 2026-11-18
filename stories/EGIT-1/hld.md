# HLD — EGIT-1: e2e-pr343 marker script

## 1. System Overview
- **What:** a new executable bash script, `qa/e2e-pr343/marker.sh`, in repo `play1`. It prints the marker line from `e2e-other-branch` as a hard-coded literal.
- **Problem:** the marker exists only in `e2e-other-branch-marker.txt` on `e2e-other-branch`. Today a developer has to switch branches or use git plumbing to read it.
- **Responsibility:** print exactly `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22` followed by one `\n` on stdout, write nothing to stderr, and exit 0.

## 2. Architecture Overview
- One self-contained component: a static shell script. It has no runtime dependencies beyond `/bin/bash`.
- **Ownership:** a new directory, `qa/e2e-pr343/`, owned entirely by this story. No other file in the repo is touched.
- **Runtime dependencies:** none. No git, no network, no environment variables, no arguments.
- **Design-time source of truth:** line 1 of `e2e-other-branch-marker.txt` on `origin/e2e-other-branch`. It is read once, only to author and verify the literal. It is never merged, cherry-picked or copied onto the work branch.

## 3. Data Flow Design
- Developer runs the script → bash prints the embedded literal and a newline → exit 0.
- Synchronous and stateless. The output is the same in any working directory and on any checked-out branch.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `qa/e2e-pr343/marker.sh` | Print the hard-coded marker line | In: none. Out: one ASCII line plus `\n` on stdout, exit 0 | `play1` |

## 5. Interface Contracts
- **CLI contract:** `qa/e2e-pr343/marker.sh` (or `./marker.sh` from inside its directory), with no arguments.
  - stdout is exactly the bytes `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22\n`.
  - stderr is empty and the exit status is 0.
- **Repository contract:** the file is tracked with git mode `100755` and its first line is exactly `#!/bin/bash`.
- There is no cross-repo contract.

## 6. Key Technical Decisions
- **Literal output.** Print a single-quoted literal with `printf`, matching the existing `qa/` scripts. The line contains no `'`, `"`, `$`, `\`, `%` or backtick, so single quotes need no escaping. `echo` would also give the right bytes, but `printf` is the repo convention and behaves the same everywhere.
- **Shebang.** `#!/bin/bash`, which the spec requires (FR2). This departs on purpose from the `#!/bin/sh` the existing `qa/` scripts use.
- **Executable bit.** Record it in git as mode `100755`, via `chmod +x` (`core.fileMode=true`) or `git update-index --chmod=+x`.
- **Optional comment.** A one-line `#` comment after the shebang, as in the existing `qa/` scripts, is allowed. It does not change the output.
- **Rejected:** reading the marker with git at run time, because FR6 and the non-goals forbid it. Bringing the marker file onto `main` was also rejected, because nothing from `e2e-other-branch` may be brought in.

## 7. Risks & Constraints
- **Byte-exactness:** a CRLF line ending, an extra or missing newline, a trailing space or a smart quote would break FR4. Mitigation: compare `od -c` of the script's output with `od -c` of line 1 of the source file before opening the PR.
- **Lost executable bit:** the file could land as `100644`. Mitigation: check `git ls-files -s qa/e2e-pr343/marker.sh`.
- **Snapshot drift:** the literal goes stale if the marker branch changes. The spec accepts this as a non-goal.
- **CI blind spot:** CI runs only pytest over `tests/` plus the `CI_FAIL` gate, so nothing in CI exercises this script. Verification is done by hand and recorded in the PR. Adding a test is forbidden by AC3.
- **Scale, performance, security:** none apply. The script has no inputs, no I/O beyond stdout, and no secrets.
