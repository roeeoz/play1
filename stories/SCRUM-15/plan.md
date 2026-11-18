# Implementation plan — SCRUM-15: Hello world bash script in a dedicated folder

## Context

SCRUM-15 asks for a runnable `hello-world/hello.sh` with a `#!/bin/bash` shebang that prints exactly `hello world` and exits 0. It must be the only file in its own top-level folder (acceptance criteria 1–4 in `spec.md` §5). The script and its pytest coverage are already on `main`, the target branch. The only missing deliverable is the change record that the repository gate requires (FR6). The change lands in `play1` on `halo/feat/scrum-15-20261118-232921`, which was cut from `main`. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/SCRUM-15/`. The work-item breakdown has a single item, `t1`.

## Research findings

**Already delivered (verified on the checkout):**
- `hello-world/hello.sh:1-2`: the file is `#!/bin/bash` followed by `echo "hello world"`, with Unix line endings (`cat -A` shows no `\r`). It is the folder's only file. `git ls-files -s` reports mode `100755`.
- It was introduced by `65938b5` ("WI-220A63-1: Add hello-world bash script in dedicated folder"). The tests came in `a2ec96d`. The last commit touching these paths is `9a5bd0b`.
- `tests/test_hello_sh.py:9-43` covers each acceptance criterion:

  | Acceptance criterion | Tests in `tests/test_hello_sh.py` |
  |---|---|
  | AC1 | `test_prints_hello_world`: returncode 0, stdout `"hello world\n"` |
  | AC2 | `test_folder_contains_only_hello_sh` |
  | AC3 | The tests run `[str(SCRIPT)]` directly, without `bash`. `test_shebang_line` and `test_executable_permission` cover the shebang and the execute bit. |
  | AC4 | `test_exact_output_no_extra_whitespace` and `test_no_stderr` |

**Change surface:**
- `CHANGELOG.md:3-8`: the `## Unreleased` section has four entries.
- Each entry follows the form ``- <KEY>: add `<path>`, a … script that prints `<text>`.``
- The last entry is at `CHANGELOG.md:8`. SCRUM-15 has no entry yet.

**Contracts:**
- Repository gate, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`:
  - Rule 4 (lines 17-20): a PR whose diff does not touch `CHANGELOG.md` gets the blocker `PLAY-G4`.
  - Rule 2 (line 15) applies only to a *new* shell script. This PR adds none.
- Canonical test gate, `.factory/testing.md`: `test-gate: pytest`, run after `pip install -e ".[test]"`, with a single required layer `package-api`, `runBy: canonical-gate`.
- CI, `.github/workflows/ci.yml`:
  - The `test` job runs `pip install -e ".[test]"`, then `pytest` on Python 3.12.
  - The `gate` job fails only if `CI_FAIL` exists at the repository root.
- `pyproject.toml:28-30` sets `testpaths = ["tests"]`, so `tests/test_hello_sh.py` is collected.

**Remaining work:**
- Create: nothing.
- Edit: one line in `CHANGELOG.md`.
- External data: none.
- Unknowns: none.

## Locked decisions and assumptions

**Locked decisions**
- The existing `hello-world/hello.sh` is the delivery and is not rewritten (`spec.md` FR5 / A1, `hld.md` §6).
- One line under `## Unreleased` in `CHANGELOG.md` is required. It is a change record, not documentation (`spec.md` FR6 / A3, repo-gate rule 4 / `PLAY-G4`).
- One terminating newline in the output is correct (`spec.md` FR4 / A2). `tests/test_hello_sh.py:15` asserts the same.
- The existing tests are reused. No new test and no CI change (`hld.md` §6, story out-of-scope list).
- Nothing in `hello-world/`, `tests/` or `.github/` changes (`work-items.md` t1, "Consumes (read-only)").

**Assumptions**
- The new entry follows the style of `CHANGELOG.md:5-8` and is appended after line 8 as the last item of the list.
  - Evidence: every previous story appended at the bottom.
  - If wrong: only the order of the list changes, and no check depends on it.
- The CI runner keeps `/bin/bash` and preserves the git `100755` mode on checkout.
  - Evidence: the runner is `ubuntu-latest` and `actions/checkout@v4` preserves file modes.
  - If wrong: `test_prints_hello_world` and `test_executable_permission` fail, but that would be a pre-existing environment fault, not something this change introduced.

## Solution proposal

Deliver SCRUM-15 as a change-record-only PR:
- Add one line under `## Unreleased` in `CHANGELOG.md` attributing `hello-world/hello.sh` to SCRUM-15.
- Rely on the existing script and the existing `tests/test_hello_sh.py`, which already prove AC1–AC4 and run in the CI `test` job on every PR.

Proposed line, in the existing style: ``- SCRUM-15: add `hello-world/hello.sh`, a bash script in its own `hello-world/` folder that prints `hello world`.``

Key decisions:
- Touch only `CHANGELOG.md`. Any other edit would either duplicate what exists or break AC2 (folder isolation).
- The PR description carries the traceability:
  - The script and its tests come from WI-220A63-1 (`65938b5`, `a2ec96d`).
  - They already meet AC1–AC4.
  - This PR adds only the record.

