# HLD — SCRUM-20: Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** a runnable `hello-world/hello.sh` at the repository root that prints exactly `hello world` and exits 0 (spec FR1–FR5).
- **Finding (verified in the checkout at `f4f61f2`, which is `main` plus the spec):** the artefact already exists and meets the spec.
  - `hello-world/hello.sh` is tracked with git mode `100755`; its content is exactly `#!/bin/bash` / `echo "hello world"` (two lines, LF endings, no trailing whitespace). It is the only file in `hello-world/`.
  - `tests/test_hello_sh.py` asserts exit 0, stdout `== "hello world\n"`, empty stderr, the shebang line, the owner-executable bit and that the folder holds only `hello.sh` (dotfiles ignored).
- **Responsibility of this story:** keep the script exactly as it is (spec A1), close the two small verification gaps below, and record the delivery in `CHANGELOG.md` so the pull request passes gate PLAY-G4.
  - Gap 1: no test runs the script the way the spec's scenarios state — `./hello-world/hello.sh` from the repository root (tests use an absolute path with an unspecified cwd).
  - Gap 2: the executable check reads the working-tree mode only; nothing asserts that git *tracks* the file as `100755`, which is what every clone receives (Scenario 3).

## 2. Architecture Overview

- No new components. Two existing files are touched; nothing else.
  - `tests/test_hello_sh.py` — the acceptance suite for the script; runs in the `test` job of `.github/workflows/ci.yml` (`pip install -e ".[test]"` then `pytest`, Python 3.12), the repo's only declared test layer (`.factory/testing.md`).
  - `CHANGELOG.md` — one new bullet under `## Unreleased`, following the existing `- <KEY>: <description>` style.
- `hello-world/hello.sh` is consumed (read and executed by tests), never modified; `hello-world/` gets no new file.
- External dependencies: `/bin/bash` on the runner (ubuntu-latest), and `git` plus the `.git` directory that `actions/checkout@v4` leaves in place, for the tracked-mode check.

## 3. Data Flow Design

- Synchronous only: developer (or pytest via subprocess) → kernel reads shebang → `/bin/bash` runs `echo` → `hello world\n` on stdout, nothing on stderr, exit 0.
- No inputs (arguments, environment, stdin), no persisted state, no events.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `hello-world/hello.sh` (existing, unchanged) | Print `hello world` | none → stdout `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` (extended) | Prove FR1–FR5 / Scenarios 1–4 in CI | script file, git index → pass/fail | play1 |
| `CHANGELOG.md` (one line) | Satisfy gate PLAY-G4 | — | play1 |

## 5. Interface Contracts

- CLI contract of the script: invoked as `./hello-world/hello.sh` from the repo root (and from any cwd by path); stdout exactly `hello world\n`; stderr empty; exit code 0; no arguments read.
- No APIs, events or cross-repo contracts.

## 6. Key Technical Decisions

- **Keep, don't rewrite** (spec A1): the shipped script already satisfies every criterion; rewriting it adds risk and diff with no behaviour gain.
- **Extend the existing test module** rather than add a new one: one place owns the script's acceptance checks, and it already runs in the CI `test` job — no CI change (spec non-goal).
- **Assert the git-tracked mode** in addition to the filesystem bit: the filesystem bit can be set locally while git records `100644` (e.g. `core.fileMode=false`), which would break Scenario 3 for every other clone.
- Alternative rejected: a shell-based test beside the script — it would put a second file in `hello-world/` (breaks FR1) and is not a declared test layer.

## 7. Risks & Constraints

- The tracked-mode check needs `git` and the `.git` directory; both are present in the CI `test` job and in a normal checkout. Outside a git checkout (e.g. an sdist) the check cannot run; skipping it there, rather than failing, is acceptable.
- Gates on the PR: `pytest` (CI `test` job), `gate` job (no `CI_FAIL` file), and the play1 layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): tests under `tests/`, no file > 200 KB, and a `CHANGELOG.md` line under `## Unreleased` (PLAY-G4). Rule 2 (new shell script executable + shebang) is not triggered — no new script is added — and the existing one already complies.
- No scale, performance or security surface: a two-line script with no input.

## 8. Assumptions

- **A1 (spec):** the existing `hello-world/hello.sh` is the deliverable and stays byte-for-byte unchanged. *Risk:* if a fresh script was intended, it surfaces only at review.
- **A2 (spec):** the one terminating newline is allowed; output is `hello world\n`. *Risk:* a raw-bytes comparison against `hello world` without newline would fail.
- **A3 (spec):** the CHANGELOG bullet is required by PLAY-G4 and is not a "documentation file" in the story's exclusion sense.
- **A4 (design):** the story key used in the CHANGELOG bullet is `SCRUM-20`, matching the plan folder name. *Risk:* none functional.
