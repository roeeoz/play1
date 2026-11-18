# Ticket draft: Hello world bash script in a dedicated folder (intake in progress)

**Status:** NOT_READY. Waiting for the developer's answers to Q1 and Q2.

## User story (as published)
As a developer, I want a hello-world bash script in its own dedicated folder in the repository, so that I have a verified, runnable starting point for shell scripting without cluttering existing directories.

## Context (as published)
This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

- **Traces to:** R1, R2, R3, R4 · steps 1–4 · RK1. The epic material was not available here, so these were not checked.
- **Priority:** Must
- **Size:** XS (≈1)
- **Pre-conditions / Blockers:** None as published. Q1 and Q2 below are open.

## Observed state of the target branch (`main`, b7b5d0a)
- `hello-world/hello.sh` exists. Commit 65938b5 added it. Its content is `#!/bin/bash` followed by `echo "hello world"`, and it is stored as mode 100755.
- It is the only file in `hello-world/`.
- Running `./hello-world/hello.sh` prints `hello world` followed by one newline and exits with 0.
- `tests/test_hello_sh.py` covers the exit code, the exact stdout (`"hello world\n"`), empty stderr, the shebang, the executable bit and folder isolation. All 6 tests pass. The repository runs `pytest` on every pull request.

## Acceptance criteria (as published, unchanged)
1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## Proposed addition (pending Q4)
5. Scenario 5 — Regression: the existing script is kept. Given `hello-world/hello.sh` and its tests already exist on `main`, When this story is delivered, Then the script and its tests are unchanged, and no other file is added to `hello-world/`.

## Open questions
- **Q1 (P0):** What does "done" mean when `main` already meets every criterion? The options are (a) evidence only, (b) a small change, or (c) something else. *Recommendation:* (a), because the deliverable exists and other stories require it to stay unchanged.
- **Q2 (P0):** Does criterion 4 allow the single line break that `echo` adds? *Recommendation:* yes, because the existing script, the existing test and PLAY-172's rule against modifying the script all depend on it.
- **Q3 (P1):** Is this a re-run of SCRUM-1 and SCRUM-2, and should it reuse their decisions?
- **Q4 (P1):** Should criterion 5 above be added?
