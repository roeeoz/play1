# Feature Specification Document

## 1. Feature Overview
- **Summary:** Add a single new documentation file, `docs/live-e2e/e2e-w21-x.md`, that records verification run `e2e-w21-x`.
- **Problem statement:** A developer needs a small, checkable piece of evidence that the delivery line (intake → design → implementation → pull request) works end to end for this run. A merged, documentation-only pull request that adds a known file with known content gives that evidence.
- **Target users / actors:** A developer who checks the delivery line by inspecting the pull request and the file it adds.

---

## 2. Goals & Non-Goals

### Goals
- Add `docs/live-e2e/e2e-w21-x.md` with exactly the specified content.
- Deliver it as one small, reviewable pull request to `main` that adds this file and nothing else.

### Non-Goals
- Changing any existing file, including `README.md`, `CHANGELOG.md`, any index or table of contents, and any configuration or CI file.
- Adding or changing tests.
- Any change to runtime behaviour, code or packaging.
- Adding other proof files, front-matter, extra headings or links to the new document.

---

## 3. Functional Requirements
- **FR1 — New file at an exact path.** The change creates `docs/live-e2e/e2e-w21-x.md`. The `docs/live-e2e/` directory doesn't exist yet and comes into being with this file.
- **FR2 — Exact content.** The file contains exactly these three lines and nothing else:
  1. `# Live coding proof`
  2. (an empty line)
  3. `Run: e2e-w21-x`

  A single newline ends the last line. There is no front-matter, no trailing whitespace and no further content.
- **FR3 — Documentation only.** No existing file is modified, renamed or deleted, and no test is added. The change set is exactly one added file.
- **Inputs:** none. The content is fixed by the story.
- **Outputs:** the new file in the repository, delivered through a pull request to `main`.
- **Edge cases:** none expected. The path is free on `main`, and nothing in `.gitignore` excludes it.

---

## 4. User Experience & Behavior
- **Key flow:** The developer opens the pull request and sees one added file, `docs/live-e2e/e2e-w21-x.md`, and no other changes. Opening the file, they see the heading "Live coding proof" followed by the line "Run: e2e-w21-x".
- **Rendered look:** In a markdown viewer such as GitHub, the file shows a single level-1 heading, "Live coding proof", above a paragraph reading "Run: e2e-w21-x".
- **Required checks:** The repository's existing checks (the pytest suite and the CI gate) behave exactly as they do on `main`.

---

## 5. Acceptance Criteria
1. The new file exists at that exact path with that exact content.
2. No existing file is modified.
3. No runtime behaviour changes: documentation only; no test is added.

---

## 6. Dependencies & Constraints (product-level)
- The work is based on `main` and its pull request targets `main`.
- A person reviews and merges the pull request; the factory never merges.
- The repository's existing pre-merge checks, `pytest` over `tests/` and the CI gate job, apply unchanged. This change neither touches nor relaxes them.
- This story depends on no other story.

---

## 7. Technical Design (deferred to STRUCTURE)
This story has no design decisions to make. It adds one static markdown file at a fixed path with fixed content. The STRUCTURE stage only needs to confirm a single work item at the smallest size.

---

## 8. Open Questions
- None blocking.
- Working assumption: the file ends with a single newline after `Run: e2e-w21-x`. The story's "exactly this content" doesn't say how the file ends. If a byte-exact check is meant to exclude the final newline, the developer should say so before implementation.
