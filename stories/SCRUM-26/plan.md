# Plan — SCRUM-26: Hello world bash script in a dedicated folder

## Context

SCRUM-26 asks for a directly executable bash script, `hello-world/hello.sh`, that prints `hello world` and exits 0. The script must be the only file in its own top-level folder (spec scenarios 1–4: correct output, folder isolation, running through the shebang, exact output). The change lands in `play1` on the work branch `halo/feat/scrum-26-20261119-023627`, cut from `main`. The approved requirement is in `spec.md`, the design in `hld.md` and the one work item (`t1`) in `work-items.md`, all three in this folder (`stories/SCRUM-26/`). The script and its test already exist on `main`, so the work is to confirm they still meet the spec and to add the `CHANGELOG.md` bullet that the play1 layout gate requires.

## Research findings

- **The script already exists and meets the spec.**
  - `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. The file uses LF line endings.
  - Git tracks it as `100755` (`git ls-files -s hello-world`).
  - Run as `./hello-world/hello.sh` (checked this turn), it prints exactly the 12 bytes `hello world\n` and exits with status 0.
  - `ls -A hello-world` lists only `hello.sh`.
- **The test already exists.** `tests/test_hello_sh.py` covers every scenario:
  - stdout equals `"hello world\n"` and the return code is 0 (`:10-15`).
  - stderr is empty (`:17-21`).
  - The output is exact (`:23-28`).
  - The shebang line is `#!/bin/bash` (`:32-34`).
  - The owner-execute bit is set (`:36-38`).
  - The folder holds only `hello.sh`, ignoring dot-entries (`:40-43`).
- **The file to edit is `CHANGELOG.md`.** Its `## Unreleased` list runs from `CHANGELOG.md:3` to `CHANGELOG.md:8`. Every entry has the form ``- KEY: add `path`, a … script that prints `X`.``, and the last one is at `CHANGELOG.md:8`.
- **The gate contract is the play1 layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):
  - Rule 1: Python source goes under `src/` and tests under `tests/`.
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file in the diff is larger than 200 KB.
  - Rule 4: every PR adds a line under `## Unreleased` in `CHANGELOG.md`. If the diff does not touch `CHANGELOG.md`, the gate raises blocker `PLAY-G4`.
- **The canonical test gate** is set in `.factory/testing.md` and the `test` job of `.github/workflows/ci.yml`. It runs `pip install -e ".[test]"`, then `pytest`, on Python 3.12. It has one required layer, `package-api`, run by `canonical-gate`. `pyproject.toml` sets `testpaths = ["tests"]`, so `tests/test_hello_sh.py` is collected. The `gate` job fails only if a `CI_FAIL` file exists at the root, and there is none.
- **No lint, format or type-check step** is configured anywhere in the repository (`.factory/testing.md`).
- **There is no `.factory/memory/` directory**, and no `AGENTS.md` or `CLAUDE.md`.
- **The change has no cross-repository or external-data dependencies.**
- **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**
- The script lives at `hello-world/hello.sh`. Its first line is `#!/bin/bash`, it is executable and it prints exactly `hello world` (spec FR1–FR5, scenarios 1–4).
- No new test, README, CI change or extra script is added (spec §2 non-goals; `work-items.md` `t1`).
- One bullet is added under `## Unreleased` in `CHANGELOG.md` (repo-gate rule 4; spec A3; `hld.md` §5).
- If the existing script meets every criterion, nothing under `hello-world/` changes (spec A1; `hld.md` §6).
- The output is `hello world` plus one trailing newline, as `echo` prints it (spec A2; pinned by `tests/test_hello_sh.py:15`).

**Assumptions**
- **The bullet text follows the existing style.** It reads: ``- SCRUM-26: add `hello-world/hello.sh`, a script that prints `hello world`.``
  - *Evidence:* `CHANGELOG.md:5-8`.
  - *If wrong:* only the wording changes. The gate needs nothing more than an added line.
- **The CI runner keeps the `100755` mode on checkout.** `actions/checkout` preserves the git mode, so the executable test passes in CI as it does locally.
  - *If wrong:* `test_executable_permission` and the execution tests fail. That would be a real failure to report, not one to work around.

## Solution proposal

Verify first, and edit only the changelog. The deliverable already satisfies every acceptance criterion byte for byte, and `tests/test_hello_sh.py` already proves it in the CI `test` job. Rewriting the script would add churn with no change in behaviour. The PR therefore makes one functional edit: a `SCRUM-26` bullet appended after `CHANGELOG.md:8`. That edit is what keeps the PR clear of blocker `PLAY-G4`. It lives outside `hello-world/`, so the folder-isolation scenario is unaffected.

