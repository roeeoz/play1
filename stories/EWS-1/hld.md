# High-Level Design — EWS-1: `e2e-w21-a` live proof document

## 1. System overview
- **What is being built:** one static Markdown file, `docs/live-e2e/e2e-w21-a.md`, that records the live verification run `e2e-w21-a`.
- **Problem:** the developer needs a small, harmless change to confirm the Halo delivery pipeline works end to end: define, structure, implement, then a pull request.
- **Responsibility:** add the file at the exact path with the exact bytes, and change nothing else.

## 2. Architecture overview
- **Repository:** `roeeoz/play1` only.
- **Component:** a documentation file under `docs/`. It is not a runtime part of the product: packaging only includes `src` (`pyproject.toml`, `where = ["src"]`), and pytest only collects `tests/`.
- **External dependencies:** none.

## 3. Data flow
- There is no runtime data flow. The file is added on the work branch, appears in the pull request diff, and a person merges it after review.
- The forge renders it as a level-1 heading, "Live coding proof", followed by a paragraph that reads "Run: e2e-w21-a".

## 4. Component breakdown
| Component | Responsibility | Inputs / outputs | Repository |
|---|---|---|---|
| `docs/live-e2e/e2e-w21-a.md` (new) | Records the live run `e2e-w21-a` | None / the static Markdown content in FR2 | roeeoz/play1 |

## 5. Interface contracts
- There are no APIs, events or cross-repo contracts.
- The only contract is the file's path and its bytes: `# Live coding proof\n\nRun: e2e-w21-a\n`.

## 6. Key technical decisions
- **No changelog entry.** The repo usually adds a line to `CHANGELOG.md`, but the spec's non-goals and acceptance criterion 2 forbid editing any existing file.
- **No new test.** Acceptance criterion 3 says no test is added. The file's content is checked by reading the diff.
- **One trailing newline.** The spec assumes it, and no repo rule (`.gitattributes`, `.editorconfig`) changes it.

## 7. Risks and constraints
- **Exact bytes:** front matter, extra blank lines, trailing spaces or a missing or doubled final newline would fail acceptance criterion 1.
- **Scope creep:** habit could lead to editing `CHANGELOG.md` or adding a link or index entry. Any of these fails acceptance criterion 2.
- **Pipeline files on the branch:** the planning files under `stories/EWS-1/` also appear on the work branch. They belong to the pipeline and are not part of the deliverable.
- **CI:** the existing `pytest` job and the `CI_FAIL` gate run as usual and are unaffected.
- **Merge:** a person merges the pull request; the factory never does.
