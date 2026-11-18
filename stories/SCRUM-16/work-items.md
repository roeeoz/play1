# Work-item breakdown — 20261118-233400Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | SCRUM-16: Record the verified hello-world script in CHANGELOG.md and confirm it meets AC1 to AC4 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "SCRUM-16: Record the verified hello-world script in CHANGELOG.md and confirm it meets AC1 to AC4",
    "summary": "**Intent:** deliver SCRUM-16 as a reviewable pull request to `play1`. `hello-world/hello.sh` and its tests already meet every acceptance criterion on `main`, so the only change is one line under `## Unreleased` in `CHANGELOG.md`, which gate PLAY-G4 requires. Before opening the pull request, confirm the script still meets the criteria.\n\n**Owns:** `CHANGELOG.md`, one new line under `## Unreleased`.\n**Consumes, read-only and must stay unchanged:**\n- `hello-world/hello.sh`\n- `tests/test_hello_sh.py`\n- `.github/workflows/ci.yml`\n- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`\n\n**Acceptance criteria:**\n- `CHANGELOG.md` gains exactly one line under `## Unreleased`. It references SCRUM-16 and `hello-world/hello.sh`, follows the existing entry style, and adds no duplicate entry.\n- The pull request diff touches no file other than `CHANGELOG.md`. In particular, `hello-world/hello.sh` keeps git mode `100755` and its two lines (`#!/bin/bash` and `echo \"hello world\"`) with LF line endings.\n- `hello-world/` contains only `hello.sh`, including hidden files: no `.gitkeep`, no README.\n- From the repository root, `./hello-world/hello.sh` runs without a `bash` prefix, writes exactly `hello world\\n` to stdout and nothing to stderr, and exits 0.\n- `pytest` passes in CI at the pull request's head commit, including all tests in `tests/test_hello_sh.py`. The CI `gate` job passes, so there is no `CI_FAIL` file.\n- The pull request description traces back to SCRUM-16.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
