# Feature Specification Document

## 1. Feature Overview
- **Summary:** Add a small run-notes document to the repository for the e2e-w2 verification run. The document is the new file `docs/e2e-w2/notes.md`.
- **Problem statement:** The e2e-w2 verification run needs a small notes file in the repository that records the run's identifier.
- **Target users / actors:** the project team and the developer running the e2e-w2 verification. Reviewers check the file's content against what the developer asked for.

---

## 2. Goals & Non-Goals

### Goals
- Create the new file `docs/e2e-w2/notes.md`, which also creates the new folder `docs/e2e-w2/`.
- Line 1 of the file is the heading `# e2e-w2 notes`.
- Line 2 is the line the developer gave: `Run: e2e-w2-20261118`.

### Non-Goals
- Changing any existing file, including `CHANGELOG.md`, `README` and any `docs/` index.
- Tests, code, configuration or CI changes, and any runtime change.
- Any content beyond the heading and the developer's one line.
- Any content or commits from other branches, such as `e2e-other-branch`. The work is based on `main` only.

---

## 3. Functional Requirements
- **FR1:** A new file exists at `docs/e2e-w2/notes.md`.
- **FR2:** Line 1 of the file is exactly `# e2e-w2 notes`.
- **FR3:** Line 2 of the file is exactly `Run: e2e-w2-20261118`, with the same characters, case and punctuation.
- **FR4:** The file has exactly these two lines, with no blank line between them and nothing after them, and ends with a single trailing newline.
- **FR5:** The change adds this one file and nothing else. No existing file is modified or deleted.
- **Edge cases:** the folder `docs/e2e-w2/` does not exist on `main` and is created by adding the file. The file must not take any content from another branch.

---

## 4. User Experience & Behavior
- **Flow:** a reader opens `docs/e2e-w2/notes.md` in the repository or on the forge. It renders as a level-1 heading, "e2e-w2 notes", followed by one line of text: "Run: e2e-w2-20261118".
- **Output format:** plain Markdown. The file is exactly the following two lines, followed by a newline:
  ```
  # e2e-w2 notes
  Run: e2e-w2-20261118
  ```
- There are no states, error messages or interactions.

---

## 5. Acceptance Criteria
1. The file exists at that path with the heading and the developer's line.
2. No existing file is modified.
3. Documentation only: no tests, no runtime change.
4. `docs/e2e-w2/notes.md` is exactly two lines with no blank line between them: line 1 is `# e2e-w2 notes`, line 2 is `Run: e2e-w2-20261118`, and the file ends with a trailing newline.

---

## 6. Dependencies & Constraints (product-level)
- The work is based on `main`, and the pull request targets `main`. Nothing from any other branch is included.
- The repository's CI gates still run and must pass. No `CI_FAIL` file may be created.
- A person merges the pull request after review.
- Because no existing file may change, this story has no CHANGELOG entry, unlike some earlier stories.

---

## 7. Technical Design (deferred to STRUCTURE)
This is a single new documentation file, so it needs no design work. The pull request should show one added file against `main` and no modified or deleted files.

---

## 8. Open Questions
- None. The developer gave the body line (`Run: e2e-w2-20261118`) and confirmed the format: two lines, no blank line between them, trailing newline.
