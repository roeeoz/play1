# Work-item breakdown — 20261118-212710Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | SCRUM-3: Harden hello-world tests to check AC1–AC4 exactly as worded (test-only, script unchanged) |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "SCRUM-3: Harden hello-world tests to check AC1–AC4 exactly as worded (test-only, script unchanged)",
    "summary": "**Intent**\nDeliver the SCRUM-3 evidence as a CI-gated pull request. The script already meets the story, so this pull request only tightens `tests/test_hello_sh.py` until each acceptance criterion is checked as the spec words it. The green `pytest` run at the pull request's head commit then confirms AC1–AC4 on `main` (spec assumption A1).\n\n**Owns / Consumes**\n- **Owns:** `tests/test_hello_sh.py`.\n- **Consumes, read-only:**\n  - `hello-world/hello.sh` and the `hello-world/` folder. They must not be modified, renamed, moved or added to.\n  - The existing `.github/workflows/ci.yml` and `pyproject.toml`, unchanged.\n- **Must not touch:**\n  - Anything under `hello-world/`.\n  - CI workflows.\n  - README or documentation files, including `CHANGELOG.md`, unless the developer explicitly allows a changelog line.\n\n**Acceptance criteria**\n- A test runs the script as `./hello-world/hello.sh` from the repository root, without invoking `bash` explicitly. It sets the working directory to the repository root, whatever directory `pytest` was started from. It asserts exit code 0 (AC1, AC3, FR3, FR5).\n- Standard output is asserted to equal exactly `hello world\\n`:\n  - lowercase\n  - no leading whitespace\n  - no trailing space or tab\n  - no second line\n  - no strip-based or loosened comparison\n\n  Error output is asserted to be empty (AC1, AC4, FR4, A2).\n- The folder isolation check counts every entry in `hello-world/`, hidden files included. It fails if anything other than `hello.sh` is present (AC2, FR1, FR2).\n- The existing checks still pass:\n  - the shebang check: line 1 is exactly `#!/bin/bash` (AC3)\n  - the executable-bit check (AC3)\n- Existing tests may be refined, but none is removed, and coverage of exit code, output, error output, shebang, executable bit and isolation stays in place.\n- `git diff main -- hello-world/` is empty, and running `./hello-world/hello.sh` still prints `hello world`.\n- `python -m pytest` passes the full suite locally, and the pull request's CI `pytest` and `gate` jobs are green at its head commit.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
