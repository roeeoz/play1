# Work-item breakdown — QA-20261110-S4 hello.sh prints hello s4

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | QA-20261110-S4 hello.sh prints hello s4 |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "2a95024f-3294-4223-b52a-b3ba03becc4c",
    "title": "QA-20261110-S4 hello.sh prints hello s4",
    "summary": "**Intent:** Add the QA sanity script `qa/20261110-s4/hello.sh`, which prints exactly `hello s4`, and its self-contained shell test `qa/20261110-s4/test_hello.sh`. Add the CHANGELOG line that play1's PR gate requires. This delivers story QA20261110-2 (Epic PRD \"סקריפט hello s4 (בדיקת שפיות של QA)\", R1–R5) in roeeoz/play1 against base `qa-20261110-s4-base`.\n\n**Owns:** new `qa/20261110-s4/hello.sh`, new `qa/20261110-s4/test_hello.sh`, and one added line under `## Unreleased` in `CHANGELOG.md`.\n\n**Consumes (read-only, must not change):** `qa/20261110-s4/BASE_MARKER.txt`, the existing pytest suite and CI (`.github/workflows/ci.yml`, `pyproject.toml`), and the format of existing CHANGELOG entries.\n\n**Acceptance criteria:**\n1. Running `qa/20261110-s4/hello.sh` from any directory writes exactly the bytes `hello s4` followed by a single newline to stdout, writes nothing to stderr, and exits 0. It takes no input (FR1, FR2; scenario 1).\n2. Running `qa/20261110-s4/test_hello.sh` with the committed `hello.sh` prints a visible success message and exits 0 (FR3; scenario 2).\n3. If the `hello.sh` next to the test prints anything other than exactly `hello s4\\n`, the test prints a visible failure message and exits non-zero. This covers different text, extra lines, an extra trailing blank line and a missing newline. The test also fails if `hello.sh` exits non-zero, even when its output is correct (FR4; scenario 3). Check this without leaving a modified file, for example by copying both scripts to a temporary directory, changing the copy and running the copied test.\n4. `test_hello.sh` finds `hello.sh` relative to its own location, not the current directory. Running it by path from the repo root, from `qa/20261110-s4/`, from `/tmp` and with `CDPATH` set gives the same result as criterion 2. It uses no network and no clock (FR5; scenario 4).\n5. Both scripts start with a shebang line (POSIX `#!/bin/sh`, matching the existing `qa/` scripts), are committed with git mode 100755, contain no CR characters and each stay well under 200 KB (gate rules 2 and 3).\n6. `CHANGELOG.md` gains exactly one new line under `## Unreleased`, in the existing entry format, naming QA20261110-2 and the new `qa/20261110-s4/hello.sh`. No other line in the file changes (FR6; gate rule 4).\n7. Excluding `stories/QA20261110-2/`, the PR's changed files are only the two new scripts and `CHANGELOG.md`. `BASE_MARKER.txt`, `src/`, `tests/`, CI config and `pyproject.toml` are untouched, and no dependencies are added (FR7, R5; scenario 5).\n8. The existing pytest suite passes and all required CI checks are green on the PR head (R5).\n9. The PR description cites story QA20261110-2 \"QA-20261110-S4 hello.sh prints hello s4\" and the Epic PRD. Because CI does not run `test_hello.sh` (RK1, accepted), the description also records the manual results of scenarios 1–4.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
