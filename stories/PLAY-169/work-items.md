# Work-item breakdown — סקריפט הבדיקה a מדפיס "a" ומסתיים בהצלחה

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261109-s6/a.sh, which prints "a" and exits 0, plus its CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/20261109-s6/a.sh, which prints \"a\" and exits 0, plus its CHANGELOG entry",
    "summary": "**Intent:** Deliver the epic's only product change: a standalone script that the PO and dev team run from the command line to get exactly the line `a` and exit code 0, plus the one `CHANGELOG.md` line that the repository's merge gate (PLAY-G4) requires. It follows the existing `qa/` scripts. Its pull request goes into `qa-20261109-s6-base`.\n\n**Owns:** the new file `qa/20261109-s6/a.sh` (this also creates the folder `qa/20261109-s6/`); one appended bullet under `## Unreleased` in `CHANGELOG.md`.\n**Consumes (read-only):** `qa/s3-a.sh` and `qa/s3-hello.sh` as style models; the existing `CHANGELOG.md` entry format; `stories/PLAY-169/*` (factory documents, allowed in the PR).\n\n**Acceptance criteria:**\n1. Running `qa/20261109-s6/a.sh` directly from the repository root, with no arguments, writes exactly the bytes `a` followed by one newline to stdout. There is no other stdout output and nothing on stderr.\n2. The command exits with status 0. The same output and status hold for `sh qa/20261109-s6/a.sh`.\n3. The file starts with a POSIX shebang (`#!/bin/sh`) and has git mode 100755 in the index. It has a short purpose comment like the existing `qa/` scripts and does not copy the stale \"called by qa/s3-b.sh\" comment.\n4. `CHANGELOG.md` gets exactly one new bullet under `## Unreleased` recording the new script, in the same style as the existing entries (for example ``- PLAY-169: add `qa/20261109-s6/a.sh`, a helper script that prints `a`.``). No other line of `CHANGELOG.md` changes.\n5. The PR's file list contains only `qa/20261109-s6/a.sh`, the `CHANGELOG.md` change, and documents under `stories/PLAY-169/`. No other file is added, changed or deleted: no tests, no README or other documentation, no `qa/20261109-s6/c.sh`, no edits to existing `qa/` scripts, and no package code.\n6. The existing GitHub `test` job (pip install, then pytest) and `gate` job pass on the PR. No `CI_FAIL` file is added.\n7. The PR description names PLAY-169 and the Epic PRD (Confluence page 34111489). Neither the PR nor the script contains secrets or personal data.\n8. The change is far below G3's 300-line limit (a few product lines).",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
