## Context

SCRUM-1 adds one static run-notes document, `docs/e2e-w2/notes.md`, and ports one file, `e2e-other-branch-marker.txt`, from `e2e-other-branch` to the repository root, in `play1` on the work branch `halo/feat/scrum-1-20261118-182955`, cut from `main`, which is also where the PR merges. The acceptance criteria: the file exists with the heading `# e2e-w2 notes` and the developer's line `Run: e2e-w2-20261118`, exactly two lines with a trailing newline (AC1, AC4); no existing file is modified (AC2); documentation only, with no tests and no runtime change (AC3). The marker-file port was added to the scope by the story owner on 2026-11-18; `spec.md` has not yet been amended to say so (see Assumptions). `spec.md`, `hld.md` and `work-items.md` are in this folder (`stories/SCRUM-1/`), next to this file.

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
- **Marker file source:** `origin/e2e-other-branch` is at `4dd65ff`. `e2e-other-branch-marker.txt` there is blob `0bf21798cef8d1b9194e74c76fcc391ddbf5b901`: 101 bytes, 2 lines, LF, trailing newline, no CR. The path does not exist on `main` or on the work branch, so the port adds a new file and overwrites nothing.
- **External data:** none beyond that one file's content.
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
- The marker file is ported at the same path (`e2e-other-branch-marker.txt`, repository root) with exactly the content of `origin/e2e-other-branch:e2e-other-branch-marker.txt`, taken with `git show` (story owner's scope change, work item t2).
- The base is `main` only. No merge, cherry-pick or rebase of `e2e-other-branch`; no commit from it or any other branch enters the work branch. Apart from that one file's content, nothing comes from another branch (target-branch rule).
- The `repo-gate` `PLAY-G4` (CHANGELOG) blocker needs a human waiver. It is never resolved by editing `CHANGELOG.md` (`hld.md` §7, work item t1).

**Assumptions**
- The story owner's scope change stands even though `spec.md` still lists content from `e2e-other-branch` as a non-goal (§2) and FR5 / §7 say one added file.
  - Evidence: the owner's instruction on 2026-11-18. The plan stage cannot edit `spec.md`.
  - If wrong: drop t2 and steps 3–4; t1 is unaffected.
- The platform's `stories/SCRUM-1/*` files in the PR diff do not count as "modifying an existing file" under AC2.
  - Evidence: `hld.md` §7 and t1 exclude them from deliverable content.
  - If wrong: a reviewer has to waive them. The deliverable itself does not change.

## Solution proposal

Add two new files. First, `docs/e2e-w2/notes.md` with the exact 36-byte content. Write it byte-exactly, for example with `printf '# e2e-w2 notes\nRun: e2e-w2-20261118\n' > docs/e2e-w2/notes.md`. Avoid an editor that might add CRLF line endings, a BOM or extra lines. Second, `e2e-other-branch-marker.txt` at the repository root, written with `git show origin/e2e-other-branch:e2e-other-branch-marker.txt > e2e-other-branch-marker.txt` so its bytes match the source blob exactly.

Key decisions:
- **No index, README or CHANGELOG entry.** The spec forbids changes to existing files, and nothing indexes `docs/`.
- **No new test.** AC3 forbids tests. Byte-level shell checks verify the files instead.
- **Port by content.** `git show` copies one file without touching history, so the base stays `main`.

Alternatives rejected:
- **A CHANGELOG line to satisfy `PLAY-G4`.** It violates FR5 and AC2.
- **A pytest asserting the file content.** It violates AC3.
- **Merging or cherry-picking `e2e-other-branch` for the marker file.** It would carry that branch's commits into the work and break the `main`-only base.

## Ordered implementation steps

1. **Create the file (AC1, AC4).** Create `docs/e2e-w2/notes.md`, which also creates `docs/e2e-w2/`, with exactly `# e2e-w2 notes` LF `Run: e2e-w2-20261118` LF.
   - Test layer: none. AC3 forbids a test, so the file is checked directly in step 2.
2. **Verify the file's bytes (AC4).** All four checks must pass:
   - `wc -l docs/e2e-w2/notes.md` prints `2`.
   - `wc -c` prints `36`.
   - `tail -c1 docs/e2e-w2/notes.md | od -An -tx1` prints `0a`.
   - `diff <(printf '# e2e-w2 notes\nRun: e2e-w2-20261118\n') docs/e2e-w2/notes.md` prints nothing.
   
   Also confirm there is no `\r` and no BOM.
3. **Port the marker file (t2).** From the repository root, run `git fetch origin e2e-other-branch` if needed, then `git show origin/e2e-other-branch:e2e-other-branch-marker.txt > e2e-other-branch-marker.txt`. Commit it as a new file on the work branch. Do not merge, cherry-pick or rebase.
   - Test layer: none; checked directly in step 4.
4. **Verify the marker file's bytes (t2).** All checks must pass:
   - `git hash-object e2e-other-branch-marker.txt` prints `0bf21798cef8d1b9194e74c76fcc391ddbf5b901`.
   - `cmp <(git show origin/e2e-other-branch:e2e-other-branch-marker.txt) e2e-other-branch-marker.txt` prints nothing.
   - `wc -lc e2e-other-branch-marker.txt` prints `2` lines and `101` bytes.
5. **Verify the diff scope (AC2, AC3).**
   - Outside `stories/SCRUM-1/`, `git diff --name-status main...HEAD` shows exactly two lines: `A	docs/e2e-w2/notes.md` and `A	e2e-other-branch-marker.txt`.
   - There are no `M` or `D` entries; `README.md` and `CHANGELOG.md` are untouched.
   - No `CI_FAIL` file exists.
   - No commit comes from another branch: `git log main..HEAD` shows only this story's commits, and `git merge-base --is-ancestor 4dd65ff HEAD` fails.
6. **Run the canonical gate (AC3, no regression).** Run `pip install -e ".[test]" && pytest`. The suite must stay green and unchanged.
   - Test layer: `package-api` (pytest).
7. **Write the PR description.** It states that the approved spec forbids a CHANGELOG entry and that the `PLAY-G4` repo-gate blocker needs a human waiver, and that the story owner brought the marker-file port into scope and it was copied by content from `e2e-other-branch`, not merged.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–2 | t1: Add docs/e2e-w2/notes.md run-notes file for the e2e-w2 verification run |
| 3–4 | t2: Port e2e-other-branch-marker.txt from e2e-other-branch to the repository root |
| 5–7 | t1 and t2 (shared verification, gate and PR description) |

t1 and t2 are independent; neither depends on the other.

## Verification and CI gate

**Canonical gate:** run `pip install -e ".[test]"`, then `pytest`, once on the committed SHA. The provider CI `test` job runs the same commands on the PR head, and that run is the authoritative result for the `package-api` layer. It runs in a pod.

**`gate` job:** stays green because no `CI_FAIL` file is added.

**CI configuration:** no provider CI change is needed.

**Factory files:** `.factory/testing.md` adds no extra obligation. `.factory/delivery-assets` does not apply.

**Done means:**
- `pytest` passes with the same tests as on `main`.
- All byte checks in steps 2 and 4 pass.
- The deliverable diff against `main` is exactly two added files.

## Risks and scope guards

**Risks**
- **Byte drift:** a missing trailing newline, CRLF line endings, a BOM or a blank line would break AC4. Steps 2 and 4 catch this before the PR opens.
- **Spec mismatch:** until `spec.md` is amended, a reviewer may flag `e2e-other-branch-marker.txt` against spec §2 and FR5. The PR description names the owner's scope change.
- **`PLAY-G4` blocker:** expected on a spec-compliant PR. A human waives it at review.

**Do NOT**
- Edit `CHANGELOG.md`, `README.md`, `docs/argo-agent-runs.md`, anything under `docs/plans/`, or any other existing file.
- Add tests, code, configuration, CI files or a `CI_FAIL` marker.
- Add content beyond the two lines to `docs/e2e-w2/notes.md`, or change any byte of the ported marker file.
- Merge, cherry-pick or rebase onto `e2e-other-branch` or any branch other than `main`, or take any file from it other than `e2e-other-branch-marker.txt`.
- Fix the `testbed` typo in `README.md`; it goes in its own story.
- Edit `stories/SCRUM-1/spec.md`, `hld.md` or `work-items.md`.
- Skip, disable or weaken `pytest` or the `gate` job. If a check fails, report it as blocked; never make it green by changing it.

## Clarification outcomes

- 2026-11-18: the story owner brought the port of `e2e-other-branch-marker.txt` (same path, exact content, via `git show`, base stays `main`) into scope, and kept the `README.md` typo out of scope.
