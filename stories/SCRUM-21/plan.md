## Context

SCRUM-21 asks for a bash script `hello-world/hello.sh` in its own folder. The script starts with `#!/bin/bash`, is executable, prints exactly `hello world` and exits 0. Spec §5 sets four scenarios: execution, folder isolation, direct execution through the shebang, and exact output. That script is already on `main`, and it already meets all four. Per spec FR6/A1, the story is delivered by verifying that existing state. The pull request's only change is the `CHANGELOG.md` line that the play1 layout gate requires. The change lands in `roeeoz/play1` on the work branch `halo/feat/scrum-21-20261119-012516`, which merges into `main`. `spec.md` (requirement), `hld.md` (design) and `work-items.md` (one work item, `t1`) sit beside this file in `stories/SCRUM-21/`.

## Research findings

- **Deliverable already exists.** `git ls-files -s` reports `hello-world/hello.sh` as mode `100755`. `hello-world/hello.sh:1` reads `#!/bin/bash` and `hello-world/hello.sh:2` reads `echo "hello world"`. The file uses LF endings and has no trailing content. It is the only file in `hello-world/`.
- **Verification already exists.** Tests in `tests/test_hello_sh.py` already cover each scenario:

  | Scenario | What the test asserts | Location |
  |---|---|---|
  | AC1 (exit 0, output) | exit code `0` and stdout `== "hello world\n"` | `tests/test_hello_sh.py:10-15` |
  | AC4 (exactness) | stderr is empty | `tests/test_hello_sh.py:17-21` |
  | AC4 (exactness) | exact output, no extra whitespace | `tests/test_hello_sh.py:23-28` |
  | AC3 (shebang) | first line is the shebang | `tests/test_hello_sh.py:32-34` |
  | AC3 (direct execution) | `S_IXUSR` is set | `tests/test_hello_sh.py:36-38` |
  | AC2 (folder isolation) | folder holds only `hello.sh`, ignoring dotfiles | `tests/test_hello_sh.py:40-43` |

  The script runs as `[str(SCRIPT)]`, with no `bash` prefix, so AC3's direct execution is exercised for real.
- **CHANGELOG contract.** `## Unreleased` is at `CHANGELOG.md:3`. Entries take the form `- <KEY>: <description>.`, and the last one is `CHANGELOG.md:8` (PLAY-175). No entry mentions `hello-world/`.
- **Layout gate.** These are the rules in `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` that apply here:
  - Rule 2: a *new* shell script must be executable and have a shebang. No new script is added.
  - Rule 3: no file over 200 KB. This is trivially met.
  - Rule 4: the PR must add a line under `## Unreleased`, or the gate raises blocker `PLAY-G4`. This is the only rule that forces a change.
- **Test gate.** `.factory/testing.md` declares one layer, `package-api`: command `pytest`, required, `runBy: canonical-gate`.
  - `.github/workflows/ci.yml` job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12.
  - Job `gate` fails only when `CI_FAIL` exists. It is absent at the repo root.
  - `pyproject.toml` sets `testpaths = ["tests"]`, so `tests/test_hello_sh.py` is collected.
  - No linter or formatter is configured.
- **External data.** None.
- **Unknowns.** None remain.

## Locked decisions and assumptions

**Locked decisions**
- `hello-world/hello.sh` stays unchanged: same content, same mode `100755`, and no other file in `hello-world/`. Sources: spec FR6/A1, hld §6, `t1` acceptance criteria.
- The diff is exactly one new bullet under `## Unreleased` in `CHANGELOG.md`, prefixed `SCRUM-21:` and placed after the existing entries. Existing entries stay untouched. Sources: `t1` acceptance criteria, repo-gate rule 4.
- The output contract is `hello world\n`: one terminating newline is allowed. Sources: spec FR5/A2, `tests/test_hello_sh.py:15`.
- No change to CI, no new docs file, no extra script. Source: spec §2 Non-Goals.

**Assumptions**
- The bullet follows the existing style. Proposed wording: `- SCRUM-21: verify \`hello-world/hello.sh\`, a bash script that prints \`hello world\`.`
  - Evidence: `CHANGELOG.md:5-8`.
  - If wrong: only the wording changes, and gate rule 4 is still met.
- No gap in `tests/test_hello_sh.py` needs a new test.
  - Evidence: the table in Research findings maps every scenario to an existing assertion.
  - If wrong: the implement phase would extend that file, at the existing pytest layer.

## Solution proposal

Verify the script and leave it as it is. The architecture already contains the deliverable (`hello-world/hello.sh`) and its executable proof (`tests/test_hello_sh.py`). Both already run on every PR through the canonical `pytest` gate.

