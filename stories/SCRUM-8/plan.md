# Plan — SCRUM-8: Hello world bash script in a dedicated folder

## Context

SCRUM-8 asks for a bash script `hello-world/hello.sh`, alone in its folder, that has a `#!/bin/bash` shebang and the executable bit, runs as `./hello-world/hello.sh`, and prints exactly `hello world` (Scenarios 1–4 in `spec.md`). The change lands in `play1`, on work branch `halo/feat/scrum-8-20261118-221925`, which merges into `main`. The script already exists on `main` and meets all four criteria. This story verifies that, leaves the script untouched, and tightens `tests/test_hello_sh.py` so that git's stored mode, LF line endings and the byte-exact output are each checked directly. The approved requirement (`spec.md`), the design (`hld.md`) and the single work item `t1` (`work-items.md`) sit beside this file in `stories/SCRUM-8/`.

## Research findings

**Deliverable (exists, compliant).**
- `hello-world/hello.sh` is indexed as `100755 2a43bb26…` (`git ls-files -s hello-world`). Its bytes are `#!/bin/bash\necho "hello world"\n`: 31 bytes, LF only, no CR.
- `hello-world/` holds only `hello.sh`.

**Existing tests** (`tests/test_hello_sh.py`):
- `tests/test_hello_sh.py:10-15` runs the script and asserts exit 0 and `stdout == "hello world\n"`.
- `tests/test_hello_sh.py:17-21` asserts stderr is empty.
- `tests/test_hello_sh.py:23-28` checks the output is exact.
- `tests/test_hello_sh.py:32-34` checks the shebang.
- `tests/test_hello_sh.py:36-38` checks the executable bit on the filesystem only (`st_mode & S_IXUSR`).
- `tests/test_hello_sh.py:40-43` checks the folder contents, ignoring dotfiles.

**Gaps against the work item's criteria:**
- G1. Nothing checks git's stored mode. `test_executable_permission` reads the working tree, which can disagree with the index under `core.fileMode=false`.
- G2. Nothing checks LF line endings. `read_text().splitlines()` at `:33` drops a trailing `\r`, so a CRLF file would still pass the shebang check (though the kernel would then fail to exec `/bin/bash\r`).
- G3. The output is checked only in text mode. `text=True` turns on universal newlines, so `hello world\r\n` would decode to `hello world\n` and pass. The script is also always run by absolute path, never as `./hello-world/hello.sh` from the repo root as Scenario 1 says.

**Gate.**
- `.factory/testing.md` declares one required layer, `package-api`: the command `pytest`, `runBy: canonical-gate`.
- `.github/workflows/ci.yml` job `test` runs `pip install -e ".[test]"`, then `pytest`, on Python 3.12. `actions/checkout@v4` provides a `.git` directory, so `git ls-files` works in CI.
- Job `gate` fails only if `CI_FAIL` exists at the repo root.
- `pyproject.toml` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- There is no linter or formatter.

**Repo-local merge gate.**
- `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (slot `mr-gate`) requires a line under `## Unreleased` in `CHANGELOG.md`. A pull request that leaves `CHANGELOG.md` untouched gets blocker `PLAY-G4`.
- Earlier script stories added a line there (`CHANGELOG.md:5-8`, PLAY-114/156/172/175).
- This conflicts with the work item's "no CHANGELOG entry" and with FR5 (see Clarification outcomes).

**External data.** None.

**Remaining unknown.** Whether the CHANGELOG line is allowed (question raised).

## Locked decisions and assumptions

**Locked decisions**
- Do not rewrite `hello-world/hello.sh` unless a criterion fails. Keep mode `100755` and LF endings. Source: `hld.md` §6; work item `t1`.
- Expected output is `hello world` plus one `\n`. Source: `spec.md` FR4 and A2.
- `hello-world/` contains only `hello.sh`. Source: `spec.md` FR1 and Scenario 2.
- Add no other scripts, no documentation, no CHANGELOG entry, no CI or workflow changes and no `CI_FAIL`. Source: `spec.md` FR5; work item `t1`.
- Tests go in the existing `tests/test_hello_sh.py`, and every existing test stays. Source: work item `t1`; `hld.md` §2.
- Reuse the existing pytest layer and CI unchanged. Source: `hld.md` §6; `.factory/testing.md`.

**Assumptions**
- **A-T1. Test file location.** Editing `tests/test_hello_sh.py` does not breach FR5, which says the change touches nothing outside `hello-world/`. Evidence: the work item owns that file, and `hld.md` §7 records this reading. If wrong, the git-mode check has nowhere to live and Scenario 3 stays covered only by the filesystem check.
- **A-T2. `git` is available.** The test runs inside a git checkout with `git` on `PATH`. Evidence: `actions/checkout@v4` in CI, and the local pod is a clone. If wrong, the new test fails with a `FileNotFoundError` or a non-zero exit. That is a real failure: do not skip it.
- **A-T3. CHANGELOG.** Until the developer answers, the plan follows the work item and does not touch `CHANGELOG.md`. Consequence: the repo-local `mr-gate` reports blocker `PLAY-G4`.

## Solution proposal

Leave the script alone and change one test file.
- The script already satisfies every criterion byte for byte, so rewriting it only adds risk: losing the mode or introducing CRLF (`hld.md` §6).
- The work is to close gaps G1–G3 in `tests/test_hello_sh.py` with small, independent test methods inside the existing test classes, using only the standard library already imported there (`subprocess`, `pathlib`).

