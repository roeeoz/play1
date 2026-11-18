# Plan: FIPSPROBE-6, Hello-world bash script in a dedicated folder (verification)

## Context

FIPSPROBE-6 delivers "Hello-world bash script in a dedicated folder" as a verification change. `hello-world/hello.sh` is already on `main`, added by commit `65938b5` (WI-220A63-1). This story adds one pytest module, linked to FIPSPROBE-6. The module proves that the script prints exactly `hello world` as one line and exits 0 when run directly (AC1, AC3). It also proves that the script starts with `#!/bin/bash` and that git records it as executable (AC2, RK1). The change touches nothing else (AC4, AC5). It lands in `roeeoz/play1` on `halo/feat/fipsprobe-6-20261118-131756`, which merges into `main`. `spec.md` (the requirement), `hld.md` (the design) and `work-items.md` (one work item, `t1`) sit beside this file in `stories/FIPSPROBE-6/`.

## Research findings

- **Script under test.** `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. Lines end in LF, with no CR. `git ls-files -s hello-world/hello.sh` shows `100755 2a43bb26… 0	hello-world/hello.sh`. The folder holds only `hello.sh`.
- **Checkout file modes cannot be trusted (RK1, confirmed).** `git config core.fileMode` is `false` in this checkout, and every file shows as `-rwxrwxrwx`. A check based on `st_mode` passes whatever git records, so only the git index is reliable.
- **Existing tests of the script.** `tests/test_hello_sh.py:9-43` runs the script without a timeout. It checks stdout, stderr, the shebang, `st_mode & S_IXUSR` (`:36-38`, the weak check) and whether the folder holds only `hello.sh` (`:40-43`). Nothing in it refers to FIPSPROBE-6. No existing test calls `git`.
- **Pattern to follow.** `tests/test_qa_s3_greeting.py:4-11` uses `SCRIPT = pathlib.Path(__file__).resolve().parent.parent / ...`, a helper that runs `subprocess.run([str(SCRIPT)] + args, capture_output=True, text=True, timeout=10)`, test classes grouped by concern, and byte-level checks with `read_bytes()` (`:21-27`).
- **Test collection.** `pyproject.toml:26-28` sets `testpaths = ["tests"]` and `addopts = "-q"`. There is no `tests/__init__.py` and no `conftest.py`, so pytest's default `prepend` import mode needs every module basename to be unique. `test_fipsprobe_6_hello_sh.py` is unique.
- **Canonical gate.** `.factory/testing.md` names `test-gate: pytest`. It runs as `pip install -e ".[test]"` then `pytest` on Python 3.12, as the `test` job in `.github/workflows/ci.yml:11-23`. That job uses `actions/checkout@v4` on `ubuntu-latest`, so `.git` and `git` are both present. The `gate` job (`ci.yml:25-35`) fails only if `CI_FAIL` exists. No linter or formatter is configured. The single declared layer is `package-api` (production-path, `runBy: canonical-gate`).
- **Factory review gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-20` is the play1 layout gate (slot `mr-gate`):
  - rule 1: tests live under `tests/`, which the new file meets;
  - rule 2: a new shell script must be executable with a shebang, which doesn't apply because no script is added;
  - rule 3: no file over 200 KB, which the new file meets;
  - rule 4 (`PLAY-G4`, blocker): a PR whose diff does not touch `CHANGELOG.md` fails. Every prior story (`CHANGELOG.md:5-8`) added a line under `## Unreleased` (`CHANGELOG.md:3`).
- **External data:** none. There are no cross-repo contracts.
- **What exists and what is new.** The script, the folder and the suite all exist. Only `tests/test_fipsprobe_6_hello_sh.py` is new.
- **Unknown after research:** only the `PLAY-G4` versus AC5 conflict, which is raised as a question.

## Locked decisions and assumptions

**Locked decisions**
- `hello-world/hello.sh` stays byte-for-byte and mode-for-mode unchanged, at the repository root. Source: spec FR1, AC5; work item `t1` AC8.
- The deliverable is one new test module, `tests/test_fipsprobe_6_hello_sh.py`, with `FIPSPROBE-6` in its file name and module docstring. No custom pytest marker. Source: hld §2, §5, §6; `t1` AC6.
- The executable bit is read from the git index with `git ls-files -s`, and the expected mode is `100755`. Source: spec §7, hld §3, §6; `t1` AC4.
- If `git` or `.git` is missing, the mode check fails with a clear message. It never skips. Source: hld §6; `t1` AC5.
- Every subprocess call has a timeout of about 10 s. Source: hld §6; `t1` AC6.
- No folder-contents assertion. `tests/test_hello_sh.py` is not edited, because FIPSPROBE-7 owns `test_folder_contains_only_hello_sh`. Source: hld §2, §6; spec Non-Goals.
- No CHANGELOG, documentation, CI, `pyproject.toml` or `src/` change. Source: spec AC5, which the developer confirmed as option (b) (spec §8). This conflicts with `PLAY-G4`; see Risks and the open question.

