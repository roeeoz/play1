# SMKL-2 — Implementation log

## What was built
Commit `ca6d80e` on `halo/feat/smkl-2-20261127-180526`:

- `hello-world/hello.sh` (mode `100755`), two lines:
  ```bash
  #!/bin/bash
  printf 'hello world'
  ```
- `CHANGELOG.md` at the repo root, holding one entry under `## Unreleased` for SMKL-2.

The plan was approved as written (`approval.json`, plan unchanged since `50fa690`), so this is
decision A: the changelog is added because the repo gate's rule 4 (`PLAY-G4`) blocks any pull
request that leaves `CHANGELOG.md` untouched. This is the one approved exception to the story's
"no documentation files" scope. `hello-world/` holds only `hello.sh`.

Nothing departs from the plan.

## Checks run (macOS, from the repo root)
| Check | Result |
|---|---|
| `./hello-world/hello.sh; echo "exit=$?"` (AC1, AC3: runs directly through the shebang) | `hello world`, `exit=0` |
| Output compared byte for byte with `printf 'hello world'` via `od -c` (AC4) | equal; `wc -c` = 11 |
| `ls -A hello-world` (AC2) | `hello.sh` only |
| `head -1 hello-world/hello.sh` | `#!/bin/bash` |
| `git ls-tree HEAD hello-world/` | `100755 … hello.sh` |
| `bash -n` and `shellcheck` | clean |
| `pytest` (fresh venv, `pip install -e ".[test]"`) | 118 passed |
| Diff against `origin/bench/two-lines/smoke` | `CHANGELOG.md`, `hello-world/hello.sh`, plus the plan folder |

Security checklist: no secrets, no personal data, no SQL, no network, no dependencies.

## Not verified
- Not run on Windows or on a system without `/bin/bash`.
- The repo gate (`mr-gate`) and GitHub CI run on the merge request, not here. Their result there is
  the record.

## Note for users of the script
The output has no trailing newline (the story requires no trailing whitespace), so in a terminal
the prompt appears straight after `hello world`.
