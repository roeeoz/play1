# SCRUM-9 implementation plan: hello-world bash script

## Context

SCRUM-9 asks for a bash script `hello-world/hello.sh` in its own folder at the root of `play1`. The script has the shebang `#!/bin/bash`, is executable, and prints exactly `hello world` with exit code 0. AC1 covers execution, AC2 folder isolation, AC3 direct execution through the shebang, and AC4 output exactness. The change lands in `play1` on the work branch `halo/feat/scrum-9-20261118-222425`, which merges into `main`. The approved requirement is `spec.md`, the design is `hld.md`, and the single work item `t1` is in `work-items.md`. All three sit beside this file in `stories/SCRUM-9/`. The deliverable already exists on `main`, so this plan confirms it and keeps it as it is (spec assumption A1).

## Research findings

**Change surface (facts, read on the work branch at `6afb292`):**
- `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. Each line ends with LF, and there is no CR.
- `git ls-files -s hello-world` lists exactly one entry, `100755 … hello-world/hello.sh`.
- `ls -A hello-world` lists only `hello.sh`, so the folder holds no hidden files.
- Running `./hello-world/hello.sh` from the repo root writes the 12 bytes `hello world\n` (checked with `od -c`) and exits 0.
- `git diff main --stat` shows the work branch differs from `main` only in `stories/SCRUM-9/*`.

**Existing tests (`tests/test_hello_sh.py`):**

| Test | Line | What it checks | AC |
|---|---|---|---|
| `test_prints_hello_world` | `tests/test_hello_sh.py:10` | Runs `[str(SCRIPT)]` directly, with no `bash` prefix, and asserts `returncode == 0` and `stdout == "hello world\n"` | AC1, AC3 |
| `test_no_stderr` | `tests/test_hello_sh.py:17` | stderr is empty | AC1, AC4 |
| `test_exact_output_no_extra_whitespace` | `tests/test_hello_sh.py:23` | Output is exactly `hello world\n` | AC4 |
| `test_shebang_line` | `tests/test_hello_sh.py:32` | Line 1 is `#!/bin/bash` | AC3 |
| `test_executable_permission` | `tests/test_hello_sh.py:36` | The `S_IXUSR` bit is set in the working-tree mode | AC3 |
| `test_folder_contains_only_hello_sh` | `tests/test_hello_sh.py:40` | `hello.sh` is the only non-dot entry in the folder | AC2 |

**Contracts:** the CLI contract and the file contract are in `hld.md` §5. No API, schema or cross-repo value is involved.

**Gate:**
- `.factory/testing.md` declares one required layer: `package-api`, which runs `pytest` with `runBy: canonical-gate`.
- `.github/workflows/ci.yml:12-24` (job `test`) runs `pip install -e ".[test]"` and then `pytest` on Python 3.12.
- `.github/workflows/ci.yml:26` (job `gate`) fails only when `CI_FAIL` exists at the repo root.
- `pyproject.toml:26-28` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- The repo has no linter, formatter or type checker.

**External data:** none.

**Exists or must be created:** everything exists. Nothing has to be created.

**Remaining unknowns:**
- Two small gaps exist in the tests, and neither causes a failure today. Git mode `100755` is checked only through the working-tree mode. The folder test skips dotfiles. Both facts are verified by the evidence commands in step 2.

## Locked decisions and assumptions

**Locked decisions:**
- Script path `hello-world/hello.sh`, shebang `#!/bin/bash`, executable bit, exact output `hello world` and exit 0. Source: `spec.md` FR1–FR4 and AC1–AC4.
- The folder holds only `hello.sh`. Additional scripts, CI/CD changes and documentation files are out of scope. Source: `spec.md` §2 Non-Goals.
- Keep the existing script and tests as they are. Reuse the `package-api` layer and the existing CI, and add no harness. Source: `hld.md` §6.
- The only work item is `t1`. It owns `hello-world/` and `tests/test_hello_sh.py`, and reads `ci.yml`, `pyproject.toml` and `.factory/testing.md` without changing them. Source: `work-items.md`.
- The base and merge target is `main`.

**Assumptions:**
- **A1 (from `spec.md`):** the story is done when AC1–AC4 hold. They hold today, so the expected product diff is empty.
  - Evidence: the research findings above.
  - If wrong: a reviewer who expects new code raises it on the pull request. The fallback in `hld.md` §7 is one `CHANGELOG.md` "Unreleased" line, outside `hello-world/`.
- **A2 (from `spec.md`):** the single trailing newline in `hello world\n` meets AC4.
  - Evidence: `echo` behaviour, and `tests/test_hello_sh.py:15` requires the newline.
  - If wrong: a byte-exact consumer of the 11 bytes `hello world` would mismatch. No such consumer exists.
- **A3 (this plan):** the existing tests cover AC1–AC4 well enough. The gaps in git mode and dotfiles are closed by evidence commands recorded in the pull request, not by changing the tests.
  - Evidence: the `work-items.md` criteria name `git ls-files` and `ls -A` as the checks, and say to change the tests only if a criterion fails.
  - If wrong: a reviewer asks for stronger tests. Tighten `test_folder_contains_only_hello_sh` to count dotfiles, and add an assertion on `git ls-files -s` inside `tests/test_hello_sh.py`. Both changes stay at the same layer.

## Solution proposal

The approach is verify and preserve, with no rebuild:
- The script and its pytest module already meet every functional requirement and acceptance criterion on the work branch.
- The implement phase confirms each criterion with direct commands and with the existing `package-api` pytest layer, and records the results as evidence in the pull request.
- It changes product files only if a check fails. In that case it makes the smallest correction to `hello-world/hello.sh` or `tests/test_hello_sh.py`, keeping mode `100755` and the folder isolation.

**Key decisions:**
1. **No product diff by default.** Rewriting the script would risk losing the executable bit or the LF ending, and it would add nothing.
2. **Evidence covers what the tests miss.** `git ls-files -s hello-world` and `ls -A hello-world` prove the git mode and the absence of hidden files. The pytest suite proves behaviour.
3. **The pull request carries only the plan documents.** The plan folder `stories/SCRUM-9/` is outside `hello-world/` and has no effect on AC2.

**Alternatives rejected:**
- *Re-create the script.* It would duplicate an existing, correct file.
- *Strengthen the tests now.* It would widen the diff beyond what any failing criterion requires. It stays available as the A3 fallback.
- *Add a CHANGELOG line now.* It is held as the `hld.md` fallback, used only if the pipeline rejects a pull request with no code change.

## Ordered implementation steps

1. **Confirm the baseline.** Check that `hello-world/hello.sh` and `tests/test_hello_sh.py` on the work branch are byte-identical to `main` (`git diff main -- hello-world tests/test_hello_sh.py` is empty).
   - AC: AC1–AC4.
   - Test layer: none, because this is a precondition check.
2. **Run the criterion evidence commands from the repo root and capture their output for the pull request:**
   - `git ls-files -s hello-world` must show one `100755` entry (AC2, AC3).
   - `ls -A hello-world` must show `hello.sh` only (AC2).
   - `head -1 hello-world/hello.sh` must show `#!/bin/bash` (AC3).
   - `./hello-world/hello.sh; echo "rc=$?"` must show `hello world` and then `rc=0` (AC1, AC3).
   - `./hello-world/hello.sh 2>/dev/null | od -c` must show exactly `h e l l o   w o r l d \n` (AC4).
   - `./hello-world/hello.sh 2>&1 >/dev/null | wc -c` must show `0`, so stderr is empty (AC1).
   - Test layer: these are direct checks that support `package-api`.
3. **Run the existing test layer.** Run `pip install -e ".[test]"` and then `pytest` (or `pytest tests/test_hello_sh.py` first, then the full suite).
   - The six tests in `tests/test_hello_sh.py` must pass, and so must the rest of the suite.
   - AC: AC1–AC4.
   - Test layer: `package-api`.
   - Dependencies come from `pip install` against `pyproject.toml`. Do not assume a warm cache.
4. **Fix only if something fails.** If step 2 or step 3 fails, correct the smallest thing:
   - Restore mode with `git update-index --chmod=+x hello-world/hello.sh`.
   - Restore content to the two lines above with LF endings.
   - Remove any stray file from `hello-world/`.
   - Then repeat steps 2 and 3.
   - AC: whichever criterion failed.
   - Test layer: `package-api`.
5. **Write the evidence into the pull request description.** Put each command from step 2 and the pytest summary from step 3 under the AC it proves.
   - If the pipeline refuses a pull request with no code change, apply the `hld.md` §7 fallback: add one `CHANGELOG.md` "Unreleased" line, for example `SCRUM-9: confirm hello-world/hello.sh against AC1–AC4`.
   - AC: AC1–AC4 traceability.
   - Test layer: none, because this is documentation.

Implicit invariants:
- Authorization, tenancy, concurrency and input validation do not apply. The script takes no input, has no state and makes no writes.
- The error path is limited to exit code 0 with empty stderr, which steps 2 and 3 check.
- There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1. Confirm baseline | `t1`: Lock in hello-world/hello.sh against AC1–AC4 through the existing pytest gate |
| 2. Evidence commands | `t1` |
| 3. Run pytest | `t1` |
| 4. Conditional fix | `t1` |
| 5. Pull request evidence and conditional CHANGELOG fallback | `t1` |

Every work item in `work-items.md` (only `t1`) has at least one step.

## Verification and CI gate

**Canonical gate:** from `.factory/testing.md` and `.github/workflows/ci.yml`, run `pip install -e ".[test]"` and then `pytest` from the repo root, on Python 3.12. Run it once locally on the committed SHA. The provider CI `test` job at the exact head is the authoritative run.

**Required layers:**
- `package-api` (pytest, production-path) is the only required layer, and it can run in a pod.
- The `gate` job is not a declared layer. It must stay green, so no `CI_FAIL` file may exist at the repo root.

**Configuration:**
- No CI configuration change is needed.
- `.factory/testing.md` needs no update because no layer changes.
- No `.factory/delivery-assets` entry applies.

**Done means:**
- All of `pytest` passes, including the six tests in `tests/test_hello_sh.py`.
- The CI `test` and `gate` jobs are green on the pull request head.
- The step 2 evidence shows: one `100755` entry, `hello.sh` as the only entry in `ls -A`, the shebang on line 1, `hello world\n` as the exact stdout, empty stderr and `rc=0`.

## Risks and scope guards

**Risks:**
- **Lost executable bit or CRLF ending if the script is touched.** Mitigation: do not edit it unless step 2 or step 3 fails. `test_executable_permission` and `test_prints_hello_world` guard both.
- **A hidden file in `hello-world/` would slip past the pytest folder test.** Mitigation: the `ls -A` evidence in step 2.
- **A pull request with no code change could be rejected by the pipeline.** Mitigation: the single `CHANGELOG.md` line fallback.

**Scope guards. The implement phase must NOT:**
- add any file to `hello-world/`, including a README, `.gitkeep`, a test or any other dotfile;
- re-create, reformat, re-mode or rename `hello-world/hello.sh`;
- add other scripts, documentation files or CI changes, or touch `.github/workflows/ci.yml`, `pyproject.toml` or `.factory/testing.md`;
- edit `stories/SCRUM-9/spec.md`, `hld.md` or `work-items.md`;
- touch unrelated code: `src/`, the other tests, or `qa/`;
- create `CI_FAIL`;
- skip, delete, weaken or mark `xfail` any test in `tests/test_hello_sh.py` or elsewhere. A failing check is fixed at its cause or reported as blocked.

## Clarification outcomes

None.
