# Work-item breakdown — e2e-w21-a live proof document

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add docs/live-e2e/e2e-w21-a.md live coding proof document |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "f49ee412-3181-4ad9-b895-bb538bb55dc3",
    "title": "Add docs/live-e2e/e2e-w21-a.md live coding proof document",
    "summary": "**Intent:** Add the documentation file that records the live verification run `e2e-w21-a` in `roeeoz/play1`, the story's only repository.\n\n**Owns / Consumes:**\n- **Owns:** `docs/live-e2e/e2e-w21-a.md`, a new file in a new directory.\n- **Consumes:** nothing. It must not modify any existing file, including `CHANGELOG.md`.\n\n**Acceptance criteria:**\n- `docs/live-e2e/e2e-w21-a.md` exists at that exact path.\n- The file's content is exactly three lines: `# Live coding proof`, then an empty line, then `Run: e2e-w21-a`.\n- The file ends with exactly one trailing newline. It has no front matter, no trailing whitespace and no extra lines: the bytes are `# Live coding proof\\n\\nRun: e2e-w21-a\\n`.\n- No existing file is modified. In particular, `CHANGELOG.md` is unchanged.\n- No code, test, configuration, CI workflow or dependency is added, changed or removed. No other documentation, index or link to the new file is added.\n- On the forge, the file renders as a level-1 heading, \"Live coding proof\", followed by a paragraph that reads \"Run: e2e-w21-a\".\n- The existing `pytest` suite still passes unchanged.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
