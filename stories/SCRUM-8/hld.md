# HLD — SCRUM-8: Hello world bash script in a dedicated folder

## 1. System overview
- **What:** `hello-world/hello.sh` is a bash script alone in its folder. It prints `hello world` and exits with code 0.
- **Current state:** it is already on `main` (commit `65938b5`), stored as executable (mode `100755`). Its content is `#!/bin/bash` followed by `echo "hello world"`, with LF line endings. Tests for it are in `tests/test_hello_sh.py` (commits `a2ec96d` and `9a5bd0b`). All four acceptance criteria hold today.
- **Job of this story:** confirm the criteria still hold on the work branch. Change the script only if a criterion fails. Close one gap in the tests: git's stored executable bit is never checked directly.

## 2. Architecture overview
| Component | Responsibility | Repo |
|---|---|---|
| `hello-world/hello.sh` | The deliverable: shebang, executable bit, prints exactly one line | play1 |
| `tests/test_hello_sh.py` | Pytest checks for all four acceptance criteria | play1 |
| `.github/workflows/ci.yml` and `pyproject.toml` (`testpaths = ["tests"]`) | Already run pytest on every pull request. Used as they are, never changed | play1 |

There are no external dependencies and no services.

## 3. Data flow
- Developer runs `./hello-world/hello.sh` → the kernel reads the shebang → `/bin/bash` runs `echo` → `hello world\n` goes to stdout → exit 0.
- Pull request → CI `test` job → `pytest` collects `tests/test_hello_sh.py` → the tests run the script as a subprocess and check its output and exit code.
- Everything is synchronous. No events, no stored state.

## 4. Component breakdown
- **hello.sh.** Input: none (no arguments, no environment variables). Output: the 12 bytes `hello world\n` on stdout, nothing on stderr, exit code 0. Repo: play1.
- **test_hello_sh.py.** Input: the checked-out repository. Output: pass or fail for each criterion. Repo: play1.

## 5. Interface contracts
- **Command-line contract:** `./hello-world/hello.sh` run from the repo root. Prints `hello world` plus one newline (assumption A2), writes nothing to stderr, exits 0.
- **File contract:**
  - git stores the file with mode `100755`;
  - the first line is `#!/bin/bash`;
  - line endings are LF;
  - `hello-world/` holds only `hello.sh`.
- No cross-repo contracts.

## 6. Key technical decisions
- **Keep the existing script.** It already meets every criterion. Rewriting it would add risk (dropping the executable bit, introducing CRLF line endings) and no value.
- **Reuse the existing pytest suite and CI.** The spec rules out CI/CD integration, so CI is not touched.
- **Add one check.** The new test asserts that git stores `hello.sh` with mode `100755`. Today's check reads the filesystem mode, which can differ from git's when `core.fileMode=false`.
- **Alternative rejected: a verification-only item with no diff.** The factory needs each item to produce a code change.
- **Alternative rejected: a README or CHANGELOG entry.** FR5 forbids documentation files, and a README inside `hello-world/` would break Scenario 2.

## 7. Risks and constraints
- **Scope creep:** anything new in `hello-world/`, documentation, or CI edits would break FR5 or Scenario 2.
- **Newline reading:** the single trailing newline is allowed (A2). A strict 11-byte reading would fail both the script and the existing tests.
- **Mode and line endings:** any edit to `hello.sh` must keep mode `100755` and LF line endings.
- **CI gate:** never create `CI_FAIL` at the repo root.
- **Test file outside `hello-world/`:** `tests/test_hello_sh.py` sits outside the folder FR5 names. It is a test file, not a script, CI change or documentation file, and earlier commits for this script set the precedent. This is recorded as an assumption.
