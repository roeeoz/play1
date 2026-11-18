# Plan — EGIT-1: e2e-pr343 marker script from another branch

## Context

EGIT-1 adds one new executable bash script, `qa/e2e-pr343/marker.sh`, to the `play1` repository. The script prints the marker line from `e2e-other-branch`, written into the script as a literal. Developers on `main` can then read the marker without switching branches. The acceptance criteria are:

1. The script exists, starts with `#!/bin/bash`, is executable, prints exactly line 1 of `e2e-other-branch-marker.txt` from `e2e-other-branch`, and exits 0.
2. The line is hard-coded, and the script never calls git.
3. No existing file is modified, and no test or documentation is added.

The change lands on the work branch `halo/feat/egit-1-20261118-141526`, which was cut from `main`, and merges into `main`. `spec.md` (requirement), `hld.md` (design) and `work-items.md` (breakdown) are next to this file in `stories/EGIT-1/`.

## Research findings

- **Source of truth (verified).** `git show origin/e2e-other-branch:e2e-other-branch-marker.txt | od -c` returns two LF-terminated lines with no CR:
  - Line 1 is `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22`. It is pure ASCII and has no `'`, `"`, `$`, `\`, `%` or backtick.
  - Line 2 is `second line: only on e2e-other-branch`. It must not be printed.
  - The file is not on `main`.
- **Change surface.** `qa/e2e-pr343/` does not exist yet, so both the directory and `marker.sh` are new. Today `qa/` holds `s3-a.sh`, `s3-hello.sh`, `20261109-s1/` and `20261110-s3/`.
- **Existing convention.** Every existing `qa/` script follows the same pattern, for example `qa/s3-hello.sh:1-3` and `qa/20261110-s3/hello.sh:1-3`:
  - It is tracked at mode `100755`.
  - Line 1 is `#!/bin/sh`.
  - Line 2 is a one-line `#` comment that describes the script.
  - Line 3 is `printf '<literal>\n'`.
- **Shebang precedent.** `tests/test_hello_sh.py:31-33` asserts `#!/bin/bash` for `hello-world/hello.sh`, so the repo already uses bash shebangs in places.
- **Git setting.** `core.fileMode` is `true` in this checkout, so a `chmod +x` before staging records mode `100755`.
- **Gate.** `.factory/testing.md` and `.github/workflows/ci.yml` define it:
  - The `test` job runs `pip install -e ".[test]"`, then `pytest` with `testpaths = ["tests"]` (`pyproject.toml`).
  - The `gate` job fails only when a `CI_FAIL` file exists at the repo root.
  - No linter or formatter is configured.
  - No test globs `qa/`. The only `iterdir` is `tests/test_hello_sh.py:42`, and it is scoped to `hello-world/`. The new file therefore cannot break or be picked up by `pytest`.
- **Contracts.** The only contract is the CLI contract in `hld.md` §5:
  - stdout is exactly the marker bytes plus `\n`.
  - stderr is empty.
  - The exit status is 0.
  - The file is tracked at mode `100755`.
  - There are no API, schema or cross-repo values.
- **Repo instructions.** There is no `AGENTS.md`, `CLAUDE.md` or `.factory/memory/` in the repo.
- **Unknowns.** None remain.

## Locked decisions and assumptions

**Locked decisions**
- Path `qa/e2e-pr343/marker.sh` (spec FR1, `work-items.md` t1).
- First line exactly `#!/bin/bash`, deliberately unlike the `#!/bin/sh` the other `qa/` scripts use (spec FR2, §6; hld §6).
- Mode `100755` recorded in git (spec FR3; hld §5).
- Output is exactly `e2e-marker-pr343: the heron counts seventeen lanterns at 14:22` plus one `\n`. Nothing goes to stderr, and the exit status is 0 (spec FR4, FR5).
- The line is a literal, with no git call and no file read (spec FR6, AC2).
- Print it with `printf` and a single-quoted literal (hld §6).
- No existing file is modified, and no test, README or CHANGELOG change is added (spec AC3, non-goals).
- The base and merge target is `main`. Nothing from `e2e-other-branch` is merged, cherry-picked or checked out into the tree (spec §6, hld §2).

**Assumptions**
- The marker on `origin/e2e-other-branch` is the one verified above.
  - Evidence: the `od -c` output above.
  - If wrong: if the branch changes before merge, the literal is stale. The spec accepts this as a non-goal.
- An optional `#` comment as line 2 is allowed and follows repo convention.
  - Evidence: hld §6 and `qa/s3-hello.sh:2`.
  - If wrong: drop the comment. The output does not change.

## Solution proposal

Add one standalone, three-line bash script in a new directory `qa/e2e-pr343/`:

1. `#!/bin/bash`
2. A one-line `#` comment saying it prints the `e2e-other-branch` marker line (EGIT-1)
3. `printf 'e2e-marker-pr343: the heron counts seventeen lanterns at 14:22\n'`

This mirrors the existing `qa/*.sh` pattern exactly, apart from the shebang that the spec mandates. The script has no inputs, no environment dependence and no I/O beyond stdout, so its output does not depend on the working directory or the checked-out branch. Set the executable bit with `chmod +x` before staging; `core.fileMode=true`, so git records `100755`. `git update-index --chmod=+x` is the fallback.

**Key decisions**
- Use `printf`, not `echo`, to match repo convention. Its behaviour is identical in every shell.
- Use a single-quoted literal. The text contains no characters that need escaping and no `%`, so it is safe as a `printf` format string.
- Write the file with LF line endings and no trailing whitespace.

