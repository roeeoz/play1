# Plan — PLAY-150: QA-20261108-S4 greeting script + bats-free test

## Context

PLAY-150 adds two items to roeeoz/play1:

- `qa/s4-greet.sh`, a POSIX greeting script that prints exactly `hello from s4` and exits 0.
- `qa/s4-greet.test.sh`, a self-contained test with no bats. It runs the greeting script and reports PASS (exit 0) or FAIL (non-zero).

It also adds one `CHANGELOG.md` bullet under `## Unreleased`, which the repo PR gate requires.

The acceptance criteria are spec scenarios 1–7 in `spec.md` §5. Work item `t1` refines them into AC1–AC11 in `work-items.md`. In short they cover the greeting output, a passing test, failure on wrong output, failure on a missing or failing script, a 3-file scope boundary, the S3 regression, and traceability with green checks.

The change goes on work branch `halo/feat/play-150-20261108-063753`, and its PR targets `qa-20261108-s4-base`. `spec.md` (requirement), `hld.md` (design) and `work-items.md` (breakdown) sit next to this file in `stories/PLAY-150/`.

## Research findings

**Change surface (all new except the changelog):**
- `qa/` contains only `qa/s3-hello.sh`, mode `100755` (`git ls-files -s qa`). It has three lines:
  - `qa/s3-hello.sh:1`: `#!/bin/sh`
  - `qa/s3-hello.sh:2`: a one-line `#` purpose comment
  - `qa/s3-hello.sh:3`: `printf 'hello\n'`

  This is the style reference.
- `CHANGELOG.md:3` is `## Unreleased`. `CHANGELOG.md:5` is the only bullet: ``- PLAY-114: add `qa/s3-hello.sh`, a helper script that prints `hello`.`` The new bullet follows this form.
- `qa/s4-greet.sh` and `qa/s4-greet.test.sh` do not exist yet. Both are new.

**Contracts:**
- Greeting stdout is the 14 bytes `hello from s4` plus LF, with exit 0 and empty stderr (`hld.md` §5).
- The test exits 0 only on PASS and 1 on any failure. It prints a `PASS` line on stdout, or a `FAIL` line with a reason on stderr (`hld.md` §4–5).
- There are no cross-repo contracts.

**Repo PR gate:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` has two rules that apply here:
- Rule 2: a new shell script must be executable and start with a shebang.
- Rule 4 (`PLAY-G4`, blocker): the PR must add a line under `## Unreleased` in `CHANGELOG.md`.

**Canonical CI gate:** `.github/workflows/ci.yml` has two jobs:
- `test`: `pip install -e ".[test]"`, then `pytest`, on Python 3.12.
- `gate`: fails if and only if `CI_FAIL` exists at the repo root.

`.factory/testing.md` declares one required layer, `package-api` (`pytest`, `runBy: canonical-gate`). There is no linter, formatter or shell layer. CI never runs `qa/` scripts (RK1).

**Existing regression coverage:** `tests/test_qa_s3_greeting.py` runs `qa/s3-hello.sh` and asserts:
- stdout is `"hello\n"`, stderr is empty, and the exit code is 0;
- the file starts with `#!/bin/sh` followed by a comment line;
- the file has LF line endings.

It covers spec scenario 6 in CI without any change.

**Branch topology (fact):**
- `qa-20261108-s4-base` is `90f1a31`, one commit on top of `d61f25b`. That commit adds `qa/s4-base-marker.txt`.
- The work branch's merge-base with the base branch is `d61f25b`. The work branch does not contain `90f1a31`.
- `git diff --name-status FETCH_HEAD...HEAD`, with FETCH_HEAD being the fetched base, currently lists only the three `stories/PLAY-150/` files. The three-dot (merge-base) diff therefore does not show the marker as deleted.
- A two-dot diff (`HEAD FETCH_HEAD`) does show the marker as a difference.

**Tooling:** `/usr/bin/dash` is available in the pod, so a POSIX check under dash is possible. `shellcheck` and `bats` are not installed.

**Unknowns remaining:** none that block. The exact PASS/FAIL wording is left open by `spec.md` §4 and is fixed below.

## Locked decisions and assumptions

**Locked decisions:**
- **Files.** Outside `stories/PLAY-150/`, exactly three paths: `A qa/s4-greet.sh`, `A qa/s4-greet.test.sh`, and `M CHANGELOG.md` with one added line. Sources: `spec.md` FR7 and scenario 5, the developer decision on P0-1/P0-2 recorded in `spec.md` §6, and `work-items.md` AC8.
- **Script style.** Both scripts have mode `100755`, a `#!/bin/sh` first line, a one-line `#` comment as the second line, LF line endings, and POSIX sh only. Sources: `hld.md` §5, `work-items.md` AC2 and AC6, and repo-gate rule 2.
- **Test design.** Sources: `hld.md` §6 and `work-items.md` AC6.
  - The test finds the greeting script relative to its own path.
  - It executes the script directly, not via `sh`.
  - It compares bytes exactly, preserving trailing newlines.
  - It writes no temp files and has no redirect hook, env var or argument.
