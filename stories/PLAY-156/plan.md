# Plan — PLAY-156: `qa/s3-a.sh` prints "A"

## Context

PLAY-156 adds `qa/s3-a.sh` to `roeeoz/play1`. The story is wave 1 of epic PLAY-155, and PLAY-157 will call the script by path. The acceptance criteria are: running it from the repo root prints exactly `A` and a newline and exits 0 (AC1); `qa/s3-hello.sh` still prints `hello` (AC2); the repository's required CI checks pass on the PR (AC3). The change lands on the work branch `halo/feat/play-156-20261108-063753` and merges into `main`. `spec.md` (the requirement), `hld.md` (the design) and `work-items.md` (one work item, `t1`) sit next to this file in `stories/PLAY-156/`.

## Research findings

- **Sibling script (pattern to copy).** `qa/s3-hello.sh:1-3` has three lines: `#!/bin/sh`, a one-line `#` purpose comment, and `printf 'hello\n'`. It uses LF endings and has git mode `100755` (from `git ls-files -s qa`). `qa/` contains only this file.
- **The script needs no package wiring.** `pyproject.toml` finds packages with `where = ["src"]` and sets `testpaths = ["tests"]` (`pyproject.toml:26-27`). `qa/` is neither a package nor a console script.
- **Existing coverage of `qa/`.** `tests/test_qa_s3_greeting.py` runs `qa/s3-hello.sh` through `subprocess` and checks the exact stdout `"hello\n"`, empty stderr and exit 0 (lines 15-20). It also checks for a `#!/bin/sh\n` shebang followed by a `#` comment line (lines 24-27) and for no `\r` (lines 29-30). This test is AC2's existing automated proof. Correction to `hld.md` §7: it says "No test globs `qa/`". That is true, because nothing globs the directory, so a new file there cannot affect any test. But one test does target `qa/s3-hello.sh` by name.
- **CHANGELOG contract.** `CHANGELOG.md:3` is `## Unreleased`. `CHANGELOG.md:5` is `- PLAY-114: add \`qa/s3-hello.sh\`, a helper script that prints \`hello\`.` The new line follows the same format.
- **Merge gate (mr-gate).** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:15` (rule 2) requires a new shell script to be executable and to start with a shebang. Line 16 (rule 3) limits each file to 200 KB or less. Lines 17-20 (rule 4, `PLAY-G4`) require a PR to add a line under `## Unreleased` in `CHANGELOG.md`.
- **CI gate.** `.github/workflows/ci.yml` has two jobs. `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. `gate` fails only if a `CI_FAIL` file exists at the repo root. `.factory/testing.md` lists one required layer, `package-api` (`pytest`, `runBy: canonical-gate`), and says the repo has no linter, formatter or type checker.
- **What exists vs. what is new.** New: `qa/s3-a.sh`. Edited: `CHANGELOG.md` (one line). Nothing else changes.
- **External data:** none. **Unknowns left after research:** none.

## Locked decisions and assumptions

**Locked decisions**
- Path `qa/s3-a.sh`. Output exactly `A\n` on stdout, nothing on stderr, exit code 0. Source: spec.md §3 FR1–FR2, §7, and the `hld.md` §5 contract that PLAY-157 depends on.
- Git mode `100755` and a shebang as the first line. Sources: `hld.md` §5 and mr-gate rule 2.
- Use `#!/bin/sh` and `printf`, not `bash` or `echo`. Source: `hld.md` §6.
- No new automated test, no `--help` handling and no docs. Source: spec.md §2 Non-Goals, PO decision Q1.
- The script only has to work when run from the repo root. Source: PO decision Q2.
- Add one `CHANGELOG.md` line under `## Unreleased`. Sources: mr-gate `PLAY-G4`, spec.md §6.
- The PR cites PLAY-156 and the Epic PRD (Confluence pageId 33292289), and contains no secrets. Sources: Engineering requirements R4 and R7, and `work-items.md` t1 AC6.

**Assumptions**
- The CHANGELOG line is a release record, not the "documentation" the PO excluded. Evidence: spec.md §6 and the PLAY-114 precedent at `CHANGELOG.md:5`. If this is wrong, the PR cannot satisfy `PLAY-G4` and the gate rule would have to change first.
- Arguments are ignored. The script never reads `$@`, so any arguments have no effect. Evidence: spec.md §3 leaves this case undefined. If this is wrong, a later story has to define argument behaviour. Nothing here depends on it.

## Solution proposal

Add a three-line POSIX shell script that copies `qa/s3-hello.sh` line for line:
- `#!/bin/sh`
- a one-line purpose comment, for example "Prints A; the first of the two QA-S3 greeting scripts (called by qa/s3-b.sh)."
- `printf 'A\n'`

Commit the file with mode `100755` so the user and PLAY-157 can run it directly by path. Add one CHANGELOG line in the PLAY-114 format, for example ``- PLAY-156: add `qa/s3-a.sh`, a helper script that prints `A`.``

Key design decisions:
- **Use `printf` instead of `echo`.** `printf` produces the exact bytes `A\n` in every POSIX shell. PLAY-157's two-line output depends on that.
- **No `set -e`, argument parsing or `cd`.** The script has no failure modes. Q2 limits support to running from the repo root, and the script does not depend on the working directory anyway.
- **Match the sibling's shape: shebang, `#` comment, LF endings.** `qa/` stays consistent, and a later pytest modelled on `tests/test_qa_s3_greeting.py` would pass as is.

