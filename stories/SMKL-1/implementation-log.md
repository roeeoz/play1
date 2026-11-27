# Implementation log — SMKL-1: Hello world bash script in a dedicated folder

## Outcome

**No product change: the script and its tests were already on `main`.** This merge request carries only the story folder (`stories/SMKL-1/`: plan, summary, approval, this log).

- `hello-world/hello.sh` was added to `main` by `65938b5` (WI-220A63-1) and later changed by `9a5bd0b`. Both commits are ancestors of `origin/main`.
- `tests/test_hello_sh.py` on `main` already covers all four acceptance criteria. The plan's AC → test table maps each one.

## Decision applied

The plan left one choice open for the developer: whether the script keeps the trailing newline (AC 4). No ruling was recorded with the approval (`approval.json` has no decision text), so the build applied the plan's default, **option A: keep `echo`**. The script prints `hello world\n`: one line, ended by a newline. `$(./hello-world/hello.sh)` captures exactly `hello world`. If the reviewer wants the literal reading (no trailing byte, option B), the change is line 2 of `hello-world/hello.sh` → `printf 'hello world'`, plus the two `== "hello world\n"` assertions in `tests/test_hello_sh.py` → `== "hello world"`.

## Departures from the plan

None.

## Verification (run locally on macOS, from the repo root, on 2026-11-27)

| Check | Result |
|---|---|
| `./hello-world/hello.sh \| od -c; echo "exit=${PIPESTATUS[0]}"` | `h e l l o   w o r l d \n`, `exit=0` |
| `[ "$(./hello-world/hello.sh)" = "hello world" ]` | true |
| stderr of the script | empty (0 bytes) |
| `ls -A hello-world` | `hello.sh` only |
| `git ls-files -s hello-world` | `100755 … hello-world/hello.sh` |
| `head -1 hello-world/hello.sh` | `#!/bin/bash` |
| `git merge-base --is-ancestor 65938b5 origin/main` and same for `9a5bd0b` | both succeed |
| `pip install -e ".[test]" && pytest` (fresh venv) | 141 passed; `tests/test_hello_sh.py`: 6 passed |
| `CI_FAIL` at repo root | absent |

## Not verified here

- CI's own environment: CI runs Python 3.12 on Linux; the local run used Python 3.14.6 and bash 3.2.57 on macOS. The CI run at the merge request's head is the authoritative result.
- The script under a shell other than bash, or on a system without `/bin/bash` (the story requires `#!/bin/bash`).
