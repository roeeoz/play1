# PLAY-190 — Implementation plan

## Context

PLAY-190 (QA factory-path story QA-20261122-S2) adds a bash greeting script `qa/s2-hello.sh` and a bash test script `qa/s2-hello-test.sh` to `roeeoz/play1`, on work branch `halo/feat/play-190-20261122-205457`, which targets `main`. The acceptance criteria: `qa/s2-hello.sh Ada` prints exactly `Hello, Ada!` and exits 0; `qa/s2-hello.sh ''` prints `name must not be empty` to stderr and exits 1. The spec replaced the ticket title's Python module (`qa/s2_hello.py`) with bash, because Python outside `src/` breaks repo-gate rule 1. The approved requirement is `spec.md`, the design is `hld.md`, and the single work item `t1` is in `work-items.md`. All three sit beside this file in `stories/PLAY-190/`.

## Research findings

- **Change surface:** two new files, `qa/s2-hello.sh` and `qa/s2-hello-test.sh`. Neither exists today. `qa/` holds `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/hello.sh` and `qa/20261110-s3/test_hello.sh`, all git mode `100755` (`git ls-files -s qa`).
- **Pattern to follow:** `qa/20261110-s3/test_hello.sh:3` locates its target with `dir=$(CDPATH= cd -P -- "$(dirname -- "$0")" && pwd)`. `qa/20261110-s3/test_hello.sh:6-9` keeps trailing newlines with a sentinel (`out=$("$target"; rc=$?; printf 'x%s' "$rc")`, then `${out##*x}` / `${out%x*}`). It prints `FAIL: …` to stderr with `exit 1` (`:14-21`) and `PASS: …` on success (`:22`). That script is `#!/bin/sh`; the new files use `#!/usr/bin/env bash` as `hld.md` §2 and the spec's FR1/FR5 require.
- **Repo gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:16-18`): rule 1 (Python under `src/`, tests under `tests/`) does not apply because no Python is added. Rule 2 ("A new shell script is executable and starts with a shebang") applies to both files. Rule 3 (≤ 200 KB) is trivially met.
- **Canonical CI gate:** `.github/workflows/ci.yml` job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. Job `gate` fails only if `CI_FAIL` exists at the repo root. `.factory/testing.md` declares `local-test-gate: pip install -q -e ".[test]" && pytest` and one layer, `package-api` (`pytest`, `runBy: canonical-gate`). `pyproject.toml` sets `testpaths = ["tests"]`, so pytest never collects anything under `qa/`.
- **No collision with existing tests:** `tests/test_qa_20261109_s1_a.py:7-8` and `tests/test_qa_s3_greeting.py:4` reference specific `qa/` files by path. No test globs `qa/`, so new files there do not affect pytest.
- **No repo memory:** `.factory/memory/` does not exist. No `AGENTS.md` or `CLAUDE.md` exists.
- **External data:** none.
- **Remaining unknowns:** none that block. The undecided behaviours (trailing newline, missing or extra argument, literal printing) are settled in `hld.md` §5–§6 and in the acceptance criteria of `t1`.

## Locked decisions and assumptions

**Locked decisions**
- The capability is bash with exactly two new files under `qa/s2-*`. No existing file changes (`spec.md` §1, §2, §6; `work-items.md` t1 "Must not change").
- Both files start with `#!/usr/bin/env bash` and are committed as mode `100755` (spec FR1, FR5; repo-gate rule 2).
- CLI contract (`hld.md` §5): for `Ada`, stdout is `Hello, Ada!\n`, stderr is empty, and the exit code is 0. For `''` or no argument, stdout is empty, stderr is `name must not be empty\n`, and the exit code is 1. For `'   '`, stdout is `Hello,    !\n` and the exit code is 0. Extra arguments are ignored. The name is printed literally, so `-n` and `%s` appear as given.
- Output is produced with `printf 'Hello, %s!\n' "$1"`, not `echo` (`hld.md` §5).
- The test checks exact stdout bytes, stderr and the exit code for both cases. It locates the target relative to its own path and prints a `FAIL:` line on stderr naming the failing case (`hld.md` §2, §6; t1 AC).
- The bash test is not wired into CI. Its output is the evidence quoted in the PR (`spec.md` §6; `hld.md` §7).

**Assumptions**
- The test compares stderr exactly (`name must not be empty\n`) by redirecting stderr to a temporary file or by capturing it through the same sentinel technique. Evidence: t1 requires stderr to be checked and empty on success. If this is wrong and stderr is only grep-checked, an extra stderr line would not be caught. The exact comparison is cheap, so choose it.
- `qa/s2-hello.sh` reads the name as `"${1-}"`, so it works under `set -u` if the implementer enables it. Evidence: `hld.md` §6 asks that a missing argument not crash. If this is wrong, a missing argument causes an unbound-variable error instead of the specified message.

## Solution proposal

Add two standalone bash scripts that mirror the existing QA pair in `qa/20261110-s3/`. This approach needs no library, no CI change and no Python.

- **`qa/s2-hello.sh`:** take `name="${1-}"`. If `[[ -z $name ]]`, write `name must not be empty` to stderr with `printf '%s\n' … >&2` and `exit 1`. Otherwise run `printf 'Hello, %s!\n' "$name"` and exit 0. Only the exact empty string is rejected, so a name of only spaces is greeted. Extra arguments are never read. `printf` with a `%s` format prints `-n`, `%s` and backslashes literally.
- **`qa/s2-hello-test.sh`:** resolve `dir` from `$0` as `qa/20261110-s3/test_hello.sh:3` does, and set `target="$dir/s2-hello.sh"`. Use one small helper function that runs the target with a given argument, captures stdout with the sentinel technique (so the trailing newline counts), captures stderr exactly and records the exit code. Compare all three with the expected values, and print `FAIL: <case>: <what differed>` to stderr for each mismatch. Run case `Ada` (expect `Hello, Ada!\n`, empty stderr, exit 0) and case `''` (expect empty stdout, `name must not be empty\n`, exit 1). Print `PASS: <case>` for each passing case. Exit 0 only when both cases pass, otherwise exit 1. Clean up any temporary file with a `trap`.
- **Alternatives rejected:** a pytest test under `tests/` would run in CI, but it adds a file outside `qa/s2-*`, which the spec declined (`hld.md` §6). Wiring the bash test into `ci.yml` changes an existing file and is out of scope (`spec.md` §2). Using `echo` would swallow `-n` (`hld.md` §5).

