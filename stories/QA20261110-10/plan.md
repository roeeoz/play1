## Context

QA20261110-10 is the only story of epic "a3 one-line hello script (round 2)". It adds one QA shell script, `qa/20261111-a3/hello.sh`. Run with no input, the script prints exactly `hello from a3\n` to stdout, writes nothing to stderr and exits 0. The PR also adds the one `CHANGELOG.md` line that the play1 repository gate requires. The acceptance criteria (spec §5, scenarios 1–6) cover:

- the happy path;
- running with no external component;
- no regression in pytest or the existing `qa/` scripts;
- a strict scope boundary (one product file plus one CHANGELOG line);
- PR traceability;
- not merging until the required checks are green.

The change lands in `roeeoz/play1` on the work branch `halo/feat/qa20261110-10-20261111-081001`, which merges into `main`. `spec.md` (the requirement), `hld.md` (the design) and `work-items.md` (one work item, `t1`) sit beside this file in `stories/QA20261110-10/`.

## Research findings

- **`qa/` convention (fact).** All five existing `qa/` scripts have git mode `100755`, start with `#!/bin/sh`, have a one-line `#` comment on line 2, use LF endings and do their work with `printf`. Examples:
  - `qa/20261110-s3/hello.sh:1-3`: `printf 'hello s3\n'`.
  - `qa/s3-hello.sh:1-3`.
  - `qa/20261109-s1/a.sh:1-3`.
- **Target path (fact).** Neither `qa/20261111-a3/` nor the round-1 path `qa/20261110-a3/` exists. The new script and its folder are both new.
- **Git settings (fact).** `core.fileMode` is `true`, so the executable bit is tracked. The repo has no `.gitattributes`, so nothing enforces LF.
- **CHANGELOG contract (fact).**
  - `CHANGELOG.md:3` is `## Unreleased`.
  - Entries `CHANGELOG.md:5-8` follow ``- <KEY>: add `<path>`, a QA script that prints `<text>`.``.
  - The last entry is `CHANGELOG.md:8` (PLAY-175).
- **Repository gate (fact).** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (slot `mr-gate`) sets four rules:
  - Rule 1: Python only under `src/`, tests under `tests/`. Met, because no Python is added.
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file over 200 KB.
  - Rule 4 (`PLAY-G4`): the PR adds a line under `## Unreleased` in `CHANGELOG.md`.
- **CI (fact).** `.github/workflows/ci.yml` has two jobs:
  - `test`: Python 3.12, `pip install -e ".[test]"`, then `pytest`.
  - `gate`: fails only if `CI_FAIL` exists at the repo root.
- **Declared test layers (fact).** `.factory/testing.md` declares one layer, `package-api` (`pytest`, required, `runBy: canonical-gate`). It declares no shell-test layer, linter or formatter.
- **pytest scope (fact).** `pyproject.toml:27` sets `testpaths = ["tests"]`. Existing tests pin neighbouring scripts:
  - `tests/test_qa_s3_greeting.py:4` pins `qa/s3-hello.sh`.
  - `tests/test_qa_20261109_s1_a.py:7-8` pins `qa/20261109-s1/a.sh` and `qa/s3-a.sh`.
  - `tests/test_hello_sh.py:6` pins `hello-world/hello.sh`.

  No test covers the new path, and per the spec non-goals none is added.
- **External data and dependencies.** None. The script uses only `/bin/sh` and the `printf` built-in.
- **Remaining unknown.** It is not visible from the checkout whether `test` and `gate` are marked required on `main`. The spec (§6) asserts that they are.

## Locked decisions and assumptions

**Locked decisions**
- **Script path.** The script is a POSIX shell script at `qa/20261111-a3/hello.sh`, not `hello.py`. Source: spec §1, §2 Non-Goals ("A Python implementation" is out) and hld §6. This was a PO decision so the change meets gate rule 1 without an exemption.
- **Output contract.** stdout is exactly `hello from a3` plus one LF. stderr is empty. The exit code is 0. The script takes no arguments or stdin, and no option handling is added. Source: spec FR1, FR2, hld §5.
- **File contract.** The first line is `#!/bin/sh`. The git mode is `100755`. Line endings are LF only. One comment line follows the shebang. The body uses `printf`, not `echo`. Source: hld §5–§6, gate rule 2.
- **CHANGELOG.** Append exactly one bullet at the end of the `## Unreleased` list, in the existing style, naming `QA20261110-10`. No existing line is edited. Source: spec FR5, hld §5, work-item `t1` AC4.
- **No tests.** No new test of any kind, including a `test_hello.sh` or a pytest file. Source: spec §2 Non-Goals, hld §6.
- **Traceability and evidence in the PR description.** The PR description names the story and the epic PRD (Confluence page 35782657). It records the manual evidence for AC2 and AC3. Source: spec FR6, §6, work-item `t1`.

