# Work-item breakdown — סקריפט שמדפיס "hello s3" ובדיקה שמוודאת אותו

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261110-s3/hello.sh (prints "hello s3") and its shell test test_hello.sh |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/20261110-s3/hello.sh (prints \"hello s3\") and its shell test test_hello.sh",
    "summary": "**Intent:**\n- Deliver the only story in epic QA-20261110-S3 (PLAY-175) in roeeoz/play1.\n- Add a greeting script that prints exactly `hello s3` followed by one newline and exits 0.\n- Add a shell test that runs the greeting script and passes only when its output and exit code are exactly right.\n- Add the CHANGELOG line that repo-gate rule 4 (`PLAY-G4`) requires.\n\n**Owns:**\n- `qa/20261110-s3/hello.sh` (new)\n- `qa/20261110-s3/test_hello.sh` (new)\n- one new line under `## Unreleased` in `CHANGELOG.md`\n\n**Consumes, read-only:**\n- the existing `qa/` scripts, as the style convention: `#!/bin/sh` with `printf`\n- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (the repo-gate rules)\n- `stories/PLAY-175/*` (the plan documents)\n\n**Must not modify:**\n- `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`\n- `src/`, `tests/`, `pyproject.toml`, `.github/`\n\n**Acceptance criteria:**\n1. Running `qa/20261110-s3/hello.sh` from the command line writes exactly `hello s3` plus one newline to stdout, with no other text, and exits 0. It takes no input. (FR1, AC1)\n2. Both new files start with a shebang, use LF line endings, and are committed as executable: `git ls-files -s qa/20261110-s3` shows mode `100755` for both. (FR2, gate rule 2)\n3. `qa/20261110-s3/test_hello.sh` runs the greeting script directly through its path, never through an explicit interpreter. It exits 0 only when the output is exactly `hello s3` plus one newline and the greeting script's exit code is 0. (FR3, AC2)\n4. The test exits non-zero in each of these cases. (FR4, AC3–AC5)\n   - The text is different, for example `hello`.\n   - The trailing newline is missing, or there are extra trailing newlines.\n   - The text is correct but the script exits 1.\n   - The greeting script is removed.\n   - The greeting script exists but is not executable. The test does not bypass the execute permission.\n5. The test finds the greeting script relative to its own location, and gives the same result when run from the repo root, from `qa/20261110-s3/`, or from an unrelated directory. (FR5)\n6. The test does not use the network or the clock. It creates or modifies no file outside `qa/20261110-s3/`, including no temp files. Two runs in a row on an offline machine both exit 0. (FR6, AC9)\n7. Outside `stories/PLAY-175/`, the PR diff contains only the two new files and one added line under `## Unreleased` in `CHANGELOG.md` that mentions PLAY-175, in the same style as the existing PLAY-172 entry. No existing file under `qa/` changes. (FR7, AC6)\n8. All required CI checks (the pytest `test` job and the `gate` job) are green. The PR is not merged before they are, and only a human reviewer merges it. (AC7)\n9. The PR description cites PLAY-175 and the epic PRD (https://roeeoz.atlassian.net/wiki/pages/viewpage.action?pageId=35192833). It reports a successful run of `qa/20261110-s3/test_hello.sh`, and the failing results of temporary, uncommitted checks for criterion 4. The broken variants are never committed. (FR8, AC8)\n10. No secrets, keys or personal data appear in the files or commit messages, and no new dependency or third-party code is added. The change stays far below 300 changed lines.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
