# Implementation plan: PLAY-181, a script that prints "hello s3" and its automated test

## Context

PLAY-181 is the only story of the epic "QA-20261111-S3 hello s3 script" (Confluence epic PRD `pageId=36798465`). It adds two things to `roeeoz/play1`. The first is a standalone Python script, `src/qa_20261111_s3.py`, which prints exactly `hello s3\n`, writes nothing to stderr and exits with code 0. The second is a pytest test, `tests/test_qa_20261111_s3.py`, which checks that output and runs in the normal CI `pytest` step. The change also adds one `CHANGELOG.md` line under `## Unreleased`. The acceptance criteria in `spec.md` §5 cover:
- AC1: the script's output
- AC2: the test is collected and passes
- AC3: the test fails on wrong output
- AC4: no regressions, and the suite finishes in under 60 s
- AC5: the diff is exactly the two new files plus one CHANGELOG line
- AC6: required checks are green, and the PR is traceable to PLAY-181 and the epic PRD

The work lands on branch `halo/feat/play-181-20261111-200625`, which was cut from `main`, and the PR targets `main`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/PLAY-181/`.

## Research findings

- **Package layout.** setuptools `src/` layout: `pyproject.toml:26-27` (`[tool.setuptools.packages.find] where = ["src"]`). `src/` currently holds only the packages `testbed_utils/` and `guestbook/`, and no top-level modules. A top-level `src/qa_20261111_s3.py` is not a package, so `packages.find` does not ship it. It is not under `[project.scripts]` (`pyproject.toml:13-17`), so it is not an installed command.
- **Test collection.** `pyproject.toml:29-31` sets `testpaths = ["tests"]` and `addopts = "-q"`. Plain `pytest` from the repo root collects `tests/test_*.py`, so FR3 needs no config change. There is no `conftest.py` and no `sys.path` manipulation in `tests/` (`.factory/testing.md`).
- **Existing pattern for script tests.** `tests/test_qa_20261109_s1_a.py:35-44` resolves the script from `pathlib.Path(__file__).resolve().parent.parent` and runs it with `subprocess.run(..., capture_output=True, text=True, timeout=10, cwd=...)`. It then asserts the exit code, exact stdout and empty stderr (lines 47-60), including a run from `tmp_path`. `tests/test_qa_s3_greeting.py:4-19` follows the same pattern. Both call shell scripts directly. The new test instead puts `sys.executable` in front of the script path, so it needs no shebang and no executable bit.
- **Canonical gate.** `.github/workflows/ci.yml` has two jobs:
  - `test` runs `pip install -e ".[test]"`, then `pytest`, on Python 3.12.
  - `gate` fails only if a `CI_FAIL` file exists at the repo root.

  `.factory/testing.md` declares one required layer, `package-api` (`pytest`, `runBy: canonical-gate`), and states that the repo has no linter, formatter or type checker.
- **Merge gate (`mr-gate` slot).** The play1 layout gate is defined in `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-20`:
  - Rule 1: Python source lives under `src/` and tests under `tests/`.
  - Rule 2: a new shell script must be executable and start with a shebang. This change adds none.
  - Rule 3: every file must be 200 KB or less.
  - Rule 4 (`PLAY-G4`): the PR must add a line under `## Unreleased` in `CHANGELOG.md`.
- **CHANGELOG.** `CHANGELOG.md:3` holds `## Unreleased`. The last entry is `CHANGELOG.md:8`, the PLAY-175 line. Entries follow the format ``- PLAY-<n>: add `<path>`, <description>.``
- **Previous epic with the same name (RK2).** Its files live in `qa/20261110-s3/`. They and the PLAY-175 CHANGELOG line stay untouched.
- **External data.** None. The script has no inputs, and the test uses no network, clock or files outside the repo.
- **Exists vs. new.** Both files are new. `CHANGELOG.md` is the only existing file that changes, and only by one added line.
- **Unknowns left after research.** None.

## Locked decisions and assumptions

