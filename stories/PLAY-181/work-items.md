# Work-item breakdown — סקריפט שמדפיס "hello s3" עם בדיקה אוטומטית שמאשרת את הפלט

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add the src/qa_20261111_s3.py script that prints "hello s3", its pytest output test and a PLAY-181 CHANGELOG line |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add the src/qa_20261111_s3.py script that prints \"hello s3\", its pytest output test and a PLAY-181 CHANGELOG line",
    "summary": "**Intent:** deliver PLAY-181 end to end in `roeeoz/play1`:\n- a standalone script that prints exactly `hello s3`\n- a pytest test, collected by the normal CI test step, that checks what a person running the script sees\n- the CHANGELOG line that layout gate rule 4 requires\n\n**Owns:**\n- `src/qa_20261111_s3.py` (new)\n- `tests/test_qa_20261111_s3.py` (new)\n- one new line under `## Unreleased` in `CHANGELOG.md`, placed after the existing PLAY-175 line and in the same style\n\n**Consumes (read-only):**\n- `pyproject.toml` (existing `testpaths` and the `test` extra)\n- `.github/workflows/ci.yml`\n- existing subprocess-style script tests, as a pattern (`tests/test_qa_s3_greeting.py`, `tests/test_qa_20261109_s1_a.py`)\n\n**Must not modify:**\n- `pyproject.toml`\n- `.github/workflows/ci.yml`\n- anything under `qa/`, including `qa/20261110-s3/*`\n- `src/testbed_utils`, `src/guestbook`\n- any existing test\n- any existing CHANGELOG line\n\n**Acceptance criteria:**\n- Running `python src/qa_20261111_s3.py` with no arguments and no input writes exactly `hello s3` plus one newline to stdout, writes nothing to stderr and exits with code 0.\n- Importing the module does not print anything. It prints only when run as a script.\n- The script is a standalone module: no package, no `[project.scripts]` entry, no `--help`, no public function. It uses only syntax that runs on CPython 3.10 and later.\n- The test runs the script as a separate process with the interpreter running the tests and does not import it. It finds the script relative to the test file, so it does not depend on the current directory. It asserts exit code 0, stdout exactly `hello s3\\n` and empty stderr.\n- The test fails if the printed text changes (for example `hello s4`), if an extra line appears or if the trailing newline is missing. Confirm this by hand before opening the PR.\n- The test uses no network, clock or files outside the repo, uses a subprocess timeout and finishes in under 1 second.\n- Plain `pytest` from the repo root, with no arguments and no config changes, collects and passes the new test.\n- All previously passing tests still pass, and the full test step finishes in under 60 seconds.\n- Excluding `stories/PLAY-181/`, the PR diff is exactly the two new files plus one added line under `## Unreleased` in `CHANGELOG.md` that mentions PLAY-181 and the added script. No dependency is added, and no existing line or file changes.\n- No file is larger than 200 KB, no new shell script is added and no `CI_FAIL` file exists at the repo root.\n- All required checks are green, including the layout gate.\n- The PR description:\n  - cites story PLAY-181 and the epic PRD \"QA-20261111-S3 hello s3 script\" (Confluence `pageId=36798465`)\n  - reports the result of running the new test\n  - notes the agreed move from the epic's `qa/` paths to `src/` and `tests/`, plus the added CHANGELOG line",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