**Assumptions**
- **PRD and backlog still say `hello.py`.** The Epic PRD (R1, §7) and the backlog still name `hello.py`. The approved spec and HLD override them for this story.
  - Evidence: spec §8 records this and states that it doesn't block delivery.
  - If wrong: the PO would ask for the `.py` file, which reopens the gate rule 1 conflict. That needs a spec revision, not a plan change.
- **Exit status.** A successful `printf` as the last command gives exit 0. No explicit `exit 0` is needed, though adding one is harmless.
  - Evidence: POSIX shell semantics, and the same pattern in `qa/20261110-s3/hello.sh:3`.
  - If wrong: AC1 fails. Step 3's manual run catches it.

## Solution proposal

Add one standalone, three-line POSIX shell script in a new folder, following the existing `qa/` convention exactly. Then append one CHANGELOG bullet. Nothing else in the repository changes.

- **`qa/20261111-a3/hello.sh`.**
  - Line 1: `#!/bin/sh`.
  - Line 2: a `#` comment that says the script prints the greeting for story QA20261110-10 (epic a3, round 2).
  - Line 3: `printf 'hello from a3\n'`.
  - LF endings, a trailing newline at the end of the file, and git mode `100755`.
- **`CHANGELOG.md`.** After line 8, append ``- QA20261110-10: add `qa/20261111-a3/hello.sh`, a QA script that prints `hello from a3`.``

**Key decisions**
- `printf` over `echo`: `echo` treats escapes and `-n` differently across dash, bash and busybox.
- `#!/bin/sh` over bash: matches every other `qa/` script and needs nothing extra (AC2).
- The script isn't registered in `pyproject.toml` `[project.scripts]` and doesn't import `testbed_utils`.

**Alternatives rejected**
- A Python `hello.py`: excluded by the spec, and it breaks gate rule 1.
- A sibling `test_hello.sh` (the PLAY-175 pattern) or a pytest file under `tests/`: breaks AC4 and the spec non-goals.
- A console-script entry: a spec non-goal.

## Ordered implementation steps

1. **Create `qa/20261111-a3/hello.sh` (new).**
   - Write the three lines from the solution proposal, with LF endings only.
   - Run `chmod +x` on the file. After staging, confirm `git ls-files -s qa/20261111-a3/hello.sh` reports `100755`. If it doesn't, use `git update-index --chmod=+x`.
   - Advances AC1 and AC2, and work-item `t1` ACs 1–3.
   - Test layer: no declared layer covers `qa/`, and adding one is out of scope. Step 3's manual run is the evidence, and this gap is stated.
2. **Append the CHANGELOG bullet in `CHANGELOG.md`.**
   - Add one line after `CHANGELOG.md:8`. Don't touch any other line.
   - Advances AC4 (scope boundary, gate rule 4 / `PLAY-G4`) and work-item `t1` AC4.
   - Test layer: none, because this is a documentation file. The repository gate checks it.
3. **Collect the manual evidence for the PR description.** Run these without installing anything:
   - The new script, both ways:
     - `sh qa/20261111-a3/hello.sh`
     - `./qa/20261111-a3/hello.sh`

     Capture stdout and stderr separately and record `$?`. Confirm with `od -c` (or `cmp` against `printf 'hello from a3\n'`) that stdout is exactly `hello from a3\n`. Confirm that stderr is empty and the exit code is 0.
   - `head -1` on the script to show the shebang, and `grep -c $'\r'` (or `od`) to show it has no CR.
   - Each existing `qa/` script, recording its output and exit code. The expected results are unchanged from today:
     - `qa/s3-hello.sh` prints `hello`.
     - `qa/s3-a.sh` prints `A`.
     - `qa/20261109-s1/a.sh` prints `A`.
     - `qa/20261110-s3/hello.sh` prints `hello s3`.
     - `qa/20261110-s3/test_hello.sh` prints `PASS: …`.

   Advances AC1, AC2, AC3 and work-item `t1` ACs 1–3 and 7.
4. **Check the diff scope.** Run `git diff --name-status main...HEAD -- . ':!stories/QA20261110-10'`. It must list only:
   - `A qa/20261111-a3/hello.sh`
   - `M CHANGELOG.md`

   `git diff main...HEAD -- CHANGELOG.md` must show exactly one added line and no removed lines. Advances AC4 and work-item `t1` AC5.
