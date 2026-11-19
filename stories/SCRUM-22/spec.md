# Feature Specification Document — Hello world bash script in a dedicated folder

> **Status: READY_FOR_SPEC.** The developer ruled that the story text and its acceptance criteria are the whole requirement, and that where they are silent the simplest reading applies and is recorded as an assumption. The earlier open questions are settled as assumptions A1–A3 (§8).

## 1. Feature Overview

- **What:** a minimal hello-world bash script, `hello-world/hello.sh`, in its own top-level folder of the play1 repository.
- **Problem:** developers want a verified, runnable starting point for shell scripting that does not clutter the existing directories (`qa/`, `src/`, `tests/`, `docs/`).
- **Target user:** a developer working in this repository.
- **Epic context:** this is the only story of its epic (traces to R1–R4, steps 1–4, risk RK1). Priority Must, size XS (≈1). No pre-conditions and no blockers are listed.

**Finding from the repository:** `main` (and so the work branch) already contains `hello-world/hello.sh` (commit `65938b5`, "WI-220A63-1: Add hello-world bash script in dedicated folder"). It is mode `100755`, its content is `#!/bin/bash` followed by `echo "hello world"`, it is the only file in `hello-world/`, and running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits 0. Under assumptions A1 and A2 (§8) this already meets all four acceptance criteria; the story's job is to keep that true and show it with evidence.

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
- Documentation files (no README or other file in `hello-world/`, no new docs elsewhere). The one-line `CHANGELOG.md` entry the repository gate requires on every pull request is not treated as a documentation file (assumption A3).
- Arguments, options, localisation or any output other than `hello world`.

## 3. Functional Requirements

- **FR1 — Location.** A folder named `hello-world` at the repository root contains exactly one file, `hello.sh`.
- **FR2 — Shebang.** The first line of `hello.sh` is exactly `#!/bin/bash`.
- **FR3 — Executable.** `hello.sh` has executable permission in the repository, so it keeps that permission in a fresh clone.
- **FR4 — Output.** The script takes no input. When run, it writes exactly the lowercase text `hello world` to standard output, with no leading or trailing spaces and no other lines. One terminating newline after the text is allowed, and nothing else (assumption A2).
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

- **Already present on `main`:** `hello-world/hello.sh` exists there from commit `65938b5` (assumption A1).
- **Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** rule 2 says a new shell script must be executable and start with a shebang. The story already requires both. Rule 4 says every pull request must add a line under `## Unreleased` in `CHANGELOG.md`, or the gate blocks it (`PLAY-G4`). It runs on every pull request and cannot be waived, so the pull request adds one such line naming this story (assumption A3).
- **Test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** the gate is `pip install -e ".[test]"` and `pytest`, plus the `CI_FAIL` marker check. Neither is affected by a bash script. The story puts CI integration out of scope, so the script is checked by hand against §5. The pull request's required checks must still be green.
- A person reviews and merges the pull request. The factory does not merge it.

## 7. Technical Design (deferred to STRUCTURE)

Nothing here needs design. How executable permission is recorded in git, and how the manual checks are written up as pull-request evidence, are left to STRUCTURE.

## 8. Open Questions

No blocking questions remain. The developer ruled that the story text and its acceptance criteria are the whole requirement, and that where they are silent the simplest reading applies. These are those readings:

- **A1 — The script already on `main` is the deliverable.** `hello-world/hello.sh` from commit `65938b5` is kept as it is, not rewritten. The story is delivered by checking it against §5 and recording that evidence in the pull request. The script is changed only if a check fails. *Risk:* if the intent was a fresh rebuild (for example as a pipeline exercise), the pull request holds almost no code change. That does not affect whether the criteria are met.
- **A2 — "Exactly `hello world`" allows one terminating newline.** The script prints `hello world\n`: no leading or trailing spaces, no other lines, and a captured value (`$(./hello-world/hello.sh)`) equals `hello world`. This is the normal output of a shell command. *Risk:* a byte-exact comparison expecting no newline at all would fail. That reading is not chosen because the story does not ask for it.
- **A3 — The `CHANGELOG.md` line is in scope.** The repository gate (`PLAY-G4`) blocks any pull request without a line under `## Unreleased`, and it cannot be waived. "Documentation files" is read as files such as a README, inside `hello-world/` or added as new docs. The changelog line goes in the existing `CHANGELOG.md` at the repository root, so Scenario 2 still holds. *Risk:* none to the criteria; it is one line outside the story's folder.