Alternatives rejected:
- Rewriting `hello.sh`: produces the identical file.
- A new test or a CI step: duplicates `tests/test_hello_sh.py`, and CI/CD is out of scope.
- A README in `hello-world/`: out of scope, and it fails `test_folder_contains_only_hello_sh`.
- Closing the story with no PR: no traceable delivery, and the developer chose A3.

## Ordered implementation steps

1. **Confirm the baseline.**
   - Read `hello-world/hello.sh` and check `git ls-files -s hello-world` (one entry, `100755`).
   - Confirm `hello-world/` has no other file.
   - Advances AC1–AC4. Covered by `tests/test_hello_sh.py` (layer `package-api`).
   - Make no change in this step.
2. **Add the change record.**
   - Append exactly one line after `CHANGELOG.md:8`, under `## Unreleased`, in the form given in the Solution proposal.
   - Keep the `- ` bullet, backticked paths and the trailing period.
   - Change no other line, and keep the file's final newline.
   - Advances FR6 / repo-gate rule 4 (`PLAY-G4`) and `t1`'s acceptance criterion "exactly one new line".
   - Test layer: none in `pytest`. The repository gate (`repo-gate` skill, rule 4) and diff review cover it.
3. **Check the diff boundary.**
   - `git diff --stat main...HEAD` lists only `CHANGELOG.md` outside `stories/SCRUM-15/`.
   - No file is added in `hello-world/`, `tests/` or `.github/`.
   - No `CI_FAIL` exists at the repository root.
   - Advances `t1`'s acceptance criterion "the diff touches nothing in `hello-world/` or `tests/`" and AC2. Covered by `test_folder_contains_only_hello_sh`.
4. **Run the canonical gate once on the committed SHA** (see Verification and CI gate).
   - Dependencies come from a clean `pip install -e ".[test]"`, with no reliance on a warm cache.
   - Advances AC1–AC4 through `tests/test_hello_sh.py` (layer `package-api`).
5. **Write the PR description.**
   - Trace it to SCRUM-15.
   - Name WI-220A63-1 (`65938b5`, `a2ec96d`) as the origin of the script and its tests.
   - Map AC1–AC4 to the tests in `tests/test_hello_sh.py`.
   - State that the PR adds only the change record.
   - Advances `t1`'s traceability criterion. Test layer: none; this is reviewer-facing.

Implicit invariants:
- Authorization and tenancy: not applicable, because there is no runtime surface.
- Concurrency and idempotency: not applicable. The script has no state and no inputs.
- Validation and error paths: not applicable, because the script takes no arguments.
- Generated deliverables: none. No binary is added, so there is no `.factory/delivery-assets` obligation.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | `t1` | Record the hello-world bash script for SCRUM-15 in CHANGELOG.md |
| 2 | `t1` | Record the hello-world bash script for SCRUM-15 in CHANGELOG.md |
| 3 | `t1` | Record the hello-world bash script for SCRUM-15 in CHANGELOG.md |
| 4 | `t1` | Record the hello-world bash script for SCRUM-15 in CHANGELOG.md |
| 5 | `t1` | Record the hello-world bash script for SCRUM-15 in CHANGELOG.md |

`t1` is the only work item, and every step maps to it.

## Verification and CI gate

**Canonical gate.** Run once, in this order, from the repository root on the committed SHA: `pip install -e ".[test]"`, then `pytest` (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`).

**Required layer.** `package-api` (`pytest`).
- It runs unprivileged in a pod, so the local run is a pre-push check.
- The authoritative result is the provider run of the `test` job at the PR head (`runBy: canonical-gate`).

**What "done" requires:**
- `pytest` passes the whole suite, including the six tests in `tests/test_hello_sh.py`.
- The CI `gate` job is green, because no `CI_FAIL` marker exists.
- The repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) reports no blocker, in particular no `PLAY-G4`.
- The diff is only the one-line `CHANGELOG.md` addition, plus the platform-committed `stories/SCRUM-15/` folder.

**Out of scope:** provider CI changes are not needed. `.factory/testing.md` needs no update, because no layer changes.

## Risks and scope guards

**Risks:**
- A reviewer may expect a change to the script in a PR that only touches the changelog. Mitigation: the PR description from step 5.
- Other `origin/halo/feat/*` branches modify `hello-world/` or the test. They are not the base. Mitigation: work only from `main`, as the branch was cut.

**Scope guards.** The implement phase must NOT:
- Modify, re-create, reformat or change the mode of `hello-world/hello.sh`.
- Add any file in `hello-world/`, which would break AC2.
- Edit `tests/test_hello_sh.py`, add tests, or touch `.github/workflows/ci.yml` or `.factory/`.
- Add a README or other documentation file.
- Edit or reorder existing `CHANGELOG.md` entries, or add more than one line.
- Edit `stories/SCRUM-15/spec.md`, `hld.md` or `work-items.md`.
- Merge or rebase onto any branch other than `main`.
- Skip, delete, mark `xfail` or weaken any test, or create `CI_FAIL`. A failing check is reported as blocked, never made green.

## Clarification outcomes

None. The developer's direction recorded in `spec.md` §8 (A1–A3) settles every open point, and no locked source conflicts with the repository.
