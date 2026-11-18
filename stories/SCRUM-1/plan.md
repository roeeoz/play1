# Implementation plan — SCRUM-1, hello-world bash script in a dedicated folder

## Context

SCRUM-1 asks for `hello-world/hello.sh`, the only file in its folder, with a `#!/bin/bash` shebang and execute permission, printing exactly `hello world` and exiting 0 (AC1 execution, AC2 folder isolation, AC3 direct execution via shebang, AC4 output exactness). The change lands in `play1` on the work branch `halo/feat/scrum-1-20261118-211648`, cut from and merging into `main`. The target branch already ships the script, so the only work is to tighten `tests/test_hello_sh.py` until every criterion is checked literally, then cite CI at the pull request's head as evidence. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-1/`.

## Research findings

- **Deliverable exists, unchanged.** `hello-world/hello.sh:1` is `#!/bin/bash`; `hello-world/hello.sh:2` is `echo "hello world"`. The git index stores it as `100755 2a43bb26… hello-world/hello.sh`. The folder holds only `hello.sh` on disk (no dotfiles). The work branch differs from `origin/main` (`b7b5d0a`) only by `stories/SCRUM-1/{spec,hld,work-items}.md`.
- **Existing test, `tests/test_hello_sh.py`:**
  - `tests/test_hello_sh.py:5-6` — `REPO_ROOT` and `SCRIPT` (absolute path) constants.
  - `tests/test_hello_sh.py:10-15` — runs `[str(SCRIPT)]` with no `cwd`, asserts `returncode == 0` and `stdout == "hello world\n"`. Invocation is by absolute path, not `./hello-world/hello.sh` from the repo root as AC1/AC3 phrase it.
  - `tests/test_hello_sh.py:17-21` — empty stderr.
  - `tests/test_hello_sh.py:23-28` — `strip()` check plus exact equality; the exact equality already subsumes the strip check.
  - `tests/test_hello_sh.py:32-34` — first line equals `#!/bin/bash`.
  - `tests/test_hello_sh.py:36-38` — checks only `S_IXUSR` on disk; nothing checks the mode git stores.
  - `tests/test_hello_sh.py:40-43` — **gap**: filters out names starting with `.`, so a dotfile in `hello-world/` would pass, contrary to AC2 as `work-items.md` t1 states it.
- **Gate.** `.factory/testing.md` declares `test-gate: pytest`, one required layer `package-api` (`runBy: canonical-gate`). `.github/workflows/ci.yml:12-24` (`test` job) runs `pip install -e ".[test]"` then `pytest` on Python 3.12 for every `pull_request`. `pyproject.toml:64-66` sets `testpaths = ["tests"]`, `addopts = "-q"`. No linter, formatter or type checker exists. `.github/workflows/ci.yml:26-38` (`gate` job) fails only if `CI_FAIL` exists at the repo root.
- **Git available in CI.** `actions/checkout@v4` checks out a working tree with `.git`, so `git ls-files -s` works in the `test` job; it also works in the local checkout.
- **Contracts touched.** None beyond the repository contract in `hld.md` §5: stdout `hello world\n`, stderr empty, exit 0, folder listing exactly `["hello.sh"]`, shebang `#!/bin/bash`, index mode `100755`.
- **External data.** None.
- **Remaining unknowns.** None blocking.

## Locked decisions and assumptions

**Locked decisions**
- Do not change `hello-world/hello.sh` or add anything to `hello-world/` — `spec.md` §2 non-goals, `hld.md` §6 "Confirm, don't rewrite", `work-items.md` t1 "Nothing outside the test file changes".
- Only `tests/test_hello_sh.py` changes — `work-items.md` t1 "Owns".
- `pyproject.toml`, `.github/workflows/ci.yml`, README and CHANGELOG stay untouched — `work-items.md` t1 "Consumes (read-only)", `spec.md` §2 non-goals.
- Stdout must equal `hello world\n`; the single trailing newline is allowed — `spec.md` §8 A2.
- AC2 counts hidden entries — `work-items.md` t1, `hld.md` §6.
- Git index mode `100755` is checked — `work-items.md` t1 AC3 bullet, `hld.md` §6.
- Evidence is the CI `test` job at the PR head commit — `.factory/testing.md`, `hld.md` §6.

**Assumptions**
- `git` is on `PATH` wherever `pytest` runs (CI and the local pod). Evidence: `ubuntu-latest` ships git and `actions/checkout@v4` keeps `.git`. If wrong, the index-mode test errors; it must then fail loudly, not be skipped.
- Running from the repository root means `subprocess.run(["./hello-world/hello.sh"], cwd=REPO_ROOT, …)`. Evidence: AC1/AC3 wording. If wrong, nothing breaks; the absolute-path form is equivalent for this script.

## Solution proposal

Edit `tests/test_hello_sh.py` in place and keep its two-class layout (`TestHelloShExecution`, `TestHelloShStructure`).

