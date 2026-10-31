# Implementation plan — hello-world bash script (story 46d9546d)

## Context

Add a new top-level folder `hello-world/` to the play1 repository (branch `halo/feat/46d9546d`). The folder holds one directly executable bash script, `hello.sh`. It prints exactly `hello world\n` and exits 0. The acceptance criteria are: exact output with exit 0 (AC1); the folder holds only `hello.sh` (AC2); the script runs through its `#!/bin/bash` shebang with the executable bit kept in a fresh clone (AC3); the output is byte-exact (AC4); and nothing else in the repo changes (AC5). The requirement is in `spec.md`, the design in `hld.md`, and the breakdown (one work item, `t1`) in `work-items.md`. All three sit beside this file in `docs/plans/46d9546d/`.

## Research findings

- **No shell scripts exist today.** `git ls-files` lists no `*.sh` file and no `hello-world/` folder, so both deliverables are new.
- **Existing Python hello feature (must stay unchanged):**
  - `src/testbed_utils/hello.py` holds the feature.
  - `pyproject.toml:20` declares the console script `testbed-hello = "testbed_utils.hello:main"`.
  - `tests/test_hello.py` and `tests/test_hello_cli.py:9` assert `GREETING = "Hello, world!\n"`. That text differs from the new script's output.
- **Test configuration:**
  - `pyproject.toml:28-30` sets `[tool.pytest.ini_options]`, `testpaths = ["tests"]` and `addopts = "-q"`.
  - The test extra is `test = ["pytest>=8"]` (`pyproject.toml:23`).
  - The suite has no `conftest.py`.
  - No test runs a subprocess today. The closest idiom is `pathlib.Path(__file__).parent / "fixtures"` (`tests/test_num_summary_cli.py:11`) plus pytest's `tmp_path` (`tests/test_guestbook_api.py:16`).
  - Test style is one `Test<Unit>` class per unit with one behaviour per test (`tests/test_hello_cli.py:25-51`).
- **Canonical gate:**
  - `.factory/testing.md` names one required layer, `package-api`. Its command is `pytest`, with `runBy: canonical-gate`.
  - Its precondition is `pip install -e ".[test]"`.
  - CI runs both in the `test` job of `.github/workflows/ci.yml:12-24` on `ubuntu-latest` with Python 3.12. That runner has `/bin/bash`.
  - The `gate` job (`ci.yml:26-36`) fails only if `CI_FAIL` exists at the root. It is not a quality layer.
  - No linter, formatter or type checker is configured.
- **Repo layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):**
  - Rule 1: tests live under `tests/`.
  - Rule 2: a new shell script is executable and starts with a shebang.
  - Rule 3: no file in the diff is over 200 KB.
  - Rule 4: the PR must add a line under `## Unreleased` in `CHANGELOG.md`, otherwise it gets blocker `PLAY-G4`.
  - `CHANGELOG.md` does not exist today.
  - Rule 4 conflicts with spec AC5. `hld.md` §6 leaves this conflict open (P0).
- **Harel layout:** the Harel pytest convention (`test/` plus `requirements.txt`) does not apply here. The repo has no `Jenkinsfile-TestOnMergeRequest` or `config_ci.yaml`, and it keeps its tests in `tests/`, so the repo's own layout governs.
- **`.gitignore`:** it does not ignore `*.sh` or anything under `hello-world/`, so the script is tracked as normal.
- **No `.factory/memory/`, `AGENTS.md` or `CLAUDE.md`** exists in the repo.
- **Remaining unknown:** the `PLAY-G4` conflict. It has been raised as a clarifying question; see below.

## Locked decisions and assumptions

**Locked decisions**
- Folder `hello-world/` at the repo root holds only `hello.sh` (spec FR1, FR2, AC2).
- The first line is exactly `#!/bin/bash` (spec FR3).
- Git mode is `100755` (spec FR4, AC3; `hld.md` §5–6).
- Stdout is exactly the bytes `hello world\n`, stderr is empty, and the exit code is 0, independent of the working directory (spec FR5, FR6, AC1, AC4; `hld.md` §5).
- No `.gitattributes` is added (`hld.md` §6).
- The automated check is included as `tests/test_hello_sh.py`, outside `hello-world/` (spec A3; `hld.md` §6; work item `t1`).
- No edits to `src/`, `tests/test_hello.py`, `tests/test_hello_cli.py`, `pyproject.toml`, `.github/`, `README.md` or `.gitignore` (spec AC5; work item `t1` "Must not touch").
- The gate is `pip install -e ".[test]"` then `pytest` (`.factory/testing.md`).