**Locked decisions**
- Paths are `src/qa_20261111_s3.py` and `tests/test_qa_20261111_s3.py`, plus one CHANGELOG line. The developer agreed to replace the epic's `qa/` paths (source: `spec.md` §1, §2; `hld.md` §2).
- The script is a standalone module. It is not a package, has no `[project.scripts]` entry, no `--help` and no public function (source: `spec.md` §6, §7; `hld.md` §6).
- Output contract: stdout is exactly `hello s3\n`, stderr is empty and the exit code is 0 (source: `spec.md` FR1; `hld.md` §5).
- The test runs the script as a child process with the current interpreter and does not import it (source: `hld.md` §6).
- The print sits behind a guard so that it runs only when the file is executed directly (source: `hld.md` §6; work item t1 AC).
- Do not change `pyproject.toml`, `.github/workflows/ci.yml`, `qa/`, any existing test or any existing CHANGELOG line (source: `spec.md` §2; work item t1 "Must not modify").
- Syntax must run on CPython 3.10 and later, and no dependency may be added (source: Engineering requirements R1 and R2, cited in `spec.md` §6).

**Assumptions**
- *Running the script with `sys.executable` matches what CI's `python` does.* Evidence: CI installs and runs pytest with the same interpreter. If wrong, the test would still exercise the same file with a valid 3.x interpreter, so nothing breaks.
- *`stories/PLAY-181/` is excluded from the AC5 file count.* Evidence: `spec.md` AC5 says this explicitly. Layout gate rule 1 concerns Python source, and `stories/` holds only Markdown. If wrong, the gate would flag pipeline artifacts that every previous story also carried, such as `stories/PLAY-175/`.
- *Proof of AC3 is a manual, uncommitted check.* Evidence: the work-item AC says "Confirm this by hand before opening the PR". The committed test asserts exact equality, so any other output fails it. If a committed negative test were required instead, it would need a fixture script, which AC5 forbids.

## Solution proposal

Add one stdlib-only top-level module and one subprocess-based test. Neither touches the installed package.

- **Script `src/qa_20261111_s3.py` (new).** It has a one-line module docstring that names PLAY-181. Its single `print("hello s3")` sits under `if __name__ == "__main__":`. There are no imports, no functions and no argument parsing. Exit code 0 comes from normal termination. The guard keeps the module silent if it is ever imported, for example through an editable-install path hook.
- **Test `tests/test_qa_20261111_s3.py` (new).** It follows the structure of `tests/test_qa_20261109_s1_a.py`:
  - Define `REPO_ROOT` from `pathlib.Path(__file__).resolve().parent.parent` and `SCRIPT = REPO_ROOT / "src" / "qa_20261111_s3.py"`.
  - Add a helper that calls `subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, timeout=10, cwd=...)`.
  - Add a normal-run test class that runs from `REPO_ROOT`.
  - Add a run-from-another-directory class that runs from `tmp_path`.
  - In each test, assert `returncode == 0`, `stdout == "hello s3\n"` and `stderr == ""`.

  Exact equality on stdout catches the AC3 cases: `hello s4`, an extra line and a missing newline.
- **CHANGELOG.** Add one line after `CHANGELOG.md:8`, in the existing style:

  ``- PLAY-181: add `src/qa_20261111_s3.py`, a QA script that prints `hello s3`, and its test `tests/test_qa_20261111_s3.py`.``

**Alternatives rejected**
- *Import the module and capture stdout in-process* (the `tests/test_hello_cli.py` style). It cannot observe the exit code of a real run, and the module is not reliably importable because it is not part of the installed distribution.
- *Invoke the script directly through a shebang and the executable bit.* That adds a file-mode dependency for no benefit. `sys.executable` is deterministic.
- *Keep the epic's `qa/` paths.* They break layout gate rule 1, and the test would not run in CI. The developer already settled this (`spec.md` §1).
- *Add a `main()` function.* It would create a public function and widen scope against `spec.md` §6.

## Ordered implementation steps

1. **Create `src/qa_20261111_s3.py`.** Give it a module docstring and a guarded `print("hello s3")`. Use no imports and only 3.10-compatible syntax. Advances AC1. Covered by the `package-api` layer through step 2's test.
2. **Create `tests/test_qa_20261111_s3.py`.** Build it as a subprocess test with `sys.executable` and `timeout=10`, finding the script relative to `__file__`. It has two cases, one with `cwd=REPO_ROOT` and one with `cwd=tmp_path`, and each asserts exit code 0, exact stdout `hello s3\n` and empty stderr. It must use no network, clock or external files. Advances AC1, AC2 and AC3, and the determinism part of AC4. Layer: `package-api` (`pytest`).
3. **Check AC3 by hand, then discard the change.** In the working tree, temporarily make three edits, one at a time:
   - change the printed text to `hello s4`
   - add a second `print`
   - use `print("hello s3", end="")`

   For each edit, run `pytest tests/test_qa_20261111_s3.py` and confirm that it fails. Then restore the file with `git checkout -- src/qa_20261111_s3.py` and confirm that it passes again. Record the result for the PR description. Advances AC3. Layer: `package-api`, manual negative run, never committed.
