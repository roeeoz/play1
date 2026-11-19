# Work-item breakdown — 20261119-023627Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Verify hello-world/hello.sh against the four scenarios and record it in CHANGELOG.md |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Verify hello-world/hello.sh against the four scenarios and record it in CHANGELOG.md",
    "summary": "**Intent:** `hello-world/hello.sh` already exists on `main` and meets the story (spec A1). This PR confirms it still meets all four acceptance scenarios and adds the `CHANGELOG.md` line the play1 layout gate requires on every PR (spec A3). play1 owns it because the script, its test and the changelog all live there.\n\n**Owns:** `CHANGELOG.md` (one new bullet under `## Unreleased`). `hello-world/hello.sh` only if verification finds a criterion unmet.\n**Consumes (read-only):** `hello-world/hello.sh`, `tests/test_hello_sh.py`, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, `.factory/testing.md`, `.github/workflows/ci.yml`.\n\n**Acceptance criteria:**\n- Running `./hello-world/hello.sh` from the repo root (without `bash` in front) prints exactly `hello world` followed by one newline (12 bytes, `hello world\\n`), writes nothing to stderr and exits 0.\n- The first line of `hello-world/hello.sh` is exactly `#!/bin/bash` and git tracks the file as mode `100755`.\n- `ls -A hello-world` lists only `hello.sh`; the PR adds no file under `hello-world/`.\n- If all of the above already hold, the diff makes no change under `hello-world/`. If one fails, only `hello-world/hello.sh` is fixed to meet it.\n- `CHANGELOG.md` gains exactly one bullet under `## Unreleased`, after the existing bullets, in the existing style, keyed `SCRUM-26`, naming `hello-world/hello.sh` as the script that prints `hello world`.\n- No new test, README, CI workflow change or extra script is added. `tests/test_hello_sh.py` is unchanged and `pytest` passes after `pip install -e \".[test]\"` on Python 3.12.\n- No `CI_FAIL` file is added, and the diff passes play1 layout gate rules 1–4.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
