# Work-item breakdown — תסריט QA שמדפיס "c" ומסתיים בהצלחה

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | PLAY-165: add qa/20261109-s6/c.sh that prints "c" and exits 0 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "PLAY-165: add qa/20261109-s6/c.sh that prints \"c\" and exits 0",
    "summary": "**Intent:** Add the epic's only deliverable: an executable bash script at `qa/20261109-s6/c.sh` that prints exactly `c` and exits 0. Also add the single CHANGELOG line required by repo-gate rule PLAY-G4. Everything lives in roeeoz/play1, so this is one PR based on `qa-20261109-s6-base`.\n\n**Owns:**\n- `qa/20261109-s6/c.sh` (new file, in the new directory `qa/20261109-s6/`)\n- one appended line at the end of `## Unreleased` in `CHANGELOG.md`, after the PLAY-156 entry and in the same style\n\n**Consumes, read-only:** `qa/s3-a.sh` and `qa/s3-hello.sh` as conventions, `.github/workflows/ci.yml`, and the repo-gate rules. Must not modify anything under `src/`, `tests/` or `.github/`, `pyproject.toml`, or any other existing file. No new test file.\n\n**Acceptance criteria:**\n1. `bash qa/20261109-s6/c.sh` with no arguments, run from the repo root:\n   - writes exactly the 2 bytes `c` + LF to stdout, with no CR and no other output\n   - writes nothing to stderr\n   - exits with code 0\n2. `bash qa/20261109-s6/c.sh --help`, and any other arguments, produce the identical stdout `c\\n`, empty stderr and exit code 0, with no help text.\n3. The file:\n   - starts with the shebang `#!/bin/bash`\n   - uses LF line endings\n   - is stored in git as mode `100755`, as shown by `git ls-files -s qa/20261109-s6/c.sh`\n   - also runs directly as `./qa/20261109-s6/c.sh` with the same output\n4. Apart from the `stories/PLAY-165/` planning docs, the PR diff contains only:\n   - `qa/20261109-s6/c.sh`, added\n   - `CHANGELOG.md`, with exactly one line added under `## Unreleased` that names PLAY-165 and `qa/20261109-s6/c.sh`\n   No other file is modified or deleted.\n5. Required CI is green:\n   - the `test` job (pytest) passes\n   - the `gate` job passes, and no `CI_FAIL` file is present\n   - repo-gate rules 2, 3 and 4 are satisfied\n6. `qa/s3-a.sh`, `qa/s3-hello.sh` and the console scripts `pdf-extract`, `testbed-num-summary`, `testbed-hello` and `guestbook` behave and print exactly as before. The PR description records that these were run manually.\n7. The PR description:\n   - cites PLAY-165 and the QA-20261109-S6 Epic PRD (Confluence pageId 33980417)\n   - shows manual runs of the new script with no arguments and with `--help`, including the exit codes and the file mode\n   - notes that the CHANGELOG line departs deliberately from the Epic PRD's R4 and §8, as decided in the story spec\n   - states that the `stories/PLAY-165/` files are planning docs, not product files\n8. The script, the PR and the commit messages contain no secrets, credentials or personal data.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