5. **Run the gate and write the PR description.** Run the canonical gate (see Verification and CI gate). The PR description must:
   - name story `QA20261110-10`, "הרצת סקריפט שמדפיס "hello from a3"";
   - name the epic PRD (Confluence page 35782657) it came from;
   - include the evidence from step 3.

   Advances AC3, AC5 and AC6, and work-item `t1` ACs 6 and 8. Test layer: `package-api` (`pytest`).

**Invariants**
- **Authorization and tenancy:** not applicable. There is no input, state or data.
- **Concurrency and idempotency:** the script is stateless and re-runnable.
- **Validation and error paths:** arguments and stdin are outside the contract and are deliberately left unhandled.
- **Dependencies:** none to acquire for the script itself. The gate's `pip install -e ".[test]"` fetches `pypdf`, `flask` and `pytest` from the index and doesn't assume a warm cache.
- **Generated deliverables:** none. There is no binary of 1 MiB or more, so `.factory/delivery-assets` doesn't apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1. Create `qa/20261111-a3/hello.sh` | `t1`: Add qa/20261111-a3/hello.sh printing "hello from a3" plus its CHANGELOG entry |
| 2. Append the CHANGELOG bullet | `t1` |
| 3. Collect the manual evidence | `t1` |
| 4. Check the diff scope | `t1` |
| 5. Run the gate and write the PR description | `t1` |

`t1` is the only work item, and every step belongs to it. No work item is left without a step.

## Verification and CI gate

- **Canonical gate.** Per `.factory/testing.md` and `.github/workflows/ci.yml`, run from the repo root:
  1. `pip install -e ".[test]"`
  2. `pytest`

  Run it once locally on the committed SHA. The provider CI run at the exact head is authoritative.
- **Required layer.** `package-api` (`pytest`) is the only required layer, and it can run in a pod. It must pass with the same result as on `main`, with no new failures. That covers `tests/test_qa_s3_greeting.py`, `tests/test_qa_20261109_s1_a.py` and `tests/test_hello_sh.py`, which pin the neighbouring scripts (AC3).
- **`gate` job.** It stays green because no `CI_FAIL` file is added. It is a testbed switch, not a declared layer.
- **Repository gate (`mr-gate`).** All four rules must pass. Rule 2 is shown by mode `100755` and the shebang. Rule 4 is shown by the CHANGELOG line.
- **Not covered by any declared layer.** The new script's own behaviour (AC1, AC2) has no automated layer. Its proof is the manual evidence from step 3, recorded in the PR. This is a known, accepted gap, because the spec forbids new tests.
- **Configuration obligations.** No provider CI change is needed. `.factory/testing.md` needs no update, and there are no `.factory/delivery-assets` obligations.
- **Done means:**
  - `test` and `gate` are green on the PR head;
  - the repository gate passes with no findings;
  - the diff-scope check from step 4 holds;
  - the PR description carries the traceability and the manual evidence.

## Risks and scope guards

**Risks**
- **Missing executable bit.** Gate rule 2 fails and `./` invocation fails. Mitigation: the `git ls-files -s` check in step 1.
- **CRLF endings or an `echo` variant.** The output is no longer exact. Mitigation: `printf`, plus the `od` and CR checks in step 3.
- **Scope creep (RK1).** Any extra file breaks AC4. Mitigation: the diff check in step 4.
- **A reviewer applies G1 or G2 (RK2).** They might expect tests or `--help`. The spec non-goals and PRD §7 record why these don't apply. Cite them in the PR description.
- **PRD and spec disagree on `.py` vs `.sh`.** Mitigation: state the PO's decision (spec §8) in the PR description.

**Scope guards: the implement phase must NOT:**
- add any test, including `qa/20261111-a3/test_hello.sh`, any file under `tests/` or any change to `pyproject.toml` `testpaths`;
- add `--help`, options, argument parsing or stdin handling;
- register a console script or touch `pyproject.toml` at all;
- edit `README.md`, `docs/`, the version, or any existing `CHANGELOG.md` line;
- touch `src/`, `tests/`, `hello-world/`, `.github/`, `.factory/`, other `qa/` files, or create or alter `qa/20261110-a3/`;
- edit `spec.md`, `hld.md` or `work-items.md` in this plan folder;
- make a check green by deleting, skipping, disabling or weakening it. A failing check is reported as blocked.

## Clarification outcomes

None.
