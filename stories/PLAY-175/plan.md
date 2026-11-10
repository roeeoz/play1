## Context

PLAY-175 is the only story of epic QA-20261110-S3. It adds `qa/20261110-s3/hello.sh`, which prints exactly `hello s3\n` and exits 0. It also adds `qa/20261110-s3/test_hello.sh`, which runs the greeting script and exits 0 only when both the output and the exit code are exactly right. The acceptance criteria (spec §5, scenarios 1–9) cover four things: the happy path, three failure modes (wrong text, wrong exit code, missing or non-executable script), a strict change boundary (the two files plus one `CHANGELOG.md` line), and offline, repeatable behaviour. The change lands in `roeeoz/play1` on the work branch `halo/feat/play-175-20261110-054540`, which merges into `main`. `spec.md` (requirement), `hld.md` (design) and `work-items.md` (one work item, `t1`) sit beside this file in `stories/PLAY-175/`.

## Research findings

- **Existing `qa/` convention.** Every script starts with `#!/bin/sh`, then a one-line `#` comment, then a single `printf`. All use LF line endings and git mode `100755`:
  - `qa/s3-hello.sh:1-3`
  - `qa/s3-a.sh:1-3`
  - `qa/20261109-s1/a.sh:1-3`
- **`qa/20261110-s3/` does not exist yet.** Both files are new.
- **Neighbouring file to protect.** `qa/s3-hello.sh` prints `hello\n`. Its output, its `#!/bin/sh\n` prefix, its comment on line 2 and its lack of `\r` are pinned by `tests/test_qa_s3_greeting.py:4-28`. Any edit to it turns CI red (RK2).
- **Git config.** `core.fileMode` is `true` and the repo has no `.gitattributes`. The executable bit is tracked, and nothing enforces LF.
- **CHANGELOG contract.** `CHANGELOG.md:3` holds `## Unreleased`. The entries follow the format `- PLAY-<n>: add \`<path>\`, a ... script that prints \`<text>\`.`; the latest is `CHANGELOG.md:7` (PLAY-172).
- **Repo gate.** In `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, two rules apply here:
  - rule 2 (line 15): a new shell script must be executable and start with a shebang;
  - rule 4 (lines 17-20, `PLAY-G4`): the PR must add a line under `## Unreleased`.
  - Rule 3 (line 16, files of 200 KB or more) is trivially met.
- **CI.** `.github/workflows/ci.yml:12-24` defines job `test`, which runs `pip install -e ".[test]"` and then `pytest`. `.github/workflows/ci.yml:26-37` defines job `gate`, which fails only if `CI_FAIL` exists.
- **pytest scope.** `pyproject.toml:27` sets `testpaths = ["tests"]`, so pytest never sees `qa/`. The new files can't break CI, and CI can't prove they work (RK1).
- **Declared test layers.** `.factory/testing.md` declares one layer, `package-api` (`pytest`). It declares no shell-test layer and no linter.
- **External data and dependencies.** None. The scripts use only `/bin/sh`, `printf` and POSIX shell built-ins.
- **Unknowns.** None remain. The HLD settles the shebang choice (`#!/bin/sh`).

## Locked decisions and assumptions

**Locked decisions**
- The product files are exactly `qa/20261110-s3/hello.sh` and `qa/20261110-s3/test_hello.sh`. On top of them comes one added line under `## Unreleased` in `CHANGELOG.md` that mentions PLAY-175. `stories/PLAY-175/` doesn't count toward this limit. Sources: spec FR7, AC6, developer decisions P0-1(a) and P0-2.
- The `hello.sh` contract: stdout is exactly the 9 bytes `hello s3\n`, the exit code is 0, and it reads no input. Sources: spec FR1, hld §5.
- The test runs `hello.sh` directly through its path, never through `sh`. It finds the script relative to its own location, compares the output exactly including the single trailing newline, and writes no files. Sources: spec §7, FR3–FR6, hld §3 and §6.
- Both files start with a shebang, use LF line endings and have mode `100755`. Source: repo gate rule 2, hld §5.
- Both files use `#!/bin/sh`. Source: hld §6.
- stderr is not checked. Source: hld §6.
- The test is not wired into CI; the PR description reports a manual run instead. Sources: spec §2 out-of-scope, FR8, RK1.

**Assumptions**
- *A sentinel-suffix capture keeps trailing newlines portably in POSIX `sh`.* The sentinel goes inside the command substitution, and the exit code is captured inside it too.
  - Evidence: hld §6 says a POSIX prototype passed every case.
  - If wrong: an output with a missing or extra newline would pass. Step 3's manual checks catch this before the PR.
- *The CI runner and dev pod run as a user for whom a mode-`644` file fails to execute.*
  - Evidence: hld §7 notes that even root needs at least one execute bit to run a file.
  - If wrong: scenario 5's non-executable variant would pass silently. Step 3 checks this directly.

## Solution proposal

