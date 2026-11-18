# Work-item breakdown — 20261118-222425Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Lock in hello-world/hello.sh against AC1–AC4 through the existing pytest gate |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Lock in hello-world/hello.sh against AC1–AC4 through the existing pytest gate",
    "summary": "**Intent:** deliver the story's script in `play1`. It already exists on `main`, so this ticket confirms it meets every requirement and keeps it exactly that way. Only if a criterion is found to fail does the ticket correct the script or its test. `play1` owns this because the script, its tests and the merge gate all live there. Per spec assumption A1, the expected code diff is empty. Do not re-create, reformat or re-mode the script.\n\n**Owns:**\n- `hello-world/hello.sh` (and the `hello-world/` folder as a whole)\n- `tests/test_hello_sh.py`\n\n**Consumes (read-only):**\n- `.github/workflows/ci.yml`\n- `pyproject.toml` (pytest config)\n- `.factory/testing.md`\n\n**Must not:**\n- add any file, including dotfiles, to `hello-world/`;\n- add other scripts, documentation files or CI changes.\n\n**Acceptance criteria:**\n- **FR1 / AC2:** `hello-world/` exists at the repo root and its only file is `hello.sh`, checked with `git ls-files hello-world` and `ls -A hello-world`.\n- **FR2 / AC3:** line 1 of `hello-world/hello.sh` is exactly `#!/bin/bash`.\n- **FR3 / AC3:** `hello.sh` has git mode `100755`, and `./hello-world/hello.sh` runs from the repo root without `bash`.\n- **FR4 / AC1 / AC4:** running `./hello-world/hello.sh`:\n  - writes exactly `hello world` followed by one newline (12 bytes) to stdout;\n  - adds no leading whitespace, trailing spaces or extra lines;\n  - writes nothing to stderr;\n  - exits with code 0.\n- `tests/test_hello_sh.py` covers each criterion above, and `pytest` passes on the work branch, including the CI `test` job and `gate` job.\n- The pull request description lists the commands run and their output as evidence for each criterion.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
