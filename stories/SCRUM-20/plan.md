## Context

SCRUM-20 asks for a bash script `hello-world/hello.sh`, alone in its own root-level folder, with a `#!/bin/bash` shebang and the executable bit. Run as `./hello-world/hello.sh`, it prints exactly `hello world` and exits 0 (spec Scenarios 1–4, FR1–FR5). The script is already on `main` and meets the spec. This story keeps it byte-for-byte unchanged (spec A1). It closes two verification gaps in `tests/test_hello_sh.py` and adds the `CHANGELOG.md` bullet that gate PLAY-G4 requires. The change lands in `play1` on the work branch `halo/feat/scrum-20-20261119-012037`, which merges into `main`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-20/`.

## Research findings

- **Script (consumed, unchanged):** `hello-world/hello.sh` is tracked as `100755` (blob `2a43bb2`). Its bytes are exactly `#!/bin/bash\necho "hello world"\n`. It is the only tracked file in `hello-world/`. The work branch differs from `main` only under `stories/SCRUM-20/`.
- **Existing acceptance suite:** `tests/test_hello_sh.py` holds the following:
  - `REPO_ROOT` and `SCRIPT` are defined from `__file__` (`tests/test_hello_sh.py:5-6`).
  - `TestHelloShExecution` runs `[str(SCRIPT)]` (an absolute path) with no `cwd`. It asserts exit 0, stdout `"hello world\n"`, empty stderr and the stripped output (`:9-28`).
  - `TestHelloShStructure` asserts the shebang line, `S_IXUSR` on the working-tree file, and that the folder holds only `hello.sh`, ignoring dotfiles (`:31-43`).
- **Gap 1:** no test runs the script as the spec states, with the relative path `./hello-world/hello.sh` and `cwd=REPO_ROOT`.
- **Gap 2:** `test_executable_permission` (`:36-38`) reads only the filesystem mode. Nothing checks the mode git records, which is the mode every clone receives.
- **Repository precedent for `cwd`:** `tests/test_qa_20261109_s1_a.py:11-13` already passes `cwd` and `timeout=10` to `subprocess.run`. No test in `tests/` calls `git` yet, and no test uses `pytest.skip` yet.
- **Changelog contract:** `CHANGELOG.md:3` is `## Unreleased`. It is followed by bullets in the form `` - <KEY>: add `<path>`, <description>. `` (`CHANGELOG.md:5-8`). The file ends after the PLAY-175 line.
- **Gates:**
  - `.factory/testing.md` declares one required layer, `package-api`: `pytest`, run by the canonical gate.
  - `.github/workflows/ci.yml` runs the `test` job (Python 3.12, `pip install -e ".[test]"`, then `pytest`) and the `gate` job (red iff `CI_FAIL` exists at the root). `actions/checkout@v4` leaves `.git` and `git` available.
  - The layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) requires tests under `tests/`, a new shell script to be executable with a shebang, no file over 200 KB, and a CHANGELOG line under `## Unreleased` (PLAY-G4).
  - No linter or formatter is configured.
- **Other facts:** `.factory/memory/` does not exist. The change has no external data dependencies.
- **Unknowns remaining:** none.

## Locked decisions and assumptions

**Locked decisions**
- `hello-world/hello.sh` stays byte-for-byte unchanged, and `hello-world/` gets no new file (spec A1, FR1; work item t1 AC1).
- The expected output is `hello world\n`, with one terminating newline allowed (spec A2).
- The acceptance tests extend `tests/test_hello_sh.py`. No new test module and no shell-based test is added (hld §6).
- A tracked-mode test asserts `100755` and skips when no git checkout is available (hld §6–7; t1 AC3).
- Exactly one `CHANGELOG.md` bullet is added under `## Unreleased`, keyed `SCRUM-20` (spec A3, hld A4; t1 AC5).
- There is no CI, README or docs change (spec non-goals; t1 AC6).

**Assumptions**
- **The `git ls-files` output gives the tracked mode.** `git ls-files -s hello-world/hello.sh` run with `cwd=REPO_ROOT` prints `100755 <sha> 0\thello-world/hello.sh`, and the test reads the first field. *Evidence:* the output observed in this checkout. *If wrong:* the test fails loudly in CI. It does not pass silently.
- **The skip conditions are enough.** The test skips when `shutil.which("git")` is `None` or `REPO_ROOT / ".git"` does not exist. *Evidence:* hld §7 accepts a skip outside a checkout. *If wrong* (for example, a worktree whose `.git` is a file): `.exists()` still holds for a `.git` file, so the check still runs.

## Solution proposal

Keep the script and make the acceptance suite prove the spec as written, as two additive tests in the existing module:

1. **Run-as-documented test.** Add a test to `TestHelloShExecution` that runs `["./hello-world/hello.sh"]` with `cwd=REPO_ROOT`, `capture_output=True`, `text=True` and `timeout=10`. It asserts `returncode == 0`, `stdout == "hello world\n"` and `stderr == ""`.
   - The argv holds no `bash`, so the kernel resolves the shebang. This proves Scenarios 1, 3 and 4 the way a developer types the command.
