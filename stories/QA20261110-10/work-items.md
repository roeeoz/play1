# Work-item breakdown — הרצת סקריפט שמדפיס "hello from a3"

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261111-a3/hello.sh printing "hello from a3" plus its CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "3de95313-a662-49a5-b8a0-56b5dd990c4d",
    "title": "Add qa/20261111-a3/hello.sh printing \"hello from a3\" plus its CHANGELOG entry",
    "summary": "**Intent:** add the one QA shell script the story asks for, and the single `CHANGELOG.md` line that the play1 repository gate (rule 4 / PLAY-G4) requires. This delivers the whole story (QA20261110-10) in one PR to roeeoz/play1.\n\n**Owns:**\n- `qa/20261111-a3/hello.sh` (new).\n- One appended bullet under `## Unreleased` in `CHANGELOG.md`.\n\n**Consumes (read-only, unchanged):** the existing `qa/` scripts and `tests/`, which serve as the convention reference and regression evidence, and `.github/workflows/ci.yml`.\n\n**Out of scope:**\n- Any test file, including any `test_hello.sh` or pytest file.\n- `--help` or any options.\n- A console-script registration.\n- Docs, version bump, or edits to existing CHANGELOG lines.\n- Anything under `src/`, `tests/`, `pyproject.toml`, `.github/`, `hello-world/`, other `qa/` paths, or `qa/20261110-a3`.\n\n**Acceptance criteria:**\n- Running `sh qa/20261111-a3/hello.sh` with no arguments and no stdin writes exactly `hello from a3` followed by one LF to stdout. It writes nothing to stderr and exits with code 0.\n- Running `./qa/20261111-a3/hello.sh` directly gives the same output and exit code. The file is mode 100755 in git (`git ls-files -s`), and its first line is a `#!/bin/sh` shebang.\n- The script uses only standard POSIX shell. It reads no files, uses no network and needs nothing installed beyond what play1 installs today. It has LF line endings only (no CR) and is far under 200 KB.\n- `CHANGELOG.md` gains exactly one new line under `## Unreleased`, appended at the end of the list. The line describes the new script in the existing entry style and names the story key QA20261110-10. No other CHANGELOG line changes.\n- Apart from the factory plan folder `stories/QA20261110-10/`, the PR diff contains only the new `qa/20261111-a3/hello.sh` and the one-line `CHANGELOG.md` addition.\n- The required CI checks `test` (pytest) and `gate` are green on the PR head.\n- The existing qa scripts produce unchanged output and exit 0. That covers `qa/s3-hello.sh` (`hello`), `qa/s3-a.sh` (`A`), `qa/20261109-s1/a.sh` (`A`), `qa/20261110-s3/hello.sh` (`hello s3`) and `qa/20261110-s3/test_hello.sh` (`PASS`).\n- The PR description:\n  - names story QA20261110-10, \"הרצת סקריפט שמדפיס \"hello from a3\"\", and the epic PRD it came from (Confluence page 35782657);\n  - records the manual evidence: the new script run under `/bin/sh` with no extra installs (AC2), with its output and exit code; and the existing qa scripts' outputs and exit codes (AC3).",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
