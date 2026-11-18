# Work-item breakdown — 20261118-222915Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Make the hello-world folder-isolation test count hidden files (AC2) |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Make the hello-world folder-isolation test count hidden files (AC2)",
    "summary": "**Intent.** Close the only gap found when checking SCRUM-10 against `main`. The test for \"the `hello-world` folder holds only `hello.sh`\" currently skips hidden files, so AC2 is not fully enforced in CI. Tighten it so every entry in the folder counts, hidden ones included. The script itself already meets AC1–AC4 and must stay byte-for-byte and mode-for-mode the same.\n\n**Owns:** `tests/test_hello_sh.py`.\n**Consumes (read-only, must not be modified):** `hello-world/hello.sh`. Its content stays `#!/bin/bash` / `echo \"hello world\"` and its git mode stays `100755`. Also consumed: the existing pytest setup (`pyproject.toml` test extras) and `.github/workflows/ci.yml`.\n**Must not touch:** anything inside `hello-world/` (no added files), `qa/`, CI workflows, docs or `CHANGELOG.md`.\n\n**Acceptance criteria**\n- The folder-isolation test passes only when `hello-world/` holds exactly one entry, `hello.sh`, counting hidden entries (names starting with `.`) and subfolders.\n- The new test is shown to fail when an extra entry exists. For example, with a temporary `hello-world/.gitkeep` it fails, and it passes again once the file is removed. The PR description records this result, and the repo is left with no extra file.\n- The existing checks stay in place and keep passing unchanged:\n  - running `./hello-world/hello.sh` directly, without `bash`, prints exactly `hello world\\n`, exits 0 and writes nothing to stderr;\n  - the first line is `#!/bin/bash`;\n  - the file has the owner-executable bit.\n- `git ls-tree HEAD hello-world/` still shows exactly one entry, `100755 … hello-world/hello.sh`, and the PR diff contains no change under `hello-world/`.\n- The repo's full required check, `pip install -e \".[test]\" && pytest` (Python 3.12), passes. No `CI_FAIL` file exists at the repo root, so the `gate` job stays green.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
