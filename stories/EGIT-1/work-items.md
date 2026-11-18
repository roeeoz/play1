# Work-item breakdown — e2e-pr343 marker script from another branch

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add executable qa/e2e-pr343/marker.sh that prints the e2e-other-branch marker line |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "f9d57bf8-ad73-40b0-94ea-5622520fd330",
    "title": "Add executable qa/e2e-pr343/marker.sh that prints the e2e-other-branch marker line",
    "summary": "**Intent:** deliver the one-command way to print the `e2e-other-branch` marker line from `main` without switching branches. The line is a hard-coded literal in a new bash script in `play1`.\n\n**Owns:** `qa/e2e-pr343/marker.sh`, a new file in a new directory.\n**Consumes:** line 1 of `e2e-other-branch-marker.txt` on `origin/e2e-other-branch`. It is read only to author and verify the literal. Nothing is merged, cherry-picked or copied from that branch. The base and merge target is `main`.\n\n**Acceptance criteria:**\n- `qa/e2e-pr343/marker.sh` exists and its first line is exactly `#!/bin/bash`.\n- The file is tracked in git with mode `100755`, checked with `git ls-files -s`.\n- Running it from the repo root, and as `./marker.sh` from inside `qa/e2e-pr343/`, writes exactly `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22` followed by a single `\\n` to stdout. There is no prefix, label, colour, CR, trailing space or extra blank line.\n- The output is byte-identical to line 1 of `e2e-other-branch-marker.txt` on `origin/e2e-other-branch`, compared with `od -c`. The file's second line is not printed.\n- stderr is empty and the exit status is 0. The output is the same from any working directory and on any checked-out branch.\n- The line is a literal in the script. The script contains no `git` invocation and reads no file.\n- No existing file is modified (`git diff --stat main` shows only the new file). No test, CHANGELOG entry, README change or other documentation is added.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
