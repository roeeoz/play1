# Ticket draft: Hello-world bash script in a dedicated folder

**Status:** blocked on one P0 decision (see Open questions).

## User story
As a developer, I want a hello-world bash script in its own folder, so that I have a runnable starting point for shell scripting.

## Story context
In: the `hello-world` folder and `hello.sh`. Out: other scripts, CI, documentation.

## Traces to
R1, R2, R5 · RK1. Priority: Must. Size: XS (≈1). Blockers: None.

## Acceptance criteria (as published)
1. Scenario 1 — Happy path: script execution. Given the repository holds `hello-world/hello.sh`, When a developer runs `./hello-world/hello.sh`, Then it prints exactly "hello world" and exits with code 0.
2. Scenario 2 — Happy path: direct execution. Given `hello.sh` starts with `#!/bin/bash` and is executable, When it is run without `bash`, Then it runs.
3. Scenario 3 — Edge case: output exactness. Given the script runs, When its output is captured, Then it is exactly one line, "hello world", with no surrounding whitespace.

## What is already on `main`
- `hello-world/hello.sh` exists. It contains `#!/bin/bash` and `echo "hello world"`, and git stores it as mode `100755`. That meets R1, R2 and R5, and mitigates RK1. It was added in commit `65938b5`.
- `tests/test_hello_sh.py` already checks:
  - criteria 1 and 3: the output is exactly `hello world`, the exit code is 0 and nothing is printed on standard error
  - criterion 2 and R5: the first line is `#!/bin/bash` and the file is executable
  - the folder holds only `hello.sh`
- The work branch has nothing beyond `main`.

## Open questions
- **P0:** What should this story deliver, given it is already met on `main`?
  - (a) Close it as done, with no code pull request.
  - (b) Open a small pull request that only adds a test linked to this story. A CHANGELOG entry is out of scope unless you approve it.
  - (c) Build it again.

  I recommend (a). I'd pick (b) if every story must end with a pull request.
- **P1:** Should the folder stay at the repository root? I recommend yes, because that's where the existing code is.

## Note for the next story ("Greet a person by name")
The existing test `test_folder_contains_only_hello_sh` will fail once `greet.sh` is added. R1 says the folder holds "only the greeting scripts", plural, so that story will need to update the test.