- **Execution (AC1, AC3, AC4).** Add one small helper in the test module that runs `./hello-world/hello.sh` with `cwd=REPO_ROOT`, `capture_output=True`, `text=True`, with no `bash` prefix and no `shell=True`, so the kernel must resolve the shebang and execute bit. Assert `returncode == 0`, `stdout == "hello world\n"` and `stderr == ""`. Exact equality rejects a missing newline, an extra line, other case and added spaces or tabs, so drop the redundant `strip()` assertion and add one explicit assertion that `stdout.splitlines() == ["hello world"]` for a readable AC4 failure.
- **Folder isolation (AC2).** Replace the dotfile-filtering comprehension with `sorted(os.listdir(SCRIPT.parent)) == ["hello.sh"]`, which counts hidden entries and subfolders.
- **Shebang and executable (AC3).** Keep the first-line check. Keep the on-disk `S_IXUSR` check. Add a test that runs `git ls-files -s -- hello-world/hello.sh` with `cwd=REPO_ROOT` and `check=True`, and asserts the first field is `100755`.

**Alternatives rejected**
- Recreating or editing the script: violates `spec.md` A1 and the non-goals.
- A new test file or new CI job: `work-items.md` t1 owns only `tests/test_hello_sh.py`; a CI change is a non-goal.
- Reading the git mode via a Python git library: adds a dependency; the `git` CLI is enough.

## Ordered implementation steps

1. Add `import os` to `tests/test_hello_sh.py` and a module-level helper that runs `./hello-world/hello.sh` from `REPO_ROOT` (no `bash`, no shell). Point `test_prints_hello_world`, `test_no_stderr` and `test_exact_output_no_extra_whitespace` at it. — AC1, AC3, AC4; layer `package-api` (`pytest`).
2. In `test_exact_output_no_extra_whitespace` (`tests/test_hello_sh.py:23-28`), replace the `strip()` assertion with `stdout.splitlines() == ["hello world"]`, keeping `stdout == "hello world\n"`. — AC4; layer `package-api`.
3. Rewrite `test_folder_contains_only_hello_sh` (`tests/test_hello_sh.py:40-43`) to compare the full, unfiltered `os.listdir` result to `["hello.sh"]`. — AC2; layer `package-api`.
4. Add `test_git_index_mode_is_executable` to `TestHelloShStructure`: `git ls-files -s -- hello-world/hello.sh` from `REPO_ROOT`, `check=True`, assert output is non-empty and its mode field is `100755`. Do not skip on missing git. — AC3; layer `package-api`.
5. Confirm no file outside `tests/test_hello_sh.py` changed (`git diff --stat origin/main...HEAD` shows only that file plus `stories/SCRUM-1/`), and that `git ls-files -s hello-world` still reports `100755 2a43bb26…`. — all ACs (non-regression); no test layer, a review check.
6. Run the gate (`pip install -e ".[test]"` then `pytest`) and confirm the whole suite passes. — all ACs; layer `package-api`.

Invariants: authorization, tenancy, concurrency and input validation do not apply (static script, no input). Error paths: each assertion must fail on its named deviation. Dependencies come from `pip install -e ".[test]"`; nothing new is added. No generated deliverables; no binary for `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–6 | t1 — Tighten hello-world tests so they check every SCRUM-1 acceptance criterion literally |

Every work item in `work-items.md` (only t1) is covered.

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"`, then `pytest` from the repo root (`.factory/testing.md`, `.github/workflows/ci.yml:21-24`). Run once locally on the committed SHA as a pre-check.
- **Required layer:** `package-api` (`pytest`), `runBy: canonical-gate`. It runs in a pod; the authoritative result is the CI `test` job at the PR head commit.
- **The `gate` job** must stay green: no `CI_FAIL` at the repo root.
- **No CI configuration change**; `.github/workflows/ci.yml` already runs the layer on `pull_request`.
- **Done means:** the full `pytest` suite passes locally and in CI at the head commit, including the tightened `tests/test_hello_sh.py` (execution, exact output, empty stderr, unfiltered folder listing, shebang, on-disk execute bit, index mode `100755`). The PR description cites that CI run as evidence for AC1–AC4.

## Risks and scope guards

**Risks**
- The index-mode test depends on `git` and a `.git` directory. Mitigation: `actions/checkout@v4` provides both; a failure there must be fixed, not skipped.
- The stricter folder check fails if any tool writes into `hello-world/` during the run. Nothing does today: the script writes nothing and pytest writes `__pycache__` only under `tests/`.

**Must NOT do**
- Do not edit, rename, re-mode or recreate `hello-world/hello.sh`; do not add any file to `hello-world/`.
- Do not touch `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/`, `README.md`, `CHANGELOG.md` or any other test file.
- Do not add a `conftest.py`, a new test file, a dependency or a CI job.
- Do not loosen any assertion (e.g. back to `strip()`, or filtering dotfiles), and do not skip, `xfail` or delete a test to make the gate green; report it blocked instead.
- Do not touch `stories/SCRUM-1/spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