## Ordered implementation steps

1. **Create `qa/s2-hello.sh`** as described in the Solution proposal. Give it a one-line header comment naming PLAY-190, the `#!/usr/bin/env bash` shebang and mode `100755` (`chmod +x`, and confirm with `git ls-files -s` after staging). This step advances AC1, AC2 and the t1 criteria for spaces-only names, literal printing, a missing argument and extra arguments. Test layer: `qa/s2-hello-test.sh` (step 2) covers AC1 and AC2. The remaining t1 behaviours (`'   '`, `-n`, `'%s'`, no argument, extra arguments) have no automated layer, so the implementer runs them by hand and records the results as PR evidence.
2. **Create `qa/s2-hello-test.sh`** as described in the Solution proposal, with the shebang, mode `100755` and target resolution relative to its own path. This step advances AC1, AC2 and the t1 criteria for the test script, including the exact trailing newline, the `FAIL:` line naming the case and running from any directory. Test layer: the script itself, a manual bash check outside CI. Error paths to cover: a non-zero or wrong exit code, wrong stdout bytes (including a missing or extra newline), and unexpected stderr.
3. **Prove the test bites (manual, not committed).** Temporarily alter the greeting or the exit code in a scratch copy, or through a temporary local edit, then revert it. Confirm that `qa/s2-hello-test.sh` exits non-zero with a `FAIL:` line. Run the test from the repo root and from another directory, for example `cd /tmp && <repo>/qa/s2-hello-test.sh`. This step advances the t1 criteria "Breaking the greeting … exit non-zero" and "finds the target relative to its own location". Leave no altered file behind.
4. **Collect PR evidence.** Capture the output and exit codes of `qa/s2-hello-test.sh`, `qa/s2-hello.sh Ada`, `qa/s2-hello.sh ''` and the manual t1 cases from step 1, for the PR description. This step advances the last t1 criterion. The platform writes the PR description.

There are no dependencies to acquire beyond bash. There are no generated deliverables, and no authz, tenancy or concurrency concerns, because the scripts are stateless, read only argv and write no files except an optional temp file removed by `trap`.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add qa/s2-hello.sh greeting script and its qa/s2-hello-test.sh test |
| 2 | t1 | Add qa/s2-hello.sh greeting script and its qa/s2-hello-test.sh test |
| 3 | t1 | Add qa/s2-hello.sh greeting script and its qa/s2-hello-test.sh test |
| 4 | t1 | Add qa/s2-hello.sh greeting script and its qa/s2-hello-test.sh test |

`t1` is the only work item, and every step maps to it.

## Verification and CI gate

- **Canonical gate:** `.github/workflows/ci.yml` job `test` runs `pip install -e ".[test]"` and then `pytest` (layer `package-api`, required, `runBy: canonical-gate`). Job `gate` passes when no `CI_FAIL` file exists. Provider CI at the exact head of the work branch is authoritative.
- **Local run:** the implement turn runs the gate once, through `run-tests-gate.sh --run` on the committed SHA, which executes `local-test-gate: pip install -q -e ".[test]" && pytest`. Do not also run `pytest` by hand.
- **Gate result required:** `pytest` passes unchanged, because the change adds no Python and nothing under `tests/`, and `gate` is green. `git diff --name-status main...HEAD` shows exactly `A qa/s2-hello.sh` and `A qa/s2-hello-test.sh`, both at mode `100755`.
- **Outside the gate:** `qa/s2-hello-test.sh` exits 0 with two `PASS:` lines. That output, plus the AC commands' output and exit codes, is the PR evidence that proves AC1 and AC2, because CI does not run the bash test (`spec.md` §6). The script can run in a pod, since it needs only bash.
- **Not needed:** no provider CI configuration change, no `.factory/testing.md` change and no `.factory/delivery-assets` entry (no binary).

## Risks and scope guards

**Risks**
- *CI does not prove the ACs.* CI stays green whether or not the scripts work. Mitigation: steps 3–4 produce the PR evidence, and the test script is designed to fail loudly.
- *Missing executable bit* breaks repo-gate rule 2 (`PLAY-G2`). Mitigation: confirm `100755` with `git ls-files -s qa/s2-*` before the commit.
- *Newline handling:* `$(...)` strips trailing newlines, which could hide a missing or extra `\n`. Mitigation: use the sentinel technique from `qa/20261110-s3/test_hello.sh:6-9`.

**Scope guards (the implement phase must NOT)**
- Change, rename or delete any existing file: `src/`, `tests/`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/` (including `testing.md` and the repo gate), `README.md`, `.gitignore`, or any existing `qa/` file (`qa/s3-*.sh`, `qa/20261109-s1/`, `qa/20261110-s3/`).
- Add a Python module, a pytest test or a CI step for the bash test.
- Add a `CHANGELOG` entry, because the changelog rule was dropped (`0fe2628`).
- Create a `CI_FAIL` file.
- Make any check green by skipping, deleting or weakening it. A failing `pytest` is reported as blocked, not worked around.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
