---
name: repo-gate
description: The play1 repository gate. Use when asked to run the project's gate on a pull request; it checks that the change keeps the repository's layout rules and writes the verdict file it is given.
halo:
  kind: workflow
  slots: [mr-gate]
  title: play1 layout gate
---

# play1 layout gate

Check the pull request's diff against these rules:

1. Python source lives under `src/`; tests live under `tests/`.
2. A new shell script is executable and starts with a shebang.
3. No file in the diff is larger than 200 KB.

Write the verdict file named in your instructions as JSON:

```json
{"pass": true, "summary": "one line", "findings": []}
```

Each broken rule is one finding: `{"id": "PLAY-G1", "severity": "blocker", "title": "...", "file": "path:line", "note": "..."}`.
`pass` is false when there is any blocker. Do not change any file.
