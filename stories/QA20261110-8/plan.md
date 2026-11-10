# Implementation plan — QA20261110-8: `qa/20261110-a3/hello.py` prints "hello from a3"

## Context

Epic a3 adds one standalone QA script to `roeeoz/play1`: `qa/20261110-a3/hello.py`. Run as `python qa/20261110-a3/hello.py` from the repo root, it writes exactly `hello from a3\n` to stdout and nothing to stderr, then exits 0. It needs only Python 3.10 or later and installs nothing. Nothing else in the repository changes. That covers spec AC1–AC5. The work lands on the work branch `halo/feat/qa20261110-8-20261110-195025`, which was cut from `main`; the PR targets `main`. The approved requirement is `spec.md`, the design is `hld.md` and the single work item `t1` is in `work-items.md`. All three sit beside this file in `stories/QA20261110-8/`.

## Research findings

- **The `qa/` directory today** (`git ls-files -s qa`) holds five shell scripts, all mode `100755`, all ASCII with LF endings:
  - `qa/s3-hello.sh`
  - `qa/s3-a.sh`
  - `qa/20261109-s1/a.sh`
  - `qa/20261110-s3/hello.sh`
  - `qa/20261110-s3/test_hello.sh`
- **The convention in those scripts:**
  - line 1 is a shebang (`#!/bin/sh`)
  - line 2 is a one-line `#` comment saying what the script prints and which epic or ticket it belongs to (e.g. `qa/20261110-s3/hello.sh:2`)
  - line 3 is the single output statement
- **The new file is the first `.py` under `qa/`, and `qa/20261110-a3/` doesn't exist yet.** Both must be created.
- **The package is unaffected.**
  - `pyproject.toml` has `[tool.setuptools.packages.find] where = ["src"]`, so `qa/` is outside the package.
  - It has `[tool.pytest.ini_options] testpaths = ["tests"]`, so pytest never collects `qa/`.
  - `requires-python = ">=3.10"`.
  - `[project.scripts]` lists `pdf-extract`, `testbed-num-summary`, `testbed-hello` and `guestbook`. It isn't touched.
- **Existing regression coverage of `qa/` scripts:**
  - `tests/test_qa_s3_greeting.py:4` pins `qa/s3-hello.sh`.
  - `tests/test_qa_20261109_s1_a.py:7-8` pins `qa/20261109-s1/a.sh` and `qa/s3-a.sh`.
  - `qa/20261110-s3/test_hello.sh` checks `qa/20261110-s3/hello.sh` (`hello s3`).
  - No test lists the contents of `qa/`. The only `iterdir` is `tests/test_hello_sh.py:42`, and it scans `hello-world/`. Adding a new directory under `qa/` therefore can't break an existing test.
- **The canonical gate** is declared in `.factory/testing.md`:
  - `pip install -e ".[test]"` and then `pytest`, the `test` job in `.github/workflows/ci.yml`, on Python 3.12
  - one required layer, `package-api` (`runBy: canonical-gate`)
  - the `gate` job fails only if `CI_FAIL` exists at the repo root
  - no linter, formatter, type checker or coverage tool exists
- **The repo-gate review skill** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):
  - Rule 4 (`PLAY-G4`) blocks any PR that doesn't touch `CHANGELOG.md`.
  - Rule 1 says "Python source lives under `src/`".
  - Both conflict with the spec's no-other-file scope. `hld.md` §6–7 already resolves this: don't comply, state the deviation in the PR and let the human reviewer waive it.
- **Interpreters:**
  - The local interpreter is Python 3.11.2 and CI uses 3.12.
  - No 3.10 interpreter is in the pod, so AC2 rests on reading the code for syntax and built-ins available in 3.10.
- **External data:** none.
- **Remaining unknowns:** none that block.

## Locked decisions and assumptions