Add two small, self-contained POSIX shell scripts in a new folder `qa/20261110-s3/`, plus one CHANGELOG line. No existing code, test or CI configuration changes.

- **`hello.sh`.** Same three-line shape as the existing `qa/` scripts:
  - shebang `#!/bin/sh`;
  - a one-line `#` comment naming epic QA-20261110-S3;
  - `printf 'hello s3\n'`.

  Exit 0 comes from `printf`'s success; an explicit `exit 0` is optional. Using `printf` rather than `echo` matches the convention and avoids `echo` portability quirks.
- **`test_hello.sh`.** A short linear script:
  1. Resolve its own directory with `dirname -- "$0"` and `cd -P`, inside a command substitution, so the caller's working directory doesn't change.
  2. Point the target at `"$dir/hello.sh"`.
  3. Run the target directly. Inside a command substitution, append a sentinel character after the target's output and its exit status, for example `out=$("$target"; rc=$?; printf 'x%s' "$rc")`. Then split the exit code and the sentinel off with parameter expansion. This keeps trailing newlines in the output without temp files.
  4. Compare the recovered output to `hello s3` followed by a literal newline, held in a variable built with `printf` and the same sentinel trick, or with an embedded newline.
  5. Compare the exit code to `0`.
  6. On success, print a short `PASS` line and exit 0. Otherwise, print a `FAIL` reason to stderr and exit 1.
- **Missing or non-executable target.** Running it directly makes the shell return 127 or 126. That code is captured as `rc` and fails the comparison, so no separate existence check is needed. A short-circuiting `[ -x "$target" ]` pre-check is still allowed for a clearer message, as long as the test never falls back to `sh "$target"`.
- **CHANGELOG.** Append `- PLAY-175: add \`qa/20261110-s3/hello.sh\`, a QA script that prints \`hello s3\`, and its test \`qa/20261110-s3/test_hello.sh\`.` after `CHANGELOG.md:7`.

**Alternatives rejected**
- A pytest wrapper under `tests/` would be a third product file, which spec FR7 forbids.
- Diffing temp files would write outside the folder, against FR6 and AC9.
- Plain `$(...)` without a sentinel strips trailing newlines, so it would accept `hello s3` or `hello s3\n\n`.
- `sh hello.sh` would bypass the execute bit, against FR4.
- bash-only features such as `[[`, `$'..'` or `BASH_SOURCE` bring no benefit and break the `#!/bin/sh` convention.

## Ordered implementation steps

1. **Create `qa/20261110-s3/hello.sh`** (new).
   - Content as in the solution proposal: `#!/bin/sh`, then a comment line, then `printf 'hello s3\n'`. LF endings only.
   - Run `chmod +x` and make sure the index records `100755` (`git update-index --chmod=+x` if needed).
   - Advances AC1 and work-item ACs 1 and 2.
   - Test layer: none of the declared layers covers it. It is covered by step 2's shell test, run manually in step 3, which is a stated gap (RK1).
2. **Create `qa/20261110-s3/test_hello.sh`** (new).
   - Write the self-locating, direct-execution, sentinel-capture test from the solution proposal. Exit 0 only when the output is `hello s3\n` and `rc` is 0; otherwise exit non-zero.
   - Rules for this file: no network, no clock (`date`, `sleep`), no `mktemp` and no `>` redirect to any file.
   - LF endings and mode `100755`.
   - Advances AC2 and AC9, and work-item ACs 2, 3, 5 and 6.
   - Test layer: self-verifying, run manually in step 3.
3. **Run the manual verification and record the results for the PR description.** Do this on the committed tree and commit nothing from it.
   - **Happy path, from three working directories.** Run `qa/20261110-s3/hello.sh | od -c` and confirm the output is exactly `h e l l o   s 3 \n` with exit 0. Run `qa/20261110-s3/test_hello.sh` from the repo root, from `cd qa/20261110-s3 && ./test_hello.sh`, and from `cd /tmp && /path/to/qa/20261110-s3/test_hello.sh`. Expect exit 0 each time (AC1, AC2, FR5).
   - **Repeatability.** Run the test twice in a row, then confirm `git status --porcelain` is empty (AC9, FR6).
   - **Failure modes.** Temporarily edit `hello.sh`, run the test and expect a non-zero exit for each of these variants:
     - prints `hello` (AC3);
     - `printf 'hello s3'`, with no newline;
     - `printf 'hello s3\n\n'`;
     - prints `hello s3\n` then `exit 1` (AC4);
     - file removed (AC5);
     - `chmod -x` (AC5).

     After each variant, restore the file with `git checkout -- qa/20261110-s3/hello.sh` and `chmod +x` as needed.
   - **Final state.** `git status` is clean and `git ls-files -s qa/20261110-s3` shows `100755` for both files.
   - Test layer: manual. Nothing here can join a declared layer without breaking FR7.
