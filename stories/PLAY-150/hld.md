# HLD — PLAY-150: QA-20261108-S4 greeting script + bats-free test

Story: PLAY-150 ("QA-20261108-S4 — greeting script that prints 'hello from s4' and a test that verifies it") · Epic PRD: https://roeeoz.atlassian.net/wiki/pages/viewpage.action?pageId=33357825 · Repo: roeeoz/play1 · Base branch: `qa-20261108-s4-base`

## 1. System Overview
- **What is being built:** two standalone POSIX shell scripts under `qa/`:
  - `qa/s4-greet.sh` prints exactly `hello from s4\n` and exits 0.
  - `qa/s4-greet.test.sh` runs it and reports PASS or FAIL with a matching exit status.
  - Plus one `CHANGELOG.md` line under `## Unreleased`.
- **Problem:** the QA run needs proof that the factory can deliver a tiny, closed initiative end to end in one small PR.
- **Responsibilities:** print the greeting; verify the greeting with no external test tool; keep the change footprint at exactly 3 files outside `stories/PLAY-150/`.

## 2. Architecture Overview
- **Components:**
  - the greeting script;
  - the self-contained test script;
  - the changelog entry.
- **What it does not touch:** no Python package code (`src/`), pytest suite (`tests/`), `pyproject.toml` or CI workflow is involved.
- **Boundary:** `qa/` holds ad-hoc helper scripts. `qa/s3-hello.sh` is the style reference and stays unchanged.
- **External dependencies:** none beyond `/bin/sh` (POSIX; must also run under `dash`) and standard utilities (`printf`, `dirname`, and similar). No bats, no network, no clock, no files outside the repo.

## 3. Data Flow
1. The user runs `qa/s4-greet.test.sh` from any working directory.
2. The test resolves the directory it lives in and builds the path to `s4-greet.sh` next to it.
3. The test executes that script directly, so the shebang and executable bit are exercised. It captures stdout in memory, preserving trailing newlines, and records the exit status.
4. Results:
   - Script missing, not executable, or non-zero exit: FAIL.
   - stdout not byte-identical to `hello from s4\n`: FAIL.
   - Otherwise: PASS.
5. Everything is synchronous and single-process. There are no events and no persisted state.

## 4. Component Breakdown
| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `qa/s4-greet.sh` | Print the greeting | In: none (ignores args). Out: stdout `hello from s4\n`; exit 0 | roeeoz/play1 |
| `qa/s4-greet.test.sh` | Verify the greeting without bats | In: sibling `s4-greet.sh`. Out: a PASS line on stdout with exit 0, or a FAIL line on stderr (with reason) and exit 1 | roeeoz/play1 |
| `CHANGELOG.md` entry | Satisfy the repo PR gate (PLAY-G4) | One appended bullet under `## Unreleased`, in the same form as the PLAY-114 line | roeeoz/play1 |

## 5. Interface Contracts
- **Greeting CLI contract:**
  - stdout is exactly the 14 bytes `hello from s4` followed by LF;
  - exit status 0;
  - no stderr output expected.
- **Test CLI contract:**
  - exit 0 only on PASS; non-zero (1) on any failure;
  - the PASS message contains `PASS`, the FAIL message contains `FAIL` and a short reason (missing/not executable, exit status N, or the unexpected output);
  - the outcome does not depend on the working directory.
- **File properties:** both scripts have mode 100755, start with `#!/bin/sh` followed by a one-line `#` purpose comment, use LF line endings, and contain no bashisms.
- **Cross-repo contracts:** none.

## 6. Key Technical Decisions
- **Locate the target relative to the test's own path** rather than the current directory, so it is robust from any directory. *Alternative:* a CWD-relative path is fragile.
- **Execute the script directly, not via `sh`**, so a missing exec bit or a broken shebang counts as a failure (the same spirit as S3's checks).
- **Byte-exact comparison that preserves trailing newlines.** A sentinel or exact compare is used instead of naive `$(...)` capture, so "exactly one line" (FR1) is actually enforced. No temp files, so G4 holds and nothing is written outside the repo.
- **No injection hook** (env var or argument) for pointing at another script. This is a spec non-goal. Failure paths are proven by temporarily editing or removing `qa/s4-greet.sh` in a local copy.
- **No pytest file and no CI wiring.** The S3 precedent added a pytest file; here that would be a 4th file and is a non-goal. Existing `tests/test_qa_s3_greeting.py` keeps proving the S3 regression (scenario 6) in CI.
- **Changelog line included** by developer decision (P0-1/P0-2), to pass the repo gate.

## 7. Risks & Constraints
- **Base mismatch (main delivery risk).**
  - The work branch forked from `main` (`d61f25b`) and lacks base commit `90f1a31`, which adds `qa/s4-base-marker.txt`.
  - Unless the work is brought onto `qa-20261108-s4-base`, the PR shows that file deleted and breaks FR7 / scenario 5.
  - The scope is measured only against `qa-20261108-s4-base`.
- **RK1: CI never runs `qa/`.** Green CI proves only pytest and `CI_FAIL`. Evidence for scenarios 2–4 is manual runs recorded in the PR description.
- **RK2: scope creep.** Any README, pytest, ci.yml or extra-doc change breaks the 3-file limit.
- **Repo gate.** New shell scripts must be executable and have a shebang. A missing `chmod +x` on the test file is a blocker. The CHANGELOG line is mandatory.
- **Scale/perf/security.** The test runs in milliseconds and adds nothing to CI time. The output contains no secrets or PII. No new dependencies or licenses.