2. **Tracked-mode test.** Add a test to `TestHelloShStructure` that runs `git ls-files -s hello-world/hello.sh` in `REPO_ROOT` and asserts that the first whitespace-separated field is `100755`.
   - It calls `pytest.skip(...)` when git or the `.git` entry is missing.
   - This catches the case where a local `chmod +x` passes while git records `100644`, for example with `core.fileMode=false`.

The existing six tests stay as they are, so absolute-path runs remain covered. A `CHANGELOG.md` bullet completes PLAY-G4.

**Alternatives rejected**
- **Rewriting the script:** spec A1 forbids it, and it would change nothing in behaviour.
- **A new test module:** it splits ownership of the script's acceptance checks with no benefit.
- **A `.bats` or shell test beside the script:** it breaks FR1, and it is not a declared layer.
- **Changing CI:** it is a non-goal, and the existing `test` job already runs the module.

## Ordered implementation steps

1. Add `import shutil` and `import pytest` to `tests/test_hello_sh.py`. In `TestHelloShExecution`, add a test (for example `test_runs_as_documented_from_repo_root`) that runs `./hello-world/hello.sh` with `cwd=REPO_ROOT` and `timeout=10`, and asserts exit 0, stdout `"hello world\n"` and empty stderr.
   - Advances t1 AC2, which covers Scenarios 1, 3 and 4. Layer: `package-api` (`pytest`).
2. In `TestHelloShStructure` in `tests/test_hello_sh.py`, add a test (for example `test_git_tracks_executable_mode`) with the following behaviour:
   - It skips via `pytest.skip` when `shutil.which("git") is None` or `not (REPO_ROOT / ".git").exists()`.
   - Otherwise it runs `git ls-files -s hello-world/hello.sh` with `cwd=REPO_ROOT`, `check=True` and `text=True`, and asserts that the output is non-empty and that its first field is `"100755"`.
   - Advances t1 AC1 and AC3 (Scenario 3). Layer: `package-api`.
   - Error path: an empty output means the file is untracked, and the test must fail on it. It must not raise an IndexError.
3. Leave the existing tests at `tests/test_hello_sh.py:10-43` untouched.
   - Advances t1 AC4. Layer: `package-api`.
4. Append one bullet after `CHANGELOG.md:8`, under `## Unreleased`, in the existing style. Example: ``- SCRUM-20: add acceptance tests for `hello-world/hello.sh` that run it as `./hello-world/hello.sh` from the repo root and check its git-tracked executable mode.``
   - Change no other line. Advances t1 AC5 and gate PLAY-G4.
   - No test layer applies, because no test reads the changelog. The layout gate checks it.
5. Install dependencies from scratch with `pip install -e ".[test]"`, which fetches `pytest>=8` and `pypdf`/`flask`. Then run `pytest` from the repo root.
   - Confirm that `git diff main -- hello-world/` is empty and that no `CI_FAIL` exists.
   - Advances t1 AC1 and AC6.

The steps carry no authz, tenancy, concurrency or idempotency surface, because the script takes no input and keeps no state. The change has no generated deliverables.

## Work-item mapping

| Step | Work item |
|---|---|
| 1, 2, 3, 4, 5 | t1 — Lock in hello-world/hello.sh acceptance: run-as-documented and git-mode tests, CHANGELOG entry |

The breakdown has only one work item, and every step maps to it.

## Verification and CI gate

- **Canonical gate:** `pip install -e ".[test]"`, then `pytest`, run once from the repo root on the committed SHA.
  - This is the only required layer (`package-api`, `runBy: canonical-gate`). It runs in a pod, unprivileged.
  - Provider CI re-runs it in the `test` job of `.github/workflows/ci.yml`. That provider run at the exact head is authoritative.
- **What the gate must show:**
  - The full suite passes, including the two new tests. On CI, `test_git_tracks_executable_mode` must run and pass, not skip.
  - The `gate` job is green because no `CI_FAIL` exists.
  - The layout gate passes: tests stay under `tests/`, no new shell script is added, all files are small, and a `CHANGELOG.md` line sits under `## Unreleased`.
- **Provider CI configuration:** none needed.
- **Delivery assets:** there is no `.factory/delivery-assets` obligation, because no binary is added. `.factory/testing.md` needs no change.

## Risks and scope guards

**Risks**
- **The tracked-mode test could skip on CI and hide a regression.**
  - *Mitigation:* `actions/checkout@v4` keeps `.git`. Check in the CI log that the test reports as passed, not skipped.
- **A relative-path run depends on `cwd`.**
  - *Mitigation:* `cwd=REPO_ROOT` is explicit, and the suite already uses this pattern in `tests/test_qa_20261109_s1_a.py:11-13`.

**Scope guards: do NOT**
- Modify, re-create or `chmod` `hello-world/hello.sh`, or add any file under `hello-world/`.
- Add any shell script, README, docs or CI file, or edit `.github/workflows/ci.yml` or `.factory/`.
- Edit or remove the existing tests in `tests/test_hello_sh.py`, or touch other test modules or the `qa/` scripts.
- Change existing `CHANGELOG.md` lines.
- Edit `stories/SCRUM-20/spec.md`, `hld.md` or `work-items.md`.
- Make a check green by deleting, skipping or weakening it. The new git test may skip only when there is no git checkout.

## Clarification outcomes

None.
