# High-Level Design — SCRUM-26: Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** a directly executable bash script `hello-world/hello.sh` that prints `hello world` and exits 0, alone in its own top-level folder (spec FR1–FR5).
- **State found in the code (verified this turn, on the work branch cut from `main` at `90f77cb`):**
  - `hello-world/hello.sh` already exists, tracked as mode `100755` (`git ls-files -s hello-world`), content exactly `#!/bin/bash` / `echo "hello world"`, LF line endings.
  - `ls -A hello-world` lists only `hello.sh`.
  - Running `./hello-world/hello.sh` emits the 12 bytes `hello world\n`, nothing on stderr, exit code 0.
  - `tests/test_hello_sh.py` (added by `9a5bd0b`) already asserts all four acceptance scenarios — stdout `== "hello world\n"`, return code 0, empty stderr, first line `#!/bin/bash`, owner-executable bit, folder contains only `hello.sh` (non-dot entries). It passes locally (6 passed) and runs in the CI `test` job.
- **Consequence:** the functional deliverable is already on `main`. Per spec A1 this story makes no change under `hello-world/` and adds no test (spec §2 non-goals); the only change is the `CHANGELOG.md` line the play1 layout gate requires (spec A3).

## 2. Architecture Overview

- One standalone artefact, no services, no runtime dependencies beyond `/bin/bash`.
- Components and ownership:
  - `hello-world/hello.sh` — the deliverable; exists; consumed (verified), not modified.
  - `tests/test_hello_sh.py` — existing pytest coverage of the four scenarios; consumed, not modified.
  - `CHANGELOG.md` (root, `## Unreleased` list) — the one file this story edits.
- Not touched: `.github/workflows/ci.yml`, `.factory/`, `src/`, `qa/`, `pyproject.toml`.

## 3. Data Flow Design

- Synchronous, single process: developer runs `./hello-world/hello.sh` → kernel reads the shebang → `/bin/bash` runs `echo` → `hello world\n` on stdout → exit 0.
- No input, no arguments, no files read or written, no events.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` and exit 0 | none / stdout `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` | Regression proof of scenarios 1–4 via the CI `test` job | the script / pass-fail | play1 |
| `CHANGELOG.md` | Record the change under `## Unreleased` (gate rule 4) | — / one new bullet | play1 |

## 5. Interface Contracts

- **CLI contract:** `./hello-world/hello.sh` with no arguments → stdout exactly `hello world` followed by a single `\n`, stderr empty, exit status 0. Arguments, if any are passed, are ignored (the script reads none); the story defines no other behaviour.
- **Filesystem contract:** `hello-world/` contains exactly one entry, `hello.sh`, tracked in git as `100755`.
- **Gate contract:** the PR diff touches `CHANGELOG.md` with one added bullet under `## Unreleased` (otherwise blocker `PLAY-G4`, `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rule 4).
- No cross-repo contracts.

## 6. Key Technical Decisions

- **Verify, don't rewrite (spec A1):** the existing script meets FR1–FR5 byte-for-byte; rewriting it would add churn and risk without changing behaviour. The work item still re-verifies it and fixes it only if a criterion fails.
- **No new test (spec §2/§6):** `tests/test_hello_sh.py` already covers every scenario and runs in the `test` job; adding another would duplicate it and the spec excludes CI/test additions.
- **`echo` (with newline) over `printf` (spec A2):** one terminating newline is the accepted reading of "no additional lines"; the existing test pins exactly `"hello world\n"`.
- **Alternative rejected:** recreating the folder/script from scratch — no behavioural gain, and would break the existing test's expectations only if done wrong.

## 7. Risks & Constraints

- **Empty-looking PR:** the PR carries only a CHANGELOG line; reviewers must read the HLD/spec to see why (spec A1 risk). Mitigated by the PR description referencing the verification.
- **Byte-exact expectation without newline (A2):** a consumer comparing against 11 bytes would fail; out of the spec's reading, and changing it would break `tests/test_hello_sh.py`.
- **Executable bit:** depends on git's tracked mode `100755`; checkouts on filesystems that drop the bit (e.g. `core.fileMode=false` on Windows) would lose direct execution — not a supported platform for this repo's CI (`ubuntu-latest`).
- **Gate constraints (every PR):** layout gate rules 1–4 (`repo-gate/SKILL.md`) and `pytest` on Python 3.12 (`.factory/testing.md`, `.github/workflows/ci.yml`). No `CI_FAIL` file may be added. Scale/performance/security: not applicable (no input, no network, no privileges).

## 8. Assumptions

- A1–A3 from the spec are carried as written.
- The CHANGELOG bullet follows the existing style (`- <TICKET>: <description>.`), here keyed `SCRUM-26`.
