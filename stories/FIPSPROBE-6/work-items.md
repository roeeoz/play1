# Work-item breakdown — Hello-world bash script in a dedicated folder

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | FIPSPROBE-6: add story-linked test proving hello-world/hello.sh output, shebang and git-recorded executable mode, plus CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "7054ee13-6ea2-4b4b-a4e4-db1f17cec6b8",
    "title": "FIPSPROBE-6: add story-linked test proving hello-world/hello.sh output, shebang and git-recorded executable mode, plus CHANGELOG entry",
    "summary": "**Intent:** Deliver FIPSPROBE-6 as a verification pull request. It adds one pytest module, linked to FIPSPROBE-6, that proves the story's acceptance criteria against the `hello-world/hello.sh` already on `main`. The module reads the executable bit from the git index, which covers RK1. The pull request also adds one CHANGELOG line, so it passes the play1 layout gate (`PLAY-G4`). roeeoz/play1 owns the script, its test suite and the gate.\n\n**Owns / Consumes:**\n- Owns (creates): `tests/test_fipsprobe_6_hello_sh.py`.\n- Owns (edits): exactly one added line under `## Unreleased` in `CHANGELOG.md`.\n- Consumes (read-only): `hello-world/hello.sh`, the git index, `pyproject.toml` (the pytest config), `tests/test_qa_s3_greeting.py` (the subprocess pattern) and `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (the gate rules).\n- Must not modify:\n  - `hello-world/` (any file);\n  - `tests/test_hello_sh.py`, including `test_folder_contains_only_hello_sh`, which FIPSPROBE-7 owns changing;\n  - `.github/`, `pyproject.toml`, `src/`, README and any other documentation;\n  - any existing line of `CHANGELOG.md`.\n\n**Acceptance criteria:**\n1. Running `hello-world/hello.sh` directly, with no `bash` prefix, from the repository root gives exit code 0 and stdout exactly `hello world\\n`, and the test asserts this.\n2. The test asserts that stdout is exactly one line, equal to `hello world`, with no leading or trailing whitespace and no extra lines, and that stderr is empty.\n3. The test asserts that the first line of `hello-world/hello.sh` is exactly `#!/bin/bash`.\n4. The test reads the mode from the git index (`git ls-files -s`), not from the checkout. It asserts that `hello-world/hello.sh` is recorded at the repository root path with mode `100755`, so it would fail if git stored the file as `100644`, even when the checkout shows it as executable.\n5. If `git` or the `.git` directory is unavailable, the mode check fails with a clear message. It does not pass or skip silently.\n6. The file name and module docstring contain `FIPSPROBE-6`. Every subprocess call has a timeout.\n7. `pip install -e \".[test]\"` and then `pytest` pass on the branch. The existing suite collects the new tests, with no CI or config change.\n8. `CHANGELOG.md` gains exactly one new line, placed under the `## Unreleased` heading, that names FIPSPROBE-6 and the hello-world test. No other line of the file changes, and the play1 layout gate's rule `PLAY-G4` passes.\n9. Scope boundary, amended AC5: the diff leaves `hello-world/hello.sh` byte-for-byte and mode-for-mode unchanged and at the repository root. It contains no documentation or CI change. Outside `stories/FIPSPROBE-6/`, it changes only the new test file and that single CHANGELOG line.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
