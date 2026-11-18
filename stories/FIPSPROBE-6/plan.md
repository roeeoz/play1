# Plan: FIPSPROBE-6, Hello-world bash script in a dedicated folder (verification)

## Context

FIPSPROBE-6 delivers "Hello-world bash script in a dedicated folder" as a verification change. `hello-world/hello.sh` is already on `main`, added by commit `65938b5`. This story adds one pytest module linked to FIPSPROBE-6. The module proves two things:

- the script prints exactly `hello world` as one line and exits 0 when run directly (AC1, AC3);
- the script starts with `#!/bin/bash` and git records it as executable (AC2, RK1).

The story also adds exactly one line under `## Unreleased` in `CHANGELOG.md`, so the PR passes the play1 layout gate rule `PLAY-G4`. The developer chose this (option b), and AC5 is amended to allow that one line. Otherwise the change touches nothing (AC4, amended AC5). It lands in `roeeoz/play1` on `halo/feat/fipsprobe-6-20261118-131756`, which merges into `main`. Three documents sit beside this file in `stories/FIPSPROBE-6/`: `spec.md` (the requirement), `hld.md` (the design) and `work-items.md` (one work item, `t1`).

## Research findings

- **Script under test.** `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`, with LF line endings. `git ls-files -s hello-world/` lists one entry, `100755 2a43bb269b6cbc65955e1906da7c4f79a1804bbf 0	hello-world/hello.sh`.
- **Checkout file modes cannot be trusted (RK1, confirmed).** In this checkout, `git config core.fileMode` is `false` and every file shows as `-rwxrwxrwx`. A check based on `st_mode` therefore proves nothing; only the git index is reliable.
- **Existing tests of the script.** `tests/test_hello_sh.py` runs the script without a timeout. It checks:
  - stdout, stderr and the shebang;
  - `st_mode & S_IXUSR`, which is the weak check;
  - that the folder holds only `hello.sh` (`test_folder_contains_only_hello_sh`), which FIPSPROBE-7 owns changing.

  Nothing refers to FIPSPROBE-6, and no existing test calls `git`.
- **Pattern to follow.** `tests/test_qa_s3_greeting.py` sets `SCRIPT = pathlib.Path(__file__).resolve().parent.parent / ...`. It has a helper that runs `subprocess.run([str(SCRIPT)] + args, capture_output=True, text=True, timeout=10)`, groups tests into classes by concern, and checks bytes with `read_bytes()`.
- **Test collection.** `pyproject.toml` sets `testpaths = ["tests"]` and `addopts = "-q"`. There is no `tests/__init__.py` or `conftest.py`, so module basenames must be unique. `test_fipsprobe_6_hello_sh.py` is unique.
- **Canonical gate.** `.factory/testing.md` names `test-gate: pytest`, which means `pip install -e ".[test]"` and then `pytest` on Python 3.12. It runs as the `test` job of `.github/workflows/ci.yml`, using `actions/checkout@v4` on `ubuntu-latest`, so `.git` and `git` are present. The `gate` job fails only if `CI_FAIL` exists. No linter or formatter is configured. There is one declared layer, `package-api` (production-path, `runBy: canonical-gate`).
- **Factory review gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-23` defines the play1 layout gate (slot `mr-gate`):
  - Rule 1 (tests under `tests/`): met.
  - Rule 2 (a new shell script is executable with a shebang): not applicable, because no script is added.
  - Rule 3 (no file over 200 KB): met.
  - Rule 4 (`PLAY-G4`, blocker): the PR must add a line describing the change under `## Unreleased` in `CHANGELOG.md`.
- **CHANGELOG shape.** `CHANGELOG.md:3` is `## Unreleased`. `CHANGELOG.md:5-8` hold four bullets of the form `` - <KEY>: add `<path>`, <what it does>. `` (PLAY-114 to PLAY-175). The file is 8 lines and ends with a single newline. No other heading follows `## Unreleased`.
- **External data:** none. There are no cross-repository contracts.
- **What exists and what is new.**
  - Exists: the script, the folder, the suite and `CHANGELOG.md`.
  - New: `tests/test_fipsprobe_6_hello_sh.py`, plus one appended `CHANGELOG.md` line.
