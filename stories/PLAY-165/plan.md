# Plan — PLAY-165: QA script that prints "c" and exits 0

## Context

PLAY-165 adds one executable bash script, `qa/20261109-s6/c.sh`, that writes exactly `c` plus LF to stdout, writes nothing to stderr, and exits 0 for any arguments, including `--help`. The change also appends the one `CHANGELOG.md` line that the repo gate (rule `PLAY-G4`) requires. The work lands in `roeeoz/play1` on the work branch `halo/feat/play-165-20261109-101128`, cut from and merging into `qa-20261109-s6-base`. The approved requirement (`spec.md`), the design (`hld.md`) and the breakdown (`work-items.md`, one item `t1`) sit beside this file in `stories/PLAY-165/`. The spec's acceptance criteria AC1–AC6 and t1's criteria 1–8 are the targets.

## Research findings

**Change surface (all facts read from the checkout):**
- `qa/` holds two flat scripts, `qa/s3-a.sh` and `qa/s3-hello.sh`. Both are git mode `100755` (`git ls-files -s qa`) and use LF endings. Each is three lines: `#!/bin/sh`, a `#` comment, then `printf '<text>\n'` (`qa/s3-a.sh:1-3`, `qa/s3-hello.sh:1-3`). There is no subdirectory under `qa/` yet, so `qa/20261109-s6/` is new.
- `CHANGELOG.md:3` is `## Unreleased`. `CHANGELOG.md:5-6` hold one bullet per story in the form ``- PLAY-<n>: add `<path>`, a helper script that prints `<x>`.`` The file ends with a single LF after line 6.
- `pyproject.toml:14-18` declares the console scripts `pdf-extract`, `testbed-num-summary`, `testbed-hello` and `guestbook`. The new script is not registered there (spec non-goal).

