# Implementation plan — PLAY-173: סקריפט שמדפיס "B" אחרי "A"

## Context

PLAY-173 is the second, dependent story of epic QA-20261109-S1 ("ברכות בטרמינל"). It adds `qa/20261109-s1/b.sh`, which runs the sibling `qa/20261109-s1/a.sh` (PLAY-172, already on `main`) and then prints `B`. A normal run prints exactly `A\nB\n` and exits 0, from any current folder. When `a.sh` is missing or fails, `b.sh` exits non-zero and never prints `B`. The story also adds new pytest tests and one `CHANGELOG.md` line. The change lands in `roeeoz/play1`, on work branch `halo/feat/play-173-20261109-131059`, which merges into `main`. The approved requirement (`spec.md`), the design (`hld.md`) and the single work item (`work-items.md`, ref `t1`) sit next to this file in `stories/PLAY-173/`.

## Research findings

- **Dependency is present.** `qa/20261109-s1/a.sh:1-3` is `#!/bin/sh`, a comment, then `printf 'A\n'`. It is committed as mode `100755` (`git ls-files -s qa`). It already names its caller in its comment (`a.sh:2`, "called by qa/20261109-s1/b.sh"). PLAY-172 was merged as commit `55574dc`.
- **Script conventions in `qa/`.** Every `qa/` script uses `#!/bin/sh`, a `#` comment on line 2, and `printf` for output (`qa/s3-a.sh:1-3`, `qa/s3-hello.sh:1-3`). `hello-world/hello.sh:1-2` is the only bash script, and it uses `echo`.
- **Test pattern to mirror.** `tests/test_qa_20261109_s1_a.py:1-50`:
  - computes `REPO_ROOT` from `__file__`
  - uses a `run_script(script, cwd=None)` helper around `subprocess.run([...], capture_output=True, text=True, timeout=10, cwd=cwd)`
  - groups tests in plain classes (`TestNormalRun`, `TestRunFromAnotherDirectory`, `TestScriptShape`, `TestExisting...Unchanged`)
  - checks shape: `#!/bin/sh\n` prefix, `stat.S_IXUSR`, no `\r`
- **Existing regression coverage.**
  - `tests/test_qa_20261109_s1_a.py` covers `a.sh` and `qa/s3-a.sh` printing `A`.
  - `tests/test_qa_s3_greeting.py:14-19` covers `qa/s3-hello.sh` printing `hello`.
  - `tests/test_hello_sh.py` covers `hello-world/hello.sh` printing `hello world`.
  - AC 7's "still prints" regression is therefore already enforced by existing tests. The new file only adds what is specific to `b.sh`.
- **Gate.** `.factory/testing.md` declares one required layer, `package-api`: `pytest`, run by `canonical-gate`. The `test` job in `.github/workflows/ci.yml` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12 / `ubuntu-latest`, with a 5-minute timeout. `pyproject.toml` sets `testpaths = ["tests"]` and `addopts = "-q"`, so a new `tests/test_*.py` is collected with no config change. The repo has no linter, formatter or type checker. The `gate` job only fails if a `CI_FAIL` file exists at the repo root.
- **Repo layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:12-20`):
  - Rule 1: tests live under `tests/`.
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file in the diff is over 200 KB.
  - Rule 4 (`PLAY-G4`): add a line under `## Unreleased` in `CHANGELOG.md`.
- **CHANGELOG shape.** `CHANGELOG.md:3-7` has `## Unreleased` followed by bullets in the form `- PLAY-NNN: add \`path\`, a ... script that prints \`X\`.`. The latest bullet is PLAY-172, on line 7.
- **To create:** `qa/20261109-s1/b.sh` and `tests/test_qa_20261109_s1_b.py`. **To edit:** `CHANGELOG.md`, by one appended line. Nothing else changes.
- **Unknowns.** None remain. The error wording and channel are settled by `hld.md` §5.

## Locked decisions and assumptions

**Locked decisions**
- **Paths.** `b.sh` lives at `qa/20261109-s1/b.sh`, next to `a.sh`. Source: PRD R2, spec FR1.
- **Exact output.** stdout is `A\nB\n`, stderr is empty, exit is 0. Source: spec FR1, `work-items.md` AC 1.
- **`A` comes from `a.sh`.** `b.sh` runs `a.sh` to get `A` and never prints `A` itself. Source: PRD R3, spec FR2.
- **`a.sh` is found from `b.sh`'s own location** (`dirname "$0"`), not from the current folder. Source: spec FR3, `hld.md` §6.
- **Missing or non-executable `a.sh`.** `b.sh` writes `b.sh: cannot run <path>/a.sh` to stderr, exits 1, and does not print `B`. Source: `hld.md` §5.
- **`a.sh` exits N ≠ 0.** `b.sh` exits N and does not print `B`. Source: `hld.md` §5, `work-items.md` AC 5.
- **Script setup.** The script uses `#!/bin/sh`, git mode `100755` and LF line endings. It runs `a.sh` directly, not through `sh`, and lets its output pass straight through without capturing it. Source: `hld.md` §5–6, repo-gate rule 2.
- **Test isolation.** Failure cases use per-test copies in pytest `tmp_path`, made with `shutil.copy`. Every subprocess call has `timeout=10`. Source: `hld.md` §6–7.
- **Files that may change.** Only `CHANGELOG.md` may change among existing files, by one line that cites PLAY-173. Source: spec §2, repo-gate rule 4.
- **Out of scope.** No `--help` and no new dependencies. Source: PRD §7–8.