The only artefact the story adds is the traceability bullet in `CHANGELOG.md`. It does two jobs:
- it satisfies gate rule 4 (`PLAY-G4`);
- it records SCRUM-21 against the existing script.

Key decisions:
- **No rewrite of the script.** It already meets FR1–FR5. Rewriting would add churn and risk, and nothing would behave differently (A1).
- **No new test.** The existing suite already covers all four scenarios, at the repository's only declared layer.

Rejected alternatives:
- **Rewrite the script or switch it to `printf`.** This breaks "kept unchanged" and gains nothing.
- **Add a README in `hello-world/`.** It violates the Non-Goals and the folder-isolation test (`tests/test_hello_sh.py:43`).
- **Close the story without a PR.** This stays the human's option (spec A1). It isn't chosen because the factory delivers per work item, and gate rule 4 needs the CHANGELOG line.

## Ordered implementation steps

1. **Confirm the baseline.** Do this before editing, as a read-only check:
   - `git ls-files -s hello-world` shows only `100755 … hello-world/hello.sh`.
   - `./hello-world/hello.sh` prints `hello world` and exits 0.
   - `ls hello-world` lists only `hello.sh`.

   AC1–AC4. Layer: covered by `package-api` (`tests/test_hello_sh.py`). If any of these checks fails, stop and report it; do not "fix" the script.
2. **Add the CHANGELOG bullet.** Append one bullet under `## Unreleased` in `CHANGELOG.md`, directly after `CHANGELOG.md:8`, using the wording in the assumption above. Keep the file's trailing newline, and touch no other line.
   - Advances: `t1` traceability and gate rule 4.
   - Test layer: none. A changelog line has no automated test. The layout gate checks it at review.
3. **Run the gate.** Run `pip install -e ".[test]"` and then `pytest` from the repo root. This acquires dependencies from PyPI with no warm cache assumed: `pypdf`, `flask>=3`, `pytest>=8`. Every test must pass, including the 6 in `tests/test_hello_sh.py`. AC1–AC4. Layer: `package-api`.
4. **Check the diff boundary.** `git diff --stat main...HEAD` must show only `CHANGELOG.md`, apart from the platform's own `stories/SCRUM-21/` folder. `hello-world/hello.sh` must keep mode `100755`, and `CI_FAIL` must stay absent. Advances: `t1` "touches no other file".

Implicit invariants: none apply. The script takes no input and has no authz, tenancy, concurrency or error path. There are no generated deliverables and no binary assets.

## Work-item mapping

| Step | Work item |
|---|---|
| 1, 2, 3, 4 | `t1` — SCRUM-21: verify hello-world/hello.sh and record it in CHANGELOG.md |

`t1` is the only work item, and all steps belong to it.

## Verification and CI gate

- **Canonical gate.** Per `.factory/testing.md`: `pip install -e ".[test]"`, then `pytest`, run once from the repo root on the committed SHA.
- **Required layer.** `package-api` (`pytest`). It can run in a pod. The provider run at the exact head is authoritative (`runBy: canonical-gate`).
- **Provider CI.** `.github/workflows/ci.yml`:
  - job `test` must be green;
  - job `gate` must be green, which requires `CI_FAIL` to be absent.
- **Configuration changes.** None needed.
- **`.factory/delivery-assets`.** Not applicable, because no binary is added.
- **Layout gate.** It must pass rules 1–4 with no `PLAY-G4`.
- **Done means all of the following:**
  - `pytest` passes, with `tests/test_hello_sh.py`'s 6 tests green;
  - the diff contains exactly one added `CHANGELOG.md` line;
  - `hello-world/hello.sh` is byte-identical and still mode `100755`.

## Risks and scope guards

**Risks**
- **No-op delivery (spec A1).** The PR has no user-visible effect. If the requester meant something else, this story doesn't deliver it. Mitigation: the assumption is recorded in the spec, and the human reviews before merge.
- **Byte-exactness (spec A2).** The output is 12 bytes, `hello world\n`. A raw comparison against 11 bytes would fail. This is accepted per the spec.
- **Lost executable bit.** On a filesystem that ignores modes, the bit could be lost. Mitigation: `tests/test_hello_sh.py:36-38` catches it.

**Scope guards.** The implement phase must NOT:
- edit, re-create, re-mode or reformat `hello-world/hello.sh`;
- add any file to `hello-world/` or anywhere else;
- touch `tests/test_hello_sh.py`, unless a real coverage gap is found;
- touch `.github/workflows/ci.yml`, `README.md`, `pyproject.toml` or the `.factory/` files;
- reword or reorder existing `CHANGELOG.md` entries;
- create `CI_FAIL`;
- skip, delete or weaken any test to get green. A failing check is reported as blocked.

## Clarification outcomes

None.
