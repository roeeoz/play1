# Plan: EWS-2 — README quotes the marker from `e2e-other-branch`

## Context

EWS-2 adds one line to the end of `README.md` in `roeeoz/play1`. The line quotes, word for word, the first line of `e2e-other-branch-marker.txt`. That file exists only on the branch `e2e-other-branch`. The acceptance criteria are: (1) `README.md` ends with `Marker from e2e-other-branch (e2e-w21-b): "<marker line 1>"`; (2) `README.md` is the only source file changed and no test is added; (3) the change is committed on the work branch `halo/feat/ews-2-20261118-154958`, which was cut from `main`, and the PR merges into `main`. The marker must be read from a real checkout or worktree of `e2e-other-branch`, never with `git show`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/EWS-2/`.

## Research findings

- **Change surface.** The only file changed is `README.md`. It has 166 lines. Its last line, `README.md:166`, is `Nothing is stored when a request is rejected.` and ends with a single `\n`, so there is no trailing blank line. No line in `README.md` starts with `Marker from`, so the new line will not duplicate one.
- **Source branch.** `origin/e2e-other-branch` exists in the checkout at `4dd65ff` ("e2e: distinctive file for the other-branch read test"). Its parent is `b7b5d0a`, which is also the tip of `origin/main` and `main`. `e2e-other-branch-marker.txt` is at the root of that branch's tree and is not on `main`. No local branch `e2e-other-branch` exists yet. `git worktree add <dir> e2e-other-branch` will create one that tracks the remote branch, because there is exactly one remote with that name.
- **Expected value.** Per `spec.md` §3, line 1 is `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22` and line 2 is `second line: only on e2e-other-branch`. This plan did not read the file itself, because FR1 requires that the implementation read it from a checkout or worktree.
- **Contracts.** The only contract is the output line format in `hld.md` §5. No API, schema or cross-repo value is touched.
- **Readers of `README.md`.** `pyproject.toml` sets `readme = "README.md"`, so the file becomes the package's long description and `pip install -e ".[test]"` reads it. Appending a plain-text line does not affect the build. No test under `tests/` reads `README.md`. The docstrings in `src/` only point to it.
- **Gate.** `.factory/testing.md` declares one required layer, `package-api`, which runs `pytest` (run by `canonical-gate`). `.github/workflows/ci.yml` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12 (job `test`). Its job `gate` fails only if `CI_FAIL` exists at the repository root. The repository has no linter or formatter.
- **Repository guidance.** There is no `AGENTS.md`, `CLAUDE.md` or `.factory/memory/` in the repository.
- **Unknowns.** None remain. The marker value is confirmed when it is read from the worktree in step 1.

## Locked decisions and assumptions

**Locked decisions**
- The output line is exactly `Marker from e2e-other-branch (e2e-w21-b): "<line 1 verbatim>"`, using plain ASCII double quotes, with no blank line before it and exactly one trailing newline (`spec.md` FR2, `hld.md` §5).
- The marker is read from `git checkout e2e-other-branch` or `git worktree add <dir> e2e-other-branch`, never with `git show` (`spec.md` FR1, §6).
- No merge, rebase or cherry-pick from `e2e-other-branch`. Nothing is committed or pushed to it. Neither commit `4dd65ff` nor the marker file reaches the work branch (`spec.md` Non-Goals, `hld.md` §6).
- Only `README.md` changes, and lines 1–166 stay byte for byte as they are (`work-items.md` t1).
- The base branch is `main` and the work branch is `halo/feat/ews-2-20261118-154958` (platform target branch).

**Assumptions**
- The files under `stories/EWS-2/` are platform process files, not source files, for acceptance criterion 2. Evidence: `spec.md` §8 and `work-items.md` t1 both exclude them. If this is wrong, the PR diff would fail criterion 2. That is a platform decision, not something this change can alter.
- The worktree lives in a temporary directory outside the repository (for example under `/tmp`). Evidence: `hld.md` §6 prefers this. If it were placed inside the repository, untracked files could be staged by mistake.

## Solution proposal

Read the marker through a temporary **worktree** created outside the repository, not through `git checkout`. A worktree never switches the branch of the work checkout, so the edit and the commit cannot land on `e2e-other-branch` by accident. It also satisfies FR1 directly.

The approach:
- Read line 1 from the worktree, with its line ending removed (both `\n` and any `\r`).
- Remove the worktree with `git worktree remove`.
- Append the formatted line to `README.md` as raw bytes, adding one final `\n`. Because `README.md` already ends with `\n`, appending directly leaves no blank line between the old last line and the new one.

Alternatives rejected:
- **`git checkout e2e-other-branch`.** It is allowed, but it moves `HEAD` of the work checkout. A missed switch-back would put the commit on the wrong branch.
- **`git show` / `git cat-file`.** Forbidden by FR1.
- **Merge or cherry-pick.** These would bring `4dd65ff` and the marker file onto the work branch, which the non-goals forbid.
- **Adding a test for the README line.** Acceptance criterion 2 forbids adding a test.

## Ordered implementation steps

1. **Read the marker from a worktree.** Run `git fetch origin e2e-other-branch` only if the ref is stale (`origin/e2e-other-branch` is present at `4dd65ff`). Then run `git worktree add /tmp/ews2-other e2e-other-branch` and read line 1 of `/tmp/ews2-other/e2e-other-branch-marker.txt`, with its line ending removed. Check that it equals `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`. If it differs, use what was read and report the difference. Do not use `git show`. Advances AC1. Test layer: none, because criterion 2 forbids a new test. Proof is the read output recorded in the evidence.
2. **Remove the worktree.** Run `git worktree remove /tmp/ews2-other` and then `git worktree prune`. Check that `git worktree list` shows only the work checkout. The local branch `e2e-other-branch` created in step 1 may stay; it is never pushed. Advances AC2 and AC3. Test layer: none, checked by command output.
3. **Append the line to `README.md`.** Confirm `git branch --show-current` is `halo/feat/ews-2-20261118-154958`. Append the bytes `Marker from e2e-other-branch (e2e-w21-b): "<line 1>"` followed by `\n` to `README.md`. Do not run an editor or formatter that could rewrite earlier lines or change line endings. Advances AC1. Test layer: none new. `pytest` (`package-api`) still runs over the installed package, whose metadata reads `README.md`.
4. **Verify the README invariants.** Check each of these:
   - `tail -n 1 README.md` equals the expected line exactly.
   - `git diff main -- README.md` shows exactly one added line and no removed lines, which proves lines 1–166 are unchanged.
   - `grep -c '^Marker from' README.md` is `1`.
   - `grep -c 'second line' README.md` is `0`.
   - The file ends with exactly one `\n`, checked with `tail -c 2 | od -c`.
   - The line contains no `\r` and no curly quotes.

   Advances AC1. Test layer: none, checked by command output.
5. **Verify the change scope.** Check each of these:
   - `git status --porcelain` lists only ` M README.md`, plus any platform files under `stories/EWS-2/`.
   - `e2e-other-branch-marker.txt` is absent from the work tree.
   - `git merge-base --is-ancestor 4dd65ff HEAD` fails, which shows `4dd65ff` is not in the branch history.

   Stage only `README.md`. Advances AC2 and AC3. Test layer: none, checked by command output.
6. **Run the gate** (see "Verification and CI gate"). Advances the requirement that CI stays green. Test layer: `package-api` (`pytest`).

Invariants: authorization, tenancy and concurrency do not apply because there is no runtime code. Idempotency: run step 3 exactly once, and the `^Marker from` count in step 4 guards against a duplicate append. Dependencies: the gate's `pip install -e ".[test]"` fetches `pypdf`, `flask>=3` and `pytest>=8` from the package index. It does not assume a warm cache. There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1. Read the marker from a worktree | t1 — Append the e2e-other-branch marker line to README.md |
| 2. Remove the worktree | t1 — Append the e2e-other-branch marker line to README.md |
| 3. Append the line to `README.md` | t1 — Append the e2e-other-branch marker line to README.md |
| 4. Verify the README invariants | t1 — Append the e2e-other-branch marker line to README.md |
| 5. Verify the change scope | t1 — Append the e2e-other-branch marker line to README.md |
| 6. Run the gate | t1 — Append the e2e-other-branch marker line to README.md |

Every work item in `work-items.md` (only t1) is covered.

## Verification and CI gate

- **Canonical gate**, in order, from the repository root: `pip install -e ".[test]"` and then `pytest` (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`). Run it once on the committed SHA. Do not use a second worktree for it.
- **Required layer.** `package-api` (`pytest`, production-path, `runBy: canonical-gate`). It can run in a pod. The authoritative result is the provider run at the PR head.
- **`gate` job.** It stays green as long as no `CI_FAIL` file is created at the repository root.
- **Provider CI.** No CI configuration change is needed. `.factory/testing.md` and `.factory/delivery-assets` need no update.
- **Done means all of the following:**
  - `pytest` passes with the same result as on `main` (the change adds no test and changes no code).
  - The `gate` job passes.
  - The checks in steps 4 and 5 hold on the committed SHA.
  - The PR diff against `main` shows only the one added `README.md` line, apart from `stories/EWS-2/`.

