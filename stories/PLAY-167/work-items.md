# Work-item breakdown — סקריפט פרידה שמדפיס "bye", ועם שם גם פרידה אישית

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | PLAY-167: add qa/20261109-s3/bye.sh farewell script and CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "PLAY-167: add qa/20261109-s3/bye.sh farewell script and CHANGELOG entry",
    "summary": "**Intent:**\n- Deliver the whole story in one PR to roeeoz/play1, based on qa-20261109-s3-base.\n- Add an executable bash script that prints `bye`, plus `bye <name>` when a non-empty first argument is given.\n- Add the one CHANGELOG line that the repo-gate (PLAY-G4) requires.\n\n**Owns:**\n- `qa/20261109-s3/bye.sh` (new)\n- One new `- PLAY-167: ...` line under `## Unreleased` in `CHANGELOG.md`, placed after the PLAY-156 line in the same format.\n\n**Consumes, read-only and unchanged:**\n- `qa/20261109-s3/BASE_MARKER.md`, `qa/s3-a.sh`, `qa/s3-hello.sh` and the rest of `CHANGELOG.md`.\n- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`.\n- The existing pytest suite and CI.\n\n**Acceptance criteria:**\n1. Running `qa/20261109-s3/bye.sh` with no arguments prints exactly one line, `bye`, and exits 0.\n2. Running `qa/20261109-s3/bye.sh Alice` prints exactly two lines, `bye` then `bye Alice`, and exits 0.\n3. Running `qa/20261109-s3/bye.sh Alice Bob` prints exactly two lines, `bye` then `bye Alice`. `Bob` doesn't appear anywhere in the output, and the exit code is 0.\n4. Running `qa/20261109-s3/bye.sh --help` prints exactly two lines, `bye` then `bye --help`. No help text appears, and the exit code is 0.\n5. Running `qa/20261109-s3/bye.sh \"\"` prints exactly one line, `bye`, and exits 0.\n6. Running `qa/20261109-s3/bye.sh \"Alice Smith\"` prints exactly two lines, `bye` then `bye Alice Smith`, and exits 0.\n7. A name containing printf metacharacters, such as `%s` or a backslash, or starting with `-`, such as `-n`, is printed literally after `bye `.\n8. In every case the output is exactly the stated lines, each ending in LF, with no other stdout or stderr output.\n9. The first line of the file is exactly `#!/bin/bash`, and the file uses LF line endings.\n10. `git ls-files -s qa/20261109-s3/bye.sh` reports mode `100755`.\n11. Outside `stories/PLAY-167/`, the PR diff contains only the new `qa/20261109-s3/bye.sh` and one added PLAY-167 line under `## Unreleased` in `CHANGELOG.md`.\n12. `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s3/BASE_MARKER.md`, `tests/`, `.github/` and `pyproject.toml` are unchanged, and no `CI_FAIL` file is added.\n13. The script uses no third-party code and no files. No pytest test is added, as the spec requires.\n14. The required play1 CI checks (pytest test job and gate job) pass on the PR, and the test step finishes in under 60 seconds.\n15. The PR description cites PLAY-167 and the epic PRD in Confluence (pageId 34013185).\n16. The PR description shows the manual runs for criteria 1–6, with their output and exit codes.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
