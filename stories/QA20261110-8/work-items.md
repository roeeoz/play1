# Work-item breakdown — הרצת סקריפט qa/20261110-a3/hello.py מדפיסה "hello from a3"

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261110-a3/hello.py that prints "hello from a3" and exits 0 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "3de95313-a662-49a5-b8a0-56b5dd990c4d",
    "title": "Add qa/20261110-a3/hello.py that prints \"hello from a3\" and exits 0",
    "summary": "**Intent:** deliver the epic's only product change: a standalone QA script in `roeeoz/play1` that prints exactly one greeting line and exits successfully, without touching anything else in the package.\n\n**Owns:** `qa/20261110-a3/hello.py` (new file, the only product change).\n**Consumes:** nothing. The script uses the standard library only and imports nothing from the package.\n**Must not modify:** any existing file. That includes `src/`, `tests/`, the existing `qa/` scripts, `pyproject.toml`, `CHANGELOG.md`, docs, version, `.github/` and other config. Do not add tests, `--help` handling or console-script registration.\n\n**Acceptance criteria:**\n1. Running `python qa/20261110-a3/hello.py` from the repo root writes exactly `hello from a3` plus one newline to stdout. There is no leading or trailing whitespace, no blank lines and no other output.\n2. The same run writes nothing to stderr and exits with code 0.\n3. The script ignores arguments, environment variables and files. It reads no input and doesn't respond to `--help`.\n4. The script runs on Python 3.10 or later with no packages installed. It uses only standard-library and built-in features available in 3.10.\n5. The file follows the existing `qa/` script pattern: a `#!/usr/bin/env python3` shebang, a one-line header comment naming epic a3 and story QA20261110-8, git mode `100755`, and ASCII text with LF line endings.\n6. The PR diff contains only the new `qa/20261110-a3/hello.py` plus the factory plan documents under `stories/QA20261110-8/`. No other file is added, changed or deleted.\n7. CI on the PR is green (`test` and `gate`), and the pytest step stays under 60 seconds.\n8. The existing `qa/` scripts print exactly what they printed before:\n   - `qa/20261110-s3/hello.sh` prints `hello s3`\n   - `qa/20261109-s1/a.sh` and `qa/s3-a.sh` each print `A`\n   - `qa/s3-hello.sh` prints `hello`\n9. The PR description:\n   - references story QA20261110-8 and the epic PRD (Confluence page 35487745)\n   - reports the manual run output and exit code, with the Python version used, plus a note that the code was read for 3.10 compatibility\n   - explicitly notes the intended deviation from repo-gate rule `PLAY-G4` (no CHANGELOG line, per spec FR5 and AC3) and from a literal reading of rule 1 (a standalone QA script, not package source), so the reviewer can waive both knowingly",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
