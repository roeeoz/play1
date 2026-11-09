# Work-item breakdown — סקריפט שמדפיס "B" אחרי "A"

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/20261109-s1/b.sh that runs a.sh then prints B, with tests and CHANGELOG entry |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/20261109-s1/b.sh that runs a.sh then prints B, with tests and CHANGELOG entry",
    "summary": "**Intent:** Deliver the dependent QA script `qa/20261109-s1/b.sh`. It runs the `a.sh` that sits next to it and then prints `B`, and fails without printing `B` when `a.sh` is missing or fails. The ticket also adds the script's automated tests and the CHANGELOG line required by the repo gate. All of the story's work lives in roeeoz/play1.\n\n**Owns:**\n- `qa/20261109-s1/b.sh` (new; git mode 100755; LF line endings; `#!/bin/sh` shebang)\n- `tests/test_qa_20261109_s1_b.py` (new)\n- one new line under `## Unreleased` in `CHANGELOG.md` citing PLAY-173\n\n**Consumes (read-only, must not change):** `qa/20261109-s1/a.sh` (PLAY-172 contract: prints `A\\n`, empty stderr, exit 0). Must also leave unchanged `qa/s3-a.sh`, `qa/s3-hello.sh`, `hello-world/hello.sh`, every existing test, `.github/workflows/ci.yml` and `pyproject.toml`.\n\n**Acceptance criteria:**\n1. Running `qa/20261109-s1/b.sh` with no arguments prints exactly two lines, `A` then `B` (stdout == `A\\nB\\n`), with empty stderr, and exits 0.\n2. In a temp folder holding a copy of `b.sh` next to a stub `a.sh` that prints other text and exits 0, running the `b.sh` copy prints that text as its first line, followed by `B`. This proves `b.sh` doesn't print `A` itself.\n3. Run from a current folder other than the scripts' folder (e.g. pytest `tmp_path`), `qa/20261109-s1/b.sh` invoked by its path prints exactly `A\\nB\\n` and exits 0. `b.sh` finds `a.sh` from its own location, not from the current folder.\n4. Missing `a.sh`: a copy of `b.sh` alone in a temp folder exits non-zero (1), writes a non-empty error message to stderr naming the missing `a.sh`, and `B` does not appear on stdout.\n5. Failing `a.sh`: a copy of `b.sh` next to a stub `a.sh` that exits non-zero results in `b.sh` exiting non-zero (passing on `a.sh`'s code), and `B` does not appear on stdout.\n6. File shape: `b.sh` starts with `#!/bin/sh\\n`, has the owner execute bit set (committed as 100755) and contains no `\\r`.\n7. Regression:\n   - `qa/20261109-s1/a.sh` and `qa/s3-a.sh` still print `A`, `qa/s3-hello.sh` prints `hello` and `hello-world/hello.sh` prints `hello world`.\n   - The only existing file the diff changes is `CHANGELOG.md`, by one added line under `## Unreleased` that cites PLAY-173.\n8. Tests:\n   - The tests live in the new file `tests/test_qa_20261109_s1_b.py`. They are picked up by the existing `pytest` CI job without any config change, and all existing and new tests pass.\n   - The tests use no network, clock or environment variables, and never modify the real `a.sh`. Failure cases use temp-folder copies.\n   - Each subprocess call has a timeout, and the test job finishes in under 60 seconds.\n9. Out of scope: no `--help` support and no new dependencies. The total diff is under 300 lines. The PR cites PLAY-173 and the epic PRD \"ברכות בטרמינל\" and is merged by a human.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