**Locked decisions**
- The path is `qa/20261110-a3/hello.py`, and its output is exactly `hello from a3\n` with empty stderr and exit 0. Source: spec FR2, FR3, AC1 and `hld.md` §5.
- The script has no input, no `--help` and no options. Source: spec FR1 and out-of-scope list.
- Only the standard library is used, compatible with Python 3.10 or later, with no new dependency. Source: spec FR4 and AC2, and `pyproject.toml` `requires-python`.
- The only product change is the new file. There are no tests, no `CHANGELOG.md` line, no `pyproject.toml` change and no edits to existing files. Source: spec FR5 and AC3, epic RK1, and `work-items.md` t1 "Must not modify".
- The file conventions are a `#!/usr/bin/env python3` shebang, a one-line header comment naming epic a3 and story QA20261110-8, git mode `100755`, and ASCII with LF endings. Source: t1 AC5 and `hld.md` §6.
- Use a module-level `print` and let the script end normally. Don't use `exit()`, `quit()` or `sys.exit`. Source: `hld.md` §6.
- The PR description:
  - cites QA20261110-8 and the epic PRD (Confluence page 35487745)
  - reports the manual run (Python version, stdout, stderr, exit code) and the 3.10 code read
  - states the `PLAY-G4` and rule-1 deviations

  Source: t1 AC9.

**Assumptions**
- **A1: reading the code satisfies AC2.**
  - Evidence: there is no 3.10 interpreter in the pod, and CI runs only 3.12. A single `print` of a string literal is valid on every Python 3.
  - If wrong: a reviewer asks for a real 3.10 run, which is a manual follow-up with no code change.
- **A2: the human reviewer accepts the repo-gate `PLAY-G4` blocker and the rule-1 finding as waived.**
  - Evidence: `hld.md` §7, and spec AC3 forbids touching `CHANGELOG.md`.
  - If wrong: the scope must be reopened through the structure turn. The implement phase never adds the line on its own.
- **A3: git keeps the executable bit when it's set in the working tree.**
  - Evidence: the existing scripts are tracked as `100755`.
  - If wrong: AC5 of t1 fails, and the fix is `git update-index --chmod=+x`.

## Solution proposal

Add one new three-line file, `qa/20261110-a3/hello.py`. It mirrors the existing `qa/` shell scripts and uses Python syntax:
1. line 1, `#!/usr/bin/env python3`
2. line 2, a `#` comment saying it prints the greeting for QA epic a3 (QA20261110-8)
3. line 3, `print("hello from a3")`

Commit it with mode `100755`.

The default `print` ends the line with exactly one `\n`. Ending the module normally gives exit code 0, and nothing is written to stderr. The script is outside `src/`, so it is not part of the installed distribution. It is outside `tests/`, so pytest never runs it.

**Alternatives rejected:**
- An `if __name__ == "__main__":` guard with a `main()` function. It adds structure the spec doesn't need, and nothing imports the script.
- `sys.stdout.write("hello from a3\n")`. It needs an import for the same result.
- `sys.exit(0)` or `exit()`. These are redundant, and `exit()` depends on `site`.
- A pytest test under `tests/`, or a `qa/20261110-a3/test_hello.sh` like PLAY-175 has. Both are forbidden by spec AC3 and the epic's out-of-scope list.
- A `CHANGELOG.md` line to satisfy `PLAY-G4`. Forbidden by spec AC3 (`hld.md` §6).

## Ordered implementation steps

1. **Create `qa/20261110-a3/hello.py`** (new directory and file) with the shebang, the header comment and the single `print` described under Solution proposal. Use ASCII, LF endings and a trailing newline at end of file.
   - Advances: spec AC1 and AC2; t1 AC1–AC5.
   - Test layer: none in the repo covers `qa/` Python scripts, and spec AC3 forbids adding one. Proof is the manual run in step 3.
2. **Set the executable bit** (`chmod +x`) so the file is tracked as `100755`.
   - Advances: t1 AC5.
   - Test layer: none. Verify with `git ls-files -s qa/20261110-a3` after staging.
3. **Run the script manually from the repo root and capture the evidence:**
   - `python qa/20261110-a3/hello.py`: stdout is exactly `hello from a3\n` (check the bytes, e.g. with `od -c`), stderr is empty and the exit code is 0
   - `./qa/20261110-a3/hello.py`: same result
   - run it with an extra argument such as `--help`, and confirm the output is unchanged (t1 AC3)
   - record the interpreter version

   Read the file to confirm that it uses only constructs valid on Python 3.10 (A1).
   - Advances: spec AC1 and AC2; t1 AC1–AC4.
   - Test layer: manual, reported in the PR.
