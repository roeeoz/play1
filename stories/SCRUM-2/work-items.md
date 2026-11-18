# Work-item breakdown — 20261118-212149Z Hello world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Assert strict hello-world folder isolation (including hidden entries) and record AC evidence |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "86d449d4-e5db-42c9-8d61-17b798bdd7e2",
    "title": "Assert strict hello-world folder isolation (including hidden entries) and record AC evidence",
    "summary": "**Intent:** `main` already meets SCRUM-2. This PR closes the one coverage gap. AC2 (\"the only file present is `hello.sh`\") is currently tested with dotfiles skipped, so a hidden file or a subdirectory in `hello-world/` would pass the gate. The PR adds a strict isolation test in a new test module, and its description records the evidence for each AC. play1 owns this because the script, the tests and the gate all live there.\n\n**Owns:** one new pytest module under `tests/` for the strict folder-isolation check, for example `tests/test_hello_world_folder.py`; the implementer picks the name.\n\n**Consumes (read-only, must stay byte-identical, with the same git mode):**\n- `hello-world/hello.sh` (100755)\n- `tests/test_hello_sh.py`\n- `pyproject.toml`\n- `.github/workflows/ci.yml`\n- `.factory/testing.md`\n- `CHANGELOG.md`\n\n**Acceptance criteria:**\n- The new test passes only when `hello-world/` exists at the repo root and its complete listing, including hidden entries and subdirectories, is exactly `hello.sh`.\n- The new test fails if any extra entry is present, for example a dotfile or a README.\n- The full gate passes at the PR head: `pip install -e \".[test]\"` then `pytest` on Python 3.12, with the 6 existing tests in `tests/test_hello_sh.py` and the new test all green. The CI `test` job at the PR head is the authoritative result.\n- Running `./hello-world/hello.sh` from the repo root, without a `bash` prefix, writes exactly `hello world` plus one trailing newline to stdout, with no leading or trailing spaces and no extra lines. It writes nothing to stderr and exits with code 0. The PR description records a run that shows this.\n- The diff touches no file under `hello-world/`. `hello.sh` keeps its content, its `#!/bin/bash` first line and git mode 100755.\n- The diff does not change `tests/test_hello_sh.py`, `.github/workflows/`, `CHANGELOG.md` or `pyproject.toml`, adds no README, and adds no `CI_FAIL` file.\n- The PR description maps AC1–AC4 to the tests that assert each one: the existing tests for AC1, AC3 and AC4, and the existing test plus the new strict test for AC2.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