**Rejected alternatives**
- Reading the marker with `git show` at run time is forbidden by FR6 and AC2.
- Copying `e2e-other-branch-marker.txt` onto `main` and `cat`-ing it would bring content over from the other branch and modify the tree beyond the single new file.
- `echo` gives the same bytes but breaks the `printf` convention.
- Adding a test is forbidden by AC3.

## Ordered implementation steps

1. **Create the script.** Create `qa/e2e-pr343/marker.sh` with the three lines from the Solution proposal: LF endings, a final newline after the `printf` line, no trailing spaces, ASCII only. Advances AC1 and AC2. Test layer: none. AC3 forbids adding tests, and no existing layer covers `qa/`, so step 3 covers this step by hand.
2. **Record the executable bit.** Run `chmod +x qa/e2e-pr343/marker.sh` before staging. After staging, confirm that `git ls-files -s qa/e2e-pr343/marker.sh` shows `100755`, and use `git update-index --chmod=+x` if it does not. Advances AC1. Covered by the manual check in step 3.
3. **Verify by hand against the source of truth.** Run each check and record its output for the PR body:
   - **Repo-root run.** From the repo root, run `qa/e2e-pr343/marker.sh > /tmp/out 2> /tmp/err; echo $?`. The command must print `0`, and `/tmp/err` must be empty.
   - **Byte comparison.** `cmp /tmp/out <(git show origin/e2e-other-branch:e2e-other-branch-marker.txt | head -n 1)` must report no difference. `od -c /tmp/out` must end in `2   2  \n` with no `\r`.
   - **Run from inside the directory.** `cd qa/e2e-pr343 && ./marker.sh` must produce identical bytes.
   - **Run from elsewhere.** Running the script from another directory, for example `/tmp`, must also produce identical bytes.
   - **Shebang.** `head -n 1 qa/e2e-pr343/marker.sh` must print exactly `#!/bin/bash`.
   - **No git.** `grep -n git qa/e2e-pr343/marker.sh` may match only the comment, if the comment names the branch, and never a command. Leave the word "git" out of the comment so the check stays clean.

   Advances AC1 and AC2. Layer: manual verification (no automated layer exists for `qa/`).
4. **Confirm the scope.** `git diff --stat main...HEAD -- . ':!stories/EGIT-1'` must list only `qa/e2e-pr343/marker.sh` as added. The platform owns the plan folder files. No file under `tests/` or `docs/`, no `README.md` change and no `CHANGELOG.md` change may appear. Advances AC3. Layer: manual check.
5. **Run the canonical gate.** Run `pip install -e ".[test]" && pytest` once, from the repo root, on the committed SHA, to show the existing suite is unaffected. Layer: `package-api` (pytest). It does not exercise the new script, and that is expected.

Implicit invariants:
- Authz, tenancy, concurrency and idempotency do not apply, because the script is stateless and takes no input.
- The only error path is none: the script cannot fail.
- No dependencies need to be installed for the script itself. The gate needs only the existing `pip install -e ".[test]"`.
- No generated deliverables, and no binary assets, so there are no `.factory/delivery-assets` obligations.

## Work-item mapping

| Step | Work item |
|---|---|
| 1. Create the script | t1 — Add executable qa/e2e-pr343/marker.sh that prints the e2e-other-branch marker line |
| 2. Record the executable bit | t1 |
| 3. Verify by hand | t1 |
| 4. Confirm the scope | t1 |
| 5. Run the canonical gate | t1 |

`work-items.md` has one work item, t1, and every step maps to it.

## Verification and CI gate

- **Canonical gate.** Per `.factory/testing.md`: `pip install -e ".[test]"`, then `pytest`, run once locally on the committed SHA. Provider CI runs the same steps (`test` job), and the `gate` job also passes, because no `CI_FAIL` file is added. The required layer `package-api` runs in a pod.
- **What done looks like:**
  - `pytest` passes with the same results as on `main`.
  - Both CI jobs are green at the PR head.
  - The manual evidence from steps 3–4 is in the PR body:
    - `cmp` reports no difference against line 1 of the source file.
    - Exit status 0 and empty stderr.
    - `git ls-files -s` shows `100755`.
    - The shebang line is `#!/bin/bash`.
    - The diff contains only the new file.
- **Coverage gap.** No automated layer covers `qa/` scripts, and AC3 forbids adding one, so the script's behaviour is proven only by the manual evidence.
- **CI and delivery assets.** No provider CI change is needed, and there are no `.factory/delivery-assets` obligations.

## Risks and scope guards

**Risks**
- Byte drift from a CRLF ending, a smart quote, a trailing space, or a missing or doubled newline. Mitigation: the `cmp` and `od -c` checks in step 3.
- The executable bit is lost, leaving the file at `100644`. Mitigation: the `git ls-files -s` check in step 2.
- The marker branch changes after authoring. This is accepted as a spec non-goal.

**Scope guards (the implement phase must NOT):**
- Modify any existing file, including the other `qa/` scripts, `README.md`, `CHANGELOG.md`, `pyproject.toml`, `.github/workflows/ci.yml` and anything under `tests/`. The plan folder files belong to the platform and are not edited here either.
- Add any test (pytest or a shell `test_*.sh`), documentation or CHANGELOG entry.
- Call git, read files, accept arguments or read environment variables in the script.
- Merge, rebase onto, cherry-pick, check out or copy anything from `e2e-other-branch`, including `e2e-other-branch-marker.txt`. That branch is read only, with `git show`, for verification.
- Use `#!/bin/sh` to match the neighbouring scripts. The spec mandates `#!/bin/bash`.
- Add a `CI_FAIL` file, or skip, disable or weaken any CI job or test.

## Clarification outcomes

None.