4. **Re-run the existing `qa/` scripts and confirm their output is unchanged:**
   - `qa/20261110-s3/hello.sh` prints `hello s3`
   - `qa/20261109-s1/a.sh` and `qa/s3-a.sh` each print `A`
   - `qa/s3-hello.sh` prints `hello`
   - `qa/20261110-s3/test_hello.sh` prints `PASS`
   - Advances: spec AC5; t1 AC8.
   - Test layer: the existing `package-api` pytest tests (`tests/test_qa_s3_greeting.py`, `tests/test_qa_20261109_s1_a.py`) plus a manual run.
5. **Run the canonical gate** once on the committed SHA: `pip install -e ".[test]"` and then `pytest`. Confirm it is green and the pytest step stays under 60 seconds.
   - Advances: spec AC4; t1 AC7.
   - Test layer: `package-api`.
6. **Check the diff scope.** `git diff --name-status main...HEAD` must list only `A qa/20261110-a3/hello.py` plus files under `stories/QA20261110-8/`.
   - Advances: spec AC3; t1 AC6.
   - Test layer: none; it is a diff inspection.
7. **Write the PR description** with the content listed under Locked decisions: the story and PRD references, the manual run evidence and 3.10 code read from step 3, and the `PLAY-G4` and rule-1 deviations.
   - Advances: spec AC3; t1 AC9.
   - Test layer: none; reviewed by a human.

**Implicit invariants:**
- Authorization, tenancy, concurrency and idempotency don't apply, because the script has no state, input or I/O beyond stdout.
- There are no validation or error paths (spec §3, edge cases).
- Dependencies come only from the existing `pip install -e ".[test]"` for the gate; the script itself needs none.
- No generated deliverables or binaries, so `.factory/delivery-assets` doesn't apply.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1–7 | `t1`: Add qa/20261110-a3/hello.py that prints "hello from a3" and exits 0 |

The breakdown has one work item, and every step belongs to it. There are no gaps.

## Verification and CI gate

- **Canonical gate** (per `.factory/testing.md`): `pip install -e ".[test]"`, then `pytest` from the repo root. Run it once locally on the committed SHA.
  - The authoritative result is the provider's `test` job at the exact head, on Python 3.12. The `gate` job must also be green; it stays green as long as no `CI_FAIL` is added.
  - The required layer is `package-api`, and it can run in a pod.
- **What the gate shows here:** the existing suite stays green and under 60 seconds. It doesn't exercise the new script, because `testpaths = ["tests"]`. That is accepted by design: spec §2 rules out tests, and so does epic PRD §7.
- **Manual checks outside the gate**, reported in the PR:
  - the AC1 byte-exact run with empty stderr and exit 0
  - the AC2 code read for 3.10. A real 3.10 run isn't possible in the pod, which has 3.11.2.
  - the AC5 existing-script outputs
  - the AC3 diff scope
- **No changes needed** to provider CI configuration, `.factory/testing.md` or `.factory/delivery-assets`.
- **Done means:** the PR's `test` and `gate` jobs are green, the diff contains only the new file plus `stories/QA20261110-8/`, and the manual evidence is in the PR description.

## Risks and scope guards

**Risks**
- **The repo-gate review reports a `PLAY-G4` blocker (no `CHANGELOG.md` line) and possibly a rule-1 finding** (a `.py` file outside `src/`).
  - Mitigation: state both deviations in the PR, citing spec AC3 and `hld.md` §6–7, so the human reviewer can waive them knowingly (A2).
- **The script itself has no automated coverage.**
  - Mitigation: manual evidence in the PR. Regression risk is negligible, because no existing file changes.
- **The executable bit could be lost** (A3).
  - Mitigation: verify `100755` in step 2.

**Scope guards: the implement phase must NOT:**
- edit any existing file: `CHANGELOG.md`, `pyproject.toml`, `README.md`, `docs/`, `src/`, `tests/`, `.github/`, `.factory/`, or any existing `qa/` script
- add a test in any form, whether under `tests/` or as `qa/20261110-a3/test_hello.sh`
- add `--help`, argument parsing, a `main()` entry point or a console-script registration
- add a dependency, or change the version
- edit `spec.md`, `hld.md` or `work-items.md`
- make the repo-gate or CI pass by deleting, skipping or weakening a check, or by adding a `CHANGELOG.md` line against spec AC3. A blocked check is reported as blocked.

## Clarification outcomes

None.