**Assumptions**
- **`sh` on CI.** CI's `/bin/sh` is dash on `ubuntu-latest`, and `dirname`, `printf` and `[ -x ]` behave as POSIX defines them. Evidence: `a.sh` and the `qa/s3-*` tests already pass there. If this is wrong, the shape and run tests fail visibly in CI.
- **Test runner can execute files.** It can execute files in `tmp_path`, which is not mounted `noexec`. Evidence: GitHub-hosted runners and standard pods allow this. If this is wrong, the copy-based tests fail with `PermissionError`, and the gate reports it.
- **No new regression tests are needed.** The existing tests listed under Research findings are enough to show that `a.sh`, `qa/s3-a.sh`, `qa/s3-hello.sh` and `hello-world/hello.sh` still print what they print today. Evidence: those test files exist. If this is wrong, add one regression assertion for `qa/20261109-s1/a.sh` in the new file. Never edit the existing test files.

## Solution proposal

Add one small POSIX `sh` script and one pytest module, following the PLAY-172 pattern. Change nothing else beyond one CHANGELOG line.

**`qa/20261109-s1/b.sh`** (about 10 lines):
- Line 1 is `#!/bin/sh`. Line 2 is a `#` comment saying it runs the sibling `a.sh` and then prints `B` (epic QA-20261109-S1).
- Set a variable to the script's folder from `dirname "$0"`, and build the path `"$dir/a.sh"` from it.
- If that path is not executable (`[ -x ... ]`), run `printf 'b.sh: cannot run %s\n' "$path" >&2` and `exit 1`.
- Run `"$path"` directly, with no capture. If it fails, exit with its status (for example `"$path" || exit $?`).
- Run `printf 'B\n'`.
- Use no `set -e`, no `cd` and no environment variables.

**Key decisions**
- **Check first with `[ -x ]`** rather than relying on the shell's own "not found" error. This gives a fixed message and exit code, and it also covers an `a.sh` that exists but is not executable.
- **Pass on `a.sh`'s exit code** with `|| exit $?`. This keeps the code exact and keeps stdout ordering intact, because there is no capture.

**Alternatives rejected**
- `bash`: inconsistent with `qa/` (`hld.md` §6).
- `sh "$dir/a.sh"`: ignores `a.sh`'s own shebang.
- Capturing `$(…)` and re-printing: this could hide the exit code or change the output.
- Resolving `a.sh` from the current folder or `PATH`: this breaks FR3.
- Permanent `.sh` fixtures under `tests/fixtures/`: there is no precedent for them, and they add files to the repo.

**`tests/test_qa_20261109_s1_b.py`** mirrors `tests/test_qa_20261109_s1_a.py`:
- **Module constants:** `REPO_ROOT`, `SCRIPT` (`b.sh`) and `A_SCRIPT` (`a.sh`).
- **Helpers:**
  - the same `run_script(script, cwd=None)` helper
  - a small helper that copies `b.sh` into `tmp_path` with `shutil.copy`, which keeps its mode
  - a helper that writes an executable stub `a.sh` into `tmp_path`: a `#!/bin/sh` body, then `os.chmod` with `S_IXUSR`
- **Test classes:**
  - `TestNormalRun`
  - `TestAComesFromSiblingScript`
  - `TestRunFromAnotherDirectory`
  - `TestMissingA`
  - `TestFailingA`
  - `TestScriptShape`
  - `TestRealAUnchanged`: runs the real `a.sh` and asserts it prints `A`, as cheap regression evidence that the tests did not touch it

## Ordered implementation steps

1. **Create `qa/20261109-s1/b.sh`** as described in the Solution proposal.
   - Make it executable (`chmod 755`), so git records it as `100755`. Use LF line endings.
   - Advances AC 1–6.
   - Covered by the `package-api` (`pytest`) layer, through the tests in step 2.
