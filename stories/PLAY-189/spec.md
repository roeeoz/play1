# Feature Specification Document — PLAY-189: QA-20261122-S7 add qa/s7_greeting.txt

> Status: READY_FOR_SPEC

## 1. Feature Overview

- **What:** add a text file `qa/s7_greeting.txt` to `roeeoz/play1` containing the single line `hello from s7`.
- **Problem:** QA needs a minimal, verifiable change to exercise the factory's go-back flow.
- **Actor:** a QA tester.
- The `qa/` folder already exists at the repository root (it holds `20261109-s1`, `20261110-s3`, `s3-a.sh`, `s3-hello.sh`); `qa/s7_greeting.txt` does not exist yet on `main`.

## 2. Goals & Non-Goals

### Goals
- `qa/s7_greeting.txt` exists in `roeeoz/play1` with exactly one line: `hello from s7`.

### Non-Goals
- Any other product file change in `roeeoz/play1` (the story says: "Only the file qa/s7_greeting.txt changes; nothing else in the repository"). The developer confirmed this allows the factory's plan folder `stories/PLAY-189/` on the same pull request.
- The README update of `roeeoz/play2`: dropped from this story by the developer (it is not a target repository of this project and contradicts the story's own scope line).

## 3. Functional Requirements

- FR1 — Create `qa/s7_greeting.txt` under the existing `qa/` folder at the root of `roeeoz/play1`.
- FR2 — The file's content is exactly one line: `hello from s7`.
- FR3 — No other product file in `roeeoz/play1` changes; the only other path on the pull request is the factory's plan folder `stories/PLAY-189/`.
- Edge cases: the file holds no extra lines, no leading/trailing spaces on the line, and no other text; `roeeoz/play2` is not touched.

## 4. User Experience & Behavior

- The QA tester opens the pull request and sees one new file, `qa/s7_greeting.txt`, whose content reads `hello from s7`.
- No UI, look-and-feel or runtime behaviour is involved.

## 5. Acceptance Criteria

1. The file qa/s7_greeting.txt exists at the repository root's qa/ folder.
2. It contains exactly one line: hello from s7
3. Apart from qa/s7_greeting.txt and the factory's plan folder stories/PLAY-189/, the pull request changes no other file in the repository.

## 6. Dependencies & Constraints (product-level)

- The repository's gates run on the pull request: the `play1 layout gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` — Python under `src/`, tests under `tests/`, new shell scripts executable with a shebang, no file over 200 KB) and the `pytest` test gate (`.factory/testing.md`, `.github/workflows/ci.yml`). A one-line text file under `qa/` breaks none of these rules.
- The factory's artifacts repo is the same repo (`roeeoz/play1`): the work branch also carries this story's plan folder `stories/PLAY-189/` (spec, design, plan); the developer confirmed this is allowed.
- A person merges the pull request; the factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

None needed beyond creating the file; deferred to STRUCTURE.

## 8. Open Questions

None. Resolved with the developer:
- Q1 — the `roeeoz/play2` README update is dropped from this story.
- Q2 — the plan folder `stories/PLAY-189/` is allowed on the pull request; no other product file changes.
- Whether the line ends with a trailing newline is not specified by the story; "exactly one line" is read as the single line `hello from s7` (a standard trailing newline is acceptable). STRUCTURE may confirm.
