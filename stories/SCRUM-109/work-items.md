# Work-item breakdown — QA-20261122-S4: a script that prints the project's QA_S4_MARKER value

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/s4_marker.sh that prints QA_S4_MARKER, with its shell test |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "29ac813e-5088-44e7-a070-28c81f32b634",
    "title": "Add qa/s4_marker.sh that prints QA_S4_MARKER, with its shell test",
    "summary": "**Intent:** Deliver the developer-facing script `qa/s4_marker.sh` that reports the exact value of the `QA_S4_MARKER` environment variable, plus a sibling shell test that proves its contract. Lives in `roeeoz/play1` under `qa/s4_*` only (spec FR4).\n\n**Owns:** `qa/s4_marker.sh` (new), `qa/s4_marker_test.sh` (new).\n**Consumes (read only, pattern):** `qa/s3-hello.sh`, `qa/20261110-s3/hello.sh` (POSIX `#!/bin/sh` helper with a purpose comment), `qa/20261110-s3/test_hello.sh` (shell test that runs its sibling and checks exact stdout and exit code). Must not change any other file — not `tests/`, `src/`, `pyproject.toml`, `.github/workflows/ci.yml`, other `qa/` scripts, nor `tests/test_qa_20261122_s4_base.py`.\n\n**Acceptance criteria:**\n- `qa/s4_marker.sh` exists, starts with a `#!/bin/sh` shebang, is LF-terminated, is committed with git mode `100755`, and runs directly as `./qa/s4_marker.sh` (repo gate rule PLAY-G2).\n- With `QA_S4_MARKER` exported and non-empty, stdout is exactly the value followed by one newline, stderr is empty, exit status is 0.\n- With `QA_S4_MARKER` exported as an empty string, stdout is exactly a single newline, stderr is empty, exit status is 0.\n- With `QA_S4_MARKER` absent from the environment, stderr is exactly `QA_S4_MARKER is not set` followed by a newline, stdout is empty, exit status is 1.\n- The value is output verbatim: `-n`, `a\\nb\\c` (literal backslashes), `%s %d`, ` sp ` (leading/trailing spaces) and a value with an embedded newline each print unchanged followed by exactly one newline, exit 0.\n- Output carries no label, prefix or quoting; arguments to the script are ignored.\n- Behaviour is identical when run under bash and under dash as `/bin/sh` (where dash is available).\n- `qa/s4_marker_test.sh` is executable (mode `100755`, `#!/bin/sh`), runs `qa/s4_marker.sh` from any working directory, covers every case above (non-empty, empty, unset, the verbatim values), prints a `PASS` line and exits 0 when all pass, and prints a `FAIL:` line on stderr and exits non-zero on any mismatch.\n- `./qa/s4_marker_test.sh` passes locally; `git diff --name-only qa-20261122-s4-base...HEAD` lists only files matching `qa/s4_*` (besides the platform's `stories/SCRUM-109/` plan files).\n- The CI `test` job's pre-existing failure from `tests/test_qa_20261122_s4_base.py` is left as is and noted in the PR description as caused by the base, not this change.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
