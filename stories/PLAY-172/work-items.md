# Work-item breakdown — סקריפט שמדפיס "A"

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261109-s1/a.sh that prints "A", with pytest coverage and a CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/20261109-s1/a.sh that prints \"A\", with pytest coverage and a CHANGELOG entry",
    "summary": "**Intent:** deliver the epic's first script, `qa/20261109-s1/a.sh`. It prints exactly `A` and exits 0 from any working directory. It comes with new automated tests in the existing pytest/CI job, and its path and output are the fixed contract PLAY-173 builds on. All of this belongs in roeeoz/play1, where the `qa/` scripts and their tests live.\n\n**Owns:**\n- `qa/20261109-s1/a.sh` (new, POSIX `#!/bin/sh`, git mode 100755)\n- `tests/test_qa_20261109_s1_a.py` (new)\n- one new line under `## Unreleased` in `CHANGELOG.md` mentioning PLAY-172\n\n**Consumes (read-only):**\n- `qa/s3-a.sh`, which is run by a regression test and must not be modified\n- the existing pytest config and CI workflow, unchanged\n\n**Acceptance criteria:**\n- Running `qa/20261109-s1/a.sh` prints exactly one line, `A` (stdout is exactly `A\\n`), with no other text, empty stderr and exit code 0.\n- Running the script by its absolute path from a working directory other than its own (for example a pytest temporary directory) gives the same stdout `A\\n`, empty stderr and exit 0.\n- The script takes no arguments and reads no files, network, clock or environment variables. It doesn't call or depend on any other `qa/` script or sibling file, so it works the same when copied alone to another directory.\n- The file starts with a shebang line, is committed as executable (git mode 100755) and contains no CR characters. The new tests assert the executable bit, the shebang and the absence of CR characters.\n- A new pytest file under `tests/` covers:\n  - the normal run (stdout, stderr, exit code)\n  - the run from a different directory\n  - the file's shape\n  - a regression check that `qa/s3-a.sh` still prints exactly `A\\n` and exits 0\n- The new tests run in the existing CI `test` job (`pytest` from the repo root) with no change to `ci.yml` or `pyproject.toml`. Each subprocess call uses a timeout, and nothing depends on the network or the clock.\n- `CHANGELOG.md` gains exactly one new line under `## Unreleased` that mentions PLAY-172 and `qa/20261109-s1/a.sh`. No other line in any existing file changes.\n- No existing file is modified or deleted, including `qa/s3-a.sh`, `qa/s3-hello.sh`, `hello-world/hello.sh` and the existing tests. Those scripts print exactly what they printed before.\n- `pytest` passes locally and in CI, with all existing and new tests green, and the test job finishes in under 60 seconds.\n- No `--help` support, no `b.sh` and no new dependencies.\n- The PR description references PLAY-172 and the epic PRD.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
