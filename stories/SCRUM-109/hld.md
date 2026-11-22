# High-Level Design — SCRUM-109: qa/s4_marker.sh prints QA_S4_MARKER

## 1. System Overview

- **What:** one POSIX shell script, `qa/s4_marker.sh`, in `roeeoz/play1`, that reports the value of the environment variable `QA_S4_MARKER` (spec FR1–FR5).
- **Problem:** a developer with a shell in a pod cannot quickly see which environment it runs with; the marker identifies it.
- **Responsibilities:** print the raw value (exit 0), including an empty value; report the unset case on stderr (exit 1). It never sets, validates or interprets the value.

## 2. Architecture Overview

- **Components:** the script `qa/s4_marker.sh`, and a self-checking test script `qa/s4_marker_test.sh` beside it. No other component; no library, service or package change.
- **Existing pattern followed:** the repo's other QA helpers are `#!/bin/sh` scripts committed with mode `100755` and a one-line purpose comment (`qa/s3-hello.sh`, `qa/s3-a.sh`, `qa/20261110-s3/hello.sh`); `qa/20261110-s3/test_hello.sh` is the precedent for a shell test that runs its sibling directly and checks exact stdout and exit code.
- **Boundary:** everything lives under `qa/s4_*` (spec FR4 / AC3). `tests/`, `src/`, `pyproject.toml`, `.github/workflows/ci.yml` and the other `qa/` scripts are untouched — so the script is **not** covered by a pytest file (that would land in `tests/`, outside scope).
- **External dependencies:** a POSIX `sh` and the shell built-in `printf`. On the dev checkout `/bin/sh` is bash; on Debian/Ubuntu pods it is typically dash — the design uses only constructs that behave identically in both.

## 3. Data Flow Design

- Synchronous, single process: process environment → script → stdout/stderr + exit status.
- `QA_S4_MARKER` present in the environment (exported; possibly empty) → value + `\n` on stdout, nothing on stderr, exit 0.
- `QA_S4_MARKER` absent from the environment → `QA_S4_MARKER is not set` + `\n` on stderr, nothing on stdout, exit 1.
- No events, no files read or written, no network.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `qa/s4_marker.sh` (new, mode 100755, shebang) | Report `QA_S4_MARKER` | In: process environment. Out: stdout / stderr / exit status per §5 | `roeeoz/play1` |
| `qa/s4_marker_test.sh` (new, mode 100755, shebang) | Run `qa/s4_marker.sh` directly in each case of §5 and exit 0 only if all pass, non-zero with a `FAIL:` line on stderr otherwise | In: none (builds each environment itself). Out: `PASS`/`FAIL` lines, exit status | `roeeoz/play1` |

## 5. Interface Contracts

CLI contract of `qa/s4_marker.sh` (no arguments; any arguments are ignored):

| Case | stdout | stderr | exit |
|---|---|---|---|
| `QA_S4_MARKER=value` exported | `value\n` exactly, byte for byte | empty | 0 |
| `QA_S4_MARKER=` (exported, empty) | `\n` | empty | 0 |
| `QA_S4_MARKER` not in the environment | empty | `QA_S4_MARKER is not set\n` | 1 |

Edge cases settled (verified in a shell on 2026-11-22):
- The value is printed verbatim: a value starting with `-` (e.g. `-n`), containing backslashes (`a\nb\c`), `%` sequences (`%s %d`), leading/trailing spaces, or embedded newlines is output unchanged, followed by exactly one `\n`. (`echo` would mangle `-n` and, under dash, backslash escapes — so it is not acceptable for the value.)
- "Set" means present in the process environment. A shell variable assigned but not exported in the caller is not visible to the script and reports as unset (exit 1) — standard environment semantics, not a defect.
- Set-but-empty is "set" (spec FR5), so the check must distinguish unset from empty rather than test for emptiness.

## 6. Key Technical Decisions

- **`#!/bin/sh` (POSIX), not bash:** matches the `qa/` precedent and runs on minimal pods without bash. Alternative `#!/bin/bash` (as in `hello-world/hello.sh`) rejected: adds a dependency for no gain.
- **Verbatim output via `printf` with a fixed `%s\n` format**, never the value as the format string and never `echo`.
- **Test as a sibling shell script under `qa/s4_*`**, following `qa/20261110-s3/test_hello.sh`. Alternative pytest file in `tests/` rejected: spec FR4/AC3 forbid files outside `qa/s4_*`. Consequence: the CI `test` job (pytest) does not exercise this script; the shell test is run by the implementer and reviewer (`./qa/s4_marker_test.sh`), and the executable bit + shebang are checked by the repo gate rule PLAY-G2 (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`).
- **One work item:** the script and its test form one small, reviewable change; splitting them would leave a tests-only or untested PR.

## 7. Risks & Constraints

- **Red CI `test` check from the base (known, accepted):** `tests/test_qa_20261122_s4_base.py` on `qa-20261122-s4-base` asserts `1 == 2`, so `pytest` fails regardless of this change. Per the developer's decision (spec §6, option b) this story does not touch it; the merge decision is the person's.
- **Executable bit lost on commit:** a file written without `chmod +x` (or on a filesystem that drops modes) fails AC1 and PLAY-G2. The work item requires git mode `100755` for both files.
- **CRLF line endings** would break the shebang; files must be LF.
- No scale, performance or security surface: the script reads one variable the caller already has and writes it to the caller's own terminal; no secrets are introduced. If an environment ever puts a secret in `QA_S4_MARKER`, the script would print it — out of this story's control and consistent with its purpose.

## 8. Assumptions

- The test script is not wired into CI (that would need a change to `.github/workflows/ci.yml`, outside scope). Risk if wrong: none to behaviour; only that CI does not re-run it automatically.
- Arguments passed to the script are ignored (spec is silent; it names no arguments). Risk if wrong: low — no caller depends on arguments.
