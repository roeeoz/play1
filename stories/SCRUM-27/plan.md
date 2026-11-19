# Plan — SCRUM-27 Hello world bash script in a dedicated folder

## Context

SCRUM-27 asks for `hello-world/hello.sh`, a bash script that prints exactly `hello world`. It must sit alone in a dedicated `hello-world` folder, start with a `#!/bin/bash` shebang and be executable (Scenarios 1–4 in `spec.md` §5). The change lands in `play1` on the work branch `halo/feat/scrum-27-20261119-024045`, which was cut from `main`. The approved spec (Assumption A1) and the design both record that this deliverable already exists on `main` and meets every acceptance criterion. The delivery therefore keeps the script and its test unchanged and adds the one `CHANGELOG.md` line the repository gate requires. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-27/`.

## Research findings

All findings were observed on the work branch at `f860c55`. Its diff against `main` touches only `stories/SCRUM-27/`.

- **Script (exists, untouched):** `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. The git index entry is `100755 2a43bb26…`. Running `./hello-world/hello.sh` from the repo root writes the bytes `hello world\n` and exits `0`. `hello-world/` contains only `hello.sh`.
- **Test (exists, untouched):** `tests/test_hello_sh.py` holds 6 tests that cover the acceptance criteria:
  - output and exit code: `:10-15`, Scenario 1
  - empty stderr: `:17-21`
  - exactness: `:23-28`, Scenario 4, which asserts `"hello world\n"`
  - shebang: `:32-34`, Scenario 3
  - exec bit: `:36-38`, Scenario 3
  - folder isolation: `:40-43`, Scenario 2, which ignores dotfiles

  `pyproject.toml` (`testpaths = ["tests"]`) picks the file up.
- **Changelog:** `CHANGELOG.md:3` is `## Unreleased`. `CHANGELOG.md:5-8` hold the entries for PLAY-114, PLAY-156, PLAY-172 and PLAY-175, each in the form `- <KEY>: add \`<path>\`, … that prints \`…\`.`. The file ends with a single `\n` after line 8.
- **Repository gate:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` has two rules that matter here:
  - Rule 4 (`PLAY-G4`, blocker): every PR adds a line under `## Unreleased` in `CHANGELOG.md`.
  - Rule 2: a *new* shell script must be executable and start with a shebang. This rule is not triggered, because no script is added.
- **Test gate:** `.factory/testing.md` declares `test-gate: pytest` with one required layer, `package-api` (`pytest`, `runBy: canonical-gate`). CI is `.github/workflows/ci.yml`:
  - job `test`: `pip install -e ".[test]"`, then `pytest`, on Python 3.12
  - job `gate`: fails iff `CI_FAIL` exists at the repo root

  No linter, formatter or type checker is configured.
- **Contracts:** CLI only — stdout `hello world\n`, stderr empty, exit `0`. There are no cross-repo or external data dependencies.
- **Exists vs. to create:** everything exists except the SCRUM-27 changelog line.
- **Unknowns remaining:** none.

## Locked decisions and assumptions

**Locked decisions**
- Reuse the existing `hello-world/hello.sh` and `tests/test_hello_sh.py`. Do not create a second script or folder. Source: `spec.md` §1 A1, `hld.md` §6.
- Output is `hello world` plus one terminating newline. Source: `spec.md` FR4 / A2 and `tests/test_hello_sh.py:15,28`.
- Exactly one new line under `## Unreleased` in `CHANGELOG.md`, starting `- SCRUM-27:`. Source: `work-items.md` t1, repo-gate rule 4 (PLAY-G4), `spec.md` FR5 / A3.
- No CI, README or docs changes. Source: `spec.md` §2 Non-Goals, `work-items.md` t1.
- One work item, t1. Source: `work-items.md`.

**Assumptions**
- Append the new line after the PLAY-175 entry (`CHANGELOG.md:8`), matching the file's chronological order. Evidence: the existing entries are appended in story order, and t1 says "after the existing entries". If this is wrong, only the line position changes; the gate is unaffected.
- The CI runner's `/bin/bash` and the preserved exec bit keep the existing tests green. Evidence: CI runs on `ubuntu-latest`, and `actions/checkout` preserves mode `100755`. If this is wrong, `test_prints_hello_world` fails, which would equally fail on `main` today.

## Solution proposal

No product code changes. The acceptance criteria are already met on `main`, so the delivery has two parts:

1. **Confirm the criteria with the existing tests.** `tests/test_hello_sh.py` already proves Scenarios 1–4 through the repository's only test layer.
2. **Add traceability.** Add one `CHANGELOG.md` line for SCRUM-27 so the PR passes repo-gate rule PLAY-G4.

Proposed line, following the existing entry style:

`- SCRUM-27: add \`hello-world/hello.sh\`, a script in its own folder that prints \`hello world\`.`

