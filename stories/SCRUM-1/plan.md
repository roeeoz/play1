## Context

SCRUM-1 adds one static run-notes document, `docs/e2e-w2/notes.md`, to `play1` on the work branch `halo/feat/scrum-1-20261118-182955`, cut from `main`, which is also where the PR merges. The acceptance criteria: the file exists with the heading `# e2e-w2 notes` and the developer's line `Run: e2e-w2-20261118`, exactly two lines with a trailing newline (AC1, AC4); no existing file is modified (AC2); documentation only, with no tests and no runtime change (AC3). `spec.md`, `hld.md` and `work-items.md` are in this folder (`stories/SCRUM-1/`), next to this file.

## Research findings

- **Change surface:** `docs/` holds only `docs/argo-agent-runs.md` and `docs/plans/`. `docs/e2e-w2/` does not exist yet and is created when the file is added. The new file is the whole change surface.
- **References into `docs/`:** nothing indexes `docs/`. No code under `src/` or test under `tests/` reads it, and `pyproject.toml` does not package it. Its only mention in `README.md` (`README.md:4`) points to an external `pdlc-infra` path. Adding the file breaks no reference.
- **Contract:** the file's exact bytes, as defined in `hld.md` §5:
  - `# e2e-w2 notes` LF `Run: e2e-w2-20261118` LF
  - UTF-8, 36 bytes, 2 lines
  - The byte count was verified with `printf '# e2e-w2 notes\nRun: e2e-w2-20261118\n' | wc -c`, which prints `36`.
- **Gate (`.factory/testing.md`, `.github/workflows/ci.yml`):**
  - The `test` job runs `pip install -e ".[test]"`, then `pytest`, on Python 3.12. It is the one declared layer (`package-api`, `runBy: canonical-gate`).
  - The `gate` job fails only if `CI_FAIL` exists at the repository root.
  - The repository has no linter, formatter or type checker.
- **Repo instructions:** there is no `AGENTS.md`, `CLAUDE.md` or `.factory/memory/`. `.factory/delivery-assets` does not exist, and this change adds no binary.
- **External data:** none.
- **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**
- The path is `docs/e2e-w2/notes.md` (spec FR1).
- The content is exactly the two lines `# e2e-w2 notes` and `Run: e2e-w2-20261118`:
  - no blank line between them
  - LF line endings
  - one trailing newline
  
  Sources: spec FR2–FR4 and AC4, `hld.md` §5.
- No existing file changes, `CHANGELOG.md` and `README.md` included (spec FR5, AC2; `hld.md` §2).
- No tests, code, configuration or CI change (spec AC3, `hld.md` §6).
- The base is `main` only. Nothing comes from `e2e-other-branch` or any other branch (spec §6, target-branch rule).
- The `repo-gate` `PLAY-G4` (CHANGELOG) blocker needs a human waiver. It is never resolved by editing `CHANGELOG.md` (`hld.md` §7, work item t1).

**Assumptions**
- The platform's `stories/SCRUM-1/*` files in the PR diff do not count as "modifying an existing file" under AC2.
  - Evidence: `hld.md` §7 and t1 exclude them from deliverable content.
  - If wrong: a reviewer has to waive them. The deliverable itself does not change.

## Solution proposal

Add the single file `docs/e2e-w2/notes.md` with the exact 36-byte content. Write it byte-exactly, for example with `printf '# e2e-w2 notes\nRun: e2e-w2-20261118\n' > docs/e2e-w2/notes.md`. Avoid an editor that might add CRLF line endings, a BOM or extra lines.

Key decisions:
- **No index, README or CHANGELOG entry.** The spec forbids changes to existing files, and nothing indexes `docs/`.
- **No new test.** AC3 forbids tests. Byte-level shell checks verify the file instead.

Alternatives rejected:
- **A CHANGELOG line to satisfy `PLAY-G4`.** It violates FR5 and AC2.
- **A pytest asserting the file content.** It violates AC3.

## Ordered implementation steps

1. **Create the file (AC1, AC4).** Create `docs/e2e-w2/notes.md`, which also creates `docs/e2e-w2/`, with exactly `# e2e-w2 notes` LF `Run: e2e-w2-20261118` LF.
   - Test layer: none. AC3 forbids a test, so the file is checked directly in step 2.
2. **Verify the file's bytes (AC4).** All four checks must pass:
   - `wc -l docs/e2e-w2/notes.md` prints `2`.
   - `wc -c` prints `36`.
   - `tail -c1 docs/e2e-w2/notes.md | od -An -tx1` prints `0a`.
   - `diff <(printf '# e2e-w2 notes\nRun: e2e-w2-20261118\n') docs/e2e-w2/notes.md` prints nothing.
   
   Also confirm there is no `\r` and no BOM.
3. **Verify the diff scope (AC2, AC3).**
   - Outside `stories/SCRUM-1/`, `git diff --name-status main...HEAD` shows exactly one line: `A	docs/e2e-w2/notes.md`.
   - There are no `M` or `D` entries.
   - No `CI_FAIL` file exists.
   - No commit comes from another branch: check `git log main..HEAD`.
4. **Run the canonical gate (AC3, no regression).** Run `pip install -e ".[test]" && pytest`. The suite must stay green and unchanged.
   - Test layer: `package-api` (pytest).
5. **Write the PR description.** It states that the approved spec forbids a CHANGELOG entry and that the `PLAY-G4` repo-gate blocker needs a human waiver.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–5 | t1: Add docs/e2e-w2/notes.md run-notes file for the e2e-w2 verification run |

t1 is the only work item, and every step maps to it.

## Verification and CI gate

**Canonical gate:** run `pip install -e ".[test]"`, then `pytest`, once on the committed SHA. The provider CI `test` job runs the same commands on the PR head, and that run is the authoritative result for the `package-api` layer. It runs in a pod.

**`gate` job:** stays green because no `CI_FAIL` file is added.

**CI configuration:** no provider CI change is needed.

**Factory files:** `.factory/testing.md` adds no extra obligation. `.factory/delivery-assets` does not apply.

**Done means:**
- `pytest` passes with the same tests as on `main`.
- All byte checks in step 2 pass.
- The deliverable diff against `main` is exactly one added file.

## Risks and scope guards

**Risks**
- **Byte drift:** a missing trailing newline, CRLF line endings, a BOM or a blank line would break AC4. Step 2's checks catch this before the PR opens.
- **`PLAY-G4` blocker:** expected on a spec-compliant PR. A human waives it at review.

**Do NOT**
- Edit `CHANGELOG.md`, `README.md`, `docs/argo-agent-runs.md`, anything under `docs/plans/`, or any other existing file.
- Add tests, code, configuration, CI files or a `CI_FAIL` marker.
- Add content beyond the two lines.
- Bring in commits or content from `e2e-other-branch` or any branch other than `main`.
- Edit `stories/SCRUM-1/spec.md`, `hld.md` or `work-items.md`.
- Skip, disable or weaken `pytest` or the `gate` job. If a check fails, report it as blocked; never make it green by changing it.

## Clarification outcomes

None.