Alternatives considered:
- **`#!/bin/bash`, as in `hello-world/`.** Rejected because it is inconsistent with `qa/` and less portable (`hld.md` §6).
- **A pytest test like the one for `s3-hello.sh`.** Rejected by PO decision Q1. AC1 is shown by a manual run recorded in the PR description instead.

## Ordered implementation steps

1. **Create `qa/s3-a.sh` (new).**
   - Content: shebang `#!/bin/sh`, then a one-line `#` purpose comment, then `printf 'A\n'`.
   - Use LF line endings and no trailing whitespace.
   - Advances AC1. Test layer: none automated, by PO decision Q1. Verify manually in step 3.
2. **Make the script executable in git.**
   - Run `chmod +x qa/s3-a.sh`.
   - Confirm that `git ls-files -s qa/s3-a.sh` reports `100755` after staging. If the filesystem drops the bit, use `git update-index --chmod=+x qa/s3-a.sh`.
   - Advances AC1 (direct execution, FR3) and mr-gate rule 2. Test layer: none automated; checked with the git command.
3. **Verify AC1 by hand from the repo root.**
   - `qa/s3-a.sh | od -c` shows exactly `A \n`.
   - `qa/s3-a.sh 2>&1 >/dev/null` shows no stderr.
   - `qa/s3-a.sh; echo $?` prints `0`.
   - Record the output, the exit code and the file mode for the PR description (t1 AC6).
4. **Add the release line to `CHANGELOG.md`.**
   - Insert one line after `CHANGELOG.md:5`, under `## Unreleased`: ``- PLAY-156: add `qa/s3-a.sh`, a helper script that prints `A`.``
   - Leave the PLAY-114 line unchanged.
   - Advances AC3 (mr-gate `PLAY-G4`). Test layer: mr-gate, run by the platform.
5. **Confirm there is no regression.**
   - `qa/s3-hello.sh` still prints `hello` (AC2). The existing layer `package-api` covers this through `tests/test_qa_s3_greeting.py`.
   - `git diff --stat main` shows exactly two paths: `qa/s3-a.sh` and `CHANGELOG.md`.
   - No `CI_FAIL` file exists.
   - Advances AC2 and AC3.

Implicit invariants: the change has no authorization, tenancy, concurrency or input-validation surface, because the script takes no input and holds no state. No dependencies are acquired, because `/bin/sh` and `printf` are already available. Nothing is generated, and `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1, 2, 3, 4, 5 | `t1` — PLAY-156: add qa/s3-a.sh that prints "A" (+ CHANGELOG entry) |

`work-items.md` has one work item, and all five steps belong to it.

## Verification and CI gate

- **Canonical gate.** Per `.factory/testing.md`, run `pip install -e ".[test]"` and then `pytest` from the repo root, once, on the committed SHA. The only required layer is `package-api` (`pytest`). It can run in a pod, but the provider CI run at the exact head is the authoritative result.
- **Provider CI.** `.github/workflows/ci.yml` jobs `test` and `gate` must both be green. `gate` stays green as long as no `CI_FAIL` file is added. No CI configuration change is needed.
- **mr-gate.** It must pass with no findings: rule 2 (mode `100755` plus shebang), rule 3 (size limit) and rule 4 / `PLAY-G4` (CHANGELOG line).
- **The gate does not cover AC1.** No automated test checks AC1, by PO decision Q1. The PR description must show the step 3 evidence: `qa/s3-a.sh` output, exit code 0, empty stderr, and the `git ls-files -s qa/s3-a.sh` mode `100755`. It must also reference PLAY-156 and the Epic PRD (pageId 33292289).
- **Done means:** `pytest` passes with every existing test, including `tests/test_qa_s3_greeting.py` (AC2); both CI jobs and the mr-gate are green (AC3); and the AC1 manual evidence is recorded.

## Risks and scope guards

**Risks**
- **The file is committed as `100644`.** Rule 2 then fails and PLAY-157 cannot run the script directly. Mitigation: the `git ls-files -s` check in step 2.
- **Stray bytes such as CR, a trailing space or a missing newline.** These would break PLAY-157's exact two-line output, and no CI test catches them. Mitigation: the `od -c` check in step 3.
- **The CHANGELOG line is missing.** `PLAY-G4` then blocks the merge. Mitigation: step 4.
- **Ordering (RK1).** PLAY-157 must not open its PR until this PR merges to `main`. That belongs to PLAY-157 and needs no action here.

**Scope guards: the implement phase must NOT:**
- touch `qa/s3-hello.sh`, `tests/`, `.github/`, `pyproject.toml`, `src/`, `README.md` or `docs/`;
- create `qa/s3-b.sh` (that is PLAY-157);
- add a pytest test, `--help` handling, argument parsing or a console-script entry for `qa/s3-a.sh`;
- add a `CI_FAIL` file;
- rewrite or reorder existing CHANGELOG lines;
- make any check green by deleting, skipping or weakening it. A failing check is reported as blocked.

## Clarification outcomes

None. Q1 (no tests and no `--help`) and Q2 (run from the repo root) were answered by the PO on 2026-11-08 before this stage. They appear above as locked decisions.

S3-GIT-EDIT