If "add" reads as misleading for an existing file, the alternative is a "confirm …" wording. Either wording satisfies t1, so the implementer may choose. The line must start `- SCRUM-27:` and name `hello-world/hello.sh` and `hello world`.

Alternatives rejected:
- **Rewrite the script with `printf 'hello world'`.** This breaks `tests/test_hello_sh.py:15,28` and contradicts spec A2.
- **Add a new script, folder or test.** This violates "no additional scripts" and the folder-isolation criterion, and the coverage it would add already exists.
- **Add a README in `hello-world/`.** This fails `test_folder_contains_only_hello_sh` and the "no documentation files" non-goal.

## Ordered implementation steps

1. **Change `CHANGELOG.md`.** Insert one line after `CHANGELOG.md:8`:
   - Start the line with `- SCRUM-27:` and describe `hello-world/hello.sh` printing `hello world`.
   - Keep line 1 (`# Changelog`), line 3 (`## Unreleased`) and lines 5–8 byte-identical.
   - End the file with a single trailing newline.

   Advances: FR5, the t1 changelog criterion and repo-gate PLAY-G4. Test layer: no pytest layer covers the changelog. The repo-gate review (`mr-gate` slot) checks it, and a `git diff` inspection confirms it.
2. **Leave the consumed files alone.** Do not edit, re-create, chmod or reformat `hello-world/hello.sh`, `tests/test_hello_sh.py` or `.github/workflows/ci.yml`. Before running the gate, confirm three things:
   - `git diff --name-only main...HEAD` lists only `CHANGELOG.md`, plus the platform's `stories/SCRUM-27/` files.
   - `git ls-files -s hello-world` shows a single entry, `100755 2a43bb26…`.
   - No `CI_FAIL` file exists at the repo root.

   Advances: Scenarios 1–4 (unchanged artefact) and the t1 "touches no other file" criterion. Test layer: `package-api` (`tests/test_hello_sh.py`, all 6 tests).
3. **Run the canonical gate.** Run `pip install -e ".[test]"`, then `pytest`, from the repo root. Dependencies come from PyPI through that install; do not assume a warm cache. Advances: Scenarios 1–4 and the t1 gate criterion. Test layer: `package-api`.

Implicit invariants: there are no inputs, authorization, tenancy, concurrency or persisted state. The only invariants are the error-path ones: stderr stays empty and the exit code stays `0`. The existing tests already assert both. There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1, 2, 3 | t1 — SCRUM-27: confirm hello-world/hello.sh and record it in CHANGELOG.md |

Every work item is mapped.

## Verification and CI gate

- **Canonical gate:** run `pip install -e ".[test]"`, then `pytest`, once locally from the repo root on the committed SHA. This is the same command as the `test` job in `.github/workflows/ci.yml`. The provider CI run at the exact head is authoritative (`.factory/testing.md`, `runBy: canonical-gate`).
- **Required layers:** `package-api` (`pytest`) is the only declared layer, and it runs unprivileged in a pod. The `gate` CI job must be green, so no `CI_FAIL` may exist at the repo root.
- **Repo-gate review (`mr-gate`):** it must report `pass: true` with no `PLAY-G4` finding.
- **What the gate must show:**
  - `pytest` passes, including all 6 tests in `tests/test_hello_sh.py`, with no skipped or deselected tests from that file.
  - The diff is limited to `CHANGELOG.md`, plus the plan folder.
  - `hello-world/hello.sh` keeps mode `100755` and its blob `2a43bb26…`.
- **Not needed:** no provider CI configuration changes and no `.factory/delivery-assets` entries.

## Risks and scope guards

**Risks**
- *Spec A1:* if the story's author wanted a fresh artefact, this delivery adds no new code. The approved spec accepts this risk.
- *Spec A2:* a byte-exact consumer sees `hello world\n`. The approved spec accepts this risk, and the existing test locks the behaviour in.
- *Exec bit loss:* any accidental touch of `hello.sh` could drop mode `100755`, which fails `test_executable_permission`. Mitigation: step 2's `git ls-files -s` check.

**The implement phase must NOT:**
- Modify, re-create, chmod or reformat `hello-world/hello.sh`.
- Add any file to `hello-world/`.
- Edit `tests/test_hello_sh.py`, `.github/workflows/ci.yml`, `.factory/`, `README.md` or `pyproject.toml`.
- Edit or reorder the existing `CHANGELOG.md` entries or headings.
- Add any new script, test, docs file or CI step.
- Edit `stories/SCRUM-27/spec.md`, `hld.md` or `work-items.md`.
- Create `CI_FAIL`.
- Skip, deselect, `xfail` or weaken any test to get green. If a check fails, report it as blocked.

## Clarification outcomes

None.