- **Out of scope.** No pytest file, no CI wiring, no `--help`, and no README change. Sources: `spec.md` §2 Non-Goals and `hld.md` §6.
- **Target branch.** `qa-20261108-s4-base`, fixed by the platform. Scope is measured against it.

**Assumptions:**
- **Merge-base diff.** The PR diff is a merge-base (three-dot) diff, as GitHub computes it and as `work-items.md` AC8 specifies. Evidence: the three-dot diff today shows no marker deletion. If wrong, a two-dot view shows `qa/s4-base-marker.txt` as deleted. The fix is the platform's branch handling, not a file change.
- **Wording.** The PASS/FAIL wording is `PASS: qa/s4-greet.sh printed 'hello from s4'` and `FAIL: <reason>`. Evidence: `spec.md` §4 leaves the wording open, and `hld.md` §5 only requires the `PASS`/`FAIL` tokens and a reason. If wrong, only the message strings change.
- **Changelog bullet text.** ``- PLAY-150: add `qa/s4-greet.sh`, a helper script that prints `hello from s4`, and its bats-free test `qa/s4-greet.test.sh`.`` Evidence: it mirrors `CHANGELOG.md:5`. If wrong, only the text changes.

## Solution proposal

The approach is two standalone POSIX sh scripts in `qa/`, next to the S3 precedent, plus one changelog bullet. No package, test-suite or CI code is touched.

**`qa/s4-greet.sh`** is a three-line copy of the S3 shape:
- the shebang;
- a purpose comment;
- `printf 'hello from s4\n'`.

It ignores arguments and writes no stderr.

**`qa/s4-greet.test.sh`** works in these steps:
1. It resolves its own directory with `dirname -- "$0"` (POSIX) and builds the path to `s4-greet.sh`. The result does not depend on the working directory (AC3).
2. If the target is missing (`[ -e ]` fails) or not executable (`[ -x ]` fails), it prints `FAIL` with that reason to stderr and exits 1 (AC5).
3. It executes the target directly and captures stdout with a sentinel so trailing newlines survive: `out=$("$target"; rc=$?; printf x; exit $rc)`. It then reads the status from `$?` and strips the trailing `x`.
4. If the status is non-zero, it prints `FAIL: exited with status N` and exits 1 (AC5).
5. It compares `out` exactly with the expected string `hello from s4` plus a literal newline, built with `printf` or a quoted multi-line literal. This catches a wrong line, extra lines and a missing newline (AC4). A mismatch prints `FAIL: unexpected output` with the captured output and exits 1.
6. Otherwise it prints `PASS: …` on stdout and exits 0 (AC3).

The script uses no `set -e`, because the failure paths are handled explicitly. It uses no temp files, network or clock.

**Alternatives rejected:**
- A pytest file for S4, which the S3 precedent had. It would be a 4th file and is a spec non-goal.
- Plain `$(...)` capture. It strips trailing newlines and cannot enforce "exactly one line".
- Running the script via `sh "$target"`. It would hide a missing exec bit or a broken shebang.
- An env-var or argument hook to point the test at another script. It is a spec non-goal, so failure paths are proven by temporary local edits instead.

## Ordered implementation steps

1. **Add `qa/s4-greet.sh`** (new) as described in the Solution proposal, and set its git mode to `100755` (`chmod +x`, and check with `git ls-files -s`).
   - Advances: spec scenario 1, `t1` AC1 and AC2.
   - Test layer: none of the repo's existing layers cover `qa/` S4 scripts (RK1). It is covered by the manual run in step 4 and by step 2's test.
2. **Add `qa/s4-greet.test.sh`** (new, mode `100755`) as described in the Solution proposal. It must use only `printf`, `dirname`, `[` and shell builtins, and no bashisms (`[[`, `local`, `$'…'`, arrays).
   - Advances: spec scenarios 2–4, `t1` AC3–AC6.
   - Test layer: the script is itself the test. CI does not run it, which is stated, not hidden.
   - Error paths to cover: missing target, non-executable target, non-zero exit, wrong line, extra line, and missing trailing newline.
3. **Append one bullet** under `## Unreleased` in `CHANGELOG.md`, directly after `CHANGELOG.md:5`, using the text from the assumptions above. No other changelog line changes.
   - Advances: spec FR6, `t1` AC7, repo-gate rule 4 (`PLAY-G4`).
   - Test layer: the repo PR gate (`repo-gate` skill).