**Assumptions**
- **A-1: the spec wins over repo-gate rule 4, so no `CHANGELOG.md` is created.**
  - Evidence: the default in `hld.md` §6, and spec AC5 ("no documentation file is added").
  - If wrong, step 4 below runs, and AC5 is amended by the owner.
  - Under this assumption the PR carries a `PLAY-G4` blocker that a human must waive.
- **A-2: the test runs only on POSIX runners.**
  - Evidence: CI uses `ubuntu-latest`, and the spec fixes `/bin/bash`.
  - If wrong (a Windows runner), the exec-bit and direct-exec assertions would fail. No such runner exists.
- **A-3: the file is created with plain shell or editor tools that keep the file mode, never through an API that drops it.**
  - Evidence: risk noted in `hld.md` §7.
  - If wrong, the mode in the index is `100644` and AC3 fails. Step 2's index check and the test's executable assertion catch it.

## Solution proposal

- **The script.** Add one two-line file, `hello-world/hello.sh`:
  - line 1: the `#!/bin/bash` shebang;
  - line 2: a single `echo "hello world"`, or an equivalent `printf 'hello world\n'`.
- **Why it is deterministic.** The script reads no arguments, environment, locale or working directory, so its output is the same on every run.
- **File format.** Write it as ASCII with LF endings, no BOM and no trailing whitespace.
- **Executable bit.** Set it in the working tree (`chmod +x`) before staging, then confirm `100755` with `git ls-files -s`. If the mode was lost, `git update-index --chmod=+x` is the fallback.
- **The test file, `tests/test_hello_sh.py`.** It sits in the existing `package-api` pytest layer and needs no CI or config change.
  - It finds the script by absolute path: `Path(__file__).resolve().parent.parent / "hello-world" / "hello.sh"`.
  - It runs the script directly with `subprocess.run([str(script)], capture_output=True, cwd=...)`. It never prefixes `bash`, so the shebang and exec bit are exercised.
  - It compares raw bytes, so a CR, BOM or extra line fails.
- **What the tests assert, grouped in a `TestHelloScript` class (one behaviour per test):**
  - stdout is exactly `b"hello world\n"`, stderr is empty and the return code is 0, with the repo root as cwd;
  - the same result with `tmp_path` as cwd, plus a repeat run giving identical output;
  - the first line of the file is exactly `#!/bin/bash`;
  - `os.access(script, os.X_OK)` is true;
  - `sorted(os.listdir(folder)) == ["hello.sh"]`, which counts hidden files;
  - the file bytes contain no `b"\r"`, do not start with a BOM, and have no line ending in a space or tab.
- **Alternatives rejected:**
  - Adding `.gitattributes` with `*.sh eol=lf`: it is a new root file, which breaks AC5 (`hld.md` §6).
  - Calling `bash hello.sh` in the test: it would not prove direct execution (AC3).
  - A bats or shellcheck layer: it would be a new test framework that the repo does not have.

## Ordered implementation steps

1. **Create the script.** Create `hello-world/hello.sh` (new) with the shebang line and the single output line. Use LF endings, ASCII only and no trailing whitespace.
   - Advances AC1, AC3 (shebang) and AC4.
   - Covered by `package-api` (pytest), through step 3.
2. **Set and check the executable bit.** Run `chmod +x hello-world/hello.sh` before staging. After staging, confirm `git ls-files -s hello-world/hello.sh` reports `100755`. Confirm `ls -A hello-world` lists only `hello.sh`, with no `.DS_Store` or editor swap files.
   - Advances AC2 and AC3.
   - Covered by `package-api` (the executable and folder-listing tests). The index mode itself is checked by the `git ls-files -s` command; no repo test layer reads git modes.
3. **Add the acceptance test.** Add `tests/test_hello_sh.py` (new) with the `TestHelloScript` tests described in the solution proposal. Use only the standard library (`os`, `pathlib`, `subprocess`) plus pytest's `tmp_path`. Import nothing from `src/` and add no dependency.
   - Advances AC1–AC4.
   - Layer: `package-api` (pytest).
