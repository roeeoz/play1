# Plan — PLAY-163: `qa/pe-greet.sh` prints "hello pe" and exits 0

## Context

PLAY-163, the only story of epic PE-20261108 greeting, adds one standalone `sh` script, `qa/pe-greet.sh`, to `roeeoz/play1`. The script prints exactly `hello pe\n` to stdout, writes nothing to stderr, ignores every argument (including `--help`) and always exits 0. It must be runnable directly. The PR also adds one line under `## Unreleased` in `CHANGELOG.md`, because the repository's merge gate requires it. Acceptance criteria in brief: AC1 is a direct run that gives `hello pe\n` and exit 0. AC2 is an empty stderr. AC3 is the same result with `--help` and with `x y`. AC4 limits the product diff to the new script plus one changelog line. AC5 is a regression check: `qa/s3-hello.sh` and `qa/s4-greet.sh` stay unchanged and the required checks are green. The change lands on the work branch `halo/feat/play-163-20261108-093418`, which was cut from and merges into `qa-20261108-s4-base`. The approved requirement (`spec.md`), the design (`hld.md`) and the breakdown (`work-items.md`, single item `t1`) sit beside this file in `stories/PLAY-163/`.

## Research findings

- **`qa/` on the base branch** holds `qa/s3-hello.sh`, `qa/s4-greet.sh` and `qa/s4-base-marker.txt`. `git ls-files -s qa` records both scripts as `100755` and the marker as `100644`. `qa/s3-a.sh`, which the epic backlog names, does not exist on this branch. The spec's AC5 already uses `qa/s4-greet.sh` instead.
- **Script convention (fact).** Each neighbour has exactly three LF-terminated lines: `#!/bin/sh` (`qa/s3-hello.sh:1`), a one-line `#` purpose comment (`qa/s3-hello.sh:2`), and one fixed `printf` with a single-quoted literal (`qa/s3-hello.sh:3` `printf 'hello\n'`, `qa/s4-greet.sh:3` `printf 'hello from s4 (base)\n'`). Neither script parses arguments.
- **Changelog (fact).** `CHANGELOG.md:1` is `# Changelog`, `:3` is `## Unreleased` and `:5` is `- PLAY-114: add `qa/s3-hello.sh`, a helper script that prints `hello`.`. The file ends after line 5 with a trailing LF and has no CRLF.
- **Merge gate (repository contract).** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:15` (rule 2) requires a new shell script to be executable and to start with a shebang. `:17-20` (rule 4, blocker `PLAY-G4`) fails any PR whose diff does not add a line under `## Unreleased` in `CHANGELOG.md`. `:16` (rule 3) caps each file at 200 KB.
- **CI and canonical gate.** `.factory/testing.md` declares `test-gate: pytest` and names one required layer, `package-api` (`pytest`, `runBy: canonical-gate`). `.github/workflows/ci.yml` runs job `test` (`pip install -e ".[test]"`, then `pytest` on Python 3.12) and job `gate` (fails only if a root `CI_FAIL` file exists). No linter, formatter or shellcheck is configured.
- **Existing tests.** `tests/test_qa_s3_greeting.py` runs `qa/s3-hello.sh` through `subprocess` and checks its shape. That covers the AC5 regression for `qa/s3-hello.sh` automatically. No test covers `qa/s4-greet.sh`, and no test runs `qa/` in general (RK2).
- **Repo settings.** There is no `AGENTS.md`, `CLAUDE.md`, `.factory/memory/` or `.gitattributes`. `core.fileMode` is `true`, so git records the executable bit from the working tree.
- **What must be created:** `qa/pe-greet.sh` (new). **What must be edited:** `CHANGELOG.md`, one appended line. There are no external data, cross-repo contracts or dependencies.
- **Unknowns remaining:** none.

## Locked decisions and assumptions