4. **Verify manually** in the pod and record the results for the PR description (`t1` AC10):
   - Run `qa/s4-greet.sh | od -c`. Expect exactly `hello from s4\n` and exit 0.
   - Run `dash qa/s4-greet.sh`.
   - Run `qa/s4-greet.test.sh` from the repo root, from `qa/` and from `/tmp`. Expect PASS and exit 0 each time.
   - Run `dash qa/s4-greet.test.sh`.
   - Check the failure paths by temporarily editing `qa/s4-greet.sh` in the working tree. Expect FAIL and a non-zero exit for each:
     - print `hello`;
     - add an extra line;
     - drop the trailing newline;
     - `exit 3`;
     - `chmod -x`;
     - move the file away.
   - Restore the file after each probe, and confirm `git status` shows no modification to `qa/s4-greet.sh` beyond the step-1 content.
   - Run `qa/s3-hello.sh`. Expect `hello` and exit 0 (scenario 6).
   - Test layer: manual, as RK1 requires.
5. **Check scope** with `git diff --name-status <base>...HEAD -- . ':!stories/PLAY-150'`. Expect only `A qa/s4-greet.sh`, `A qa/s4-greet.test.sh` and `M CHANGELOG.md`, with `qa/s4-base-marker.txt` absent from the list.
   - Advances: spec scenario 5, `t1` AC8.
6. **Run the canonical gate:** `pip install -e ".[test]"` (acquires `pytest` and the package dependencies from the index, with no cache assumed), then `pytest`.
   - Advances: spec scenarios 6–7, `t1` AC9 and AC11.
   - Test layer: `package-api`.

There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply. Authorization, tenancy and concurrency do not apply: these are single-process scripts with no state.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–6 | `t1` — QA-20261108-S4 (PLAY-150): add qa/s4-greet.sh and bats-free qa/s4-greet.test.sh |

`t1` is the only work item, and every step maps to it. `t1` AC10 (PR title and description naming PLAY-150 and the epic PRD, with manual results) belongs to the platform's PR step and is fed by step 4's results.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`): `pip install -e ".[test]"`, then `pytest`, from the repo root. Run it once locally on the committed SHA. Provider CI runs it again at the PR head, and that run is authoritative.
- **Required layer:** `package-api` (`pytest`). It runs in a pod. It must pass unchanged, including `tests/test_qa_s3_greeting.py`.
- **`gate` job:** green as long as no `CI_FAIL` file exists at the root. The change creates none.
- **Repo PR gate** (`repo-gate`): both new scripts are executable with a shebang, no file is over 200 KB, and the `CHANGELOG.md` line exists under `## Unreleased`.
- **Not in CI:** `qa/s4-greet.test.sh` is not run by CI (RK1). The evidence for spec scenarios 2–4 is step 4's manual runs, recorded in the PR description.
- **No CI changes:** the change needs no provider CI configuration.
- **Done means:**
  - `pytest` is green;
  - the `test` and `gate` jobs are green;
  - the repo gate passes;
  - step 4 shows PASS on the happy path and FAIL plus a non-zero exit on every failure probe;
  - step 5 shows exactly the three expected paths.

## Risks and scope guards

**Risks:**
- **RK1:** green CI does not prove the new test passes. Mitigation: step 4's manual runs, recorded in the PR.
- **Missing base commit.** The work branch lacks base commit `90f1a31`. Mitigation: AC8 is checked with the three-dot diff against `qa-20261108-s4-base`, which is clean today. Do not "fix" this by editing files.
- **Missing exec bit.** A missing exec bit on either script is a gate blocker. Mitigation: step 1 and step 2 check the git mode.
- **Trailing-newline loss.** Naive command substitution loses trailing newlines and would let a wrong output pass. Mitigation: the sentinel capture and the probe without a trailing newline in step 4.

**Scope guards (do NOT):**
- Touch `qa/s3-hello.sh`, `qa/s4-base-marker.txt`, `src/`, `tests/`, `pyproject.toml`, `.github/workflows/ci.yml`, `README.md`, `.factory/` or `stories/PLAY-150/{spec,hld,work-items}.md`.
- Add a pytest file, CI wiring, `--help` handling, a redirect hook or env var, or any changelog edit beyond the one bullet.
- Delete, recreate or copy `qa/s4-base-marker.txt`, or merge or rebase any branch other than the target `qa-20261108-s4-base`.
- Leave a failure-probe edit to `qa/s4-greet.sh` in the committed tree.
- Make any check green by deleting, skipping or weakening it. A failing check is reported as blocked.

## Clarification outcomes

None.
