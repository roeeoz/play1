# PLAY-190 — High-Level Design: bash greeting script and its test

## 1. System Overview

- **What:** two new executable bash scripts in `roeeoz/play1`: `qa/s2-hello.sh` (prints `Hello, NAME!`, rejects the empty string) and `qa/s2-hello-test.sh` (runs both cases and fails if either is wrong).
- **Why:** QA factory-path story QA-20261122-S2 — the smallest change that can run end to end. The ticket title still names `qa/s2_hello.py`; the approved spec (section 1, section 6) replaced the Python module with bash because Python outside `src/` breaks rule 1 of the repo gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`). This design follows the spec.
- **Scope:** exactly two new files under `qa/s2-*`; no existing file changes.

## 2. Architecture Overview

- Standalone scripts, no library, no runtime dependency beyond bash (`#!/usr/bin/env bash`).
- Pattern to follow: the earlier QA run's script pair `qa/20261110-s3/hello.sh` + `qa/20261110-s3/test_hello.sh` — the test locates its target relative to its own path (`dirname "$0"`), captures stdout and the exit code, prints `PASS:`/`FAIL:` and exits non-zero on failure.
- Neighbouring files `qa/s3-hello.sh`, `qa/s3-a.sh`, `qa/20261109-s1/`, `qa/20261110-s3/` are untouched.
- Not wired into CI: `.github/workflows/ci.yml` and `.factory/testing.md` run only `pytest` over `tests/` (`pyproject.toml`); per the spec the test script is run by hand and its output is the evidence in the merge request.

## 3. Data Flow Design

- Synchronous, single process: argv[1] → check for exactly the empty string → stdout + exit 0, or stderr + exit 1.
- `qa/s2-hello-test.sh` → runs `qa/s2-hello.sh Ada` and `qa/s2-hello.sh ''` as child processes → compares stdout, stderr and exit code with the expected values → exit 0 only if both cases pass.
- No state, no files written, no network.

## 4. Component Breakdown

| Component | Responsibility | In / Out | Repo |
|---|---|---|---|
| `qa/s2-hello.sh` | Greet a name; reject the empty string | In: argv. Out: stdout/stderr, exit code | `roeeoz/play1` |
| `qa/s2-hello-test.sh` | Verify the two acceptance cases | In: none. Out: `PASS`/`FAIL` lines, exit code | `roeeoz/play1` |

## 5. Interface Contracts

`qa/s2-hello.sh` (CLI contract):

| Invocation | stdout | stderr | exit |
|---|---|---|---|
| `qa/s2-hello.sh Ada` | `Hello, Ada!` + one newline | nothing | 0 |
| `qa/s2-hello.sh '   '` | `Hello,    !` + one newline | nothing | 0 |
| `qa/s2-hello.sh ''` | nothing | `name must not be empty` + one newline | 1 |
| `qa/s2-hello.sh` (no argument) | nothing | `name must not be empty` + one newline | 1 |
| `qa/s2-hello.sh Ada Bob` | `Hello, Ada!` + one newline (extra arguments ignored) | nothing | 0 |

- The name is printed literally: names starting with `-` (e.g. `-n`, `-e`) or containing `%`/`\` are printed as given — verified in a shell prototype that `printf 'Hello, %s!\n' "$1"` does this, while `echo` would swallow `-n`.
- `qa/s2-hello-test.sh`: exit 0 when both cases pass; non-zero when either fails, with a `FAIL:` line on stderr naming the case.

## 6. Key Technical Decisions

- **Missing argument = empty name.** The spec leaves it open; treating an unset `$1` like `''` avoids an unbound-variable crash and gives one clear error path. Extra arguments are ignored. Neither case is in the acceptance criteria, so the test script does not have to cover them.
- **Exact output, trailing newline:** one line ending in a single `\n`, as the spec's working assumption states; the test compares the exact bytes (including the trailing newline, using the sentinel technique from `qa/20261110-s3/test_hello.sh`) so a missing or extra newline fails.
- **Test locates the target by its own path**, so it works from the repo root or any other directory.
- **Alternative rejected:** a pytest test under `tests/` — would run in CI but changes the agreed two-files-only scope and was declined in the spec.

## 7. Risks & Constraints

- **Not proven by CI:** CI stays green but runs only `pytest`; the acceptance criteria are proven by running `qa/s2-hello-test.sh` and quoting its output in the merge request (accepted in the spec).
- **Repo gate rule 2:** both files must be committed with the executable bit (git mode `100755`) and start with `#!/usr/bin/env bash`; rule 3 (≤ 200 KB) is trivially met.
- **Portability:** bash only (developer has bash 5.1; GitHub runners have bash 5); no bash-4+-only features are needed.
- No scale, performance or security concerns: no input beyond argv, nothing evaluated or written.
