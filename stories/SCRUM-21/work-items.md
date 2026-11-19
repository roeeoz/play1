# Work-item breakdown — 20261119-012516Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | SCRUM-21: verify hello-world/hello.sh and record it in CHANGELOG.md |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "SCRUM-21: verify hello-world/hello.sh and record it in CHANGELOG.md",
    "summary": "**Intent:** Deliver SCRUM-21 against the existing state of `main`: `hello-world/hello.sh` (mode 100755, added in commit 65938b5) already meets the story, so it is kept unchanged and verified by the existing `tests/test_hello_sh.py`; the PR's only change is the `CHANGELOG.md` line the play1 layout gate requires (rule 4, PLAY-G4).\n\n**Owns:** `CHANGELOG.md` (one new bullet under `## Unreleased`).\n**Consumes (read/run only, must not change):** `hello-world/hello.sh`, `tests/test_hello_sh.py`, `.github/workflows/ci.yml`, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`.\n\n**Acceptance criteria:**\n- `CHANGELOG.md` gains exactly one new bullet under `## Unreleased`, after the existing entries, prefixed `SCRUM-21:` and describing the `hello-world/hello.sh` script that prints `hello world`; existing entries are untouched.\n- The diff touches no other file: `hello-world/hello.sh` keeps its content (`#!/bin/bash` then `echo \"hello world\"`) and git mode `100755`; no new file is added to `hello-world/` or anywhere else; `.github/workflows/ci.yml` is unchanged; no README/docs file is added.\n- Running `./hello-world/hello.sh` from the repo root without `bash` prints exactly `hello world` followed by a single newline, nothing on stderr, and exits 0 (Scenarios 1, 3, 4).\n- `ls hello-world` lists only `hello.sh` (Scenario 2).\n- `pip install -e \".[test]\" && pytest` passes from the repo root, including all tests in `tests/test_hello_sh.py`; no `CI_FAIL` file exists at the root.\n- The play1 layout gate passes (rules 1–4; no PLAY-G4 blocker).",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
