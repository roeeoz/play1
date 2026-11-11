# Plan — QA20261110-12: the `hello aw` script and its CI test

## Context

Story QA20261110-12 (epic AW-20261111, a delivery sanity check) adds a POSIX shell script, `qa/20261111-aw/hello.sh`, that prints exactly `hello aw` and one newline. It also adds one pytest test that runs the script on every pull request and fails on any deviation in stdout, stderr or exit code. The acceptance criteria cover: exact output and success (AC1), the test showing up and passing in the PR's required checks (AC2), the test failing on wrong output (AC3) or on failure or stderr (AC4), no regression and no network dependency (AC5), and only the two new files (AC6). The change lands in `roeeoz/play1` on the work branch `halo/feat/qa20261110-12-20261111-090107`, which merges into `main`. `spec.md` (requirement), `hld.md` (design) and `work-items.md` (one work item, `t1`) sit next to this file in `stories/QA20261110-12/`.

## Research findings

- **What CI runs.** `.github/workflows/ci.yml:12-24` defines the `test` job: `pip install -e ".[test]"` and then `pytest` on Python 3.12, triggered by `pull_request` (`ci.yml:6`). The `gate` job (`ci.yml:26-36`) only checks whether `CI_FAIL` exists, so it doesn't matter here.
- **Where pytest looks.** `pyproject.toml:27-29` sets `testpaths = ["tests"]` and `addopts = "-q"`. A test is collected only under `tests/`. Anything under `qa/` (for example `qa/20261110-s3/test_hello.sh`, from PLAY-175) never runs in CI. That is the RK1 failure this story must not repeat.
- **The canonical gate.** `.factory/testing.md` declares one required layer, `package-api`, whose command is `pytest` (`runBy: canonical-gate`). No linter, formatter, type checker or coverage tool is configured. `.factory/delivery-assets` does not exist, and nothing here needs it.
- **Existing script layout.** `qa/20261109-s1/a.sh:1-3` and `qa/20261110-s3/hello.sh:1-3` are each three lines: `#!/bin/sh`, a `#` comment line, then `printf '…\n'`. `git ls-files -s qa` shows every one at mode `100755`.
- **Existing test pattern to copy.** `tests/test_qa_20261109_s1_a.py`:
  - `REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent` (`:6`).
  - A `run_script` helper that calls `subprocess.run([str(script)], capture_output=True, text=True, timeout=10, cwd=cwd)` (`:11-15`).
  - Exact assertions on exit code, stdout and stderr (`:19-23`).
  - A run from `tmp_path` (`:27-31`).
  - Shape checks for the shebang, executable bit and absence of `\r` (`:34-42`).
  - `tests/test_qa_s3_greeting.py:7-11` passes extra arguments, which is the same mechanism this test needs for "ignores arguments".
- **Shell in the environment.** `/bin/sh` is `dash` locally, and it is dash on `ubuntu-latest` too. The script must stay POSIX (`printf`, not `echo -e`).
- **Python versions.** The local pod has Python 3.11.2, CI uses 3.12, and `pyproject.toml:10` declares `>=3.10`. The planned test uses only `os`, `pathlib`, `stat` and `subprocess`, all available on 3.10.
- **Files that must not change.** Existing tests pin the earlier scripts (for example `tests/test_qa_20261109_s1_a.py:45-50` pins `qa/s3-a.sh`). `pyproject.toml:15-19` lists `[project.scripts]`, which must stay unchanged (AC6).
- **Repo-gate rule.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:17-20` (rule `PLAY-G4`) raises a blocker when a PR doesn't touch `CHANGELOG.md`. That conflicts with AC6. See the risks section.
- **To create:** `qa/20261111-aw/` (new directory), `qa/20261111-aw/hello.sh` (new) and `tests/test_qa_20261111_aw_hello.py` (new). No existing file is changed.
- **Unknowns after research:** none that block. Whether branch protection makes `test` a required check can't be seen from the checkout. The spec (§8) already accounts for this.

## Locked decisions and assumptions

**Locked decisions**
- The script path is `qa/20261111-aw/hello.sh`. Its output is exactly `hello aw\n` on stdout, with empty stderr and exit code 0 (spec FR1, AC1; PRD R1).
- There is one test, it runs in the PR's required checks, and it compares output exactly rather than by containment (spec FR2/FR3, AC2–AC4; hld §6).
- The test file is `tests/test_qa_20261111_aw_hello.py`. It is a pytest test collected by the existing `test` job (hld §2, §6; `pyproject.toml:28`).
- The test runs the script directly as an executable, not through `sh hello.sh` (hld §6).
- The script is POSIX `sh` with a `#!/bin/sh` shebang and LF line endings, committed at mode 100755 (hld §2; work item `t1`).
- The change is limited to these two new files. There is no `CHANGELOG.md`, `pyproject.toml`, CI, `src/`, documentation or `--help` change (spec FR5, AC6, Non-Goals; PRD §8).
- There is no new dependency, and the test has no network, clock or outside-repo file access (spec FR4, AC5; PRD R3).

