# Work-item breakdown — סקריפט שמדפיס "hello aw" ובדיקה אוטומטית שמאשרת את הפלט בכל בקשת שינוי

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261111-aw/hello.sh and a pytest test that checks its exact output |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "3de95313-a662-49a5-b8a0-56b5dd990c4d",
    "title": "Add qa/20261111-aw/hello.sh and a pytest test that checks its exact output",
    "summary": "**Intent:** Add the sanity-check script and the one automated test that runs it in the PR's required checks. The test goes under `tests/` so the existing CI `test` job collects it, which closes RK1.\n\n**Owns:** `qa/20261111-aw/hello.sh` (new, mode 100755) and `tests/test_qa_20261111_aw_hello.py` (new).\n**Consumes (read only, do not modify):**\n- the existing pytest setup in `pyproject.toml`\n- `.github/workflows/ci.yml`\n- the existing test `tests/test_qa_20261109_s1_a.py`, as a pattern to follow\n\n**Acceptance criteria**\n- Running `qa/20261111-aw/hello.sh` from the repo root:\n  - writes exactly `hello aw` and a single newline to stdout, with no other output;\n  - writes nothing to stderr;\n  - exits with code 0;\n  - ignores any arguments.\n- The script is POSIX `sh`, starts with a `#!/bin/sh` shebang, uses LF line endings, and is committed executable. `git ls-files -s` shows mode 100755.\n- The new test runs the script directly from inside the repo and passes only if all three hold:\n  - stdout equals `hello aw\\n` exactly (an exact comparison, not containment);\n  - stderr is empty;\n  - the exit code is 0.\n- The test fails if the output has an extra, missing or different character (for example `hello aw!`), has no trailing newline, or has more than one trailing newline.\n- The test also fails if the script exits non-zero or writes to stderr, even when stdout is correct.\n- The test is collected by plain `pytest` from the repo root and its name appears in the CI `test` job results.\n- The test uses no network, clock or files outside the repo, uses a subprocess timeout, and adds negligible run time.\n- The full `pytest` suite passes. Every test that passed before the change still passes.\n- Outside `stories/QA20261110-12/`, the PR adds only these two files. No existing file changes, including `CHANGELOG.md`, `pyproject.toml` (and its `[project.scripts]`), CI config, `src/`, other `qa/` scripts and other tests.\n- There is no new dependency, and no secrets or personal data. The change is well under 300 lines.\n- The PR description references story QA20261110-12 and the epic PRD for AW-20261111.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
