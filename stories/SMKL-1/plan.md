# Plan — SMKL-1: Hello world bash script in a dedicated folder

## Context

SMKL-1 asks for `hello-world/hello.sh` in the `play1` repo: the only file in its folder, starting with `#!/bin/bash`, executable, and printing exactly "hello world".

**The work is already on `main`.** I checked this against the git history:

- The work branch `halo/feat/smkl-1-20261127-180057` is at the same commit as `origin/main` (`c7252c1`). `git log origin/main..HEAD` is empty, so the branch has no commits of its own.
- `hello-world/hello.sh` was added by `65938b5` (WI-220A63-1) and later changed by `9a5bd0b`. `git merge-base --is-ancestor` confirms both commits are ancestors of `origin/main`. Reading the file from `main` (`git show origin/main:hello-world/hello.sh`) gives `#!/bin/bash\necho "hello world"\n`, 31 bytes, git mode `100755`.
- `hello-world/` has no other file in it.
- `tests/test_hello_sh.py` is also on `main`. It checks the exit code, the exact stdout `"hello world\n"`, that stderr is empty, the shebang, the executable bit, and that the folder holds only `hello.sh`.
- Running `./hello-world/hello.sh` locally printed `hello world\n` and exited with code 0.

## Acceptance criteria → existing evidence

| AC | Covered by |
|----|------------|
| 1. `./hello-world/hello.sh` prints "hello world" and exits 0 | `TestHelloShExecution.test_prints_hello_world` |
| 2. Only `hello.sh` in `hello-world/` | `TestHelloShStructure.test_folder_contains_only_hello_sh` |
| 3. Shebang `#!/bin/bash` + executable, runs directly | `test_shebang_line`, `test_executable_permission`; the execution tests run the script directly, without calling `bash` |
| 4. Exact output, no extra whitespace or lines | `test_exact_output_no_extra_whitespace` (this depends on the decision below) |

## Decision for the developer: the trailing newline (AC 4)

AC 4 says the captured output contains exactly "hello world" with "no leading or trailing whitespace and no additional lines". Today the script prints `hello world\n`: `echo` adds one newline at the end. Whether that meets AC 4 is a matter of reading, and the developer chooses when approving this plan:

- **A. Keep `echo`. This is the default if nothing else is said.** The newline ends the one line of output. It does not add a line, and `$(./hello-world/hello.sh)` captures exactly `hello world`. The repo stays as it is.
- **B. The literal reading: no trailing byte at all.** The build changes line 2 of `hello-world/hello.sh` to `printf 'hello world'`. In `tests/test_hello_sh.py` it changes the two `== "hello world\n"` assertions to `== "hello world"`. The shebang, mode `100755` and the folder stay as they are. The cost: an interactive shell prompt will then appear on the same line as the output.

## Build steps

1. Apply the developer's choice above. With A, nothing changes under `hello-world/` or `tests/`. With B, change only the two places named in B.
2. Run the checks in Verification.
3. Write the build log at `stories/SMKL-1/implementation-log.md`. The platform expects this file in the story's plan folder, next to `plan.md` and `summary.md`. It is the factory's record of the build, not product documentation, so it does not fall under the story's "no documentation files" exclusion. The build adds no README or any other doc under `hello-world/` or anywhere else in the product tree. With A, the merge request contains only the plan-folder files. Its description should say plainly that the script is already on `main` (commits `65938b5` and `9a5bd0b`), and it should include the evidence from Verification.
4. Leave CI files, docs and other scripts alone. They are out of scope.

## Verification

From the repo root `play1-79db628f23`:

- `./hello-world/hello.sh | od -c; echo "exit=${PIPESTATUS[0]}"` should print `exit=0`. The bytes should be `h e l l o   w o r l d \n` under A, or `h e l l o   w o r l d` under B.
- `ls -A hello-world` should list only `hello.sh`.
- `git ls-files -s hello-world` should show mode `100755`.
- `head -1 hello-world/hello.sh` should print `#!/bin/bash`.
- `git merge-base --is-ancestor 65938b5 origin/main && git merge-base --is-ancestor 9a5bd0b origin/main` should succeed.
- The repo's test gate (`.factory/testing.md`): `pip install -q -e ".[test]" && pytest`. The whole suite must pass, including `tests/test_hello_sh.py`.

## Risk

- RK1: the story duplicates work that is already on `main`. Under A, nothing gets reworked, and the merge request carries only the factory's record. If the developer would rather close SMKL-1 with no merge request at all, that is their decision.