- **Unknowns remaining:** none. The `PLAY-G4` versus AC5 conflict is settled (see Clarification outcomes).

## Locked decisions and assumptions

**Locked decisions**

- `hello-world/hello.sh` stays byte-for-byte and mode-for-mode unchanged, at the repository root. Source: spec FR1 and AC5; `t1` AC9.
- The deliverable is one new test module, `tests/test_fipsprobe_6_hello_sh.py`. Its file name and module docstring carry `FIPSPROBE-6`, and it uses no custom pytest marker. Source: hld §2, §5, §6; `t1` AC6.
- The test reads the executable bit from the git index with `git ls-files -s` and expects mode `100755`. Source: spec §7; hld §3, §6; `t1` AC4.
- If `git` or `.git` is missing, the mode check fails with a clear message and never skips. Source: hld §6; `t1` AC5.
- Every subprocess call has a timeout. Source: `t1` AC6.
- The test makes no folder-contents assertion, and `tests/test_hello_sh.py` is not edited. Source: hld §2, §6; spec Non-Goals.
- `CHANGELOG.md` gains exactly one line under `## Unreleased`. The line names `FIPSPROBE-6` and the hello-world test, and no existing line changes. Source: developer plan feedback (option b); hld §2, §5, §6; `t1` AC8.
- AC5 is amended to: no documentation or CI change, and outside `stories/FIPSPROBE-6/` the diff touches only the new test file and that single CHANGELOG line. Source: developer plan feedback; `t1` AC9. `spec.md` §5 AC5 and §8 still read "no CHANGELOG". That text predates the developer's decision and is superseded for this PR. This stage does not edit it.

**Assumptions**

- The repository root is `Path(__file__).resolve().parent.parent`, and it is passed to `git` and the script as `cwd`.
  - Evidence: the same pattern appears in `tests/test_qa_s3_greeting.py`.
  - If wrong (pytest run from another directory), the explicit `cwd` keeps the call independent of the current directory.
- `/bin/bash` exists on the runner and in the pod.
  - Evidence: `ubuntu-latest` uses a merged `/usr`.
  - If wrong, the execution test fails, which correctly signals that R5 does not hold.
- The new CHANGELOG bullet goes after `CHANGELOG.md:8`, the last existing bullet, which keeps chronological order.
  - Evidence: the four prior entries were each appended at the end.
  - If wrong, only the position within `## Unreleased` changes. `PLAY-G4` still passes.

## Solution proposal

Add one self-contained pytest module, `tests/test_fipsprobe_6_hello_sh.py`, which the existing suite collects. Append one bullet to `CHANGELOG.md` under `## Unreleased`. Nothing else changes.

- **Execution checks (AC1, AC3).** A module-level helper runs `[str(SCRIPT)]` directly, with no `bash` prefix. It uses `capture_output=True`, `text=True`, `timeout=10` and `cwd=REPO_ROOT`. The test asserts:
  - `returncode == 0`;
  - `stdout == "hello world\n"`;
  - `stdout.splitlines() == ["hello world"]`, so there is exactly one line, with no surrounding whitespace;
  - `stderr == ""`.
- **Shebang check (AC2).** Assert `SCRIPT.read_bytes().split(b"\n", 1)[0] == b"#!/bin/bash"`. The comparison is on exact bytes, so a CR or a trailing space fails it.
- **Repository-mode check (AC2, RK1).** Run `git ls-files -s -- hello-world/hello.sh` with `cwd=REPO_ROOT` and `timeout=10`, and parse its single line as `<mode> <sha> <stage>\t<path>`.
  - Assert that the path is exactly `hello-world/hello.sh`. This also proves the root location (FR1).
  - Assert that the mode is `100755`.
  - Call `pytest.fail` with an explanatory message in any of these cases:
    - `shutil.which("git")` is `None`;
    - `REPO_ROOT / ".git"` is missing;
    - the command exits non-zero;
    - the output is empty, meaning the file is untracked.
