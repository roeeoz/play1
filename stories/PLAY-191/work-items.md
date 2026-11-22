# Work-item breakdown — QA-20261122-S7 add qa/s7_stop.txt

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add qa/s7_stop.txt with the single line 'stop and retry' |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "5c6a2c74-bde7-47e2-bb43-d0d8566d942e",
    "title": "Add qa/s7_stop.txt with the single line 'stop and retry'",
    "summary": "**Intent:** Deliver the QA fixture file `qa/s7_stop.txt` that the factory's stop / retry check is run against (PLAY-191). `roeeoz/play1` owns it because `qa/` lives at its root.\n\n**Owns / Consumes:** Owns (creates) `qa/s7_stop.txt` only. Consumes nothing; existing `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/`, `qa/20261110-s3/`, `src/`, `tests/`, `.github/workflows/ci.yml`, `.factory/` and `pyproject.toml` stay unchanged.\n\n**Acceptance criteria:**\n- `qa/s7_stop.txt` exists in the `qa/` folder at the repository root and is tracked by git.\n- It contains exactly one line, `stop and retry`: lowercase, one space between words, no quotes, no leading or trailing whitespace, no blank or extra lines.\n- Its bytes are exactly `stop and retry` followed by a single LF (15 bytes; no CR, no BOM, nothing after the LF); `wc -l` reports 1.\n- If the run is stopped and retried, the delivered file still has exactly these bytes (written whole, never appended), with no duplicate line.\n- The pull request changes no file other than `qa/s7_stop.txt`, except the factory's plan folder `stories/PLAY-191/`; in particular no `CI_FAIL` file is created.\n- No new automated test is added; the existing `test` job (`pip install -e \".[test]\"` + `pytest`) and `gate` job in `.github/workflows/ci.yml` stay green, and the play1 `repo-gate` reports no finding.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
