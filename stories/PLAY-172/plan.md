# Plan — PLAY-172: `qa/20261109-s1/a.sh` prints "A"

## Context

PLAY-172 adds the first script of epic QA-20261109-S1: a new POSIX shell script, `qa/20261109-s1/a.sh`. It prints exactly `A\n` and exits 0 from any working directory. New pytest coverage and one `CHANGELOG.md` line ship with it. Acceptance criteria in brief: AC1 is the exact output and exit 0. AC2 is the same result from another working directory. AC3 is that the existing scripts are unchanged and no existing file changes except one `## Unreleased` line. AC4 is that CI is green in under 60 s with no network or clock. The change lands in `roeeoz/play1` on the work branch `halo/feat/play-172-20261109-124602`, which merges into `main`. The approved requirement (`spec.md`), the design (`hld.md`) and the breakdown (`work-items.md`, one work item `t1`) are next to this file in `stories/PLAY-172/`. PLAY-173 (`b.sh`) consumes this script's path and output contract.

## Research findings

- **Existing `qa/` scripts:** `qa/s3-a.sh:1-3` (`#!/bin/sh`, a comment line, `printf 'A\n'`) and `qa/s3-hello.sh:1-3` (same shape, prints `hello`). Both are git mode `100755`, as is `hello-world/hello.sh` (`#!/bin/bash`, `echo "hello world"`). `qa/20261109-s1/` does not exist yet and must be created.
- **Test convention:** `tests/test_qa_s3_greeting.py:4` resolves the script from `pathlib.Path(__file__).resolve().parent.parent / "qa" / ...`. It runs the script through `subprocess.run([...], capture_output=True, text=True, timeout=10)` (`:137-141`) and asserts exit code, stdout and stderr (`:145-149`). It checks the file's shape: it starts with `b"#!/bin/sh\n"`, line 2 starts with `#`, and the file has no `\r` (`:153-159`). `tests/test_hello_sh.py` covers `hello-world/hello.sh` and imports `stat` for an executable-bit check.
- **No test covers `qa/s3-a.sh` today.** It is only listed in `CHANGELOG.md:6`.
- **Test discovery:** `pyproject.toml:27-29` has `[tool.pytest.ini_options]` with `testpaths = ["tests"]` and `addopts = "-q"`, so a new `tests/test_*.py` file is collected without any config change. The suite has no `conftest.py`.
- **Canonical gate** (`.factory/testing.md:3-10`, `.github/workflows/ci.yml:10-23`): `pip install -e ".[test]"`, then `pytest` on Python 3.12, with a job timeout of 5 minutes. The one declared layer is `package-api` (`pytest`, `runBy: canonical-gate`). There is no linter, formatter or type checker. The `gate` job (`ci.yml:25-37`) fails only if `CI_FAIL` exists at the repo root.
- **PR layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): rule 1 puts tests under `tests/`. Rule 2 requires a new shell script to be executable and to start with a shebang. Rule 3 caps files at 200 KB. Rule 4 requires a new line under `## Unreleased` in `CHANGELOG.md`, and missing it is blocker `PLAY-G4`.
- **Changelog shape:** `CHANGELOG.md:3-6`. `## Unreleased` is followed by entries like `- PLAY-156: add \`qa/s3-a.sh\`, a helper script that prints \`A\`.`
- **Contract to PLAY-173** (`hld.md` §5): the path is `qa/20261109-s1/a.sh`, the file is executable with a shebang on line 1, stdout is exactly `A\n`, stderr is empty, exit is 0, and the script does not depend on its own location or any sibling file.
- **External data:** none. **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**
- The path is `qa/20261109-s1/a.sh`. The output is exactly one line `A`, with exit 0 (spec FR1/FR3, PRD R1).
- Output is the same from any working directory (spec FR2, PRD R4).
- The script takes no input and reads no files, network, clock or environment variables (spec FR4).
- The interpreter is `#!/bin/sh` and the script prints with `printf 'A\n'`, matching `qa/s3-a.sh` (`hld.md` §6).
- Tests go in the new file `tests/test_qa_20261109_s1_a.py` and use pytest + `subprocess` with `timeout=10` (`hld.md` §4, §6).
- The regression check for `qa/s3-a.sh` goes in the new test file, and the script itself is not modified (`hld.md` §6, spec §7).
- `CHANGELOG.md` gets exactly one new line under `## Unreleased` naming PLAY-172. It is the only edit to an existing file (spec FR6, repo-gate rule 4).
- No `--help`, no `b.sh`, no new dependencies, and no changes to `ci.yml` or `pyproject.toml` (spec Non-Goals, work item t1).
- The file is committed as git mode `100755`, with LF line endings (repo-gate rule 2, `hld.md` §7).