4. **Add the CHANGELOG line to `CHANGELOG.md`.** Append one line after `CHANGELOG.md:7`, in the PLAY-172 style, that mentions PLAY-175 and `qa/20261110-s3/hello.sh`.
   - Advances AC6 and work-item AC 7, and satisfies `PLAY-G4`.
   - Test layer: the repo gate (rule 4).
5. **Check the change boundary and secrets.**
   - Run `git diff --stat main...HEAD -- . ':!stories/PLAY-175'`. Expect exactly the two new files and `CHANGELOG.md` (1 insertion).
   - Run `git diff main...HEAD -- qa/s3-hello.sh qa/s3-a.sh qa/20261109-s1/a.sh`. Expect it to be empty.
   - Confirm there are no secrets or personal data, and that `grep -c $'\r'` finds no CR in the new files.
   - Advances AC6, RK2 and work-item ACs 7 and 10.
   - Test layer: review / repo gate.
6. **Run the canonical gate:** `pip install -e ".[test]"`, then `pytest`, from the repo root. It must pass unchanged. That proves `tests/test_qa_s3_greeting.py` still holds and that nothing else regressed.
   - Advances AC7 and work-item AC 8.
   - Test layer: `package-api` (pytest).
7. **The PR description** (written by the platform or build stage, not committed) must:
   - cite PLAY-175 and the epic PRD URL;
   - include the step 3 transcript: a successful `test_hello.sh` run and the failing exit codes of the temporary variants.

   Advances AC8 and work-item AC 9.

**Invariants:**
- Authorization and tenancy: not applicable, since this is a local script with no data.
- Concurrency and idempotency: the test is read-only and stateless, so repeated or parallel runs are safe (AC9).
- Validation and error paths: covered in step 3.

**Dependencies:** none to install for the scripts. The gate install in step 6 uses `pip install -e ".[test]"` from PyPI and doesn't assume a warm cache.

**Generated deliverables:** none.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–7 | `t1` — Add qa/20261110-s3/hello.sh (prints "hello s3") and its shell test test_hello.sh |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate** (per `.factory/testing.md` and `.github/workflows/ci.yml:21-24`): `pip install -e ".[test]"`, then `pytest`, from the repo root on Python 3.12. Run it once locally on the committed SHA. Provider CI reruns it as job `test`, and job `gate` must stay green (no `CI_FAIL` file).
- **Required layer:** `package-api` (`pytest`). It runs in a pod. No new tests are expected in it, and the existing suite must pass unchanged.
- **Shell test:** `qa/20261110-s3/test_hello.sh` belongs to no declared layer and is not run by CI (RK1, deliberately out of scope). Its evidence is the step 3 manual run, reported in the PR description. It runs in a pod with no extra environment.
- **Repo gate (`mr-gate`):**
  - rule 2: both files have a shebang and mode `100755`;
  - rule 3: every file is tiny;
  - rule 4 (`PLAY-G4`): the CHANGELOG line is present.
- **Obligations under `.factory/testing.md`:** none beyond the gate. No `.factory/delivery-assets` entry, because there are no binaries.
- **Done means all of the following:**
  - `pytest` is green;
  - CI jobs `test` and `gate` are green at the PR head;
  - the repo gate passes;
  - `git ls-files -s qa/20261110-s3` shows two `100755` entries;
  - the diff outside `stories/PLAY-175/` is the two files plus one CHANGELOG line;
  - the PR reports a passing `test_hello.sh` run and failing results for the scenario 3–5 variants.

## Risks and scope guards

**Risks**
- **Executable bit lost (mode `100644`).** This breaks repo-gate rule 2 and direct execution. Mitigation: `chmod +x` / `git update-index --chmod=+x`, then check the mode in step 5.
- **Trailing newlines stripped by a naive `$(...)`.** The test would wrongly pass. Mitigation: use the sentinel capture, and step 3 includes the no-newline and double-newline variants.
- **CRLF line endings.** They break the `#!/bin/sh` line. Mitigation: author with LF and check for CR in step 5.
- **RK1: CI green doesn't prove the shell test ran.** Mitigation: report the manual run in the PR (AC8).
- **RK2: accidental edit to `qa/s3-hello.sh`.** CI would go red through `tests/test_qa_s3_greeting.py`. Mitigation: step 5 diff check.

**The implement phase must NOT:**
- modify `qa/s3-hello.sh`, `qa/s3-a.sh`, `qa/20261109-s1/a.sh` or any existing CHANGELOG line;
- modify `src/`, `tests/`, `pyproject.toml`, `.github/` or `.factory/`;
- add a pytest wrapper or wire `test_hello.sh` into CI;
- add `.gitattributes`, `--help` handling, extra files or any dependency;
- commit any broken variant of `hello.sh` used in step 3;
- edit `spec.md`, `hld.md` or `work-items.md`;
- check stderr or make message wording part of the contract;
- make `test_hello.sh` fall back to `sh hello.sh`, write temp files, or read the clock or the network.

A failing CI job or gate rule may be reported as blocked, but must never be made green by deleting, skipping or weakening a test or check.

## Clarification outcomes

None.
