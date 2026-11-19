# Plan — SCRUM-22 Hello world bash script in a dedicated folder

## Context

SCRUM-22 asks for `hello-world/hello.sh`, a bash script that is the only file in its own top-level folder, starts with `#!/bin/bash`, is executable, and prints exactly `hello world` with exit code 0 (Scenarios 1–4 in `spec.md` §5). The change lands in `play1` on the work branch `halo/feat/scrum-22-20261119-012944`, which merges into `main`. The script already exists on `main`, so the work is to check it against the criteria, add the `CHANGELOG.md` line the repository gate requires, and record the evidence in the PR. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/SCRUM-22/`.

## Research findings

- **Script (exists, unchanged):** `hello-world/hello.sh:1` is `#!/bin/bash`; `hello-world/hello.sh:2` is `echo "hello world"`. Line endings are LF with a trailing newline (`cat -A`). The git index mode is `100755` (`git ls-files -s hello-world/`). `ls -A hello-world/` lists only `hello.sh`, with no dot-files.
- **Existing automated coverage:** `tests/test_hello_sh.py` already asserts:
  - exit 0 and `stdout == "hello world\n"` (`tests/test_hello_sh.py:10-15`);
  - empty stderr (`:17-21`);
  - exact output (`:23-28`);
  - shebang (`:32-34`);
  - the user-execute bit (`:36-38`);
  - that the folder holds only `hello.sh`, ignoring dot-files (`:40-43`).

  It runs the script directly through `subprocess`, with no `bash` prefix, so it exercises the shebang path for Scenario 3. It does not run the script from inside `hello-world/` (the cwd edge case). It does not see dot-files.
- **Changelog:** `CHANGELOG.md:3` is `## Unreleased`, followed by entries in the form `- PLAY-NNN: add \`path\`, ...` (`CHANGELOG.md:5-8`). No entry mentions `hello-world` yet.
- **Gate contracts:**
  - `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, rule 2: a shell script must be executable and start with a shebang. This is already true.
  - The same file, rule 4: the PR must add a line under `## Unreleased` in `CHANGELOG.md`. Without it, blocker `PLAY-G4` fails the gate.
  - Rule 3: no file over 200 KB. This does not apply here.
- **Canonical test gate:** `.factory/testing.md` and `.github/workflows/ci.yml` define it. The `test` job runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. It has one declared layer, `package-api` (`runBy: canonical-gate`). The `gate` job fails only if `CI_FAIL` exists at the repo root, and that file is absent. There is no linter or formatter.
- **Dependencies:** there is no external data and no other system involved. The only runtime is `/bin/bash`.
- **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**
- Keep the existing `hello-world/hello.sh` as the deliverable. Change it only if a check fails (spec A1, `hld.md` §6).
- "Exactly `hello world`" allows one terminating newline (spec A2). This matches `tests/test_hello_sh.py:15`.
- One `CHANGELOG.md` line under `## Unreleased` is in scope and is not a "documentation file" (spec A3; repo-gate rule 4, `PLAY-G4`).
- Do not add scripts, tests, CI jobs or docs (spec §2 Non-Goals; `hld.md` §6).
- There is one work item, `t1` (`work-items.md`).

**Assumptions**
- The changelog line uses the story key `SCRUM-22` in the existing entry style. Evidence: `CHANGELOG.md:5-8` uses `<KEY>: add \`path\`, ...`. If this is wrong, the line only needs rewording, and the gate still passes because it checks only that the line exists.
- The PR description is the place for the manual evidence (`work-items.md` t1, last criterion). If this is wrong, the evidence moves to wherever the reviewer asks. The code does not change.

## Solution proposal

Change no code. The script already satisfies FR1–FR5. Rewriting it would only add risk, for example losing the mode or introducing CRLF line endings.

The deliverable is:
1. One added line under `## Unreleased` in `CHANGELOG.md` that names SCRUM-22 and `hello-world/hello.sh`.
2. A recorded run of the manual checks for Scenarios 1–4 in the PR description. This includes the cwd edge case and the dot-file listing, which `tests/test_hello_sh.py` does not cover.
3. A green canonical gate. The existing `tests/test_hello_sh.py` provides the automated proof for each scenario.

**Alternatives rejected**
- *Rebuild the script:* rejected because it contradicts spec A1.
- *Add a test for the cwd case or dot-files:* rejected because the spec rules out CI integration and new tests (Non-Goals), and `hld.md` §6 says not to add tests. Manual evidence covers these gaps instead.
- *Leave `CHANGELOG.md` alone:* rejected because the gate would block the PR with `PLAY-G4`.

## Ordered implementation steps