Key decisions:
- **Git mode (G1).** Run `git ls-files -s hello-world/hello.sh` with `cwd=REPO_ROOT`, with `check=True` and text output. Assert the first whitespace-separated field is `"100755"`. Keep the filesystem test as well, because both views matter.
- **LF endings (G2).** Read `SCRIPT.read_bytes()`. Assert there is no `b"\r"` and that the content starts with `b"#!/bin/bash\n"`.
- **Byte-exact, repo-root invocation (G3).** Run `["./hello-world/hello.sh"]` with `cwd=REPO_ROOT` and no `text=True`. Assert `returncode == 0`, `stdout == b"hello world\n"` and `stderr == b""`. This is Scenario 1 exactly as written, and it also covers Scenario 3 because the script is run without `bash` in front.

Alternatives rejected:
- A verification-only item with no diff. The factory needs a change set per work item (`hld.md` §6).
- Rewriting the script. It adds risk and no value.
- A git-level folder-contents check. Scenario 2 is already covered at `:40-43`, and adding it is scope beyond the work item's criteria.

## Ordered implementation steps

1. **Re-verify the deliverable.**
   - Run `git ls-files -s hello-world`, and inspect `hello-world/hello.sh` byte by byte (for example with `od -c`).
   - Confirm mode `100755`, LF endings, and that the folder holds only `hello.sh`. Edit the script only if one of these fails; none fails today.
   - Advances: Scenarios 1–4.
   - Test layer: `package-api` (existing tests at `tests/test_hello_sh.py:10-43`).
2. **Add the git-mode test** to `TestHelloShStructure` in `tests/test_hello_sh.py`.
   - Assert that git's index mode for `hello-world/hello.sh` is `100755`.
   - Advances: Scenario 3 and the work item's `git ls-files -s` criterion.
   - Test layer: `package-api`.
3. **Add the LF and shebang byte test** to `TestHelloShStructure` in `tests/test_hello_sh.py`.
   - Assert the file contains no `\r` and its bytes start with `#!/bin/bash\n`.
   - Advances: Scenario 3 and the work item's LF criterion.
   - Test layer: `package-api`.
4. **Add the byte-exact test** to `TestHelloShExecution` in `tests/test_hello_sh.py`.
   - Run the script as `./hello-world/hello.sh` from `REPO_ROOT` in binary mode.
   - Assert exit `0`, stdout `b"hello world\n"` and stderr `b""`.
   - Advances: Scenarios 1, 3 and 4.
   - Test layer: `package-api`.
5. **Run the gate.** Run `pip install -e ".[test]"`, then `pytest`, from the repo root.
   - Make sure every existing test is untouched and the new ones pass.
   - Make sure `git status` shows only `tests/test_hello_sh.py` changed, plus `CHANGELOG.md` if the developer allows it.
   - Advances: all acceptance criteria.
   - Test layer: `package-api`.

Invariants:
- Authorization, tenancy and concurrency do not apply: this is a stateless script with no input.
- The error path: if `git ls-files` fails, the test must fail. Do not catch the error or skip the test.
- Dependencies come only from `pip install -e ".[test]"`. There are no new dependencies.
- There are no generated deliverables or binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–5 | `t1` — Confirm hello-world/hello.sh meets the spec and add a test that git stores it as executable |

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`), run once locally on the committed SHA in this order:
  1. `pip install -e ".[test]"`
  2. `pytest`
- **Required layer:** `package-api` (`pytest`). It can run in a pod. Its authoritative result is the CI `test` job at the exact head.
- **CI job `gate`:** green as long as there is no `CI_FAIL`.
- **Provider CI changes:** none needed.

The gate must show:
- every test in `tests/` passing, including all six existing tests in `tests/test_hello_sh.py` and the three new ones;
- no test skipped or marked `xfail`;
- a diff limited to `tests/test_hello_sh.py`, plus `CHANGELOG.md` only if the clarification allows it.

## Risks and scope guards

**Risks**
- **Repo-local gate blocker.** `mr-gate` raises blocker `PLAY-G4` because no CHANGELOG line is added. This is resolved by the clarification question, not by a silent choice.
- **Git not on the test runner's `PATH`.** This holds in CI and in the pod. If it ever doesn't, the test fails loudly, which is the intended behaviour.
- **Accidental edits to `hello.sh`.** An edit could drop mode `100755` or bring in CRLF. The new tests catch both.

**Do NOT**
- Add any file to `hello-world/`, or rewrite `hello.sh` when it already complies.
- Add a README or other documentation, or change `CHANGELOG.md`, unless the clarification allows the one line.
- Edit `.github/workflows/ci.yml`, `pyproject.toml` or `.factory/`, or create `CI_FAIL`.
- Delete, weaken, skip or `xfail` any existing test, including the filesystem executable check at `tests/test_hello_sh.py:36-38`.
- Clean up other scripts (`hello-world` vs `qa/*`) or other tests.

## Clarification outcomes

One question was raised and is awaiting the developer's answer. The repo-local `mr-gate` rule PLAY-G4 requires a `CHANGELOG.md` line under `## Unreleased`. The work item `t1` and `spec.md` FR5 forbid a CHANGELOG entry and documentation files. Until the developer answers, the plan follows the work item (assumption A-T3).