**Assumptions**
- The tests resolve the repository root as `Path(__file__).resolve().parent.parent` and pass it to `git` as `cwd`. Evidence: the same pattern in `tests/test_qa_s3_greeting.py:4`. If wrong, for example when pytest is run from another directory, the explicit `cwd` still makes the git call independent of the current directory.
- `/bin/bash` exists on the runner and in the pod. Evidence: `ubuntu-latest`; `which bash` gives `/usr/bin/bash` with merged `/bin`. If wrong, the execution test fails, which correctly signals that R5 does not hold.

## Solution proposal

Add one self-contained pytest module, `tests/test_fipsprobe_6_hello_sh.py`. The existing suite collects it, and nothing else changes.

- **Execution checks (AC1, AC3).** A module-level helper runs `[str(SCRIPT)]` with `capture_output=True`, `text=True`, `timeout=10` and `cwd=REPO_ROOT`, with no `bash` prefix. Assertions:
  - `returncode == 0`;
  - `stdout == "hello world\n"`;
  - `stdout.splitlines() == ["hello world"]`, so there is exactly one line, and that line equals its own `.strip()`;
  - `stderr == ""`.
- **Shebang check (AC2).** `SCRIPT.read_bytes().split(b"\n", 1)[0] == b"#!/bin/bash"`. This uses exact bytes, so a CR or trailing space would fail it.
- **Repository-mode check (AC2, RK1).** Run `git ls-files -s -- hello-world/hello.sh` with `cwd=REPO_ROOT` and `timeout=10`. Parse the single output line as `<mode> <sha> <stage>\t<path>`. Assert that the path is exactly `hello-world/hello.sh`, which also proves the location at the root (FR1), and that the mode is `100755`. Fail with an explanatory `pytest.fail` message in these cases:
  - `shutil.which("git")` is `None`;
  - `REPO_ROOT / ".git"` is missing;
  - the command exits non-zero;
  - the output is empty, which means the file is untracked.
- **Traceability (AC4).** The module docstring names FIPSPROBE-6 and maps each test to its acceptance criterion.

**Alternatives rejected**
- Editing `tests/test_hello_sh.py` to replace its `st_mode` check would touch a file outside this story's ownership, one that FIPSPROBE-7 must edit (hld §6).
- `git ls-tree HEAD` misses staged state during development, so the index is preferred (hld §6).
- Checking `st_mode` is unreliable under `core.fileMode=false` (RK1).
- `pytest.skip` when git is missing would hide RK1.
- A custom marker would need a `pyproject.toml` change.

## Ordered implementation steps

1. **Create `tests/test_fipsprobe_6_hello_sh.py` with its scaffolding.**
   - Add a module docstring containing `FIPSPROBE-6` and the AC mapping.
   - Add `REPO_ROOT`, `SCRIPT = REPO_ROOT / "hello-world" / "hello.sh"` and `RELPATH = "hello-world/hello.sh"`.
   - Add a `run_script()` helper with `timeout=10` and `cwd=REPO_ROOT`.
   - Imports come from the standard library only: `pathlib`, `shutil`, `subprocess`, `pytest`.
   - Advances AC4 (traceability) and `t1` AC6. Layer: `package-api` (pytest).
2. **Add the execution tests (class `TestHelloShExecution`).**
   - Assert that the exit code is 0, that stdout is exactly `hello world\n` as one line with no surrounding whitespace, and that stderr is empty.
   - Advances AC1, AC3 and `t1` AC1–AC2. Layer: `package-api`.
3. **Add the shebang test (class `TestHelloShRepositoryShape`).**
   - Assert on the exact first-line bytes `#!/bin/bash`.
   - Advances AC2 and `t1` AC3. Layer: `package-api`.
