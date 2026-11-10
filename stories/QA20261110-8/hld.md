# High-Level Design — QA20261110-8: `qa/20261110-a3/hello.py` prints "hello from a3"

## 1. System Overview
- **What is built:** one new standalone script, `qa/20261110-a3/hello.py`, in `roeeoz/play1`. It prints exactly `hello from a3\n` to stdout, writes nothing to stderr and exits with code 0.
- **Problem:** test the agentic factory end to end on the smallest possible change, one that doesn't touch package code (Epic PRD §1–2, goal G3).
- **Responsibilities:** the script's only job is to print one line and exit successfully. It has no input, no options and no dependencies.

## 2. Architecture Overview
- **Component:** one file under `qa/`, next to the existing shell scripts there (`qa/s3-hello.sh`, `qa/s3-a.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/hello.sh`). It is the first Python file in `qa/`.
- **Boundaries:**
  - The script is not part of the `play1` package: it is not under `src/` and not registered in `[project.scripts]`.
  - pytest never collects it, because `testpaths = ["tests"]`.
  - It imports nothing from the package.
- **External dependencies:** none. It uses the Python standard library only and runs on Python 3.10 or later.
- **Ownership:** the single ticket t1 owns the new file. Nothing else changes, apart from the factory's own plan documents under `stories/QA20261110-8/`.

## 3. Data Flow Design
- The user runs `python qa/20261110-a3/hello.py` from the repo root.
- The script writes `hello from a3\n` to stdout.
- The process ends with exit code 0.
- Everything happens synchronously. There are no events, no state and no I/O other than stdout.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repository |
| --- | --- | --- | --- |
| `qa/20261110-a3/hello.py` | Print the a3 greeting and exit 0 | In: none (ignores args and env). Out: stdout `hello from a3\n`, empty stderr, exit 0 | roeeoz/play1 (`3de95313-a662-49a5-b8a0-56b5dd990c4d`) |

## 5. Interface Contracts
- **CLI contract:**
  - invocation: `python qa/20261110-a3/hello.py` from the repo root
  - stdout: exactly `hello from a3\n`
  - stderr: empty
  - exit code: 0
- No APIs, events or cross-repo contracts.

## 6. Key Technical Decisions
- **Follow the `qa/` convention, adapted to Python:**
  - shebang `#!/usr/bin/env python3`
  - a one-line `#` header comment naming the epic (a3) and story (QA20261110-8)
  - git mode `100755`
  - ASCII text with LF line endings

  None of this is needed for acceptance, since the script is run as `python <path>`, but it keeps the file consistent with its neighbours.
- **Print with a plain `print` at module level.** Don't use `exit()` or `quit()`, which depend on the `site` module. Don't use `sys.stdout.write` without a newline. Ending the script normally gives exit code 0.
- **No tests, no CHANGELOG, no `pyproject.toml` change.** The approved spec rules all of these out (§2, FR5, AC3, RK1).
  - Alternative considered: adding a CHANGELOG line to satisfy repo-gate rule `PLAY-G4`, as PLAY-172 and PLAY-175 did. Rejected, because it breaks AC3.
  - What happens instead: the PR description states the deviation and cites the spec, so the human reviewer can waive it knowingly.
- **Python 3.10 support (AC2)** is shown by a code read: the script uses only syntax and built-ins available in Python 3.0 and later. A manual run on the local interpreter (3.11) or CI's (3.12) is reported in the PR.

## 7. Risks & Constraints
- **Repo-gate `PLAY-G4` vs. the no-CHANGELOG scope.** The review gate will report a blocker. CI is unaffected: the `test` job runs `pytest` on `tests/`, and the `gate` job only checks that no `CI_FAIL` file exists. A human waives the finding at review.
- **Repo-gate rule 1 ("Python source lives under `src/`").** A literal reading could flag a `.py` file in `qa/`. The PR explains that this is a standalone QA script, not package source.
- **Scope creep (RK1).** Earlier stories set a pattern of adding tests or a CHANGELOG line. The ticket explicitly forbids touching any existing file.
- **No automated coverage of the script.** AC1, AC2 and AC5 rest on manual runs reported in the PR. Regression risk is negligible: no existing file changes, and the existing pytest tests keep pinning `qa/s3-hello.sh`, `qa/s3-a.sh` and `qa/20261109-s1/a.sh`.
- **Operational:** CI runtime is unchanged (G4, under 60 s), the change is far below the 300-line limit (G3), and there are no secrets and no new dependencies.