- **Traceability (AC4).** The module docstring names FIPSPROBE-6 and maps each test to its acceptance criterion.
- **Gate line (`PLAY-G4`, amended AC5).** Append one bullet after `CHANGELOG.md:8`, in the house style, for example: `` - FIPSPROBE-6: add `tests/test_fipsprobe_6_hello_sh.py`, a test proving `hello-world/hello.sh` prints `hello world`, starts with `#!/bin/bash` and is stored executable in git. `` Keep the trailing newline so that the diff is exactly one added line and zero removed lines.

**Alternatives rejected**

- **Keep no CHANGELOG line and ask for a `PLAY-G4` waiver.** The developer rejected this in favour of option (b).
- **Edit `tests/test_hello_sh.py`.** That file is outside this story's ownership, and FIPSPROBE-7 must edit it.
- **Use `git ls-tree HEAD`.** It misses staged state during development.
- **Check `st_mode`.** It is unreliable under `core.fileMode=false`.
- **Call `pytest.skip` when git is missing.** It would hide RK1.
- **Add a custom marker.** It needs a `pyproject.toml` change.

## Ordered implementation steps

1. **Create `tests/test_fipsprobe_6_hello_sh.py` with its scaffolding.** Advances AC4 and `t1` AC6. Layer: `package-api` (pytest).
   - Add a module docstring that contains `FIPSPROBE-6` and the AC mapping.
   - Define `REPO_ROOT`, `SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"` and `RELPATH = "hello-world/hello.sh"`.
   - Add a `run_script()` helper with `timeout=10` and `cwd=REPO_ROOT`.
   - Use only standard-library imports plus `pytest`.
2. **Add the execution tests (class `TestHelloShExecution`).** Advances AC1, AC3 and `t1` AC1–AC2. Layer: `package-api`.
   - Assert exit code 0.
   - Assert that stdout is exactly `hello world\n`, as one line with no surrounding whitespace.
   - Assert that stderr is empty.
3. **Add the shebang test (class `TestHelloShRepositoryShape`).** Assert that the first line's bytes are exactly `#!/bin/bash`. Advances AC2 and `t1` AC3. Layer: `package-api`.
4. **Add the git-index mode test (same class).** Advances AC2, RK1 and `t1` AC4–AC5. Layer: `package-api`.
   - Run `git ls-files -s -- hello-world/hello.sh` with `timeout=10`, `cwd=REPO_ROOT` and `capture_output=True, text=True`.
   - Fail with an explanatory message if git or `.git` is missing, the command exits non-zero, or the output is empty.
   - Assert exactly one entry, with path equal to `RELPATH` and mode `100755`.
   - Invariants: the query is read-only and idempotent. Validation and error paths are the explicit failures above.
5. **Append the CHANGELOG line.** Advances AC5 (amended), `PLAY-G4` and `t1` AC8. Layer: none in pytest. The `mr-gate` layout gate and the diff inspection in step 6 prove it.
   - Add exactly one bullet after `CHANGELOG.md:8`, under `## Unreleased`, naming `FIPSPROBE-6` and the new test. Use the house format `` - <KEY>: add `<path>`, <description>. ``
   - Do not touch any other line, the heading or the final newline.
