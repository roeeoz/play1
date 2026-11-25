# HLD — Hello world bash script in a dedicated folder (SMKS-1)

## 1. System Overview

- **What:** a standalone bash script `hello-world/hello.sh` at the root of `play1` that prints `Hello, World!!` and exits 0, plus a pytest module that verifies it, plus the `CHANGELOG.md` line the repository gate requires.
- **Change of 2026-11-25 (developer, structure review):** the default greeting is exactly `Hello, World!!` (capital H and W, comma, one space, two exclamation marks). This replaces the lowercase `hello world` of spec FR3, §4 and §5 scenarios 1 and 4; every other requirement of the approved spec stands as written. The existing Python CLI `src/testbed_utils/hello.py` (prints `Hello, world!`) is a separate product surface and is not changed.
- **Problem:** the repository holds only Python (`src/testbed_utils/`, `src/guestbook/`, `tests/`); there is no shell script and no `hello-world/` folder today (checked on `halo/feat/smks-1-20261125-120918` at `3badfbd`). `CHANGELOG.md` does not exist either.
- **Responsibilities:** emit one exact line on stdout; be directly executable via its shebang; keep its folder single-file; be covered by the existing `pytest` gate.

## 2. Architecture Overview

- **Script** — `hello-world/hello.sh` (new). Not part of the Python package: it is not registered under `[project.scripts]` in `pyproject.toml` and is not installed; it runs from the checkout.
- **Tests** — `tests/test_hello_sh.py` (new), beside the existing suite (`tests/test_hello_cli.py` is the nearest pattern: it asserts exact stdout, empty stderr and the exit code). Collected by the existing config `[tool.pytest.ini_options] testpaths = ["tests"]` in `pyproject.toml`.
- **Changelog** — `CHANGELOG.md` (new) with `## Unreleased` and one line, required by rule 4 of `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`.
- **Unchanged:** `.github/workflows/ci.yml` (its `test` job already runs `pytest` on Python 3.12, ubuntu-latest — that is what runs the new tests), `pyproject.toml`, `src/`, `README.md`.
- **External dependency:** `/bin/bash` on the machine running the script/tests (present on ubuntu-latest and macOS).

## 3. Data Flow Design

- Synchronous, single process: developer (or test) execs `hello-world/hello.sh` → kernel reads the `#!/bin/bash` shebang → bash prints `Hello, World!!\n` to fd 1 → exit 0.
- Test path: pytest → `subprocess.run([<abs path to hello.sh>])` (no `bash` prefix, so the shebang and exec bit are actually exercised) → asserts on captured stdout/stderr/returncode.
- No state, no files read or written, no network, no events.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Print the greeting | none → `Hello, World!!\n` on stdout, empty stderr, exit 0 | play1 |
| `tests/test_hello_sh.py` | Verify spec §5 scenarios 1–4 and FR1–FR3 | the script file → pass/fail under `pytest` | play1 |
| `CHANGELOG.md` | Repo-gate rule 4 line | — | play1 |

## 5. Interface Contracts

- **CLI contract (the only interface):** `./hello-world/hello.sh` with no arguments → stdout is exactly the bytes `Hello, World!!\n` (capital `H` and `W`, a comma, one space, two `!`, single trailing LF, no CR, no other line), stderr is empty, exit status 0. `$(./hello-world/hello.sh)` therefore yields exactly `Hello, World!!`.
- Works from any current directory (it reads nothing relative to cwd).
- **Arguments:** no contract (spec FR4, a recorded exception to the `qa/` script rule). The script neither parses nor refuses them; tests must not assert any argument behavior.
- **File contract:** first line exactly `#!/bin/bash`; git mode `100755`; `hello-world/` contains no other file.
- No cross-repo contracts.

## 6. Key Technical Decisions

- **One work item.** Script, tests and changelog line are one XS vertical slice; splitting would leave a tests-only or script-only PR that fails the repo gate (rule 4 needs the changelog in every PR).
- **Tests run the script as a subprocess, directly (no `bash` prefix),** located from the test file's own path (`tests/` → repo root), not from cwd — so they pass whether pytest is started from the root or elsewhere, and they genuinely prove the shebang + exec bit (scenario 3). Byte-exact comparison of stdout (`Hello, World!!\n`) covers scenarios 1 and 4 together; a separate check that `$(...)`-style capture (stdout with the trailing newline stripped) equals `Hello, World!!` documents the user-facing contract.
- **`!` is safe in the script.** Bash history expansion is off in non-interactive scripts, so the literal prints as written (verified: `echo "Hello, World!!"` in a `#!/bin/bash` script emits `Hello, World!!\n` on bash 3.2). Single quotes are the robust choice, so the line survives being pasted into an interactive shell; the byte-exact test catches any expansion.
- **Executable bit is carried in git** (`100755`), not set by the test or CI; the test asserts the file is executable rather than chmod-ing it, so a lost mode fails loudly. Local checkout has `core.fileMode=true`.
- **No `set -euo pipefail` / no argument handling required** — nothing can fail; the implementer may add strict mode, but must not add output or argument behavior.
- **Alternative rejected:** registering it as a `[project.scripts]` entry or a Python wrapper — out of the spec (a bash script in its own folder).

## 7. Risks & Constraints

- **Exec bit lost** (e.g. a commit from a filesystem/tool with `core.fileMode=false`) → direct execution fails with permission denied; mitigated by the test asserting executability and running it directly, and by repo-gate rule 2.
- **CRLF line endings** would break the shebang (`/bin/bash\r`) and add `\r` to output; mitigated by the byte-exact assertion. No `.gitattributes` exists, so the file must be committed with LF.
- **`/bin/bash` absent** (e.g. minimal Alpine) → not a concern for CI (ubuntu-latest) or developer Macs (bash 3.2 at `/bin/bash`; `echo`/`printf` behave identically for this literal across bash 3.2–5.x).
- **Folder isolation:** stray files (`.DS_Store`, editor backups) in `hello-world/` would break FR1 — the test checks the folder lists only `hello.sh`; `.gitignore` is not changed.
- **Gate constraints:** `pytest` stays green (`.factory/testing.md`); repo-gate rules 1 (tests under `tests/`), 2 (shebang + executable), 3 (<200 KB), 4 (`CHANGELOG.md` `## Unreleased` line) are all met by the single PR. `.github/workflows/ci.yml` is not touched (spec non-goal).
- Scale/performance/security: none material — no input, no I/O beyond one line of stdout, no secrets.

## 8. Assumptions

- The `CHANGELOG.md` line is the only file outside `hello-world/` and `tests/` that changes; it is not a "documentation file" in the sense of the spec's non-goal (spec §6).
- Behavior with arguments is deliberately unspecified (spec FR4); passing arguments is assumed to still print `Hello, World!!` if the implementer ignores them, but nothing tests or promises it. Risk if wrong: none for the stated users, who invoke it without arguments.
- "The default greeting" in the developer's change of 2026-11-25 is read as this script's output (its only greeting, printed with no arguments); it does not ask for a configurable or alternative greeting, and does not reach `src/testbed_utils/hello.py`. Risk if wrong: a follow-up change to that CLI or to add greeting options would be a separate story.
