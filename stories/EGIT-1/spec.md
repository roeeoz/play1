# Feature Specification Document — EGIT-1: e2e-pr343 marker script from another branch

## 1. Feature Overview
- **Summary:** Add a small executable bash script, `qa/e2e-pr343/marker.sh`, that prints the marker line kept on the branch `e2e-other-branch`. The line is hard-coded in the script.
- **Problem statement:** The marker line lives only on `e2e-other-branch`, in `e2e-other-branch-marker.txt`. Today a developer has to switch branches or run git plumbing to see it.
- **Target users / actors:** Developers working on `main` who need to check the marker line.

## 2. Goals & Non-Goals
### Story context
the marker line is the FIRST line of the file `e2e-other-branch-marker.txt` at the root of the branch `e2e-other-branch` of this repository (the file is not on `main`). Read that file from that branch in your checkout and quote its first line verbatim in your reply before anything else.

### Goals
- Developers can print the `e2e-other-branch` marker line from `main` with one command and without switching branches.
- The script's output is exactly the marker line as it is on `e2e-other-branch` today: `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`

### Non-Goals
- Reading the marker from git at run time. The script must not call git.
- Merging, rebasing onto or bringing in any content from `e2e-other-branch`.
- Changing any existing file. That includes other `qa/` scripts, a README and a CHANGELOG.
- Adding tests or documentation.
- Keeping the hard-coded line in sync automatically if the marker on `e2e-other-branch` changes later.

## 3. Functional Requirements
- **FR1:** A new file `qa/e2e-pr343/marker.sh` exists in the repository.
- **FR2:** The file's first line is exactly `#!/bin/bash`.
- **FR3:** The file is executable, and the executable bit is recorded in the repository (not only set on someone's local file).
- **FR4:** Running the script prints exactly `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22` to standard output, followed by a single newline, and nothing else.
- **FR5:** The script exits with status 0.
- **FR6:** The line is a literal in the script. The script does not run git and does not read the file from any branch.
- **Inputs:** None. The script takes no arguments and needs no environment.
- **Outputs:** The marker line on stdout. Nothing is written to stderr.
- **Edge cases:** The output is the same from any working directory and on any checked-out branch, because the line is hard-coded.

## 4. User Experience & Behavior
- **Flow:** A developer on any branch runs `qa/e2e-pr343/marker.sh` (or `./marker.sh` from inside `qa/e2e-pr343/`). The terminal shows the one marker line and the command returns success.
- **Output format:** exactly one line, plain ASCII, with no prefix, label, colour or extra blank lines.
- **Error states:** none. The script needs no input and does not fail.

## 5. Acceptance Criteria
1. `qa/e2e-pr343/marker.sh` exists, starts with `#!/bin/bash`, is executable, prints exactly the first line of `e2e-other-branch-marker.txt` as it is on `e2e-other-branch` and exits 0
2. the line is hard-coded in the script (the script does not call git)
3. no existing file is modified and no test or documentation is added

## 6. Dependencies & Constraints (product-level)
- **Source of truth:** the first line of `e2e-other-branch-marker.txt` on `e2e-other-branch`, as it is now: `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`.
- **Base branch:** the change is based on `main` and merges into `main`. `e2e-other-branch` is only where the marker is read from, never a base or merge source.
- **Shebang:** the story requires `#!/bin/bash`, although the existing `qa/` scripts use `#!/bin/sh`.
- **Delivery:** a person merges the pull request after review.

## 7. Technical Design (deferred to STRUCTURE)
STRUCTURE decides how the line is printed and quoted, and how the executable mode is committed. The product only requires that the output is byte-exact and that the script makes no git call.

## 8. Open Questions
- None blocking. The assumptions are that the output ends in one newline, and that the hard-coded line is a snapshot that can go out of date if the marker branch changes.
