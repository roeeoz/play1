# Implementation plan — PLAY-169: test script `qa/20261109-s6/a.sh` prints "a" and exits successfully

## Context

PLAY-169 is the only story of the controls-probe epic QA-20261109-S6. It adds one standalone POSIX script, `qa/20261109-s6/a.sh`. The script prints exactly the line `a` and exits 0. The change also adds one bullet under `## Unreleased` in `CHANGELOG.md`, which the repository's merge gate (rule `PLAY-G4`) requires. The acceptance criteria cover four things: exact output and exit 0 (AC1), a file list limited to the script, the CHANGELOG line and `stories/PLAY-169/` (AC2), green `test` and `gate` CI jobs with human-approved merge (AC3), and PR traceability with no secrets (AC4). The change lands in `roeeoz/play1` on the work branch `halo/feat/play-169-20261109-101304`, cut from and merging into `qa-20261109-s6-base`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/PLAY-169/`.

## Research findings

- **Model scripts.** `qa/s3-a.sh:1-3` and `qa/s3-hello.sh:1-3` are three lines each: `#!/bin/sh`, a one-line `#` purpose comment, and `printf '<text>\n'`. They use LF endings and no explicit `exit`. Both have git mode `100755` (`git ls-files -s qa`). `qa/s3-a.sh:2` has the stale comment "(called by qa/s3-b.sh)". It must not be copied (work item t1, AC3).
- **`qa/20261109-s6/` does not exist.** It is new and gets created by adding the file. `qa/` has no subfolders today.
- **No package or test wiring.** `pyproject.toml` sets `[tool.setuptools.packages.find] where = ["src"]` and `[tool.pytest.ini_options] testpaths = ["tests"]`. `qa/` is not a package, a console script (`[project.scripts]`) or a test path.
- **Existing tests on `qa/`.** `tests/test_qa_s3_greeting.py` targets `qa/s3-hello.sh` by name: exact stdout `"hello\n"`, empty stderr, exit 0, shebang followed by a comment, no `\r`. No test globs `qa/`, so a new file there cannot change any test result. `tests/test_hello_sh.py` targets `hello-world/hello.sh`.
- **Canonical gate.** `.factory/testing.md` declares one required layer, `package-api` (`pytest`, `runBy: canonical-gate`), with `pip install -e ".[test]"` as its precondition. `.github/workflows/ci.yml` has two jobs. `test` runs install and then `pytest` on Python 3.12. `gate` fails only if a `CI_FAIL` file exists at the repo root. No linter, formatter or type checker is configured.
- **Merge-request gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:15` (rule 2) requires a new shell script to be executable and start with a shebang. `SKILL.md:16-20` (rule 4, id `PLAY-G4`) requires a line under `## Unreleased` in `CHANGELOG.md`.
- **CHANGELOG format.** `CHANGELOG.md:3` is `## Unreleased`. Lines 5-6 are bullets of the form ``- PLAY-<n>: add `qa/<file>`, a helper script that prints `<text>`.``. The last line is line 6, so the new bullet is appended after it.
- **Precedent.** PLAY-156 (`stories/PLAY-156/plan.md`) delivered `qa/s3-a.sh` the same way: one script, one CHANGELOG bullet, no new test.
- **External data.** None. **Unknowns remaining.** None.

## Locked decisions and assumptions

**Locked decisions**
- File path `qa/20261109-s6/a.sh`. Output exactly `a\n`, exit 0. Source: spec.md FR1-FR3, Epic PRD R1/R2.
- Only `a.sh`, one `CHANGELOG.md` bullet and `stories/PLAY-169/*` may appear in the PR. No tests, docs, `c.sh` or `--help`. Source: spec.md §2 Non-Goals, FR4, FR5; Epic PRD §8; risk RK1.
- `#!/bin/sh` shebang, `printf` rather than `echo`, git mode `100755`, no stale "called by" comment. Source: hld.md §6; work item t1, AC3; repo-gate rule 2.
- The PR description names PLAY-169 and the Epic PRD (Confluence pageId 34111489), with no secrets or personal data. Source: spec.md AC4; engineering requirements R4/R7.
- The target branch is `qa-20261109-s6-base`. Source: the platform contract.

**Assumptions**
- Adding an explicit `exit 0` is optional (hld.md §6). The plan follows the sibling scripts and omits it. Evidence: `printf` to a writable stdout returns 0, and the siblings have no `exit`. If wrong: if stdout were closed, the exit status would be non-zero. That is outside AC1's "run from the command line".
- The repo-gate rule 2 check reads the mode from the git index, not just the working tree. Evidence: the rule speaks of "executable", and the siblings are `100755` in the index. If wrong: none, because the plan sets both.

## Solution proposal

Add one three-line POSIX shell script modelled on `qa/s3-hello.sh`:
- line 1: `#!/bin/sh`;
- line 2: a one-line `#` purpose comment, for example that it prints `a` for the QA-20261109-S6 controls probe;
- line 3: `printf 'a\n'`.

Use LF endings, end with a final newline, and add no trailing whitespace. Commit it with mode `100755` (`chmod +x` and/or `git update-index --chmod=+x`). Append one bullet to `CHANGELOG.md` after line 6: ``- PLAY-169: add `qa/20261109-s6/a.sh`, a helper script that prints `a`.``

Key decisions:
- **`printf` over `echo`.** The bytes are identical in every `sh`.
- **No explicit `exit`.** This matches the siblings, and the exit status is `printf`'s 0.
- **No code in `src/`, `tests/` or CI.** The script is outside every package, test path and workflow, so the existing gate is unaffected.

