# High-Level Design — SCRUM-22 Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** `hello-world/hello.sh`, a bash script in its own top-level folder of play1 that prints `hello world` and exits 0 (spec FR1–FR5, Scenarios 1–4).
- **Current state (verified in the checkout, branch `halo/feat/scrum-22-20261119-012944` at `dbc3dccdeeb5`):**
  - `hello-world/hello.sh` exists, git mode `100755` (`git ls-files -s hello-world/`), content is exactly two lines: `#!/bin/bash` and `echo "hello world"` (LF line endings, trailing newline). It is the only file in `hello-world/`. Added in `65938b5`.
  - **Beyond what the spec records:** `tests/test_hello_sh.py` (commits `a2ec96d`, `9a5bd0b`) already asserts the script's behaviour — exit 0, stdout `== "hello world\n"`, empty stderr, first line `#!/bin/bash`, the user-execute bit, and that `hello-world/` lists only `hello.sh` (ignoring dot-files). It runs in the existing `test` job of `.github/workflows/ci.yml` via `pytest`. So the acceptance criteria are already covered by automated evidence, not only the manual checks the spec plans for.
- **Responsibility of this story:** keep that state true (spec A1), satisfy the repository gate, and attach evidence of Scenarios 1–4 to the pull request.

## 2. Architecture Overview

- One artefact, no services: `hello-world/hello.sh` (owned by this story; unchanged unless a check fails).
- Consumed, not changed: `tests/test_hello_sh.py` (existing assertions), `.github/workflows/ci.yml` (`test` + `gate` jobs), `.factory/testing.md` (test gate = `pytest`).
- Repository gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`: rule 2 (shell script executable + shebang — already true), rule 4 / `PLAY-G4` (a line under `## Unreleased` in `CHANGELOG.md` — the only file this story must change).
- No external dependencies; `/bin/bash` on the developer's machine is the runtime.

## 3. Data Flow Design

- Synchronous, single step: developer (or pytest via `subprocess`) executes `./hello-world/hello.sh` → kernel reads shebang → `/bin/bash` runs `echo` → `hello world\n` on stdout, nothing on stderr, exit 0.
- The script reads no input, environment, or working directory, so output is identical from any cwd (spec edge case).

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world`, exit 0 | none / stdout `hello world\n`, exit 0 | play1 |
| `CHANGELOG.md` `## Unreleased` entry | Satisfy gate rule 4 (`PLAY-G4`) | — / one added line naming SCRUM-22 | play1 |
| `tests/test_hello_sh.py` (existing, consumed) | Automated evidence of FR1–FR5 in CI | runs the script / pytest pass | play1 |

## 5. Interface Contracts

- **CLI contract:** `./hello-world/hello.sh` with no arguments → stdout exactly `hello world` + one `\n` (A2), stderr empty, exit code 0; first line `#!/bin/bash`; git mode `100755`.
- No APIs, events, or cross-repo contracts.

## 6. Key Technical Decisions

- **Keep the existing script (A1).** It already meets every criterion; rewriting it adds risk and no value. It is changed only if a check during implementation fails.
- **Executable bit lives in the git index** (mode `100755`), so it survives a fresh clone (FR3). Any edit must preserve it (`git update-index --chmod=+x` if needed).
- **No new tests or CI jobs.** The spec puts CI integration out of scope; the existing `tests/test_hello_sh.py` already runs in CI and is left as is. The PR evidence is the green `test` job plus a recorded manual run of Scenarios 1–4 (including from inside `hello-world/`).
- **One work item.** A single XS change in one repo; splitting it would be fragmentation.

## 7. Risks & Constraints

- **Near-empty diff (A1):** the PR's only file change is the `CHANGELOG.md` line. Acceptable per spec; reviewers should expect it.
- **`PLAY-G4`:** a PR without the `CHANGELOG.md` line is blocked — the line is mandatory.
- **Existing test vs. A2:** `tests/test_hello_sh.py` asserts `stdout == "hello world\n"`, which matches A2. If someone reads "exactly" as no newline, both script and test would have to change — out of scope under A2.
- **Folder isolation test ignores dot-files:** a stray `.gitkeep`/`.DS_Store` in `hello-world/` would break Scenario 2 without failing CI; the implementer verifies with `git ls-files hello-world/` and `ls -A hello-world/`.
- **Line endings / mode:** a CRLF edit or lost mode would break direct execution; both are checked in the evidence.
- No scale, performance, or security concerns: a static two-line script with no input.
