# Work-item breakdown — 20261118-232451Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Confirm hello-world/hello.sh meets SCRUM-14 and record it in CHANGELOG.md |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Confirm hello-world/hello.sh meets SCRUM-14 and record it in CHANGELOG.md",
    "summary": "**Intent:** Deliver SCRUM-14 on play1. The existing `hello-world/hello.sh` already meets all four acceptance criteria, and the existing tests check them, so the only change is the `CHANGELOG.md` line that rule `PLAY-G4` requires. Do not rewrite the script (FR5 / A1).\n\n**Owns:** `CHANGELOG.md`, adding one line under `## Unreleased`.\n**Consumes (read-only, must remain unchanged):** `hello-world/hello.sh`, `tests/test_hello_sh.py`, `.github/workflows/ci.yml`.\n\n**Acceptance criteria:**\n- `CHANGELOG.md` has one new line under `## Unreleased` that names SCRUM-14 and `hello-world/hello.sh`, in the existing `- <KEY>: ...` format. No other changelog entries change.\n- `hello-world/` still contains only `hello.sh` (no README, no dot-files added), and the file's git mode stays 100755.\n- From the repository root, `./hello-world/hello.sh` (without `bash`) writes exactly `hello world` followed by a single newline to stdout. It writes nothing to stderr and exits 0.\n- Line 1 of `hello.sh` is `#!/bin/bash`, and the script content is byte-for-byte unchanged from `main`.\n- `pytest` passes in full, including all tests in `tests/test_hello_sh.py`.\n- The PR adds no `CI_FAIL` file, no CI changes and no extra scripts or documentation files. The PR description states that it confirms the existing script meets the SCRUM-14 acceptance criteria.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
