# High-Level Design: SCRUM-1, e2e-w2 run notes file

## 1. System overview
- **What:** a new Markdown document at `docs/e2e-w2/notes.md` in `play1` that records the e2e-w2 verification run's identifier.
- **Problem:** the e2e-w2 run needs a notes file in the repository that names the run (`e2e-w2-20261118`).
- **Responsibility:** static documentation only. Nothing reads it at runtime.

## 2. Architecture overview
- **Component:** one static documentation file in the new folder `docs/e2e-w2/`. That folder does not exist on `main`; adding the file creates it.
- **Boundaries:**
  - No code, tests, configuration or CI change.
  - No existing file changes, including `CHANGELOG.md`, `README.md` and anything else under `docs/`.
- **Ownership:** the single ticket (t1) owns `docs/e2e-w2/notes.md`.
- **External dependencies:** none. The base is `main` (`b7b5d0a`). Nothing comes from `e2e-other-branch` or any other branch.

## 3. Data flow
- The flow is static. A reader opens the file in the checkout or on the forge, and it renders as an H1 heading "e2e-w2 notes" followed by the line "Run: e2e-w2-20261118".
- There is no sync or async processing and no events.

## 4. Component breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `docs/e2e-w2/notes.md` | Record the e2e-w2 run identifier | Input: the developer's line. Output: a 2-line Markdown file | play1 (`07c4e808-028f-45a4-b864-5e3baf454c57`) |

## 5. Interface contracts
- **The file's exact bytes** (36 bytes, UTF-8, LF line endings):
  - line 1 is `# e2e-w2 notes`
  - line 2 is `Run: e2e-w2-20261118`
  - one trailing newline, no blank line between the lines, and nothing after line 2
- No APIs, events or cross-repository contracts.

## 6. Key technical decisions
- **No index, README or CHANGELOG update.** The spec forbids changes to existing files. The research also found that nothing in the repository indexes `docs/` and no code or test reads it, so adding the file breaks no reference.
- **No new test.** The spec says documentation only, with no tests. The file is checked directly instead: 2 lines, last byte `0a`, and an exact `diff` against the expected content.
- **Alternative rejected:** adding a CHANGELOG line to satisfy `repo-gate` rule 4. It would break FR5 and acceptance criterion 2.

## 7. Risks and constraints
- **`PLAY-G4` gate blocker.** The `mr-gate` repo-gate rule 4 requires a `CHANGELOG.md` edit, so a spec-compliant PR will get this blocker. The resolution is a human waiver at review, not a CHANGELOG edit.
- **Exact bytes.** An editor or agent could drop the trailing newline, add a blank line, or write CRLF line endings. The file's bytes must be checked before the PR is opened.
- **Diff scope.** The PR diff against `main` also includes the platform's `stories/SCRUM-1/*` files. Only `docs/e2e-w2/notes.md` is deliverable content.
- **CI.** The `test` job (pip install plus pytest on `tests/`) and the `gate` job (fails if `CI_FAIL` exists) are unaffected. No `CI_FAIL` file may be created.
- **Scale, performance, security:** not applicable to a static 36-byte document.
