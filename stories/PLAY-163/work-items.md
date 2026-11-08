# Work-item breakdown — הרצת התסריט qa/pe-greet.sh מדפיסה "hello pe" ומסתיימת בהצלחה

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/pe-greet.sh (prints "hello pe", exits 0) and its CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/pe-greet.sh (prints \"hello pe\", exits 0) and its CHANGELOG entry",
    "summary": "**Intent:** Add the epic's single deliverable: a directly runnable POSIX sh script in the existing `qa/` directory that prints exactly `hello pe` followed by one newline and always exits 0. Also add the one `CHANGELOG.md` line that merge-gate rule 4 (PLAY-G4) requires. play1 owns both files.\n\n**Owns:** `qa/pe-greet.sh` (new), and one new line under `## Unreleased` in `CHANGELOG.md`.\n\n**Consumes (read-only, must not change):** `qa/s3-hello.sh` and `qa/s4-greet.sh` as style references, plus the existing `CHANGELOG.md` entry format.\n\n**Out of scope:** tests, `--help` or any options, other docs, CI changes, `src/`, `tests/`.\n\n**Acceptance criteria:**\n1. Running `qa/pe-greet.sh` directly from the repo root, without calling `sh` or `bash` first, writes exactly the bytes `hello pe\\n` to stdout (lowercase, one space, no leading or trailing whitespace, one LF) and exits with code 0.\n2. The script writes nothing to stderr.\n3. `qa/pe-greet.sh --help` and `qa/pe-greet.sh x y` produce the same stdout (`hello pe\\n`), an empty stderr and exit code 0.\n4. The script's first line is `#!/bin/sh`, it uses LF line endings, and git records it as executable (`git ls-files -s qa/pe-greet.sh` shows mode 100755). It follows the neighbouring scripts' shape: shebang, one-line purpose comment, fixed output.\n5. `CHANGELOG.md` gains exactly one line, placed under `## Unreleased`, in the existing style, for example: - PLAY-163: add `qa/pe-greet.sh`, a helper script that prints `hello pe`. The existing PLAY-114 entry and every other line stay unchanged.\n6. The PR's product-file changes are exactly the new `qa/pe-greet.sh` and the one-line addition to `CHANGELOG.md`. There are no tests, no other docs and no other files (plan documents under `stories/PLAY-163/` are platform artifacts).\n7. Regression: after the change, `qa/s3-hello.sh` still prints `hello` and `qa/s4-greet.sh` still prints `hello from s4 (base)`, both exiting 0. All required PR checks (`test`/pytest, `gate`, repo merge gate) are green.\n8. The PR description references story PLAY-163 and the epic PRD PE-20261108 greeting. The script, the changelog line and commit messages contain no secrets, credentials or personal data.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
