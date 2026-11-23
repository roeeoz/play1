# Work-item breakdown — QA-20261122-GAP Start with a target-branch override (add qa/gap-hello.txt)

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/gap-hello.txt containing 'hello from gap' |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "29ac813e-5088-44e7-a070-28c81f32b634",
    "title": "Add qa/gap-hello.txt containing 'hello from gap'",
    "summary": "**Intent:** Add one static text file, `qa/gap-hello.txt`, on the work branch cut from `qa-20261122-s4-base`, so the factory's delivery onto a non-default base branch is exercised. Nothing else in the repository changes.\n\n**Owns:** `qa/gap-hello.txt` (new).\n**Consumes (read-only, must not change):** existing `qa/` files (`qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/`, `qa/20261110-s3/`), `tests/test_qa_20261122_s4_base.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/`.\n\n**Acceptance criteria:**\n- `qa/gap-hello.txt` exists with the text `hello from gap`; `cat qa/gap-hello.txt` prints `hello from gap`.\n- The file content is exactly one lowercase line, `hello from gap`, with no quotes, no leading/trailing spaces, no BOM, LF line ending (not CRLF) and exactly one trailing newline: 15 bytes (`wc -c` reports 15).\n- The file is a regular, non-executable text file (git mode 100644).\n- Compared with `qa-20261122-s4-base`, the change adds `qa/gap-hello.txt` and changes no other file (outside the platform-owned plan folder `stories/SCRUM-112/`).\n- No test, script, package or CI change is added; `tests/test_qa_20261122_s4_base.py` is NOT fixed, skipped, deleted or marked xfail.\n- The required `pytest` gate is expected to be red solely because of the pre-existing failing base test (`assert 1 == 2`); the PR reports this as the expected QA outcome, not as a story failure, and does not seek a gate exemption. The CI `gate` job stays green (no `CI_FAIL` at the repo root).\n- The repo layout gate passes: PLAY-G1 (no Python added), PLAY-G2 (no shell script added), PLAY-G3 (file far below 200 KB).",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
