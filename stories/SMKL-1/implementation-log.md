# SMKL-1 — implementation log

## What was built

One new file, `hello-world/hello.sh` (git mode `100755`), exactly as the approved plan specifies:

```bash
#!/bin/bash
printf 'hello world'
```

It uses `printf` instead of `echo`, so standard output is exactly the 11 bytes `hello world` with no trailing newline (AC4). In a terminal, the shell prompt therefore appears right after the text. Nothing else in the repository changed: no test, no CI change, no changelog.

Commit: `SMKL-1: add hello-world/hello.sh hello world bash script` on `halo/feat/smkl-1-20261127-213539`.

## Departures from the plan

None.

## Verification (run locally on macOS before committing)

| Check | Result |
|---|---|
| `./hello-world/hello.sh` (no `bash` prefix) | printed `hello world`, exit 0 (AC1, AC3) |
| `./hello-world/hello.sh \| od -c` | `h e l l o   w o r l d`, no `\n` (AC4) |
| `./hello-world/hello.sh \| wc -c` | `11` |
| `ls -A hello-world` | `hello.sh` only (AC2) |
| `head -1 hello-world/hello.sh` | `#!/bin/bash` (AC3) |
| `git ls-files -s hello-world/hello.sh` | mode `100755` (AC3) |
| `bash -n`, `shellcheck` | clean, no findings |
| `pip install -e ".[test]" && pytest` (Python 3.14 venv) | 118 passed |

CI runs the same `pytest` on Python 3.12. Its result at the head commit is the authoritative one.

## Known open items for the reviewer

- **The repo layout gate will report blocker `PLAY-G4`.** The gate's rule 4 (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) requires every MR to touch `CHANGELOG.md`. The story puts documentation files out of scope, and the approved plan chose not to add one. If you want the gate to pass, approve a root `CHANGELOG.md` holding `## Unreleased` and `- Add hello-world/hello.sh, a minimal hello world bash script (SMKL-1).` It sits outside `hello-world/`, so AC2 still holds.
- **No automated regression test.** The approved plan left one out, so CI will not catch a later change that breaks the exact output.
- **Not verified:** running on Linux or on Windows. `/bin/bash` is assumed to exist wherever the script runs.
