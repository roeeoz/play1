# Work-item breakdown — הרצת סקריפט A מדפיסה A

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | PLAY-156: add qa/s3-a.sh that prints "A" (+ CHANGELOG entry) |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "PLAY-156: add qa/s3-a.sh that prints \"A\" (+ CHANGELOG entry)",
    "summary": "**Intent:** Add the executable POSIX shell script `qa/s3-a.sh`. Run from the repo root, it prints exactly one line, `A`, and exits 0. It is the script PLAY-157 will call by path. Add the CHANGELOG release line that the repo's mr-gate (PLAY-G4) requires. The script follows the `qa/s3-hello.sh` style: shebang, purpose comment, one printf.\n\n**Owns / Consumes:**\n- Owns (creates): `qa/s3-a.sh`.\n- Owns (edits): one new line under `## Unreleased` in `CHANGELOG.md`, after the PLAY-114 line.\n- Consumes (read-only, must not change): `qa/s3-hello.sh`, `tests/`, `.github/workflows/ci.yml`, `pyproject.toml`.\n- No new automated test (PO decision Q1). No docs or `--help` support.\n\n**Acceptance criteria:**\n1. Running `qa/s3-a.sh` from the repo root writes exactly `A` plus a newline to stdout: no other characters, no CR, no extra lines. stderr is empty and the exit code is 0.\n2. The file starts with a shebang and is stored in git as executable, mode 100755 in `git ls-files -s qa/s3-a.sh`. It can be run directly by path, by a user or from another shell script.\n3. `qa/s3-hello.sh` is unchanged and still prints `hello`.\n4. `CHANGELOG.md` has a new line under `## Unreleased` describing the PLAY-156 addition of `qa/s3-a.sh`, so the PLAY-G4 gate passes.\n5. The repo's required CI checks (`test` running pytest, and `gate`) pass on the PR. No `CI_FAIL` file is added, and nothing in `tests/`, `.github/` or `pyproject.toml` changes.\n6. The PR description references PLAY-156 and the Epic PRD (Confluence pageId 33292289). It shows a manual run of `qa/s3-a.sh` with its output and exit code, plus the file mode. No secrets appear in the code or commit messages.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
