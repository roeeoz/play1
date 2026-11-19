# Work-item breakdown — 20261119-012944Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Confirm hello-world/hello.sh against SCRUM-22 criteria and record it in CHANGELOG |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Confirm hello-world/hello.sh against SCRUM-22 criteria and record it in CHANGELOG",
    "summary": "**Intent:** Deliver SCRUM-22 on play1: keep the existing `hello-world/hello.sh` (already on `main` from `65938b5`, mode `100755`) as the deliverable, verify it against Scenarios 1–4, and add the `CHANGELOG.md` line the repository gate (`PLAY-G4`) requires. The script is changed only if a check fails.\n\n**Owns:** `hello-world/hello.sh` (left unchanged unless a check fails; must stay mode `100755`, LF endings, sole file in `hello-world/`); one new line under `## Unreleased` in `CHANGELOG.md`.\n**Consumes (do not modify):** `tests/test_hello_sh.py` (existing automated checks), `.github/workflows/ci.yml`, `.factory/testing.md`, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`.\n\n**Acceptance criteria:**\n- Running `./hello-world/hello.sh` from the repo root prints exactly `hello world` followed by one newline, writes nothing to stderr, and exits 0; `$(./hello-world/hello.sh)` equals `hello world`.\n- Running `cd hello-world && ./hello.sh` gives the same output and exit code.\n- The first line of `hello-world/hello.sh` is exactly `#!/bin/bash`, and the script runs directly without `bash` in front.\n- `git ls-files -s hello-world/` shows only `hello-world/hello.sh` with mode `100755`, and `ls -A hello-world/` lists only `hello.sh` (no dot-files, no README or other files).\n- `CHANGELOG.md` gains one line under `## Unreleased` naming SCRUM-22 and the hello-world script; no other documentation file is added.\n- No new scripts, tests, or CI jobs are added; `pip install -e \".[test]\"` then `pytest` passes (including `tests/test_hello_sh.py`), and no `CI_FAIL` file exists.\n- The PR description records the output of the checks above as evidence for Scenarios 1–4.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
