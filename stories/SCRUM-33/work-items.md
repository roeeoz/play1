# Work-item breakdown — 20261119-040915Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Record SCRUM-33 hello-world script delivery in CHANGELOG |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Record SCRUM-33 hello-world script delivery in CHANGELOG",
    "summary": "**Intent:** `hello-world/hello.sh` already meets SCRUM-33 on `main` (spec FR1–FR4, verified: mode 100755, `#!/bin/bash`, prints `hello world\\n`, exit 0, folder holds only `hello.sh`; `tests/test_hello_sh.py` passes). Per spec FR5/A1 this PR keeps the script and test unchanged and adds the `CHANGELOG.md` line the repo gate requires, recording SCRUM-33 as delivered by the existing script.\n\n**Owns:** one new bullet under `## Unreleased` in `CHANGELOG.md`.\n**Consumes (read-only, must not change):** `hello-world/hello.sh`, `tests/test_hello_sh.py`.\n\n**Acceptance criteria:**\n- `CHANGELOG.md` gains exactly one new bullet under `## Unreleased`, appended after the existing bullets, in the existing style (`- SCRUM-33: …`), stating SCRUM-33 is delivered by the existing `hello-world/hello.sh` (prints `hello world`); existing entries are unchanged.\n- The diff touches no file other than `CHANGELOG.md`: `hello-world/hello.sh` stays byte-identical with mode 100755, and no file is added to `hello-world/` or `tests/`.\n- From the repo root, `./hello-world/hello.sh` (without invoking bash) writes exactly `hello world\\n` to stdout, nothing to stderr, and exits 0; `$(./hello-world/hello.sh)` equals `hello world`.\n- `pip install -e \".[test]\" && pytest` passes, including all of `tests/test_hello_sh.py` (output, exit code, empty stderr, shebang `#!/bin/bash`, executable bit, `hello-world/` contains only `hello.sh`).\n- The play1 repo gate passes (rule 4 satisfied, no `PLAY-G4` blocker) and no `CI_FAIL` file exists at the repo root.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