2. **Create `tests/test_qa_20261109_s1_b.py`** with one test per criterion. All tests use `timeout=10`, no network, no clock and no environment variables:
   - **AC 1:** run `SCRIPT` with `cwd=REPO_ROOT`. Assert exit `0`, stdout `"A\nB\n"` and stderr `""`.
   - **AC 2:** copy `b.sh` into `tmp_path` and write a stub `a.sh` that prints `not-A` and exits 0. Run the copy and assert stdout `"not-A\nB\n"` and exit `0`.
   - **AC 3:** run the real `SCRIPT` with `cwd=tmp_path`. Assert exit `0`, stdout `"A\nB\n"` and stderr `""`.
   - **AC 4:** put a copy of `b.sh` alone in `tmp_path` and run it. Assert exit `1`, `"B"` not in stdout, and stderr non-empty and containing `a.sh`.
   - **AC 5:** copy `b.sh` next to a stub `a.sh` that runs `exit 3`, then run it. Assert exit `3` (non-zero, and passed on) and `"B"` not in stdout.
   - **AC 6:**
     - `SCRIPT.read_bytes().startswith(b"#!/bin/sh\n")`
     - `os.stat(SCRIPT).st_mode & stat.S_IXUSR`
     - `b"\r" not in` the file bytes
   - **AC 7:** in `TestRealAUnchanged`, assert that the real `A_SCRIPT` still prints `"A\n"` with exit 0. The other scripts stay covered by their existing tests.
   - Layer: `package-api` (`pytest`), picked up through `testpaths = ["tests"]` with no config change (AC 8).
3. **Append one line to `CHANGELOG.md`** under `## Unreleased`, after line 7, in the existing style: `- PLAY-173: add \`qa/20261109-s1/b.sh\`, a QA script that runs \`a.sh\` and then prints \`B\`.`
   - Advances AC 7 (the only existing file changed) and repo-gate rule 4.
   - No test layer covers this. The repo-gate review checks it.
4. **Confirm the diff's shape before the gate:**
   - `git ls-files -s qa/20261109-s1/b.sh` shows `100755`.
   - `git diff --stat main` lists only the two new files and `CHANGELOG.md` (+1 line), under 300 lines in total (AC 7, AC 9).
   - No test layer applies. This is a manual check of the diff.
5. **Run the gate** described under Verification and CI gate (AC 8).

Implicit invariants:
- **Authorization, tenancy, concurrency:** not applicable. This is a stateless local script.
- **Idempotency:** the script can be run any number of times with the same result.
- **Validation and error paths:** covered by AC 4 and AC 5.
- **Dependencies:** none new. `pip install -e ".[test]"` already provides `pytest` from a cold cache.
- **Generated deliverables:** none, and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1. Create `b.sh` | t1 — Add qa/20261109-s1/b.sh that runs a.sh then prints B, with tests and CHANGELOG entry |
| 2. Create `tests/test_qa_20261109_s1_b.py` | t1 |
| 3. CHANGELOG line | t1 |
| 4. Diff shape check | t1 |
| 5. Gate | t1 |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate** (from `.factory/testing.md` and `.github/workflows/ci.yml` `test` job), run from the repo root in this order:
  1. `pip install -e ".[test]"`
  2. `pytest`
- Run the gate once locally on the committed SHA. The Stop hook and the provider CI run it again. Use no second worktree.
- **Required layer:** `package-api` (`pytest`, `runBy: canonical-gate`). It runs unprivileged in a pod, and the provider run at the exact head is authoritative.
- **What the gate must show:**
  - every existing test still passes, including `tests/test_qa_20261109_s1_a.py`, `tests/test_qa_s3_greeting.py` and `tests/test_hello_sh.py`
  - every test in `tests/test_qa_20261109_s1_b.py` passes
  - the `test` job finishes well under 60 seconds
- The `gate` job stays green because no `CI_FAIL` file is added.
- No provider CI configuration change is needed. `ci.yml` and `pyproject.toml` stay untouched.

## Risks and scope guards

**Risks**
- **Faked dependency (R3).** If `b.sh` printed `A` itself, AC 1 would still pass. The AC 2 stub test catches this.
- **Ignored failure (R5).** If `b.sh` did not stop on `a.sh`'s failure, it would still print `B`. The AC 4 and AC 5 tests catch this, and they assert the exact passed-on code `3`.
- **Mode lost.** If `b.sh` were committed as `100644`, it would break repo-gate rule 2 and the AC 6 test. Step 4 verifies the mode with `git ls-files -s`.
- **Sourced or symlinked `b.sh` (RK2).** Running `b.sh` this way resolves `a.sh` differently. It is outside the acceptance criteria and is recorded in `hld.md` §7 only.

**Scope guards (the implement phase must NOT):**
- Edit `qa/20261109-s1/a.sh`, `qa/s3-a.sh`, `qa/s3-hello.sh`, `hello-world/hello.sh`, any existing test, `.github/workflows/ci.yml`, `pyproject.toml` or `README.md`.
- Create `qa/s3-b.sh`, add `--help`, add a console entry point or package docs, or add dependencies.
- Make `b.sh` refer to `qa/s3-*.sh`, use `cd`, or read environment variables.
- Write anything into the real `qa/20261109-s1/` folder from tests. All stubs and copies go in `tmp_path`.
- Delete, skip, `xfail` or weaken any test to make the gate green. A failing check is reported as blocked.
- Reword or reorder existing `CHANGELOG.md` lines.

## Clarification outcomes

None.
