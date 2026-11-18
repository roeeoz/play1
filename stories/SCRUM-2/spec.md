# Ticket draft: 20261118-212149Z Hello world bash script in a dedicated folder

**Status:** NOT_READY. Waiting for the developer's answers to P0-1 and P0-2.

## User story
As a developer, I want a hello-world bash script in its own dedicated folder in the repository, so that I have a verified, runnable starting point for shell scripting without cluttering existing directories.

## Context (as published)
This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

- Traces to: R1, R2, R3, R4 · steps 1–4 · RK1
- Priority: Must
- Size: XS (≈1)
- Pre-conditions: none
- Blockers: none listed. The two P0 questions below act as blockers.

## Acceptance criteria (as published, unchanged)
1. Scenario 1 — Happy path: script execution. Given the repository contains a folder named `hello-world` with a file named `hello.sh`, When a developer executes `./hello-world/hello.sh`, Then the script prints exactly "hello world" to standard output and exits with code 0.
2. Scenario 2 — Happy path: folder isolation. Given the `hello-world` folder exists in the repository, When a developer lists its contents, Then the only file present is `hello.sh`.
3. Scenario 3 — Happy path: direct execution via shebang. Given `hello.sh` has a shebang line `#!/bin/bash` and executable permissions set, When a developer runs the script without explicitly invoking bash, Then it executes successfully without requiring `bash hello.sh`.
4. Scenario 4 — Edge case: output exactness. Given the script is executed, When the output is captured, Then it contains exactly the lowercase string "hello world" with no leading or trailing whitespace and no additional lines.

## What `main` (b7b5d0a) already has
| Criterion | State on `main` |
| --- | --- |
| AC1 | Met. Prints `hello world` and exits with code 0. |
| AC2 | Met. `hello-world/` contains only `hello.sh`. |
| AC3 | Met. The file starts with `#!/bin/bash` and is mode 100755. |
| AC4 | Met only if one trailing newline is allowed (see P0-2). |

Existing coverage: `tests/test_hello_sh.py` (6 tests, all passing) runs in CI on every PR.

## Open P0 questions
- **P0-1.** What should this delivery produce, given the deliverable is already on `main`? Recommended: (a), close as already met and attach the evidence.
- **P0-2.** Can the output in AC4 end with a newline? Recommended: (a), yes, and reword AC4 to say the output is exactly `hello world` plus one newline.
