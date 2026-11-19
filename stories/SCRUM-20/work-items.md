# Work-item breakdown — 20261119-012037Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Lock in hello-world/hello.sh acceptance: run-as-documented and git-mode tests, CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Lock in hello-world/hello.sh acceptance: run-as-documented and git-mode tests, CHANGELOG entry",
    "summary": "**Intent:** `hello-world/hello.sh` already exists on `main` and meets the spec (FR1–FR5); this PR keeps it unchanged, closes the two verification gaps in its acceptance suite, and records the delivery in `CHANGELOG.md` so gate PLAY-G4 passes. play1 owns the script, its tests and its changelog.\n\n**Owns:** `tests/test_hello_sh.py` (extend), `CHANGELOG.md` (one bullet under `## Unreleased`).\n**Consumes (read/execute only, must not change):** `hello-world/hello.sh`; CI `test` job in `.github/workflows/ci.yml` (no change).\n\n**Acceptance criteria:**\n- `hello-world/hello.sh` is byte-for-byte unchanged and still tracked as mode `100755`; `hello-world/` contains no file other than `hello.sh`; no other shell script is added anywhere.\n- A test runs the script exactly as the spec states — `./hello-world/hello.sh` with the repository root as working directory, without invoking `bash` — and asserts exit code 0, stdout exactly `hello world\\n` (lowercase, no leading/trailing whitespace, one line), and empty stderr.\n- A test asserts that git tracks `hello-world/hello.sh` with executable mode `100755`; where no git checkout is available the test is skipped, not failed.\n- The existing checks in `tests/test_hello_sh.py` (exit 0, exact output, empty stderr, shebang `#!/bin/bash` on line 1, executable bit, folder holds only `hello.sh`) remain and pass.\n- `CHANGELOG.md` gains exactly one bullet under `## Unreleased`, in the existing `- <KEY>: <description>` style, keyed `SCRUM-20`, describing the hello-world script delivery; no other changelog lines change.\n- `pip install -e \".[test]\" && pytest` passes from the repo root; no `CI_FAIL` file; no new docs, README or CI files.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
