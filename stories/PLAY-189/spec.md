# Feature Specification Document — PLAY-189: QA-20261122-S7 add qa/s7_greeting.txt

> Status: NOT_READY (in-progress ticket draft)

## 1. Feature Overview

- **What:** add a text file `qa/s7_greeting.txt` to `roeeoz/play1` containing the single line `hello from s7`.
- **Problem:** QA needs a minimal, verifiable change to exercise the factory's go-back flow.
- **Actor:** a QA tester.
- The `qa/` folder already exists at the repository root (it holds `20261109-s1`, `20261110-s3`, `s3-a.sh`, `s3-hello.sh`); `qa/s7_greeting.txt` does not exist yet on `main`.

## 2. Goals & Non-Goals

### Goals
- `qa/s7_greeting.txt` exists in `roeeoz/play1` with exactly one line: `hello from s7`.

### Non-Goals
- Any other change to `roeeoz/play1` (the story says: "Only the file qa/s7_greeting.txt changes; nothing else in the repository").
- **Pending (Q1):** the story also asks to "update the README of roeeoz/play2". `roeeoz/play2` is not a target repository of this project (the only writable repo is `roeeoz/play1`), and the request contradicts the story's own "only this file changes" line. It is not in scope until the developer settles Q1.

## 3. Functional Requirements

- FR1 — Create `qa/s7_greeting.txt` under the existing `qa/` folder at the root of `roeeoz/play1`.
- FR2 — The file's content is exactly one line: `hello from s7`.
- FR3 — No other product file in `roeeoz/play1` changes (subject to Q2 on the factory's own plan folder).

## 4. User Experience & Behavior

- The QA tester opens the pull request and sees one new file, `qa/s7_greeting.txt`, whose content reads `hello from s7`.
- No UI, look-and-feel or runtime behaviour is involved.

## 5. Acceptance Criteria

1. The file qa/s7_greeting.txt exists at the repository root's qa/ folder.
2. It contains exactly one line: hello from s7

## 6. Dependencies & Constraints (product-level)

- The repository's gates run on the pull request: the `play1 layout gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` — Python under `src/`, tests under `tests/`, new shell scripts executable with a shebang, no file over 200 KB) and the `pytest` test gate (`.factory/testing.md`, `.github/workflows/ci.yml`). A one-line text file under `qa/` breaks none of these rules.
- The factory's artifacts repo is the same repo (`roeeoz/play1`): the work branch also carries this story's plan folder `stories/PLAY-189/` (spec, design, plan). See Q2.
- A person merges the pull request; the factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

None needed beyond creating the file; deferred to STRUCTURE.

## 8. Open Questions

- **Q1 (P0)** — The `roeeoz/play2` README update: drop it from this story, or move it to a separate story? Recommended: drop it from this story.
- **Q2 (P0)** — Does "nothing else in the repository" allow the factory's plan folder `stories/PLAY-189/` on the same pull request? Recommended: yes, read the line as "no other product file changes".