**Locked decisions**
- Output is exactly `hello pe\n`, stderr is empty and the exit code is always 0. Arguments are ignored, and there is no `--help` (spec FR1–FR3; backlog blocker register).
- The shebang is `#!/bin/sh` and the script is committed executable (spec FR4; `hld.md` §6; repo-gate rule 2).
- Exactly one line goes under `## Unreleased` in `CHANGELOG.md` (spec FR5; repo-gate rule 4 `PLAY-G4`).
- No tests, no other docs and no other product files (spec FR6, AC4; `hld.md` §6).
- The PR description references PLAY-163 and the epic PRD PE-20261108 greeting. No secrets or personal data appear anywhere (spec §6).
- The base and merge target is `qa-20261108-s4-base`.

**Assumptions**
- *A purpose comment on line 2 is allowed even though the spec says "nothing else".* Evidence: `hld.md` §6, work-item AC4 and both neighbours. A comment does not affect the output. If this is wrong, a reviewer drops one line, and behaviour does not change.
- *AC4's "only these files" applies to product files.* Evidence: `hld.md` §7 and work-item AC6. The platform commits `stories/PLAY-163/*`. If this is wrong, the plan-folder docs need a scope decision by the platform, not by this story.
- *The changelog line text is* `- PLAY-163: add `qa/pe-greet.sh`, a helper script that prints `hello pe`.`, appended directly after `CHANGELOG.md:5`. Evidence: the house style of the PLAY-114 line and work-item AC5. If this is wrong, a wording change touches only that line.

## Solution proposal

Add a three-line POSIX `sh` script that mirrors `qa/s3-hello.sh` exactly: the `#!/bin/sh` shebang, a one-line `#` purpose comment, and `printf 'hello pe\n'`. After `printf` succeeds, the script's exit status is 0, so it needs no explicit `exit 0`. It has no argument handling, so arguments are ignored by construction (AC3). Commit the file with mode `100755` so it runs directly (AC1, gate rule 2). Append one changelog line after the PLAY-114 entry to satisfy `PLAY-G4`.

Key decisions:
- **`printf` with a single-quoted literal, not `echo`.** `echo`'s handling of escapes and `-n`-like arguments differs between `sh` implementations. `printf` with a constant format is byte-exact and matches the neighbours.
- **`sh`, not `bash`.** The spec requires it, it matches the directory, and the script needs no bash features.
- **No `set -e`, `set -x` or `exit` line.** Those lines add nothing. `set -x` would write to stderr, which breaks AC2.

Alternatives rejected:
- *Adding a pytest test such as `tests/test_qa_pe_greet.py`.* `tests/test_qa_s3_greeting.py` gives a ready pattern, but the spec forbids tests (FR6, AC4). Verification is a manual run plus review, as RK2 accepts.
- *Omitting the changelog line, as the original epic PRD says.* That makes `PLAY-G4` a blocker. The approved spec brings the line into scope.

## Ordered implementation steps

1. **Create `qa/pe-greet.sh` (new)** with exactly these three LF-terminated lines: `#!/bin/sh`, a one-line purpose comment (for example `# Prints "hello pe"; the PE-20261108 greeting helper script.`), and `printf 'hello pe\n'`. The file has no BOM, no CRLF and no trailing whitespace. Advances AC1, AC2 and AC3. Test layer: there is no automated layer, because tests are excluded by spec FR6. It is covered by the manual checks in step 3.
2. **Make the script executable and record the mode.** Run `chmod +x qa/pe-greet.sh`. When the file is staged, confirm that `git ls-files -s qa/pe-greet.sh` reports `100755`. If the filesystem drops the bit, use `git update-index --chmod=+x qa/pe-greet.sh`. Advances AC1 and gate rule 2. Test layer: none automated. Checked by the `git ls-files` command and the repo gate.
3. **Verify the behaviour manually from the repo root:**
   - `qa/pe-greet.sh >out 2>err; echo $?` must give `0`, with `out` equal to the bytes `hello pe\n` (check with `od -c out`) and `err` empty.
   - Repeat the run with `--help` and with `x y`.
   - Confirm there is no `\r` in the file (`grep -c $'\r' qa/pe-greet.sh` gives `0`).

   Advances AC1, AC2 and AC3. Layer: manual run, as RK2 accepts.
