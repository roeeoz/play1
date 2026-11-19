# HLD — SCRUM-27 Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** a runnable `hello-world/hello.sh` that prints `hello world`, in a folder holding nothing else.
- **Finding (verified on the work branch at `88e990d`, base `main` at `b7b5d0a`):** the deliverable already exists and meets every acceptance criterion:
  - `hello-world/hello.sh` is tracked with git mode `100755`, content `#!/bin/bash` / `echo "hello world"` (31 bytes); it is the only entry in `hello-world/`.
  - Running it prints the bytes `hello world\n`, nothing on stderr, exit 0 — also from inside `hello-world/`, with an empty environment (`env -i`), and with stray arguments (they are ignored).
  - `tests/test_hello_sh.py` (6 tests: output, stderr, exactness, shebang, exec bit, folder isolation) passes locally and runs in the CI `test` job.
- **Responsibility of this story (spec A1):** keep the script unchanged and record SCRUM-27 in `CHANGELOG.md`, which the repository gate requires of every PR.

## 2. Architecture Overview

- Components: `hello-world/hello.sh` (existing, untouched), `tests/test_hello_sh.py` (existing, untouched — it already encodes Scenarios 1–4), `CHANGELOG.md` (one appended line).
- No external dependencies beyond `/bin/bash` on the runner (present on `ubuntu-latest`).
- Gates every PR meets: `.github/workflows/ci.yml` (`test`: `pip install -e ".[test]"` + `pytest`; `gate`: no `CI_FAIL` at root), `.factory/testing.md` (test-gate `pytest`), `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (rule 2: shell scripts executable with shebang; rule 4 / PLAY-G4: a line under `## Unreleased` in `CHANGELOG.md`).

## 3. Data Flow Design

- Synchronous, stateless: developer runs `./hello-world/hello.sh` → kernel resolves the `#!/bin/bash` shebang → `echo` writes `hello world\n` to stdout → exit 0. No inputs, no persisted state, no events.

## 4. Component Breakdown

| Component | Responsibility | In / Out | Repo | Change |
|---|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` | none / stdout `hello world\n`, exit 0 | play1 | none |
| `tests/test_hello_sh.py` | Assert Scenarios 1–4 | — | play1 | none |
| `CHANGELOG.md` | Traceability (FR5, PLAY-G4) | — | play1 | append one SCRUM-27 line under `## Unreleased` |

## 5. Interface Contracts

- CLI contract: `./hello-world/hello.sh` → stdout exactly `hello world` plus one terminating newline (spec A2), stderr empty, exit code 0; arguments and environment are ignored.
- No cross-repo contracts.

## 6. Key Technical Decisions

- **Reuse, don't recreate:** the existing script and test already satisfy FR1–FR4; rewriting them would add risk and no value. (Alternative rejected: a second script/folder — violates "no additional scripts" and FR2.)
- **Keep the existing newline semantics (A2):** `echo` output `hello world\n` stays; switching to `printf 'hello world'` would break `tests/test_hello_sh.py` and terminal UX.
- **One work item:** the only file change is the `CHANGELOG.md` line; splitting further would be micro-fragmentation.

## 7. Risks & Constraints

- **A1 risk:** if a fresh/different artefact was intended, this delivery adds no new code (accepted in the approved spec).
- **A2 risk:** a byte-exact consumer would see `hello world\n` rather than 11 bytes.
- **Exec bit:** must stay `100755` in git; any accidental touch of `hello.sh` that drops it fails `test_executable_permission` and repo-gate rule 2 — hence the work item must not modify the script.
- **Folder isolation:** adding any non-dot file to `hello-world/` (e.g. a README) fails `test_folder_contains_only_hello_sh`.
- No scale, performance or security concerns: no input, no network, no secrets.
