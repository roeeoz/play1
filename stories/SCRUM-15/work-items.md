# Work-item breakdown — 20261118-232921Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Record the hello-world bash script for SCRUM-15 in CHANGELOG.md |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Record the hello-world bash script for SCRUM-15 in CHANGELOG.md",
    "summary": "**Intent:** Deliver SCRUM-15 by recording the existing `hello-world/hello.sh` in the repository change record, as the repository gate requires (FR6, rule 4 / `PLAY-G4`). The script already on `main` is kept as the delivery (FR1–FR5). The existing `tests/test_hello_sh.py`, which CI runs, verifies it.\n\n**Owns:** `CHANGELOG.md`, adding one line under `## Unreleased`.\n**Consumes (read-only, must not be modified):** `hello-world/hello.sh`, `tests/test_hello_sh.py`, `.github/workflows/ci.yml`.\n\n**Acceptance criteria:**\n- `CHANGELOG.md` has exactly one new line under `## Unreleased`. It names SCRUM-15 and `hello-world/hello.sh`, says the script prints `hello world`, and follows the style of the existing entries. No other line in the file changes.\n- The diff touches nothing in `hello-world/` or `tests/`, adds no README or other documentation file, and makes no CI change.\n- Running `./hello-world/hello.sh` from the repo root without `bash` in front prints exactly `hello world` plus one terminating newline, with no other characters, whitespace or lines, writes nothing to stderr, and exits 0.\n- `hello-world/` contains only `hello.sh`. Its first line is exactly `#!/bin/bash` and git records it as `100755`.\n- `pytest` passes, including all tests in `tests/test_hello_sh.py`. The repository gate reports no `PLAY-G4` blocker.\n- The PR description traces to SCRUM-15. It says the script and its tests were added earlier (WI-220A63-1) and already meet acceptance criteria 1–4, so this PR adds only the change record.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