4. **Only if the developer answers that the repo gate wins (otherwise skip):** create `CHANGELOG.md` (new) with a `## Unreleased` heading and one bullet describing `hello-world/hello.sh`.
   - Satisfies repo-gate rule 4; AC5 is amended accordingly.
   - No test layer covers it: it is a review-gate artefact.
5. **Run the gate and check the diff.** Run `pip install -e ".[test]"` then `pytest` once. Confirm that `git diff --stat` against the base adds only `hello-world/hello.sh` and `tests/test_hello_sh.py` (plus `CHANGELOG.md` under step 4) and modifies nothing.
   - Advances AC5.
   - Layer: `package-api`, plus the diff check.

Implicit invariants:
- Authorization, tenancy and concurrency do not apply: there is no input, no state and no network.
- The only error path is "script missing or not executable". The test reports it as a failure, never a skip.
- No new dependencies are needed: the test uses only the standard library and the already-declared `pytest>=8`.
- There are no generated deliverables, and no binary assets that would need declaring in `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add hello-world/hello.sh executable bash script with subprocess acceptance test |
| 2 | t1 | Add hello-world/hello.sh executable bash script with subprocess acceptance test |
| 3 | t1 | Add hello-world/hello.sh executable bash script with subprocess acceptance test |
| 4 (conditional) | t1 | Add hello-world/hello.sh executable bash script with subprocess acceptance test |
| 5 | t1 | Add hello-world/hello.sh executable bash script with subprocess acceptance test |

## Verification and CI gate

- **Gate command:** `pip install -e ".[test]"` then `pytest`, from the repo root, run once locally on the committed SHA. This follows `.factory/testing.md` and `.github/workflows/ci.yml:20-24`.
- **Authority:** the provider run of the CI `test` job at the exact head is authoritative for the `package-api` layer.
- **Pod:** the `package-api` layer can run in a pod, but `/bin/bash` must be present there.
- **What the gate must show:**
  - the new `tests/test_hello_sh.py` tests pass;
  - every existing test passes unchanged, including `tests/test_hello.py` and `tests/test_hello_cli.py`;
  - no test is skipped.
- **Outside pytest:**
  - `git ls-files -s hello-world/hello.sh` reports `100755`;
  - the diff contains only the files listed in step 5;
  - the CI `gate` job stays green (no `CI_FAIL` added).
- **CI and test-layer files:**
  - No CI configuration change is needed or allowed.
  - `.factory/testing.md` needs no update: the new test sits in the existing `package-api` layer.
  - `.factory/delivery-assets` does not apply.
- **Repo gate:** the review stage will run the layout gate (`repo-gate`). Under assumption A-1, expect blocker `PLAY-G4` and surface it to a human for a waiver. Never work around it by changing the gate.

## Risks and scope guards

**Risks and mitigations**
- **Executable bit lost when writing the file:** caught by the `git ls-files -s` check in step 2 and the `os.X_OK` test.
- **CRLF, a BOM or trailing whitespace:** caught by the byte-exact stdout assertion and the file-content test.
- **Stray files in `hello-world/` (`.DS_Store`, swap files):** caught by the exact folder-listing test.
- **Repo-gate `PLAY-G4` blocker:** pending the clarifying question. The default leaves it to a human waiver.
- **Portability (no `/bin/bash`):** out of scope by spec. The CI runner has it.

**The implement phase must NOT:**
- edit `src/` (including `src/testbed_utils/hello.py` and the `testbed-hello` command);
- edit `tests/test_hello.py`, `tests/test_hello_cli.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `README.md`, `.gitignore` or `.factory/`;
- add `.gitattributes`, a `conftest.py`, `requirements.txt`, a `test/` directory or any other script;
- add a file inside `hello-world/` other than `hello.sh`;
- create `CHANGELOG.md` unless the developer's answer selects step 4;
- add a new test framework (bats, shellcheck);
- skip, mark xfail or loosen any assertion. If a check fails, fix the cause or report it blocked; never weaken it.

## Clarification outcomes

One question has been raised through the platform's plan conversation. It asks whether repo-gate rule 4 (`PLAY-G4`, which requires a `CHANGELOG.md` entry under `## Unreleased`) or spec AC5 (no added documentation file) wins. No answer has come back yet. Until it does, the plan follows assumption A-1: AC5 wins, step 4 is skipped, and `PLAY-G4` goes to a human for a waiver.
