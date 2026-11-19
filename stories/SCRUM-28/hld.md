# HLD — SCRUM-28 Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** a bash script `hello-world/hello.sh` that prints `hello world`, alone in its folder at the repo root.
- **Verified existing state (on `main` = work-branch base, checked this turn):**
  - `hello-world/hello.sh` is tracked with mode `100755` (`git ls-files -s`), content `#!/bin/bash` / `echo "hello world"`, added in commit `65938b5`.
  - `ls -a hello-world` shows only `hello.sh` (no dotfiles either).
  - Running `./hello-world/hello.sh` emits exactly the bytes `hello world\n` (checked with `od -c`), exit 0, nothing on stderr (GNU bash 5.2).
  - `tests/test_hello_sh.py` already asserts all four acceptance criteria (stdout == `"hello world\n"`, return code 0, empty stderr, first line `#!/bin/bash`, user exec bit, folder contents == `["hello.sh"]`), and passes locally.
  - `CHANGELOG.md` `## Unreleased` has no entry for `hello-world/`.
- **Consequence:** the code and the spec agree; every functional criterion is already met. The only missing piece is the `CHANGELOG.md` line the repository gate (`PLAY-G4`) requires on every PR. This story is delivered as one verification PR (spec A1).

## 2. Architecture Overview

- Single repository `play1`; no services, no runtime dependencies beyond `/bin/bash`.
- Components: the script `hello-world/hello.sh`; its pytest coverage `tests/test_hello_sh.py` (subprocess-based, so it exercises the real file as a developer would run it); the release note in `CHANGELOG.md`.
- Follows the existing pattern of other repo shell scripts (`qa/s3-hello.sh`, `qa/20261110-s3/hello.sh`): shebang + executable bit + a pytest under `tests/` + a `CHANGELOG.md` line.

## 3. Data Flow Design

- Synchronous, stateless: developer runs `./hello-world/hello.sh` → bash executes `echo` → `hello world\n` on stdout → exit 0.
- CI: `.github/workflows/ci.yml` `test` job runs `pip install -e ".[test]"` then `pytest` (includes `tests/test_hello_sh.py`); `gate` job fails only if `CI_FAIL` exists at the root.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Print `hello world` | none → stdout `hello world\n`, exit 0 | play1 |
| `tests/test_hello_sh.py` | Prove the four acceptance criteria | runs the script as subprocess → pass/fail | play1 |
| `CHANGELOG.md` | Gate-required release line under `## Unreleased` | — | play1 |

## 5. Interface Contracts

- CLI: `./hello-world/hello.sh` with no arguments; stdout exactly `hello world\n`; stderr empty; exit code 0. Arguments, if passed, are ignored (the script never reads them) — no contract beyond that.
- No APIs, events or cross-repo contracts.

## 6. Key Technical Decisions

- **Keep script and test as they are.** Both already satisfy the criteria; rewriting them adds churn with no behavioral gain. Changing them is allowed only if the implementer finds a criterion unmet at build time.
- **Output contract is `hello world\n`** (one terminating newline, spec A2) — matches `echo` and the existing test; `printf 'hello world'` was rejected because it diverges from the test and from shell convention.
- **One PR** — the delivery is a single-line changelog addition plus verification; splitting would be micro-fragmentation.

## 7. Risks & Constraints

- Gate `PLAY-G4`: the PR must add a line under `## Unreleased` in `CHANGELOG.md`, else blocked.
- Gate rule 2 (exec + shebang) already holds; git mode must stay `100755` — a checkout on a filesystem without exec bits (or `core.fileMode=false`) must not commit a mode change.
- No new files may be added to `hello-world/` (FR3); the existing test would fail if one were.
- No scaling, performance or security surface: no input, no secrets, no network.
- `pytest` must pass and no `CI_FAIL` file may exist at the root (`.factory/testing.md`, `.github/workflows/ci.yml`).

## 8. Assumptions

- Spec A1–A4 are adopted as written. A1 (verification PR with no functional change) was confirmed against the code this turn.
- The folder-isolation test ignores dotfiles; there are none today, and Scenario 2 ("lists its contents") is read as a plain listing, so this is accepted.
