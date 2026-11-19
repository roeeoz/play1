# Work-item breakdown — 20261119-024453Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Verify hello-world/hello.sh against SCRUM-28 criteria and add CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Verify hello-world/hello.sh against SCRUM-28 criteria and add CHANGELOG entry",
    "summary": "**Intent:** Deliver SCRUM-28 as a verification PR. `hello-world/hello.sh` and `tests/test_hello_sh.py` already exist on `main` and meet all four acceptance criteria (verified at design time); this PR confirms that and adds the `CHANGELOG.md` line the repository gate (`PLAY-G4`) requires. The script or test is changed only if a criterion is found unmet.\n\n**Owns:** `CHANGELOG.md` (one new line under `## Unreleased`); `hello-world/hello.sh` and `tests/test_hello_sh.py` only if a fix is needed.\n**Consumes:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, `.factory/testing.md`, `.github/workflows/ci.yml`.\n\n**Acceptance criteria:**\n- Running `./hello-world/hello.sh` from the repository root (without `bash`) prints exactly `hello world` followed by a single newline to stdout, nothing to stderr, and exits 0.\n- `hello-world/hello.sh` starts with the line `#!/bin/bash` and is tracked in git with mode `100755`.\n- `hello-world/` contains no file other than `hello.sh`; the PR adds no file to that folder and no README/docs for the script.\n- Output is lowercase `hello world` with no leading/trailing whitespace and no additional lines.\n- `tests/test_hello_sh.py` asserts each of the above and passes.\n- `CHANGELOG.md` gains one line under `## Unreleased` describing the `hello-world/hello.sh` script (SCRUM-28), in the style of existing entries.\n- `pip install -e \".[test]\" && pytest` passes from the repo root; no `CI_FAIL` file exists at the root; no file outside `CHANGELOG.md` (and, only if a fix was needed, the script/test) is changed.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
