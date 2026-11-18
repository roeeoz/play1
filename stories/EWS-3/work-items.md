# Work-item breakdown — e2e-w21-x live proof document (plan review)

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add docs/live-e2e/e2e-w21-x.md live proof document |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "f49ee412-3181-4ad9-b895-bb538bb55dc3",
    "title": "Add docs/live-e2e/e2e-w21-x.md live proof document",
    "summary": "**Intent:** Add the static proof file that records verification run `e2e-w21-x`. The file must have exactly the specified content, and the PR to `main` adds it and nothing else. `roeeoz/play1` is the only target repository and owns `docs/`.\n\n**Owns / Consumes:**\n- Creates and owns `docs/live-e2e/e2e-w21-x.md`, which also creates the new directory `docs/live-e2e/`.\n- Consumes nothing. Every other file in the repo is read-only for this ticket.\n\n**Acceptance criteria:**\n- `docs/live-e2e/e2e-w21-x.md` exists at exactly that path.\n- The file content is exactly three lines: `# Live coding proof`, an empty line, then `Run: e2e-w21-x`. One newline (LF) ends the last line.\n- The file has no front-matter, no trailing whitespace, no CRLF line endings, no BOM and no extra headings, links or content.\n- On GitHub, the file renders as one level-1 heading \"Live coding proof\" above a paragraph reading \"Run: e2e-w21-x\".\n- The ticket's change set is exactly one added product file. No existing file is modified, renamed or deleted, including `README.md`, `CHANGELOG.md`, any index, config or CI file. No test is added, and no code, packaging or runtime behaviour changes.\n- The repository's existing checks, the `pytest` suite over `tests/` and the CI `gate` job, behave exactly as they do on `main`.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