1. **Verify the script.** Do not edit any file in this step. Run each check below from the repo root and save the output for the PR. *Test layer:* manual evidence, plus `tests/test_hello_sh.py` in the `package-api` layer.
   - `./hello-world/hello.sh; echo "exit=$?"` (Scenario 1)
   - `./hello-world/hello.sh 2>&1 >/dev/null | wc -c` should print `0` (no stderr)
   - `[ "$(./hello-world/hello.sh)" = "hello world" ]` and `./hello-world/hello.sh | od -c` (Scenario 4: exactly `hello world\n`)
   - `(cd hello-world && ./hello.sh; echo "exit=$?")` (cwd edge case)
   - `head -1 hello-world/hello.sh` (Scenario 3)
   - `git ls-files -s hello-world/` should show only `100755 ... hello-world/hello.sh`
   - `ls -A hello-world/` should list only `hello.sh` (Scenario 2)
   - `file hello-world/hello.sh` should not report CRLF

   If any check fails, fix only `hello-world/hello.sh`. Keep its two-line content, LF line endings and mode `100755` (`git update-index --chmod=+x` if needed). Re-run the checks after the fix.
2. **Add the changelog line.** Append one line to `CHANGELOG.md` directly after the last existing `## Unreleased` entry (`CHANGELOG.md:8`), in the existing style. For example: `- SCRUM-22: add \`hello-world/hello.sh\`, a bash script in its own folder that prints \`hello world\`.` Do not change any other line. *Advances:* the gate requirement (`PLAY-G4`), spec A3. *Test layer:* none in the repo. The repo-gate rule 4 reviewer checks it at PR time.
3. **Run the canonical gate** once on the committed SHA: `pip install -e ".[test]"`, then `pytest`. Confirm that `CI_FAIL` is absent. *Advances:* all four scenarios through `tests/test_hello_sh.py`. *Test layer:* `package-api`.
4. **Write the PR evidence.** Put the Step 1 outputs in the PR description, mapped to Scenarios 1–4 and the cwd edge case. Add one sentence explaining that the diff contains only the changelog line, because the script was already on `main` (spec A1). *Test layer:* not applicable (documentation of evidence).

**Invariants:**
- Authorization, tenancy, concurrency and input validation do not apply: the script takes no input and holds no state.
- Dependencies come only from `pip install -e ".[test]"` (pytest, pypdf). Do not assume a warm cache.
- There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Confirm hello-world/hello.sh against SCRUM-22 criteria and record it in CHANGELOG |
| 2 | t1 | Confirm hello-world/hello.sh against SCRUM-22 criteria and record it in CHANGELOG |
| 3 | t1 | Confirm hello-world/hello.sh against SCRUM-22 criteria and record it in CHANGELOG |
| 4 | t1 | Confirm hello-world/hello.sh against SCRUM-22 criteria and record it in CHANGELOG |

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"`, then `pytest`, from the repo root on Python 3.12. Run it once locally on the committed SHA. The provider `test` job reruns it at the PR head, and that run is authoritative (`.factory/testing.md`).
- **Required layer:** `package-api` (`pytest`). It can run in a pod without privileges.
- **`gate` job:** passes as long as there is no `CI_FAIL` at the repo root.
- **Provider CI changes:** none.
- **`.factory/delivery-assets`:** not applicable.
- **Done means all of the following:**
  - `pytest` is fully green, including all 6 tests in `tests/test_hello_sh.py`.
  - Both CI jobs are green.
  - The diff touches only `CHANGELOG.md`, plus `hello-world/hello.sh` only if a Step 1 check failed.
  - `git ls-files -s hello-world/` still shows only `hello.sh` at `100755`.
  - The PR carries the Step 1 evidence.

## Risks and scope guards

**Risks**
- **Near-empty diff:** this is expected under spec A1. Mitigation: the PR description says so explicitly.
- **A stray dot-file in `hello-world/` (`.gitkeep`, `.DS_Store`):** this would break Scenario 2 without failing CI, because `tests/test_hello_sh.py:42` ignores dot-files. Mitigation: the `ls -A` and `git ls-files` checks in Step 1.
- **An edit to the script that drops the mode or adds CRLF line endings:** this would break direct execution. Mitigation: do not edit the script unless a check fails, and re-check the mode and line endings afterwards.

**Scope guards (do NOT)**
- Do not add files under `hello-world/`, including a README, `.gitkeep` or extra scripts.
- Do not add or modify tests. In particular, leave `tests/test_hello_sh.py` unchanged and do not loosen its newline assertion.
- Do not touch `.github/workflows/ci.yml`, `.factory/`, `README.md`, `pyproject.toml`, `qa/`, `src/` or `docs/`.
- Do not rewrite the existing `CHANGELOG.md` entries. Add exactly one line.
- Do not create `CI_FAIL`.
- Do not make a failing check green by deleting, skipping or weakening it. Report it as blocked instead.

## Clarification outcomes

None.
