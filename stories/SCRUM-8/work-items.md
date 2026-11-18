# Work-item breakdown — 20261118-221925Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Confirm hello-world/hello.sh meets the spec and add a test that git stores it as executable |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Confirm hello-world/hello.sh meets the spec and add a test that git stores it as executable",
    "summary": "**Intent**\nMake sure `main` carries a `hello-world/hello.sh` that meets all four acceptance criteria. The script already exists: change it only if a criterion fails. Add one test that checks git's stored executable bit, so Scenario 3 holds on any checkout and not only on the local filesystem. play1 owns the script and its tests.\n\n**Owns / Consumes**\n- Owns: `hello-world/hello.sh`. Edit it only if a criterion fails, keeping mode `100755` and LF line endings.\n- Owns: `tests/test_hello_sh.py`. Add tests to it; keep all existing tests.\n- Consumes, unchanged: `.github/workflows/ci.yml`, `pyproject.toml`, `.factory/testing.md`.\n\n**Acceptance criteria**\n- Running `./hello-world/hello.sh` from the repo root, without `bash` in front, writes exactly `hello world` plus one newline to stdout. It writes nothing to stderr and exits with code 0.\n- Output exactness:\n  - the text is all lowercase, with a single space;\n  - no leading or trailing spaces;\n  - no lines besides the one.\n- The first line of `hello.sh` is `#!/bin/bash`, and the file uses LF line endings.\n- `git ls-files -s hello-world/hello.sh` reports mode `100755`, and a pytest test asserts this from git, not only from the filesystem.\n- `hello-world/` contains only `hello.sh`.\n- Nothing else is added or changed. In particular:\n  - no other scripts;\n  - no README or other documentation;\n  - no CHANGELOG entry;\n  - no CI or workflow changes;\n  - no `CI_FAIL` file.\n- `pytest` passes locally and in the CI `test` job.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