Alternatives rejected:
- A pytest test modelled on `tests/test_qa_s3_greeting.py`. It is out of scope by PO instruction (spec.md Non-Goals). AC1 is shown by a recorded manual run instead.
- A Python console entry in `pyproject.toml`. It changes package code, which is out of scope.
- `echo a`. Its behaviour differs between shells.

## Ordered implementation steps

1. **Create `qa/20261109-s6/a.sh`** (new file and new folder) with the three lines described in the Solution proposal. Advances AC1 (spec AC1; t1 AC1-AC3). Test layer: no automated layer covers this by PO decision. It is verified manually in step 3.
2. **Set the executable bit** on `qa/20261109-s6/a.sh` so the git index shows mode `100755`. Advances AC1 (direct run) and repo-gate rule 2 (t1 AC3). Test layer: none automated. Checked with `git ls-files -s qa/20261109-s6/a.sh` in step 3.
3. **Verify the script by hand** from the repo root and record the results for the PR description:
   - `qa/20261109-s6/a.sh; echo $?` prints `a` and then `0`;
   - `sh qa/20261109-s6/a.sh` gives the same result;
   - stderr is empty;
   - `od -c qa/20261109-s6/a.sh` shows no `\r` and a final `\n`;
   - stdout bytes are exactly `a\n` (for example `qa/20261109-s6/a.sh | od -c`);
   - the index mode is `100755`.

   Advances AC1 (t1 AC1-AC3). Test layer: manual evidence, as there is no automated layer.
4. **Append the CHANGELOG bullet** after `CHANGELOG.md:6` under `## Unreleased`, with no other line touched. Advances AC2 and gate rule `PLAY-G4` (t1 AC4). Test layer: none automated. It is checked by the repo-gate mr-gate and by `git diff` showing a single `+` line.
5. **Check the scope** with `git diff --stat qa-20261109-s6-base...HEAD`. It must list only `qa/20261109-s6/a.sh`, `CHANGELOG.md` and `stories/PLAY-169/*`, and no `CI_FAIL`. Advances AC2 and AC3 (t1 AC5, AC6, AC8). Test layer: none automated. This is a review check against risk RK1.
6. **Run the canonical gate** (see Verification) and confirm that every existing test passes, including `tests/test_qa_s3_greeting.py`. Advances AC3 (t1 AC6). Test layer: `package-api` (`pytest`).
7. **Write the PR description.** It names PLAY-169 and the Epic PRD (Confluence pageId 34111489), includes the step 3 evidence, and contains no secrets or personal data. Advances AC4 (t1 AC7). Test layer: none, as this is checked in human review.

Implicit invariants:
- No authorization or tenancy concerns, no concurrency or idempotency concerns, and no input validation, because the script takes no input and has no state.
- No dependencies to acquire beyond the gate's `pip install -e ".[test]"`.
- No generated deliverables, and no binaries for `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1-7 | t1 — Add qa/20261109-s6/a.sh, which prints "a" and exits 0, plus its CHANGELOG entry |

Every work item (t1 only) is mapped.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`): run `pip install -e ".[test]"`, then `pytest` from the repo root, once, on the committed SHA. The only required layer is `package-api` (`pytest`). It runs unprivileged in a pod, but the provider CI run at the exact head is authoritative.
- **Provider CI.** `.github/workflows/ci.yml` jobs `test` and `gate` must both be green. `gate` stays green because no `CI_FAIL` is added. No CI configuration change is needed.
- **mr-gate** (`claims-dev:repo-gate`) must pass rule 2 (executable, shebang) and rule `PLAY-G4` (CHANGELOG line). Rules 1 and 3 hold trivially: no Python is added, and the files are a few bytes.
- **`.factory/testing.md` obligations:** no new layer and no change to the declared layer. **`.factory/delivery-assets`:** not applicable.
- **Gap stated plainly:** the gate does not exercise AC1, because no automated test is added by PO decision. AC1 rests on the step 3 manual evidence recorded in the PR.
- **Done means:**
  - `pytest` passes with every existing test;
  - CI `test` and `gate` and the mr-gate are green;
  - the diff contains only the allowed files, with `a.sh` at mode `100755`;
  - the AC1 evidence and the traceability are in the PR description;
  - the merge waits for human approval.

## Risks and scope guards

**Risks**
- **Lost executable bit.** If `a.sh` lands as `100644`, the mr-gate rule 2 fails and a direct run fails. Mitigation: step 2 and the `git ls-files -s` check.
- **Stray bytes.** A CR, a BOM, a trailing space or `echo` variance would break the exact-output criterion, and no test catches them. Mitigation: the `od -c` checks in step 3.
- **Scope creep (RK1).** Mitigation: the step 5 diff check.
- **Missing CHANGELOG line.** It would cause a `PLAY-G4` blocker. Mitigation: step 4.

**The implement phase must NOT:**
- add `qa/20261109-s6/c.sh`, a pytest test, a README or docs entry, `--help` or argument handling, or a `[project.scripts]` entry;
- touch `qa/s3-a.sh` (including its stale comment), `qa/s3-hello.sh`, `src/`, `tests/`, `hello-world/`, `docs/`, `README.md`, `pyproject.toml`, `.github/` or `.factory/`;
- edit or reorder existing `CHANGELOG.md` lines;
- add a `CI_FAIL` file;
- edit `spec.md`, `hld.md` or `work-items.md`;
- skip, delete, disable or weaken any check. A failing check is reported as blocked, never made green.

## Clarification outcomes

None. The PO's scope decisions (no tests, no `--help`, one script plus the required CHANGELOG line) are already fixed in `spec.md`, so no question was needed.