**Assumptions**
- The CI runner (`ubuntu-latest`) has `/bin/sh`. Evidence: `qa/s3-hello.sh` already runs under it in `tests/test_qa_s3_greeting.py`. If wrong, the existing tests would fail too.
- A comment on line 2 is acceptable and keeps the folder's convention. Evidence: both `qa/s3-*.sh` files have one. If wrong, it only affects style; output is unchanged.
- For AC3, "existing scripts print what they print today" means `qa/s3-a.sh` → `A\n` (`qa/s3-a.sh:3`), `qa/s3-hello.sh` → `hello\n` and `hello-world/hello.sh` → `hello world\n`. The last two are already pinned by the existing tests. If wrong, the regression coverage would miss a different expected output.

## Solution proposal

Add a three-line POSIX script that mirrors `qa/s3-a.sh`: shebang `#!/bin/sh`, a one-line comment that it prints `A` for epic QA-20261109-S1 and is called by `qa/20261109-s1/b.sh`, and `printf 'A\n'`. The script uses no `$0`/`dirname` and no reference to a sibling file, so it is independent of the working directory and can be copied alone, which PLAY-173's error-path tests rely on. Commit it with the executable bit.

Add one pytest module, `tests/test_qa_20261109_s1_a.py`, using the pattern in `tests/test_qa_s3_greeting.py`: a module-level `REPO_ROOT`/`SCRIPT` resolved from `__file__`, and a `run_script(cwd=None)` helper that calls `subprocess.run([str(SCRIPT)], capture_output=True, text=True, timeout=10, cwd=cwd)`. The module has these test classes:
- **normal run:** stdout `== "A\n"`, stderr `== ""`, exit `0` (AC1).
- **another directory:** `cwd=tmp_path`, same three assertions (AC2).
- **shape:** content starts with `b"#!/bin/sh\n"`, `os.stat(...).st_mode & stat.S_IXUSR` is set, and `b"\r"` is not in the bytes (repo-gate rule 2, `hld.md` §7).
- **regression:** `qa/s3-a.sh` prints exactly `A\n` with exit 0 (AC3). The existing `qa/s3-hello.sh` and `hello-world/hello.sh` tests stay as they are and cover the rest of AC3.

Add one `CHANGELOG.md` line in the existing style.

**Alternatives rejected:**
- A `#!/bin/bash` script: it adds nothing, and the folder convention is `sh` (`hld.md` §6).
- Extending `tests/test_qa_s3_greeting.py` with the new checks: that modifies an existing file, which R6 forbids.
- A shell-based test harness such as bats: it would be a new layer and a new dependency.
- A git-mode assertion via `git ls-files`: CI checkouts keep the mode, so the filesystem `stat` check is enough and needs no git subprocess.

## Ordered implementation steps

