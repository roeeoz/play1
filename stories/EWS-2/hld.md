# High-Level Design: EWS-2 (README quotes the marker from `e2e-other-branch`)

## 1. System overview
- **What:** Append one line to the end of `README.md` in `roeeoz/play1`. The line quotes the first line of `e2e-other-branch-marker.txt` word for word. That file exists only on the branch `e2e-other-branch`.
- **Problem:** The marker can't be seen from `main`. After the merge, the README on `main` shows it.
- **Responsibilities:**
  - Read the marker from a real checkout or worktree of `e2e-other-branch`.
  - Append the formatted line on the work branch.
  - Keep every other file unchanged.

## 2. Architecture overview
- There is no runtime component. This is a documentation change in one repository, `roeeoz/play1`.
- **Source of truth (read only):** `origin/e2e-other-branch`, file `e2e-other-branch-marker.txt` at the repository root, line 1.
- **Target (written):** `README.md` on `halo/feat/ews-2-20261118-154958`. The work branch was cut from `main`, and the PR merges into `main`.
- **External dependencies:** git only, using checkout or worktree. `git show` is explicitly not allowed for reading the marker.

## 3. Data flow
1. Get a working copy of `e2e-other-branch`, either with `git checkout` or with `git worktree add` into a folder outside the repository.
2. Read line 1 of the marker file, without its line break.
3. Return to the work branch, or remove the worktree.
4. Append the line `Marker from e2e-other-branch (e2e-w21-b): "<line 1>"` to `README.md`, followed by a single newline.
5. Commit only `README.md` on the work branch. The PR targets `main`.

Every step is synchronous and run by hand. There are no events.

## 4. Component breakdown
| Component | Responsibility | Input / Output | Repo |
|---|---|---|---|
| README marker line | Show the marker from the other branch on `main` | In: marker line 1. Out: the last line of `README.md` | roeeoz/play1 |

## 5. Interface contracts
- **Output format, exact:** `Marker from e2e-other-branch (e2e-w21-b): "<marker line 1 verbatim>"`
  - The quotes are plain ASCII double quotes.
  - There is no blank line before it.
  - The file ends with exactly one trailing newline.
- **Expected value (from research, to be confirmed by reading the checkout):** `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`
- There are no APIs, event schemas or cross-repo contracts.

## 6. Key technical decisions
- **Read method:** either a checkout or a worktree satisfies FR1.
  - A worktree created outside the repository folder is safer, because it never changes the branch of the work checkout.
  - If `git checkout` is used, switch back to the work branch before editing.
- **No merge, rebase or cherry-pick from `e2e-other-branch`.** Any of them would bring commit `4dd65ff` and the marker file onto the work branch.
- **One work item.** The change is one line in one file, so splitting it further would add nothing.

## 7. Risks and constraints
- Editing or committing while on `e2e-other-branch`. Prevented by checking which branch is current before committing.
- Worktree files or the marker file being staged by mistake. Prevented by staging only `README.md` and confirming the diff touches only that file.
- The quoted text not matching exactly: case, the colon after `pr343`, `14:22`, curly quotes, or trailing whitespace.
- Line endings: no extra blank line, and exactly one final newline.
- The local tracking branch `e2e-other-branch` that the checkout creates is left behind. It does no harm and may be deleted.
- CI (`pytest` and the `CI_FAIL` gate) must stay green. A README-only change doesn't affect it. There are no scale, performance or security concerns.