4. **Append one line to `CHANGELOG.md`** directly after line 5 (the PLAY-114 entry): `- PLAY-163: add `qa/pe-greet.sh`, a helper script that prints `hello pe`.`. Keep the final trailing LF and change nothing else. Advances AC4 and gate rule 4 (`PLAY-G4`). Test layer: none automated. Checked by `git diff --stat`, which must show `CHANGELOG.md | 1 +` and nothing removed.
5. **Check the regression and the scope.**
   - `qa/s3-hello.sh` must print `hello` and `qa/s4-greet.sh` must print `hello from s4 (base)`, each exiting 0.
   - `git diff --name-status qa-20261108-s4-base...HEAD -- . ':!stories/PLAY-163'` must list only `A qa/pe-greet.sh` and `M CHANGELOG.md`.
   - No `CI_FAIL` file exists at the root.

   Advances AC4 and AC5. Test layer: `package-api` (`pytest`, including `tests/test_qa_s3_greeting.py`) plus manual runs.
6. **Run the canonical gate** (`pip install -e ".[test]"` then `pytest`) and confirm it is green. Write the PR description to reference PLAY-163 and the epic PRD PE-20261108 greeting, with no secrets or personal data. Advances AC5 and spec §6 traceability. Test layer: `package-api`.

Implicit invariants: there is no authorization, tenancy, concurrency or input validation surface, because the script reads no input, files or environment. There are no dependencies to acquire beyond the existing editable install, no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–6 | `t1` — Add qa/pe-greet.sh (prints "hello pe", exits 0) and its CHANGELOG entry |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`): `pip install -e ".[test]"` and then `pytest` from the repo root on Python 3.12. Run it once locally on the committed SHA. The provider CI run at the exact head is the authoritative result. It runs in a pod without privileges.
- **Required layer:** `package-api` (`pytest`). It must pass with the existing suite unchanged and no new test files.
- **Other PR checks:** CI job `gate` must be green, so no `CI_FAIL` file. The repo merge gate (`repo-gate`) must pass rule 2 (script is `100755` and starts with `#!/bin/sh`), rule 3 (under 200 KB) and rule 4 (`PLAY-G4`: a line under `## Unreleased`).
- **Not covered by automation (RK2):** AC1–AC3 for `qa/pe-greet.sh` and the `qa/s4-greet.sh` regression. The evidence for these is the manual commands in steps 3 and 5, recorded with their output.
- **Provider CI changes:** none. **Done means:** `pytest` is green, `gate` is green, repo-gate passes, the manual checks match the exact bytes and exit codes, and the product diff is exactly `A qa/pe-greet.sh` (`100755`) plus `M CHANGELOG.md` (+1/−0).

## Risks and scope guards

**Risks**
- *Executable bit not recorded* (the file lands as `100644`). AC1 and gate rule 2 then fail. Mitigation: the `git ls-files -s` check in step 2.
- *Stray bytes in the output* from CRLF, a BOM, trailing spaces, `echo` variants or `set -x`. This breaks AC1 and AC2. Mitigation: a fixed `printf` literal and the byte checks in step 3.
- *Wrong changelog edit*: the line is placed outside `## Unreleased`, more than one line is added, or the PLAY-114 line is reformatted. Mitigation: the `+1/−0` diff check in step 4.
- *The epic text is out of date*: it names `qa/s3-a.sh` and says "one file, no changelog". The approved spec governs. Do not create `qa/s3-a.sh`.

**The implement phase must NOT:**
- Add a test (for example `tests/test_qa_pe_greet.py`), a `--help` or options branch, argument parsing, configurable text, or an explicit `exit` or `set` lines.
- Touch `qa/s3-hello.sh`, `qa/s4-greet.sh`, `qa/s4-base-marker.txt`, `src/`, `tests/`, `pyproject.toml`, `README.md`, `docs/`, `.github/workflows/ci.yml` or `.factory/`.
- Add `.gitattributes`, shellcheck or any CI step that runs `qa/`.
- Create a `CI_FAIL` file, or rebase onto, merge or diff against any branch other than `qa-20261108-s4-base`.
- Make any check green by deleting, skipping, disabling or weakening it. A failing check is reported as blocked.

## Clarification outcomes

None.