**Contracts:**
- CLI contract (`hld.md` §5): stdout is the bytes `0x63 0x0A`, stderr is empty, exit code is 0, and arguments are ignored.
- Repo contract: git mode `100755`, first line a shebang, LF line endings.
- Repo-gate rules (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:15-20`):
  - Rule 2: a new shell script is executable and has a shebang.
  - Rule 3: no file over 200 KB.
  - Rule 4 / `PLAY-G4`: the PR adds a line under `## Unreleased` in `CHANGELOG.md`.

**Tests and gate:**
- `.factory/testing.md:3` declares `test-gate: pytest`. The single required layer is `package-api` (`runBy: canonical-gate`).
- `.github/workflows/ci.yml` has two jobs:
  - `test`: `pip install -e ".[test]"` then `pytest` on Python 3.12.
  - `gate`: fails iff `CI_FAIL` exists at the repo root.
- No linter, formatter, type checker or coverage tool is configured.
- `tests/test_qa_s3_greeting.py:4` and `tests/test_hello_sh.py` address their scripts by explicit path; nothing globs `qa/`. So the new directory cannot change the existing suite's result.

**External data:** none.

**Unknowns remaining:** none.

## Locked decisions and assumptions

**Locked decisions:**
- Path `qa/20261109-s6/c.sh`, output `c` then LF, exit 0, arguments ignored, no help text (spec FR1–FR4, AC1–AC2; Epic PRD §7).
- Shebang `#!/bin/bash` (spec §7 default; `hld.md` §6; t1 criterion 3).
- Print with `printf`, not `echo` (`hld.md` §6).
- No automated test file (spec Non-Goals; Epic PRD §7, §8; `hld.md` §6).
- Exactly one `CHANGELOG.md` line under `## Unreleased`. This deliberately departs from Epic PRD R4 and §8 (spec §6 and §8 override them; t1 criterion 4).
- Git mode `100755` and LF endings (repo-gate rule 2; t1 criterion 3).
- The PR description cites PLAY-165 and the QA-20261109-S6 Epic PRD (Confluence pageId 33980417), with no secrets or personal data (spec FR7, AC6; t1 criteria 7–8).
- Base and merge target are `qa-20261109-s6-base` only.

**Assumptions:**
- A one-line `#` comment after the shebang, following the `qa/s3-*.sh` convention, is not "other output".
  - Evidence: comments produce no output.
  - If wrong: drop the comment. The behaviour is unchanged.
- The CHANGELOG line follows the existing wording: ``- PLAY-165: add `qa/20261109-s6/c.sh`, a QA script that prints `c`.``
  - Evidence: `CHANGELOG.md:5-6`.
  - If wrong: rewording costs nothing, and rule 4 only needs a describing line.

## Solution proposal

Add a standalone leaf script that mirrors the existing `qa/s3-*.sh` scripts. It has three lines:
1. The shebang `#!/bin/bash`.
2. A one-line `#` comment naming its purpose (PLAY-165 / QA-20261109-S6).
3. `printf 'c\n'`.

The script never reads its arguments, so `--help` and any other input produce the same 2 bytes and exit 0. `printf` returns 0, so the script exits 0 without an explicit `exit 0` (adding one is harmless). Create the file inside the new directory `qa/20261109-s6/`. Set its executable bit in the index so git records `100755`.

Append one bullet to the end of the `## Unreleased` list in `CHANGELOG.md`, after the PLAY-156 line and in its style.

Alternatives rejected:
- `#!/bin/sh`: matches the siblings, but the spec's bash default wins.
- `echo c`: `printf` is byte-exact across shells.
- An argument-parsing `--help` branch: violates AC2 and the Epic decision.
- A pytest file: forbidden as an extra product file.
- Registering the script in `[project.scripts]`: a non-goal.

## Ordered implementation steps

1. **Create `qa/20261109-s6/c.sh` (new).**
   - Content: `#!/bin/bash`, a one-line comment, then `printf 'c\n'`.
   - Use LF endings with a trailing LF and no CR.
   - Advances AC1, AC2 and t1 criteria 1–3.
   - Test layer: none in the repo, because an automated test is out of scope. Prove it by the manual runs in step 4.
2. **Make the script executable and record mode `100755`.** Run `chmod +x qa/20261109-s6/c.sh`, then confirm with `git ls-files -s qa/20261109-s6/c.sh` once it is staged.
   - Advances t1 criterion 3 and repo-gate rule 2.
   - Test layer: none. Prove it by the mode check.
3. **Append the changelog line in `CHANGELOG.md`.** Add one line after `CHANGELOG.md:6`: ``- PLAY-165: add `qa/20261109-s6/c.sh`, a QA script that prints `c`.`` Keep the file's trailing LF and touch no other line.
   - Advances AC3, t1 criterion 4 and rule `PLAY-G4`.
   - Test layer: none. Prove it with `git diff` showing exactly one added line.
4. **Verify behaviour by hand from the repo root, and record the output for the PR description.**
   - Run `bash qa/20261109-s6/c.sh | od -c`: expect `c  \n` only.
   - Run `bash qa/20261109-s6/c.sh 2>&1 >/dev/null | wc -c`: expect `0`.
   - Run `bash qa/20261109-s6/c.sh; echo $?`: expect `0`.
   - Repeat the three checks with `--help` and with an arbitrary argument.
   - Run `./qa/20261109-s6/c.sh` directly and expect the same output.
   - Run `grep -c $'\r' qa/20261109-s6/c.sh`: expect `0`.
   - Advances AC1, AC2 and t1 criteria 1–3.
5. **Regression runs (AC5, t1 criterion 6).**
   - Run `qa/s3-a.sh` and `qa/s3-hello.sh`: expect `A` and `hello`.
   - After `pip install -e ".[test]"`, run `pdf-extract --help`, `testbed-num-summary --help`, `testbed-hello` and `guestbook --help`. Confirm the output matches the base branch. These files are untouched, so this is evidence, not a fix.
   - Covered by the existing `package-api` layer (`pytest`), which already exercises these entry points and the `qa/s3-*.sh` scripts.
6. **Diff hygiene (AC3, t1 criteria 4 and 8).**
   - `git diff --stat qa-20261109-s6-base...HEAD`, excluding `stories/PLAY-165/`, lists only `qa/20261109-s6/c.sh` (added) and `CHANGELOG.md` (+1 line).
   - No `CI_FAIL` file at the root.
   - No secrets or personal data in the script or commit messages.
7. **PR description (AC6, t1 criterion 7).** It must:
   - cite PLAY-165 and the QA-20261109-S6 Epic PRD (Confluence pageId 33980417);
   - paste the step 4 runs (with no arguments and with `--help`, the exit codes, and the `git ls-files -s` mode);
   - note that the CHANGELOG line departs deliberately from Epic PRD R4 and §8, per the story spec;
   - state that `stories/PLAY-165/` holds planning docs, not product files.

Invariants:
- Authorization and tenancy, concurrency and idempotency: not applicable. The script holds no state and takes no input.
- Validation and error paths: not applicable, because arguments are ignored by contract.
- Dependencies: none beyond `bash`. The gate's install step installs from `pyproject.toml` with no warm cache.
- Generated deliverables: none, so nothing goes in `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–7 | `t1` — PLAY-165: add qa/20261109-s6/c.sh that prints "c" and exits 0 |

`t1` is the only work item, and every step maps to it.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md:3`; `.github/workflows/ci.yml`): `pip install -e ".[test]"` then `pytest` from the repo root on Python 3.12. Run it once locally on the committed SHA. The provider's `test` job at the PR head is the authoritative result for the `package-api` layer.
- **`gate` job:** green iff there is no `CI_FAIL` at the root.
- **Repo gate (`mr-gate` slot):** rules 2, 3 and 4 must pass. The script is `100755` with a shebang, both files are well under 200 KB, and the `## Unreleased` line is present.
- **Required layers:** only `package-api`, and it runs in a pod. No layer needs another environment.
- **No CI configuration change.** No edit to `.factory/testing.md` and no `.factory/delivery-assets` entry.
- **What done looks like:**
  - `pytest` passes with the same test count as the base branch, since no test is added or removed.
  - The `test` and `gate` jobs are green on the PR.
  - The step 4 manual evidence shows stdout of exactly `c\n`, empty stderr and exit 0, both bare and with `--help`.
  - `git ls-files -s` shows `100755`.

## Risks and scope guards

**Risks:**
- **Missing executable bit:** gate rule 2 fails. Mitigation: step 2's mode check.
- **No CI check on the output:** a wrong output would still pass CI. Mitigation: the byte-level manual evidence in steps 4 and 7.
- **CHANGELOG conflict with a parallel story:** resolve by keeping both lines. Never rebase onto or merge another branch.
- **Reviewer reads "one file" literally (AC3, RK1/RK2):** the PR description explains the CHANGELOG override and the planning docs.

**The implement phase must NOT:**
- touch `qa/s3-a.sh`, `qa/s3-hello.sh`, `src/`, `tests/`, `.github/`, `.factory/`, `pyproject.toml`, `README.md`, `docs/`, or any CHANGELOG line other than the one appended;
- add a test, documentation or a `[project.scripts]` entry;
- add `--help` handling or any output beyond `c`;
- create a `CI_FAIL` file;
- edit `spec.md`, `hld.md` or `work-items.md`;
- base on, diff against, or merge any branch other than `qa-20261109-s6-base`.

A failing check may be reported as blocked. It must never be skipped, deleted or weakened, for example with `-k` subsets, skip markers or `|| true`.

## Clarification outcomes

None.