1. **Create `qa/20261109-s1/a.sh`** (new) with the shebang, a comment and `printf 'A\n'`. Use LF endings and a trailing newline. Run `chmod +x` and confirm `git ls-files -s qa/20261109-s1/a.sh` shows `100755` once it is staged by the build. Advances AC1 and AC2. Covered by the `package-api` (`pytest`) layer through step 2.
2. **Create `tests/test_qa_20261109_s1_a.py`** (new) with the four test groups from the Solution proposal: normal run, run from `tmp_path`, file shape (shebang, executable bit, no CR), and the `qa/s3-a.sh` regression. Every `subprocess.run` gets `timeout=10`. Use no network, clock, environment variables or `sleep`. Advances AC1, AC2 and AC3, plus the AC4 determinism requirement. Test layer: `package-api` (`pytest`).
3. **Append one line under `## Unreleased` in `CHANGELOG.md`**, after `CHANGELOG.md:6`: `- PLAY-172: add \`qa/20261109-s1/a.sh\`, a QA script that prints \`A\`.` Change nothing else. Advances AC3 (the one allowed edit) and repo-gate rule 4. No test layer applies; the repo-gate PR check verifies it.
4. **Run the gate locally:** `pip install -e ".[test]"`, then `pytest` from the repo root. Confirm all tests pass and the run takes seconds. Then check `git diff --stat main` (against the target branch `main`). It should list only `qa/20261109-s1/a.sh`, `tests/test_qa_20261109_s1_a.py`, `CHANGELOG.md` (+1 line) and the `stories/PLAY-172/` plan files. Advances AC3 and AC4. Test layer: `package-api`.

Implicit invariants: there are no authz, tenancy, concurrency or idempotency concerns, because the script has no input and no state. The only error-path concern is stray output on stderr or stdout, which the exact-match assertions catch. Dependencies come only from `pip install -e ".[test]"` (pytest), and nothing new is added. There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add qa/20261109-s1/a.sh that prints "A", with pytest coverage and a CHANGELOG entry |
| 2 | t1 | Add qa/20261109-s1/a.sh that prints "A", with pytest coverage and a CHANGELOG entry |
| 3 | t1 | Add qa/20261109-s1/a.sh that prints "A", with pytest coverage and a CHANGELOG entry |
| 4 | t1 | Add qa/20261109-s1/a.sh that prints "A", with pytest coverage and a CHANGELOG entry |

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`): `pip install -e ".[test]"`, then `pytest`, from the repo root on the committed SHA. Run it once; the Stop hook and the provider CI `test` job run it again. It runs unprivileged in a pod.
- **Required layer:** `package-api` (`pytest`, `runBy: canonical-gate`). The provider run at the exact head is authoritative.
- **No change to provider CI:** `.github/workflows/ci.yml` already runs `pytest` on every `pull_request`. The `gate` job stays green because no `CI_FAIL` file is created.
- **Done means** all of these hold:
  - every existing test and every test in `tests/test_qa_20261109_s1_a.py` passes
  - the `test` job finishes well under 60 s
  - `qa/20261109-s1/a.sh` is mode `100755`
  - the diff touches no existing file except the single added `CHANGELOG.md` line, which satisfies repo-gate rules 1–4
- **PR description:** references PLAY-172 and the epic PRD.

## Risks and scope guards

**Risks and mitigations**
- **Executable bit lost (mode `100644`):** direct execution fails, which breaks repo-gate rule 2 and PLAY-173. Mitigation: `chmod +x`, the `S_IXUSR` assertion and a `git ls-files -s` check.
- **CRLF endings or stray output** break the shebang or PLAY-173's contract. Mitigation: the no-`\r` assertion and exact stdout/stderr matches.
- **Merge order (RK1):** PLAY-173's PR opens only after this one merges to `main`. That is outside this story's control, so it is noted here and not acted on.

**Scope guards — the implement phase must NOT:**
- modify, rename, delete or call into `qa/s3-a.sh`, `qa/s3-hello.sh`, `hello-world/hello.sh` or any existing test file
- create `qa/s3-b.sh` or `qa/20261109-s1/b.sh`
- add `--help` handling, arguments or environment-variable handling to the script
- touch `.github/workflows/ci.yml`, `pyproject.toml`, `.factory/` or `README.md`
- add a dependency, a `conftest.py` or a new test framework
- edit any `CHANGELOG.md` line other than adding the one new entry
- edit `spec.md`, `hld.md` or `work-items.md`
- delete, skip, xfail or weaken any check to get green; a failing check is reported, not bypassed

## Clarification outcomes

None.
