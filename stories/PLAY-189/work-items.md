# Work-item breakdown — QA-20261122-S7 add qa/s7_greeting.txt

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/s7_greeting.txt containing the line "hello again from s7" |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/s7_greeting.txt containing the line \"hello again from s7\"",
    "summary": "**Intent:** Add the QA marker file `qa/s7_greeting.txt` to `roeeoz/play1` so QA can exercise the factory's go-back flow with a minimal, verifiable change.\n\n**Owns:** `qa/s7_greeting.txt` (new). **Consumes:** the existing `qa/` folder at the repo root (read-only; `qa/20261109-s1/`, `qa/20261110-s3/`, `qa/s3-a.sh`, `qa/s3-hello.sh` stay unchanged).\n\n**Acceptance criteria:**\n- `qa/s7_greeting.txt` exists in the repo root's `qa/` folder.\n- Its content is byte-exact `hello again from s7` followed by one LF: `printf 'hello again from s7\\n' | cmp - qa/s7_greeting.txt` succeeds (20 bytes; no BOM, no CR, no leading/trailing spaces, no extra or blank lines).\n- The file is a regular non-executable file (git mode `100644`) with no shebang.\n- Apart from `qa/s7_greeting.txt` (and the factory's plan folder `stories/PLAY-189/`), no file in the repository is added, changed or deleted — no test module, no README or `.gitignore` edit, no `CI_FAIL` file; `roeeoz/play2` is not touched.\n- The repo gates pass: the play1 layout gate (rules PLAY-G1..G3) and the existing `pip install -e \".[test]\" && pytest` suite on Python 3.12, unchanged.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