**Assumptions**
- *Shape assertions are part of the "one test".* "One test" means one test file, which may hold several test functions, following the `tests/test_qa_20261109_s1_a.py` precedent. hld §6 allows these assertions. If a reviewer reads "one test" as a single function, merge the assertions into one function. The behaviour doesn't change.
- *How AC3 and AC4 are proved.* They are proved by the strictness of the assertions (`==` on stdout, `== ""` on stderr, `== 0` on the exit code), not by committing broken copies of the script. If a reviewer wants a demonstration, mutate the script locally, show the test go red, and revert the mutation. A mutant fixture must never be committed, because that would break AC6.
- *What the script does with arguments.* It ignores arguments simply by never reading `$@` (work item `t1`). If argument handling were expected, that would be a scope change, which the spec forbids.

## Solution proposal

- **Approach.** Mirror the two most recent QA sanity-check precedents, choosing the one that CI actually runs.
  - **Script.** `qa/20261111-aw/hello.sh` is three lines: `#!/bin/sh`, a comment naming epic AW-20261111 / story QA20261110-12, and `printf 'hello aw\n'`. It is committed executable.
  - **Test.** `tests/test_qa_20261111_aw_hello.py` follows `tests/test_qa_20261109_s1_a.py`. It resolves `REPO_ROOT` from `__file__` and runs the script directly through `subprocess.run` with `capture_output=True`, `text=True` and `timeout=10`. It asserts `returncode == 0`, `stdout == "hello aw\n"` and `stderr == ""`.
- **Key design decisions.**
  - **Location under `tests/`.** It is the only path `pytest` collects (`pyproject.toml:28`). This closes RK1 and needs no CI change.
  - **Direct execution.** A missing executable bit or a broken shebang fails the test, which an `sh` wrapper would hide.
  - **Exact equality.** `==` catches extra, missing or different characters, a missing trailing newline and an extra trailing newline (RK2, AC3).
  - **stderr and exit code asserted alongside stdout.** A script that prints the right text but exits non-zero or writes to stderr still fails (AC4).
  - **Shape checks.** The `#!/bin/sh\n` prefix, the user-executable bit and the absence of `\r` are checked, so problems that are platform-dependent fail loudly and with a clear message.
  - **Run from repo root and from `tmp_path`.** AC1 says "from the repo directory". A run from another cwd costs nothing and proves the script doesn't depend on its cwd. The test has no clock or network dependency.
  - **Argument test.** One run with a stray argument (for example `--help`) asserts the same exact output. That pins "ignores any arguments" from `t1` and RK3 without adding `--help` behaviour.
- **Alternatives rejected.**
  - A shell test under `qa/`: CI never collects it, which is exactly the PLAY-175 failure (RK1).
  - A new CI step: the spec rules out changing the build process.
  - A console-script entry in `pyproject.toml`: out of scope, and AC6 forbids it.
  - `echo`: its behaviour differs across shells. The existing scripts use `printf`.
  - A containment assertion: it would pass with `hello aw!` or a missing newline.

## Ordered implementation steps

1. **Create the script.** Create `qa/20261111-aw/hello.sh` (new) with exactly three LF-terminated lines: `#!/bin/sh`, a `#` comment naming AW-20261111 / QA20261110-12, and `printf 'hello aw\n'`.
   - Set the mode to executable (`chmod +x`) and confirm `git ls-files -s` reports `100755` once the build stages it.
   - Advances AC1. It is covered by the `package-api` (`pytest`) layer through step 2.
2. **Create the test file.** Create `tests/test_qa_20261111_aw_hello.py` (new) following `tests/test_qa_20261109_s1_a.py:1-42`:
   - Module constants: `REPO_ROOT` and `SCRIPT = REPO_ROOT / "qa" / "20261111-aw" / "hello.sh"`.
   - A `run_script(args=(), cwd=None)` helper: `subprocess.run([str(SCRIPT), *args], capture_output=True, text=True, timeout=10, cwd=cwd)`.
   - A normal run with `cwd=REPO_ROOT` asserting `returncode == 0`, `stdout == "hello aw\n"` and `stderr == ""` (AC1, AC3, AC4).
   - The same assertions with `cwd=tmp_path` (AC1, AC5: no outside-repo dependency).
   - The same assertions when called with one extra argument (ignores arguments, RK3).
   - Shape checks: bytes start with `b"#!/bin/sh\n"`, `os.stat(SCRIPT).st_mode & stat.S_IXUSR`, and `b"\r" not in` the bytes.
   - Use only the standard library plus pytest's `tmp_path`. No network, no clock, no new dependency.
   - Advances AC1, AC3, AC4 and AC5. The layer is `package-api` (`pytest`).
