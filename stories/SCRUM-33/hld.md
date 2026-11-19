# HLD — SCRUM-33 Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** a runnable `hello-world/hello.sh` at the play1 repo root that prints `hello world\n` and exits 0 (spec FR1–FR4).
- **Finding, verified against the code on this branch (`ae40089`, cut from `main` `b7b5d0a`):** the deliverable already exists and meets every acceptance criterion.
  - `hello-world/hello.sh` is tracked with mode `100755`; content is `#!/bin/bash` + `echo "hello world"` (added in `65938b5`).
  - Running it emits exactly the bytes `hello world\n`, exit code 0 (checked with `od -c`).
  - `hello-world/` holds only `hello.sh`.
  - `tests/test_hello_sh.py` asserts output, exit code, empty stderr, shebang, executable bit and folder isolation; it passes locally (6 passed) and runs in CI's `test` job.
- **What this story changes (spec FR5 / A1):** one line under `## Unreleased` in `CHANGELOG.md` recording SCRUM-33 as delivered by the existing script. Nothing in `hello-world/` or `tests/` changes.

## 2. Architecture Overview

- Components (all in repo `play1`, no services, no external dependencies beyond `/bin/bash`):
  - `hello-world/hello.sh` — the script (existing; consumed, not modified).
  - `tests/test_hello_sh.py` — pytest checks of the script (existing; consumed, not modified).
  - `CHANGELOG.md` — repository changelog; the only file this story edits.
- Boundary: the story owns one line in `CHANGELOG.md` under `## Unreleased`. It does not touch `qa/`, `src/`, CI, or other stories' entries.

## 3. Data Flow Design

- Synchronous, local: developer runs `./hello-world/hello.sh` → kernel honours the shebang → bash runs `echo` → `hello world\n` on stdout → exit 0.
- No input, no arguments, no state, no events. Arguments, if passed, are ignored (existing behaviour, `echo` does not read `$@`).

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Print the greeting | none / `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` | Verify spec scenarios 1–4 | script / pytest pass-fail | play1 |
| `CHANGELOG.md` entry | Satisfy repo-gate rule 4 (`PLAY-G4`) and record delivery | — / one bullet under `## Unreleased` | play1 |

## 5. Interface Contracts

- CLI contract: `./hello-world/hello.sh` → stdout exactly `hello world\n`, stderr empty, exit code 0 (per spec A2, the single terminating newline is allowed; `$(…)` yields exactly `hello world`).
- Changelog contract: a `- SCRUM-33: …` bullet appended to the existing bullet list under `## Unreleased`, following the existing style (e.g. `- PLAY-175: add …`), stating that SCRUM-33 is delivered by the existing `hello-world/hello.sh`. Existing entries stay unchanged.
- No cross-repo contracts.

## 6. Key Technical Decisions

- **Reuse, don't rewrite (spec A1):** the existing script and test already meet FR1–FR4; rewriting them would be churn with merge risk and no behavioural gain.
- **Single work item:** the only change is one changelog line; splitting further would be micro-fragmentation.
- **No new test:** `tests/test_hello_sh.py` already covers every scenario; the CI `test` job (`pytest`) is the gate (`.factory/testing.md`).
- Alternative considered: closing the story with no PR. Rejected because the spec (FR5) asks for the changelog PR, and the repo gate requires a `CHANGELOG.md` line on every PR.

## 7. Risks & Constraints

- **Gates every PR must pass:** repo-gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) — rule 4 requires a `CHANGELOG.md` line under `## Unreleased` (else blocker `PLAY-G4`); rule 3 caps files at 200 KB; CI `test` (pytest, Python 3.12) and `gate` (fails iff `CI_FAIL` exists at the root) in `.github/workflows/ci.yml`.
- **Risk (spec A1):** the PR carries no product change; if SCRUM-33 expected new code, a human reviewer closes it instead.
- **Risk:** a concurrent PR editing the `## Unreleased` list could conflict textually; resolved by appending a single line at the end of the list.
- **Constraint:** nothing may be added to `hello-world/` (FR4; `test_folder_contains_only_hello_sh` would fail).
- Scale/performance/security: not applicable — a static echo with no input.
- No `.factory/memory/` directory exists in this repo.