4. **Append the PLAY-181 line under `## Unreleased` in `CHANGELOG.md`.** Place it after the PLAY-175 line, in the same format, and leave every existing line unchanged. Advances AC5 and AC6 (layout gate rule 4). There is no test layer, because the layout gate (`mr-gate`) checks this.
5. **Check scope.** Run `git diff --stat main...HEAD -- . ':!stories/PLAY-181'` and confirm that it shows exactly the two new files and `CHANGELOG.md` with `+1` and no deletions. Confirm that no `CI_FAIL` file exists, that no file exceeds 200 KB and that `pyproject.toml` is unchanged. Advances AC5. There is no test layer; this is a diff inspection.
6. **Write the PR description.** It must:
   - cite PLAY-181 and the epic PRD "QA-20261111-S3 hello s3 script" (`pageId=36798465`)
   - report the result of the new test and of the step 3 negative checks
   - explain the agreed move from the epic's `qa/` paths to `src/` and `tests/`, plus the CHANGELOG line

   Advances AC6. There is no test layer; a human reviews it.

Implicit invariants:
- Authorization, tenancy and concurrency do not apply: there is a single synchronous process and no state.
- Validation and error paths reduce to the wrong-output case (AC3).
- Dependencies come from `pip install -e ".[test]"`, which pulls in `pytest>=8` from the existing `test` extra. Nothing new is fetched.
- There are no generated deliverables and no binaries.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–6 | t1: Add the src/qa_20261111_s3.py script that prints "hello s3", its pytest output test and a PLAY-181 CHANGELOG line |

`work-items.md` lists only t1, and every step belongs to it.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`): run `pip install -e ".[test]"`, then `pytest` from the repo root, once locally on the committed SHA. It runs unprivileged in a pod. The provider run at the exact head is the authoritative result for layer `package-api`.
- **What the gate must show:**
  - `tests/test_qa_20261111_s3.py` is collected and both of its cases pass, in under 1 s.
  - Every previously passing test still passes.
  - The whole `pytest` run takes under 60 s.
  - There are no skips, xfails or deselections added by this change.
- **Provider CI:**
  - The `test` and `gate` jobs are green. `gate` stays green as long as no `CI_FAIL` file is added.
  - The play1 layout gate (`mr-gate`) passes rules 1–4.
  - No CI configuration change is needed.
- **AC3 evidence:** the manual negative runs from step 3, reported in the PR. They are not part of the committed gate.
- **`.factory/delivery-assets`:** not applicable, because no binary is added.

## Risks and scope guards

**Risks**
- *The epic PRD and backlog still name `qa/` paths and "exactly two files".* Reviewers may read the diff as out of scope. Mitigation: the PR description explains the agreed change (step 6).
- *The test hangs in CI.* Mitigation: `timeout=10` on `subprocess.run`, and the CI job's `timeout-minutes: 5`.
- *Results depend on the working directory.* Mitigation: the script path is resolved from `__file__`, and the `tmp_path` case proves this.

**Scope guards.** The implement phase must NOT:
- modify `pyproject.toml` (`testpaths`, `[project.scripts]`, dependencies), `.github/workflows/ci.yml` or `.factory/`
- touch anything under `qa/`, including `qa/20261110-s3/*`, or any existing test in `tests/`
- edit or reorder any existing `CHANGELOG.md` line, including the PLAY-175 line
- add a package, an `__init__.py`, a `main()` or other public function, `--help`, argument parsing or a console-script entry
- add a dependency, a shell script, a fixture script for the negative case or a `CI_FAIL` file
- edit `stories/PLAY-181/spec.md`, `hld.md` or `work-items.md`
- make any required check green by deleting, skipping, disabling or weakening it; a failing check is reported as blocked

## Clarification outcomes

None.
