## Context

SCRUM-16 asks for a top-level folder `hello-world/` holding only `hello.sh`. The script starts with `#!/bin/bash`, is executable, and prints exactly `hello world`. The acceptance criteria are spec §5 scenarios 1–4: output and exit code, folder isolation, direct execution through the shebang, and exact output. The target branch `main` already holds this deliverable and its tests. Per spec FR4 and A1, this delivery verifies the existing state and adds only the `CHANGELOG.md` line that gate `PLAY-G4` requires. The change lands in `roeeoz/play1` on `halo/feat/scrum-16-20261118-233400` and merges into `main`. `spec.md` (requirement), `hld.md` (design) and `work-items.md` (one work item, `t1`) sit beside this file in `stories/SCRUM-16/`.

## Research findings

- **The script already exists.**
  - `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. The file is 31 bytes of ASCII with LF line endings.
  - Git stores it as `100755` (blob `2a43bb2`). It was added in `65938b5`.
  - `hello-world/` holds no other file, hidden files included.
- **Existing coverage.** `tests/test_hello_sh.py` (from `a2ec96d` and `9a5bd0b`) already pins every criterion:
  - AC1 and AC4: `tests/test_hello_sh.py:10-28` runs the script with no `bash` prefix and asserts exit `0`, stdout `"hello world\n"` and empty stderr.
  - AC3: `tests/test_hello_sh.py:32-38` checks the shebang line and `S_IXUSR`.
  - AC2: `tests/test_hello_sh.py:40-43` checks that the folder holds only `hello.sh`. It ignores dotfiles, so a hidden file would pass this test and still break AC2 (hld §7).
- **CHANGELOG contract.**
  - `CHANGELOG.md:3` is `## Unreleased`, and the file is 8 lines long.
  - Entries follow `- <KEY>: add \`<path>\`, a ... script that prints \`<text>\`.`; the last one is `CHANGELOG.md:8` (PLAY-175).
  - No entry mentions `hello-world` or SCRUM-16 yet.
- **Repo gate.** The rules are in `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`:
  - Rule 4 (`PLAY-G4`, blocker): the pull request must add a line under `## Unreleased`. This is the only rule this change has to act on.
  - Rule 2 (new shell scripts are executable and have a shebang) does not fire, because no script is added.
  - Rule 3 (files under 200 KB) is trivially met.
- **CI.**
  - In `.github/workflows/ci.yml`, job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12.
  - Job `gate` fails only when `CI_FAIL` exists at the repo root.
  - `pyproject.toml` sets `testpaths = ["tests"]`, so `tests/test_hello_sh.py` runs in CI.
- **Declared test layers.** `.factory/testing.md` declares one layer, `package-api` (`pytest`, `runBy: canonical-gate`). No linter or formatter is configured.
- **Git config.** `core.fileMode` is `true` and the repo has no `.gitattributes`. The executable bit is tracked, and nothing enforces LF line endings.
- **Repo memory.** The repo has no `.factory/memory/`.
- **External data and dependencies.** None.
- **Unknowns.** None remain.

## Locked decisions and assumptions

**Locked decisions**
- Leave `hello-world/hello.sh` and `tests/test_hello_sh.py` unchanged. Sources: spec FR4 and A1, hld §6, work item `t1` "Consumes, read-only".
- The output contract is stdout `hello world\n`, empty stderr and exit `0`. The trailing newline from `echo` is allowed. Sources: spec FR3 and A2, hld §5.
- The only product file the change touches is `CHANGELOG.md`, with one line under `## Unreleased`. Sources: spec A3, `PLAY-G4`, work item `t1`.
- Add no new test harness, CI change or documentation file. Sources: spec §2 non-goals, hld §6.

**Assumptions**
- *The "diff touches no file other than `CHANGELOG.md`" criterion excludes `stories/SCRUM-16/`.* The platform commits that folder on the work branch.
  - Evidence: the PLAY-175 precedent (`stories/PLAY-175/plan.md`) scoped its change boundary the same way.
  - If wrong: a reviewer would flag the plan-folder files, and the platform's commit layout would decide, not this delivery.
- *The CI runner executes the `100755` file directly.*
  - Evidence: the same test has already passed on `main` since `9a5bd0b`.
  - If wrong: `test_prints_hello_world` fails in CI. Report it as blocked; do not change the test.

## Solution proposal

Treat the story as already implemented. Deliver it as a one-line changelog pull request backed by the existing pytest coverage.

- **Add one line under `## Unreleased`.** Append it after `CHANGELOG.md:8`, in the existing style. Proposed text: `- SCRUM-16: add \`hello-world/hello.sh\`, a bash script that prints \`hello world\`, alone in its own \`hello-world/\` folder.`
  - It names SCRUM-16 and the path, which `t1` requires.
  - It satisfies `PLAY-G4`.
- **Prove AC1–AC4 with what already exists.**
  - The `tests/test_hello_sh.py` tests run in the CI `test` job at the pull request's head.
  - Before the pull request opens, run a manual check that confirms the two invariants the tests cannot see: git mode `100755`, and no hidden file in `hello-world/`.
