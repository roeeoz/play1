# Ticket draft (not ready): SCRUM-1, Hello world bash script in a dedicated folder

## User story (as published)
As a developer, I want a hello-world bash script in its own dedicated folder in the repository, so that I have a verified, runnable starting point for shell scripting without cluttering existing directories.

## Context (as published)
This is the only story of the epic. The script lives in a new folder named `hello-world` with no other files in it. The script is named `hello.sh`, includes a shebang line (`#!/bin/bash`), has executable permissions, and prints exactly "hello world" to standard output when run. Out of scope: additional scripts, CI/CD integration, documentation files.

## Acceptance criteria (as published) and where `main` stands today
| # | Criterion | Status on `main` (`b7b5d0a`) |
|---|---|---|
| 1 | `./hello-world/hello.sh` prints exactly "hello world" and exits with 0 | Met (checked by running it) |
| 2 | `hello.sh` is the only file in `hello-world/` | Met |
| 3 | `#!/bin/bash` shebang and executable permission; runs without calling `bash` | Met (mode 100755) |
| 4 | Exactly "hello world", lowercase, no leading or trailing whitespace, no extra lines | Unclear: the output is `hello world\n` (see Q2) |

Supporting evidence: commit `65938b5` added the script. `tests/test_hello_sh.py` checks output, exit code, empty stderr, shebang, executable bit and the folder's contents. CI runs it through `pytest`.

## Open questions (blocking)
- **Q1.** The deliverable is already on `main`. Should the story (a) close as already done, with the check as evidence, (b) add one named missing thing, or (c) fix a named problem? I recommend (a).
- **Q2.** Does criterion 4 allow the final newline after "hello world"? I recommend yes, which keeps today's script and test unchanged.
