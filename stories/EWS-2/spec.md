# Feature Specification Document

## 1. Feature Overview
- **Summary:** Add one line to the end of the repository `README.md`. The line quotes, word for word, the first line of `e2e-other-branch-marker.txt`. That file exists only on the branch `e2e-other-branch`.
- **Problem statement:** The marker line is kept on another branch. A developer working on `main` can't see it without leaving `main`.
- **Target users / actors:** Developers who read the repository README on `main`.

---

## 2. Goals & Non-Goals
### Story context
the marker is the FIRST line of the file `e2e-other-branch-marker.txt` at the root of the branch `e2e-other-branch` of this repository (the file is not on `main`).

### Goals
- The README on the story's work branch, and on `main` once the PR is merged, ends with one new line. That line quotes the marker's first line word for word.
- The marker is read from a real checkout or worktree of `e2e-other-branch`, as the story requires.
- The change is committed on the story's own work branch.

### Non-Goals
- Quoting any line of the marker file other than the first one.
- Bringing `e2e-other-branch-marker.txt`, or any commit from `e2e-other-branch`, onto the work branch or onto `main`.
- Merging or rebasing with `e2e-other-branch`, or committing anything to it.
- Adding or changing tests, code, CI or any file other than `README.md`.
- Rewording, reformatting or reordering anything already in `README.md`.

---

## 3. Functional Requirements
- **FR1: Read the marker from the other branch.** Before changing anything, check out `e2e-other-branch`, using either `git checkout e2e-other-branch` or `git worktree add <dir> e2e-other-branch`. Read the first line of `e2e-other-branch-marker.txt` there, word for word. Do not use `git show` for this step.
- **FR2: Append the line.** On the story's work branch, add exactly one line at the end of `README.md`:
  `Marker from e2e-other-branch (e2e-w21-b): "<the first line of the marker file, verbatim>"`
  - Copy the quoted text character for character, including case, punctuation and the time value. Put it between plain double quotes. Leave out the file's line break and its second line.
  - Every existing line in `README.md` stays exactly as it is. The file ends with the new line followed by a single trailing newline.
- **FR3: Commit on the work branch.** Commit the change on the story's own work branch, not on `e2e-other-branch`. If `git checkout` was used, switch back to the work branch before editing. If a worktree was used, remove it, and none of its files go into the commit.
- **Edge cases:**
  - **Only line 1 is quoted.** The marker file has a second line, and it must not be quoted.
  - **The marker file stays off `main`.** It must not appear on the work branch.
  - **No duplicate.** No existing line starts with `Marker from`, so this is the only one.
- **Note from research:** a read of the remote branch found this first line: `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`. Implementation must still read it from a checkout or worktree, as FR1 says, and use what it reads there.

---

## 4. User Experience & Behavior
- **Flow:** A developer opens `README.md` on `main` after the PR is merged. The last line shows the marker from `e2e-other-branch`, in the agreed format, without the developer switching branches.
- **Output format:** exactly `Marker from e2e-other-branch (e2e-w21-b): "<marker line 1>"`, as a single line at the end of the file.
- The rest of the README is unchanged and nothing else is visible to the user.

---

## 5. Acceptance Criteria
1. `README.md` ends with that one new line, quoting the marker's first line verbatim between double quotes.
2. `README.md` is the only source file changed; nothing else in the repository is modified and no test is added.
3. The change is committed on the story's own work branch, not on `e2e-other-branch`.

---

## 6. Dependencies & Constraints (product-level)
- The story depends on the branch `e2e-other-branch` and its file `e2e-other-branch-marker.txt` being available.
- The work is based on `main`, and the PR merges into `main`. A person merges the PR after review.
- The repository's CI gate (`pytest`, plus the `CI_FAIL` gate job) must stay green. A change that only touches the README should not affect it.
- How the marker is read is part of the requirement: a checkout or a worktree, never `git show`.

---

## 7. Technical Design (deferred to STRUCTURE)
- This is a single work item at the smallest tier. There are no design choices to make beyond the steps in §3.

---

## 8. Open Questions (if any remain)
- None blocking.
- Assumption: the platform's plan documents under `stories/EWS-2/` are process files, not source files, under criterion 2. Other stories in this epic treat them the same way.
