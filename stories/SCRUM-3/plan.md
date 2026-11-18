# SCRUM-3 implementation plan — hello-world bash script

## Context

SCRUM-3 asks for `hello-world/hello.sh`: a `#!/bin/bash` script with the executable bit, alone in its folder, that prints exactly `hello world` and exits 0 (AC1–AC4). The script already exists on `main` and meets the story (spec assumption A1). The deliverable is therefore a test-only change to `tests/test_hello_sh.py` in `play1`. It makes the suite check each criterion as the spec words it, and the CI `pytest` run at the pull request's head is the evidence. The change lands on the work branch `halo/feat/scrum-3-20261118-212710`, cut from `main`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-3/`. There is one work item, `t1`.

## Research findings

- **Script (read-only):** `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. Git stores it as mode `100755` (`git ls-files -s hello-world`). The folder holds only `hello.sh`, with no hidden entries on the checkout.
- **Existing tests:** `tests/test_hello_sh.py` has 6 tests.
  - `REPO_ROOT` and `SCRIPT` are defined at `tests/test_hello_sh.py:5-6`. `SCRIPT` is an absolute path.
  - The 3 execution tests (`tests/test_hello_sh.py:10-28`) run `[str(SCRIPT)]` by absolute path with no `cwd`. Nothing exercises the spec's literal `./hello-world/hello.sh` from the repo root (AC1, AC3 gap).
  - `test_exact_output_no_extra_whitespace` (`tests/test_hello_sh.py:23-28`) carries a redundant `.strip()` assertion next to the exact one. HLD §6 forbids strip-based comparisons.
  - `test_shebang_line` (`tests/test_hello_sh.py:32-34`) and `test_executable_permission` (`tests/test_hello_sh.py:36-38`) already cover AC3's structure.
  - `test_folder_contains_only_hello_sh` (`tests/test_hello_sh.py:40-43`) filters out names starting with `.`, so a hidden file would pass. That is the AC2 gap.
- **Other references:** no other test references `hello-world/` (`tests/test_textutils.py:6` only matches a slug string). `tests/test_qa_s3_greeting.py` targets `qa/s3-hello.sh` and is unrelated.
- **Gate:** `.factory/testing.md` declares one layer, `package-api` (`pytest`, `runBy: canonical-gate`). `.github/workflows/ci.yml` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12 (job `test`). The job `gate` fails only if `CI_FAIL` exists at the root. `pyproject.toml` sets `testpaths = ["tests"]` and `addopts = "-q"`. No linter, formatter or type checker is configured.
- **Dependencies:** stdlib only (`subprocess`, `stat`, `pathlib`, `os` if needed), plus `pytest>=8` from the `test` extra. Nothing new is acquired.
- **Unknowns remaining:** none that block. The epic trace IDs (spec §8) are unchecked and do not affect the code.

## Locked decisions and assumptions

**Locked decisions**
- `hello-world/hello.sh` and the `hello-world/` folder are unchanged: no edit, rename, move or added file (spec Non-Goals; PLAY-172 FR7; HLD §6).
- `tests/test_hello_sh.py` is the only file changed (HLD §2, work item `t1` Owns).
- Output is asserted as exactly `hello world\n`, with no strip-based or loosened comparison (spec A2; HLD §6).
- No change to `.github/workflows/ci.yml`, `pyproject.toml`, README or `CHANGELOG.md` (spec Non-Goals; `t1` Must not touch).
- No existing test is removed. Coverage of exit code, stdout, stderr, shebang, executable bit and isolation stays (`t1` AC).

**Assumptions**
- *Running the script with `cwd=REPO_ROOT` and argv `["./hello-world/hello.sh"]` satisfies "run from the repository root without invoking bash".* Evidence: `subprocess.run` with a relative path containing `/` resolves it against `cwd` on POSIX and execs it through the shebang. If wrong, the test would fail with `FileNotFoundError` and surface as a red gate, not a false pass.
- *"Only file present" (AC2) means the folder has exactly one entry of any kind, `hello.sh`.* Evidence: HLD §5 ("exactly one entry … and no hidden files"). If a stricter or looser reading was meant, only the isolation assertion changes.
- *No `__pycache__` or other artefact appears in `hello-world/` during the test run.* Evidence: the folder holds no Python and pytest writes caches only under `.pytest_cache/` and `tests/`. If wrong, the hardened isolation test fails, which is the intended behaviour.

## Solution proposal

Harden `tests/test_hello_sh.py` in place, keeping its two classes and the absolute-path `SCRIPT` constant.

1. **Root-relative execution (AC1, AC3, FR3, FR5).** Add one execution test that calls `subprocess.run(["./hello-world/hello.sh"], cwd=REPO_ROOT, capture_output=True, text=True)`. It asserts `returncode == 0`, `stdout == "hello world\n"` and `stderr == ""`. Passing `cwd` explicitly makes the test independent of where `pytest` was started. Passing a list with no `bash` in it and no `shell=True` proves the shebang and the executable bit do the work.
2. **Exact output (AC4, A2).** Drop the `.strip()` assertion in `test_exact_output_no_extra_whitespace` and keep the exact equality. Optionally add explicit checks that the output has exactly one line and that the line is `hello world`. These checks are derived from the exact string, never loosened.
3. **Isolation (AC2, FR1, FR2).** Change `test_folder_contains_only_hello_sh` to list every entry with `iterdir()` and no dot-filter. Assert that the sorted names equal `["hello.sh"]`, and also assert that `hello.sh` is a regular file.

Existing absolute-path tests stay. They still cover the script itself, and the new test adds the developer's literal invocation.

**Alternatives rejected**
- Replacing the absolute-path tests with root-relative ones: this removes existing tests, which `t1` forbids.
- Using `os.chdir` in a fixture: it mutates process state that other tests share. `cwd=` is local to the call.
- Using `git ls-files hello-world` for isolation: it misses untracked files, which AC2 ("lists its contents") covers.
- Touching the script, CI or the changelog: out of scope (Locked decisions).

## Ordered implementation steps

1. **Add the root-relative execution test** in `tests/test_hello_sh.py` (class `TestHelloShExecution`). Run `["./hello-world/hello.sh"]` with `cwd=REPO_ROOT` and no `bash` and no `shell=True`. Assert exit code 0, stdout exactly `"hello world\n"` and empty stderr. Advances AC1 and AC3 (FR3, FR5). Layer: `package-api` (`pytest`).
2. **Tighten the exact-output test** in `tests/test_hello_sh.py:23-28`. Remove the `.strip()` comparison and keep `result.stdout == "hello world\n"`. Exactness is not weakened anywhere else. Advances AC4 (FR4, A2). Layer: `package-api`.
3. **Make the isolation test count hidden entries** in `tests/test_hello_sh.py:40-43`. Remove the `startswith(".")` filter, compare the sorted list of all entry names with `["hello.sh"]` and assert that `hello.sh` is a regular file. Advances AC2 (FR1, FR2). Layer: `package-api`.
4. **Keep the structure tests unchanged** (`test_shebang_line`, `test_executable_permission`) and run the full suite with `python -m pytest`. Confirm that `git diff main -- hello-world/` is empty and that `./hello-world/hello.sh` still prints `hello world`. Advances AC3 and the `t1` regression criterion. Layer: `package-api`.

Implicit invariants: authorization, tenancy, concurrency and input validation do not apply, because the script takes no input and has no state. The only error path is a missing or non-executable script. The tests report it as a failure (`FileNotFoundError` / `PermissionError` raised by `subprocess.run`), and nothing catches or swallows it. No generated deliverables and no binaries are involved, so there are no `.factory/delivery-assets` entries.

## Work-item mapping

| Step | Work item |
|---|---|
| 1 | `t1` — SCRUM-3: Harden hello-world tests to check AC1–AC4 exactly as worded (test-only, script unchanged) |
| 2 | `t1` |
| 3 | `t1` |
| 4 | `t1` |

## Verification and CI gate

- **Canonical gate** (per `.factory/testing.md` and `.github/workflows/ci.yml`, in this order): `pip install -e ".[test]"`, then `pytest` from the repo root. Run it once locally on the committed SHA. The provider CI run at the PR head is the authoritative result.
- **Required layer:** `package-api` (`pytest`, production-path). It runs unprivileged in a pod. No other layer exists, and none is needed.
- **Provider CI:** no configuration change. Both jobs, `test` and `gate`, must be green at the head. `gate` stays green because no `CI_FAIL` file is added.
- **Done means:**
  - The full suite passes, including all original `test_hello_sh.py` tests (refined, not removed) and the new root-relative test.
  - `git diff main --stat` shows only `tests/test_hello_sh.py` outside `stories/SCRUM-3/`.
  - `git diff main -- hello-world/` is empty.

## Risks and scope guards

**Risks**
- *The executable bit is lost on checkout* (`core.fileMode=false`, Windows). The tests would fail, and correctly so. This is not this story's environment (HLD §7). Do not work around it with `bash` in argv or `chmod` in the test.
- *The tests depend on the working directory.* Mitigation: pass `cwd=REPO_ROOT` explicitly (step 1).
- *Stray local files in `hello-world/`* would now fail the isolation test. This is intended behaviour per AC2.

**Scope guards: the implement phase must NOT**
- Modify, rename, move or add anything under `hello-world/`.
- Touch `.github/workflows/ci.yml`, `pyproject.toml`, `README.md`, `CHANGELOG.md`, `.factory/` or any other test file.
- Delete, skip, `xfail` or loosen any existing assertion, apart from the redundant `.strip()` line that the HLD forbids. The exact `== "hello world\n"` assertion beside it stays.
- Invoke the script through `bash` or `shell=True` in the root-relative test.
- Add a `conftest.py`, fixtures shared with other modules, or a new test framework.
- Make a red check green by any means other than a correct fix. A blocked check is reported as blocked.

## Clarification outcomes

None.
