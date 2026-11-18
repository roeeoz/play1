# High-Level Design — EWS-3: e2e-w21-x live proof document

## 1. System Overview
- **What is being built:** one static markdown file, `docs/live-e2e/e2e-w21-x.md`, in `roeeoz/play1`.
- **Problem:** a developer needs a small, checkable piece of evidence that the delivery line (intake → design → implementation → PR) worked end to end for run `e2e-w21-x`.
- **Responsibility:** add the file with exactly the specified content, in one reviewable PR to `main`, and change nothing else.

## 2. Architecture Overview
- **Component:** one documentation artifact. There are no services, modules, code or runtime parts.
- **Boundary:** the new directory `docs/live-e2e/`, which this story creates. Today `docs/` holds only `argo-agent-runs.md` and `plans/`.
- **Ownership:** the single work item owns `docs/live-e2e/e2e-w21-x.md`.
- **External dependencies:** none.

## 3. Data Flow Design
- The fixed content comes from the story, is written to the file, committed on the work branch and opened as a PR against `main`. A person reviews and merges it.
- Nothing runs at runtime and there are no events or async processing.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| Proof document `docs/live-e2e/e2e-w21-x.md` | Record the run `e2e-w21-x` as a level-1 heading plus one paragraph | In: the fixed content from the spec. Out: the committed file | `roeeoz/play1` |

## 5. Interface Contracts
- **File contract (byte-exact):** `# Live coding proof` + LF + LF + `Run: e2e-w21-x` + LF. The file is UTF-8 with no BOM, no CRLF, no trailing whitespace and no front-matter.
- **Rendered contract:** on GitHub, the file shows one H1 "Live coding proof" above a paragraph "Run: e2e-w21-x".
- **Cross-repo contracts:** none. There are also no APIs or event schemas.

## 6. Key Technical Decisions
- **One work item, not split:** the deliverable is a single file, and any split would be micro-fragmentation.
- **No index, README or CHANGELOG update:** the repo has no docs index, and the spec's non-goals forbid touching existing files.
- **No test added:** FR3 rules out adding a test. Acceptance is checked by inspecting the diff and the file bytes.
- **Final newline:** the file ends with one LF, per the working assumption in spec §8. The repo has no `.editorconfig`, `.gitattributes`, markdownlint or pre-commit config, so no tooling will change the bytes.

## 7. Risks & Constraints
- **Byte exactness:** an editor or tool could add CRLF, a BOM or trailing whitespace. The implementer should check the committed bytes, for example with a hex dump or `git diff` on `main`.
- **Scope reading:** the PR diff to `main` will also include the plan documents under `stories/EWS-3/` from the work branch. Review should count one *product* file under FR3.
- **CI:** the `test` job only runs pytest over `tests/`, and the `gate` job only checks for a root `CI_FAIL` file. Neither reads `docs/`, so neither result can change.
- **Scale, performance and security:** not applicable. The change is a static public documentation file with no secrets.