4. **Add the git-index mode test (same class).**
   - Add the `git ls-files -s -- hello-world/hello.sh` call, with `timeout=10`, `cwd=REPO_ROOT` and `capture_output=True, text=True`.
   - Fail with a message if git or `.git` is missing, if the command exits non-zero, or if the output is empty.
   - Assert that exactly one entry is listed, that its path equals `RELPATH` and that its mode equals `100755`.
   - Advances AC2, RK1 and `t1` AC4–AC5. Layer: `package-api`.
   - Invariants: this is a read-only git query, with no writes to the index or worktree, and it is idempotent. Validation and error paths are the explicit failure messages above.
5. **Verify scope and run the gate.**
   - Run `git diff --stat main...HEAD -- . ':!stories/FIPSPROBE-6'`. Expect only `tests/test_fipsprobe_6_hello_sh.py`, plus the single `CHANGELOG.md` line only if the open question is answered (b).
   - Run `git ls-files -s hello-world/hello.sh` and expect it unchanged (`100755 2a43bb26…`).
   - Then run the gate as described under Verification and CI gate.
   - Advances AC4, AC5 and `t1` AC7–AC8. Layer: `package-api` (gate run) plus the diff inspection.
   - Dependencies: `pip install -e ".[test]"` fetches `pytest>=8`, `pypdf` and `flask>=3` from the index. Assume no warm cache.
   - No generated deliverables, and no binaries for `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–5 | `t1` — FIPSPROBE-6: add story-linked test proving hello-world/hello.sh output, shebang and git-recorded executable mode |

`t1` is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate, in order.** Run `pip install -e ".[test]"` then `pytest` from the repository root, once, on the committed SHA. The Stop hook and the GitHub Actions `test` job re-run it at the head.
- **Required layer.** `package-api` (`pytest`, `runBy: canonical-gate`) can run in a pod. Provider CI at the exact head is the authoritative result.
- **What the gate must show:**
  - every existing test still passes;
  - the four new test groups (execution, output exactness, shebang, git mode) are collected from `tests/test_fipsprobe_6_hello_sh.py` and pass;
  - the `gate` job is green because no `CI_FAIL` exists.
- **Not needed:** no provider CI configuration change. `.factory/testing.md` needs no change, because the new test sits in the existing layer. `.factory/delivery-assets` doesn't apply.
- **play1 layout gate (`mr-gate`).** Rules 1–3 pass. Rule 4 (`PLAY-G4`) fails as a blocker under the spec's no-CHANGELOG decision unless the developer answers otherwise (see Clarification outcomes).

## Risks and scope guards

**Risks**
- **`PLAY-G4` versus spec AC5 (blocking).** The layout gate requires a `CHANGELOG.md` line, and AC5 forbids one. This is raised as the open question. Until it is answered, the plan follows the locked spec (no CHANGELOG), and the `PLAY-G4` finding is reported blocked, not worked around.
- **First test that shells out to `git`.** It depends on `git` being on PATH and on `.git` being present. Both hold in CI and in a clone. If they're missing, the test fails loudly by design.
- **Overlap with `tests/test_hello_sh.py`.** The two files duplicate the output assertions. This is accepted (hld §7), and the runtime cost is negligible.

**Scope guards — the implement phase must NOT:**
- modify, move, re-mode or reformat anything in `hello-world/`;
- edit `tests/test_hello_sh.py`, including its weak `st_mode` check and `test_folder_contains_only_hello_sh`;
- touch `.github/`, `pyproject.toml`, `src/`, `README.md`, `docs/`, `.factory/` or `qa/`;
- add a pytest marker, `conftest.py` or `tests/__init__.py`;
- add a folder-contents assertion, which would couple this story to FIPSPROBE-7;
- touch `CHANGELOG.md`, unless the developer answers (b), and then add exactly one line under `## Unreleased`;
- make a failing check green by skipping, deleting, `xfail`-ing or weakening it. In particular, the git-mode check must never `skip` when git is missing.

## Clarification outcomes

One question is open through the plan conversation, `/halo-out/plan-questions.json`:

- **`PLAY-G4` versus AC5.** Should the PR (a) keep the spec's no-CHANGELOG decision and have the `PLAY-G4` blocker waived by a human, or (b) add one line under `## Unreleased` in `CHANGELOG.md`, which would amend AC5?
  - Recommendation: (a). It is the decision the developer already confirmed (spec §8), and AC5 states it explicitly.
  - Answer (b) instead if the `mr-gate` blocker cannot be waived for this PR.
  - Until the developer answers, the plan proceeds on (a).