- **Alternatives rejected.**
  - *Re-create or rewrite `hello.sh`:* it adds nothing, and it risks losing mode `100755` or bringing in CRLF line endings (hld §6).
  - *Switch to `printf 'hello world'`:* it contradicts spec A2 and would fail `tests/test_hello_sh.py:15`.
  - *Tighten the dotfile check in `tests/test_hello_sh.py:42`:* it is outside scope, since the test is read-only in `t1`. A manual check covers the gap instead.
  - *A pull request with no changes:* `PLAY-G4` would block it.

## Ordered implementation steps

1. **Pre-check the existing state (read-only).** Covers AC1–AC4. There is no test layer for this step; it is a manual check, and its results go in the pull request description.
   - `git ls-files -s hello-world` shows exactly one entry, `100755 … hello-world/hello.sh`.
   - `ls -A hello-world` lists only `hello.sh`.
   - `head -1 hello-world/hello.sh` is `#!/bin/bash`, and the file contains no `\r`.
   - From the repo root, `./hello-world/hello.sh` prints `hello world`, writes nothing to stderr and exits `0`.
   - If any check fails, stop and report it. Do not fix the script, because it is out of scope.
2. **Append the changelog line.** Add the single line from the Solution proposal directly after `CHANGELOG.md:8`, under `## Unreleased`.
   - Edit no other line. Keep the trailing newline. Do not add a duplicate entry.
   - Advances work item `t1` (changelog criterion) and `PLAY-G4`.
   - There is no automated test layer for the changelog; the repo-gate review covers it.
3. **Run the canonical gate locally as a pre-push check.** Run `pip install -e ".[test]"`, then `pytest` from the repo root.
   - Covers AC1–AC4 through `tests/test_hello_sh.py`, in layer `package-api`.
   - The whole suite must pass.
4. **Confirm the diff boundary.** Run `git diff --stat main...HEAD -- . ':!stories/SCRUM-16'`; it must list only `CHANGELOG.md` with one insertion.
   - `git diff main...HEAD -- hello-world tests` must be empty.
   - Make sure no `CI_FAIL` file exists.
   - Covers the `t1` boundary criterion and AC2.
5. **Write the pull request description for traceability.** It references SCRUM-16 and maps AC1–AC4 to the `tests/test_hello_sh.py` tests and the step 1 checks.
   - There is no test layer; this is review evidence.

Implicit invariants:
- Authorization, tenancy and concurrency do not apply.
- The script takes no input, so it has no validation or error paths.
- Dependency acquisition is limited to `pip install -e ".[test]"` (pytest, pypdf, flask) from a cold cache.
- There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1 | `t1` — SCRUM-16: Record the verified hello-world script in CHANGELOG.md and confirm it meets AC1 to AC4 |
| 2 | `t1` |
| 3 | `t1` |
| 4 | `t1` |
| 5 | `t1` |

## Verification and CI gate

- **Canonical gate (from `.factory/testing.md`).** Run `pip install -e ".[test]"`, then `pytest`, from the repo root on Python 3.12+.
  - Run it once locally on the committed SHA. Provider CI runs it again.
  - The required layer is `package-api` (`pytest`, `runBy: canonical-gate`). It can run in a pod, but only the provider run at the pull request's head counts.
- **Provider CI (`.github/workflows/ci.yml`).**
  - Job `test` must be green, with all six tests in `tests/test_hello_sh.py` passing.
  - Job `gate` must be green, which means no `CI_FAIL` file.
  - No CI configuration change is needed.
- **Repo gate.** The `repo-gate` verdict must pass with no `PLAY-G4` finding.
- **Done means:** CI is green at the head, and the diff outside `stories/SCRUM-16/` is exactly one added line in `CHANGELOG.md`. `hello-world/hello.sh` stays mode `100755` with byte-identical content.
- **Obligations.** `.factory/testing.md` needs no update. `.factory/delivery-assets` does not apply.

## Risks and scope guards

**Risks**
- **Accidental edit to `hello.sh`.** Rewriting the file, even with identical content, can drop mode `100755` or bring in CRLF line endings.
  - Mitigation: never open the file for writing. Step 4 checks the diff boundary.
- **Hidden file in `hello-world/`.** It would break AC2 without failing the test.
  - Mitigation: step 1 runs `ls -A`, and step 4 checks the diff.
- **Missing changelog line.** Without it, `PLAY-G4` blocks the pull request.
  - Mitigation: step 2 adds it, and step 4 confirms it.

**Scope guards: the implement phase must NOT**
- modify, rename, re-create or `chmod` `hello-world/hello.sh`, or add any file to `hello-world/` (no `.gitkeep`, no README);
- edit `tests/test_hello_sh.py`, including tightening its dotfile filter, or add new tests;
- touch `.github/workflows/ci.yml`, `pyproject.toml`, `.factory/`, or `src/testbed_utils/hello.py` (the unrelated `testbed-hello` CLI);
- reformat or reorder existing `CHANGELOG.md` entries;
- create `CI_FAIL`;
- make any check green by deleting, skipping or weakening it. A failing check is reported as blocked.

## Clarification outcomes

None. No question was needed: the spec's assumptions A1–A3 and the HLD settle every open point.
