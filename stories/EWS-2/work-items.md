# Work-item breakdown — e2e-w21-b README quotes the marker from another branch

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Append the e2e-other-branch marker line to README.md |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "f49ee412-3181-4ad9-b895-bb538bb55dc3",
    "title": "Append the e2e-other-branch marker line to README.md",
    "summary": "**Intent:** Read line 1 of `e2e-other-branch-marker.txt` from a real checkout or worktree of `e2e-other-branch` (not with `git show`). Then append it to the end of `README.md`, in the agreed format, on the story's work branch, so that it is visible on `main` after the merge.\n\n**Owns:** `README.md` (the one appended line only).\n**Consumes (read only, never committed):** `e2e-other-branch-marker.txt` on branch `e2e-other-branch`.\n\n**Acceptance criteria:**\n- The marker is read from a checkout (`git checkout e2e-other-branch`) or a worktree (`git worktree add <dir> e2e-other-branch`) of `e2e-other-branch`, and never with `git show`.\n- The last line of `README.md` is exactly `Marker from e2e-other-branch (e2e-w21-b): \"<line 1 of the marker file>\"`:\n  - The quoted text matches what was read character for character, including case, punctuation and the time value. The expected value is `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`.\n  - The quotes are plain ASCII double quotes.\n  - There is no trailing space or line break inside the quotes.\n- The second line of the marker file (`second line: only on e2e-other-branch`) does not appear anywhere in `README.md`.\n- The first 166 lines of `README.md` are byte-for-byte unchanged. There is no blank line between the old last line and the new one, and the file ends with exactly one trailing newline.\n- Exactly one line in `README.md` starts with `Marker from`.\n- The PR diff against `main` changes only `README.md`, apart from the platform's process files under `stories/EWS-2/`:\n  - no test, code or CI file is added or changed;\n  - `e2e-other-branch-marker.txt` is not on the work branch;\n  - no commit from `e2e-other-branch` (for example `4dd65ff`) is in the branch history.\n- The change is committed on `halo/feat/ews-2-20261118-154958`, and nothing is committed or pushed to `e2e-other-branch`.\n- If a worktree was used, it has been removed and none of its files are in the change.\n- CI (`pytest` and the `CI_FAIL` gate) stays green.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