6. **Verify scope, then run the gate.** Advances AC4, amended AC5 and `t1` AC7–AC9. Layer: `package-api` (gate run) plus diff inspection.
   - `git diff --stat main...HEAD -- . ':!stories/FIPSPROBE-6'` lists only `tests/test_fipsprobe_6_hello_sh.py` and `CHANGELOG.md`.
   - `git diff main...HEAD -- CHANGELOG.md` shows exactly `1 insertion(+)`, `0 deletions(-)`, and the added line falls inside `## Unreleased`.
   - `git ls-files -s hello-world/hello.sh` is unchanged: `100755 2a43bb26…`.
   - Then run the gate as described under Verification and CI gate.
   - Dependencies: `pip install -e ".[test]"` fetches the test extras from the index. Assume no warm cache.
   - There are no generated deliverables and no `.factory/delivery-assets` binaries.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–6 | `t1` — FIPSPROBE-6: add story-linked test proving hello-world/hello.sh output, shebang and git-recorded executable mode, plus CHANGELOG entry |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate, in order.** Run `pip install -e ".[test]"` and then `pytest` from the repository root, once, on the committed SHA. The Stop hook and the GitHub Actions `test` job re-run it at the head.
- **Required layer.** `package-api` (`pytest`, `runBy: canonical-gate`) can run in a pod. The provider CI run at the exact head is authoritative.
- **What the gate must show.**
  - Every existing test still passes.
  - The new tests in `tests/test_fipsprobe_6_hello_sh.py` are collected and pass: execution, output exactness, shebang and git mode.
  - The `gate` job is green, because no `CI_FAIL` exists.
- **play1 layout gate (`mr-gate`).** All four rules pass, with no waiver. `PLAY-G4` is met by the single added `## Unreleased` line.
- **Not needed.** No provider CI configuration change. No `.factory/testing.md` change, because the test sits in the existing layer. `.factory/delivery-assets` does not apply.

## Risks and scope guards

**Risks**

- **Misplaced or duplicated CHANGELOG line.**
  - If the line lands outside `## Unreleased`, `PLAY-G4` fails.
  - If the edit adds more than one line or rewrites an existing one, amended AC5 fails.
  - Mitigation: the diff check in step 6 (exactly 1 insertion and 0 deletions).
- **Wording drift between the spec and the PR.** `spec.md` AC5 still says "no CHANGELOG". A reviewer reading only the spec may flag the line.
  - Mitigation: the PR description cites the developer's option (b), amended AC5 and `t1` AC8–AC9.
- **First test that shells out to `git`.** It needs `git` on PATH and `.git` present. Both hold in CI and in any clone. If either is missing, the test fails loudly by design.
- **Overlap with `tests/test_hello_sh.py`.** The output assertions are duplicated. This is accepted (hld §6), and the runtime cost is negligible.

**Scope guards: the implement phase must NOT**

- modify, move, change the mode of or reformat anything in `hello-world/`;
- edit `tests/test_hello_sh.py`, including its weak `st_mode` check and `test_folder_contains_only_hello_sh`;
- touch `.github/`, `pyproject.toml`, `src/`, `README.md`, `docs/`, `.factory/` or `qa/`;
- add more than one line to `CHANGELOG.md`, or edit, reorder or reformat any existing line, the heading or the final newline;
- add a pytest marker, a `conftest.py` or a `tests/__init__.py`;
- add a folder-contents assertion, which would couple this story to FIPSPROBE-7;
- edit `spec.md`, `hld.md` or `work-items.md`;
- make a failing check green by skipping, deleting, `xfail`-ing or weakening it. In particular, the git-mode check never skips.

## Clarification outcomes

- **`PLAY-G4` versus AC5.** The earlier plan asked whether to (a) keep the no-CHANGELOG decision and get the `PLAY-G4` blocker waived, or (b) add one line under `## Unreleased` in `CHANGELOG.md`.
  - The developer answered (b): add exactly one line under `## Unreleased` for this test, and amend AC5 to allow it, so that the PR passes `PLAY-G4` without a waiver.
  - Folded into: Locked decisions (the CHANGELOG line and amended AC5), Solution proposal (gate line), step 5 and step 6, Verification (all `mr-gate` rules pass) and the scope guards (one line only).
- No further questions are open.
