# Work-item breakdown — 20261118-211648Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Tighten hello-world tests so they check every SCRUM-1 acceptance criterion literally |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Tighten hello-world tests so they check every SCRUM-1 acceptance criterion literally",
    "summary": "**Intent:** `main` already ships `hello-world/hello.sh` and meets the story. This ticket turns the existing `pytest` coverage into an exact, literal check of all four acceptance criteria. CI at the pull request's head then serves as the evidence that the story is done. It changes test code only and leaves the script and its folder untouched.\n\n**Owns:** `tests/test_hello_sh.py`.\n**Consumes (read-only, must not be modified):**\n- `hello-world/hello.sh` and the `hello-world/` folder\n- `pyproject.toml`\n- `.github/workflows/ci.yml`\n\n**Acceptance criteria**\n- **Execution and output (AC1, AC4).** Running `./hello-world/hello.sh` directly (no `bash` prefix) from the repository root:\n  - exits with code 0\n  - writes exactly `hello world\\n` to stdout: lowercase, no leading or trailing spaces or tabs, one line only\n  - writes nothing to stderr\n  - fails the test on any deviation, such as a missing newline, an extra line, different case or added whitespace\n- **Folder isolation (AC2).** The listing of `hello-world/` must be exactly `hello.sh`, hidden entries included. Any other file, subfolder or dotfile fails the test.\n- **Shebang and executable (AC3).**\n  - The first line of `hello.sh` is exactly `#!/bin/bash`.\n  - The file has execute permission on disk.\n  - Git stores it as mode `100755`, so a commit that drops the execute bit fails the test.\n- **Nothing outside the test file changes.**\n  - `hello-world/hello.sh` keeps its content and its `100755` mode exactly as on `main`.\n  - No file is added to `hello-world/`.\n  - No CI, README or CHANGELOG change.\n- **The full gate passes.** The whole `pytest` suite passes locally and in the CI `test` job at the pull request's head commit. The pull request description cites that CI result as the evidence for AC1–AC4.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
