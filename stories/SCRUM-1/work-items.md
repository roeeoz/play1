# Work-item breakdown — e2e-w2-1118 run notes file and ported marker file

| # | Ref | Title | Depends on |
|---|---|---|---|
| 1 | t1 | Add docs/e2e-w2/notes.md run-notes file for the e2e-w2 verification run |  |
| 2 | t2 | Port e2e-other-branch-marker.txt from e2e-other-branch to the repository root |  |

The fenced JSON below is the machine-readable breakdown the platform materializes on approval. Edits must keep it valid JSON with the same schema.

```json
[
  {
    "ref": "t1",
    "repoId": "07c4e808-028f-45a4-b864-5e3baf454c57",
    "title": "Add docs/e2e-w2/notes.md run-notes file for the e2e-w2 verification run",
    "summary": "**Intent:** Add the e2e-w2 run-notes document to `play1`, the only repository this story targets. It records the run identifier exactly as the developer gave it.\n\n**Owns:**\n- `docs/e2e-w2/notes.md`, a new file. Adding it creates the new folder `docs/e2e-w2/`.\n\n**Consumes:** nothing. The work branch is based only on `main`. (The marker file ported from `e2e-other-branch` belongs to t2, not to this item.)\n\n**Acceptance criteria:**\n- `docs/e2e-w2/notes.md` exists at that exact path.\n- Line 1 is exactly `# e2e-w2 notes`.\n- Line 2 is exactly `Run: e2e-w2-20261118`, with the same characters, case and punctuation.\n- The file has exactly these two lines and no blank line between them. It ends with a single trailing newline, uses LF line endings and has nothing after line 2. Checks:\n  - `wc -l` reports 2.\n  - The last byte is `0a`.\n  - The file is 36 bytes.\n  - An exact `diff` against the expected two-line content is empty.\n- On Markdown platforms it renders as a level-1 heading \"e2e-w2 notes\" followed by the text line \"Run: e2e-w2-20261118\".\n- Against `main`, this item's only change is this one added file (t2 adds the other deliverable file). No existing file is modified or deleted, and that includes `CHANGELOG.md`, `README.md` and the existing `docs/` content. The platform's `stories/SCRUM-1/*` plan files are not deliverable content.\n- No tests, code, configuration or CI files are added or changed. No `CI_FAIL` file is created, and the existing CI jobs (`test`, `gate`) pass unchanged.\n- The PR targets `main` and contains no commits from any other branch.\n- The `repo-gate` `PLAY-G4` blocker (missing CHANGELOG line) is not resolved by editing `CHANGELOG.md`. The PR description notes that the approved spec forbids a CHANGELOG entry and that the blocker needs a human waiver.",
    "dependsOn": [],
    "requirementRefs": []
  },
  {
    "ref": "t2",
    "repoId": "07c4e808-028f-45a4-b864-5e3baf454c57",
    "title": "Port e2e-other-branch-marker.txt from e2e-other-branch to the repository root",
    "summary": "**Intent:** Bring the marker file from `e2e-other-branch` onto this story's branch, byte for byte, at the same path. The story owner added this to the scope on 2026-11-18. The base stays `main`: the file's content is copied, not the branch's history.\n\n**Owns:**\n- `e2e-other-branch-marker.txt` at the repository root, a new file. It does not exist on `main`.\n\n**Consumes:** the content of `origin/e2e-other-branch:e2e-other-branch-marker.txt` (branch commit `4dd65ff`, blob `0bf21798cef8d1b9194e74c76fcc391ddbf5b901`), read with `git show origin/e2e-other-branch:e2e-other-branch-marker.txt > e2e-other-branch-marker.txt`.\n\n**Acceptance criteria:**\n- `e2e-other-branch-marker.txt` exists at the repository root.\n- Its content is exactly that of `origin/e2e-other-branch:e2e-other-branch-marker.txt`. Checks:\n  - `git hash-object e2e-other-branch-marker.txt` prints `0bf21798cef8d1b9194e74c76fcc391ddbf5b901`.\n  - `cmp <(git show origin/e2e-other-branch:e2e-other-branch-marker.txt) e2e-other-branch-marker.txt` prints nothing.\n  - The file is 101 bytes and 2 lines, uses LF line endings and ends with a trailing newline.\n- No merge, cherry-pick or rebase involving `e2e-other-branch`. `git log main..HEAD` shows only this story's own commits, and `git merge-base --is-ancestor 4dd65ff HEAD` fails (the other branch's commit is not in the history).\n- No other file is taken from `e2e-other-branch`, and no existing file is modified or deleted, `README.md` and `CHANGELOG.md` included.\n- No tests, code, configuration or CI files are added or changed, and no `CI_FAIL` file is created.\n- The PR description states that the story owner brought this port into scope and that it was copied by content, not merged.",
    "dependsOn": [],
    "requirementRefs": []
  }
]
```