3. **Check that the test fails when it should.** In the working tree only, temporarily change the script:
   - to `printf 'hello aw!\n'`, then to `printf 'hello aw'`, and confirm the test fails each time (AC3);
   - to add `echo err >&2` or `exit 1` after a correct `printf`, and confirm it fails (AC4).
   - Revert every mutation before the change is finalised. Nothing from this step is committed. Layer: `package-api`, run ad hoc.
4. **Run the full suite.** Run `pip install -e ".[test]"` and then `pytest` from the repo root. Confirm that every pre-existing test still passes and that the new tests are collected (AC2, AC5). Layer: `package-api`.
5. **Check the scope.** Confirm that `git diff --stat main...HEAD -- . ':!stories/QA20261110-12'` lists only the two new files, and that `pyproject.toml`, `CHANGELOG.md`, `.github/` and `src/` are untouched (AC6). No test layer covers this; it is a diff inspection.
6. **PR traceability.** The PR description cites story QA20261110-12 and the AW-20261111 Epic PRD (spec §6). Opening the PR is the platform's job. The provider run of the `test` job must list `tests/test_qa_20261111_aw_hello.py` (AC2, RK1).

Invariants:
- Authorization, tenancy, concurrency and idempotency don't apply: this is a stateless script with no input.
- Validation and error paths are covered by the stderr and exit-code assertions.
- Dependencies come from `pip install -e ".[test]"`, with `pytest>=8` taken from `pyproject.toml:25`. Nothing new is needed.
- There are no generated deliverables.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1 | `t1` | Add qa/20261111-aw/hello.sh and a pytest test that checks its exact output |
| 2 | `t1` | (same) |
| 3 | `t1` | (same) |
| 4 | `t1` | (same) |
| 5 | `t1` | (same) |
| 6 | `t1` | (same) |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate.** It is defined in `.factory/testing.md` and `.github/workflows/ci.yml:19-24`, in this order:
  1. `pip install -e ".[test]"`
  2. `pytest` (repo root)
- **When it runs.** Run the gate once locally on the committed SHA. The provider's `test` job at the PR head is the authoritative result.
- **Required layer.** `package-api` (`pytest`) is the only required layer, and it runs unprivileged in a pod.
- **CI configuration.** No CI configuration change is needed. The `gate` job stays green because no `CI_FAIL` is added.
- **Other obligations.** No `.factory/delivery-assets` obligation applies (no binary).
- **What the gate must show to call the change done:**
  - `pytest` exits 0.
  - The run includes the tests in `tests/test_qa_20261111_aw_hello.py`, and they pass.
  - The count of passed tests equals the previous count plus the new ones, with no failures, skips or errors added.
  - The provider `test` job at the PR head is green and lists the new test file.

## Risks and scope guards

**Risks**
- **Repo-gate rule `PLAY-G4` conflicts with the spec** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:17-20`).
  - The rule requires a `CHANGELOG.md` line, but AC6 and FR5 forbid touching any existing file. The spec makes not touching it a deliberate departure, and hld §7 locks that choice.
  - If the repo-gate runs on this PR, expect a `PLAY-G4` blocker. Someone with authority must waive it for this story.
  - The implement phase must not edit `CHANGELOG.md` to satisfy the rule.
- **The executable bit is lost, or CRLF line endings creep in.** Either one breaks direct execution. Steps 1–2 check both. Confirm mode `100755` in the index.
- **The test isn't actually collected** (RK1). The file must be named `tests/test_*.py`, and step 4/6 confirms it appears in the results.
- **`test` may not be a required status check on `main`.** The checkout can't confirm this. A human merges only when everything is green (spec §8).

**Scope guards: the implement phase must NOT**
- modify `CHANGELOG.md`, `pyproject.toml` (including `[project.scripts]`), `.github/workflows/ci.yml`, `README.md`, `docs/`, `src/` or `.factory/`;
- modify the existing `qa/` scripts (`qa/s3-*.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/*`) or any existing `tests/test_*.py`;
- add `--help`, argument parsing, a console-script entry, a `conftest.py`, a new dependency, or a shell test under `qa/`;
- commit any mutated or broken copy of the script used in step 3;
- skip, `xfail`, delete or weaken any existing test, or loosen the new assertions to containment, to get a green result.

## Clarification outcomes

None.