Alternatives rejected:
- **Recreate the folder and script:** no behavioural gain, and a risk of breaking the mode or the bytes.
- **Add a second test or a shell-level test:** it duplicates existing coverage, and the spec excludes it.
- **Switch to `printf 'hello world'` (no newline):** this contradicts spec A2 and would break `tests/test_hello_sh.py:15`.

Contingency: if verification in step 1 shows a criterion is not met, fix only `hello-world/hello.sh` until it is. That covers the content, the shebang, or the mode via `git update-index --chmod=+x`.

## Ordered implementation steps

1. **Verify `hello-world/hello.sh` against scenarios 1–4.** Do not edit anything in this step.
   - Check that `./hello-world/hello.sh` prints exactly `hello world\n`, writes nothing to stderr and exits 0.
   - Check that `head -1` returns `#!/bin/bash`.
   - Check that `git ls-files -s hello-world` shows `100755` and that `ls -A hello-world` shows only `hello.sh`.
   - If every check holds, leave `hello-world/` untouched. Otherwise apply the contingency in the Solution proposal.
   - *Advances:* `t1` AC 1–4 and spec scenarios 1–4.
   - *Test layer:* `package-api` (`pytest`, via `tests/test_hello_sh.py`).
2. **Append the changelog bullet.** Add ``- SCRUM-26: add `hello-world/hello.sh`, a script that prints `hello world`.`` as the last bullet under `## Unreleased`, after `CHANGELOG.md:8`. Leave the existing lines unchanged.
   - *Advances:* `t1` AC 5 and repo-gate rule 4.
   - *Test layer:* none in `pytest`. The play1 layout gate checks it at PR time.
3. **Confirm the diff stays in scope.** The only expected change is `CHANGELOG.md`, plus `hello-world/hello.sh` if the contingency applied.
   - Confirm that `tests/test_hello_sh.py` is unchanged, that nothing new exists under `hello-world/` and that no `CI_FAIL` file exists.
   - *Advances:* `t1` AC 3, 4, 6 and 7, and gate rules 1–4.
   - *Test layer:* `package-api` for the folder contents. The layout gate checks the rest.
4. **Run the canonical gate.** Run `pip install -e ".[test]"`, then `pytest`, on Python 3.12. The install step fetches dependencies, so no warm cache is assumed.
   - *Advances:* `t1` AC 6.
   - *Test layer:* `package-api`.

Implicit invariants: the change has no authorization or tenancy surface, no concurrency and no input validation, because the script reads no input or arguments. The change produces no generated deliverables and no binaries, so nothing goes into `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item |
|---|---|
| 1 | `t1` — Verify hello-world/hello.sh against the four scenarios and record it in CHANGELOG.md |
| 2 | `t1` — Verify hello-world/hello.sh against the four scenarios and record it in CHANGELOG.md |
| 3 | `t1` — Verify hello-world/hello.sh against the four scenarios and record it in CHANGELOG.md |
| 4 | `t1` — Verify hello-world/hello.sh against the four scenarios and record it in CHANGELOG.md |

There is only one work item, and every step belongs to it.

## Verification and CI gate

- **The gate:** from the repo root on Python 3.12, run `pip install -e ".[test]"` and then `pytest`. Run it once on the committed SHA.
  - It is the only required layer (`package-api`, `runBy: canonical-gate`) and it can run in a pod.
  - The provider's `test` job at the exact head is the authoritative result (`.factory/testing.md`).
- **The `gate` job** must stay green, which means no `CI_FAIL` file at the root.
- **The play1 layout gate** must pass rules 1–4. Rule 4 in particular is met by the new `CHANGELOG.md` bullet.
- **No provider CI configuration change** is needed. The change produces nothing for `.factory/delivery-assets`.
- **Done means:**
  - `pytest` reports every test passing, including all six in `tests/test_hello_sh.py`.
  - The diff touches only `CHANGELOG.md` (plus `hello-world/hello.sh` if the contingency applied).
  - The layout gate verdict is `pass: true`.

## Risks and scope guards

**Risks**
- **The PR looks empty of functional change.** Mitigate this with a PR description that cites the verification in step 1 and spec A1.
- **A byte-exact reader expecting 11 bytes** (no newline) would disagree with spec A2. Spec A2 is locked, so do not change the script for this.

**The implement phase must NOT:**
- Rewrite, reformat or re-mode `hello-world/hello.sh` while it meets the criteria.
- Add any file under `hello-world/`, including a README or `.gitkeep`.
- Edit `tests/test_hello_sh.py`, or add a new test or shell test.
- Touch `.github/workflows/ci.yml`, `.factory/`, `src/`, `qa/` or `pyproject.toml`.
- Edit or reorder existing `CHANGELOG.md` bullets.
- Add a `CI_FAIL` file.
- Skip, delete, mark xfail or weaken any `pytest` test or gate rule to get green. A failing check is reported as blocked.

## Clarification outcomes

None.