## Risks and scope guards

**Risks and mitigations**
- **The edit or commit lands on `e2e-other-branch`.** Mitigation: the worktree approach never moves `HEAD`, and step 3 checks the current branch.
- **Worktree files or the marker file get staged.** Mitigation: the worktree lives outside the repository, it is removed in step 2, and only `README.md` is staged.
- **The quoted text does not match exactly.** This covers case, `pr343:`, `14:22`, smart quotes, a trailing space or `\r`. Mitigation: step 4 compares bytes.
- **The end of the file is wrong.** This covers a blank line before the new line, or a missing or doubled final newline. Mitigation: append raw bytes and run the `od` check.

**Scope guards: the implement phase must NOT**
- use `git show`, `git cat-file` or any read path other than a checkout or worktree for the marker;
- merge, rebase or cherry-pick from `e2e-other-branch`, or commit or push anything to it;
- add the marker file, any other file, or a test;
- change code, CI, `pyproject.toml`, `CHANGELOG.md` or `.factory/`;
- reword, reformat, re-wrap or normalise line endings anywhere in `README.md`;
- quote line 2 of the marker file;
- edit `spec.md`, `hld.md` or `work-items.md`;
- make `pytest` or the `gate` job green by skipping, deleting or weakening anything. If either fails for reasons unrelated to the README, report it as blocked.

## Clarification outcomes

None.
