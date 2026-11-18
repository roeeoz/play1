# High-Level Design: SCRUM-1, e2e-w2 run notes file and ported marker file

## 1. System overview
- **What:** two new static files in `play1`:
  - a Markdown document at `docs/e2e-w2/notes.md` that records the e2e-w2 verification run's identifier;
  - `e2e-other-branch-marker.txt` at the repository root, a byte-identical copy of `origin/e2e-other-branch:e2e-other-branch-marker.txt`. The story owner added this port to the scope on 2026-11-18.
- **Problem:** the e2e-w2 run needs a notes file in the repository that names the run (`e2e-w2-20261118`).
- **Responsibility:** static documentation only. Nothing reads it at runtime.

## 2. Architecture overview
- **Components:**
  - one static documentation file in the new folder `docs/e2e-w2/`. That folder does not exist on `main`; adding the file creates it.
  - one static text file, `e2e-other-branch-marker.txt`, at the repository root. It does not exist on `main` or on the work branch.
- **Boundaries:**
  - No code, tests, configuration or CI change.
  - No existing file changes, including `CHANGELOG.md`, `README.md` and anything else under `docs/`.
- **Ownership:** t1 owns `docs/e2e-w2/notes.md`. t2 owns `e2e-other-branch-marker.txt`. They touch different paths and are independent.
- **External dependencies:** the content of one file on `e2e-other-branch` (commit `4dd65ff`, blob `0bf2179`), read with `git show`. The base stays `main` (`b7b5d0a`): no merge, cherry-pick or rebase, and no commit from `e2e-other-branch` or any other branch enters the work branch. Only that one file's content is copied.

## 3. Data flow
- The flow is static. A reader opens `docs/e2e-w2/notes.md` in the checkout or on the forge, and it renders as an H1 heading "e2e-w2 notes" followed by the line "Run: e2e-w2-20261118".
- The marker file is produced once, at implementation time: `git show origin/e2e-other-branch:e2e-other-branch-marker.txt > e2e-other-branch-marker.txt`, then committed as a new file on the work branch.
- There is no sync or async processing and no events.

## 4. Component breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `docs/e2e-w2/notes.md` | Record the e2e-w2 run identifier | Input: the developer's line. Output: a 2-line Markdown file | play1 (`07c4e808-028f-45a4-b864-5e3baf454c57`) |
| `e2e-other-branch-marker.txt` | Carry the `e2e-other-branch` marker onto this story's branch | Input: `origin/e2e-other-branch:e2e-other-branch-marker.txt`. Output: the same 101 bytes at the repository root | play1 (`07c4e808-028f-45a4-b864-5e3baf454c57`) |

## 5. Interface contracts
- **`docs/e2e-w2/notes.md` exact bytes** (36 bytes, UTF-8, LF line endings):
  - line 1 is `# e2e-w2 notes`
  - line 2 is `Run: e2e-w2-20261118`
  - one trailing newline, no blank line between the lines, and nothing after line 2
- **`e2e-other-branch-marker.txt` exact bytes:** identical to blob `0bf21798cef8d1b9194e74c76fcc391ddbf5b901` on `e2e-other-branch` (101 bytes, 2 lines, LF, trailing newline, no CR). `git hash-object e2e-other-branch-marker.txt` must print that blob ID.
- No APIs, events or cross-repository contracts.

## 6. Key technical decisions
- **No index, README or CHANGELOG update.** The spec forbids changes to existing files. The research also found that nothing in the repository indexes `docs/` and no code or test reads it, so adding the file breaks no reference.
- **No new test.** The spec says documentation only, with no tests. The file is checked directly instead: 2 lines, last byte `0a`, and an exact `diff` against the expected content.
- **Port by content, not by history.** The marker file is taken with `git show` and committed as a new file. A merge or cherry-pick of `e2e-other-branch` is rejected: it would bring that branch's commits into the work and change the base, which stays `main`.
- **Alternative rejected:** adding a CHANGELOG line to satisfy `repo-gate` rule 4. It would break FR5 and acceptance criterion 2.

## 7. Risks and constraints
- **`PLAY-G4` gate blocker.** The `mr-gate` repo-gate rule 4 requires a `CHANGELOG.md` edit, so a spec-compliant PR will get this blocker. The resolution is a human waiver at review, not a CHANGELOG edit.
- **Spec mismatch.** `spec.md` still lists content from `e2e-other-branch` as a non-goal (§2, line 21) and says the change adds one file (FR5, §6, §7). The story owner changed the scope; the spec must be amended at the define stage to match, or a reviewer will read the marker file as out of scope.
- **Exact bytes.** An editor or agent could drop the trailing newline, add a blank line, or write CRLF line endings. Both files' bytes must be checked before the PR is opened.
- **Diff scope.** The PR diff against `main` also includes the platform's `stories/SCRUM-1/*` files. Only `docs/e2e-w2/notes.md` and `e2e-other-branch-marker.txt` are deliverable content.
- **CI.** The `test` job (pip install plus pytest on `tests/`) and the `gate` job (fails if `CI_FAIL` exists) are unaffected. No `CI_FAIL` file may be created.
- **Scale, performance, security:** not applicable to two small static files.
