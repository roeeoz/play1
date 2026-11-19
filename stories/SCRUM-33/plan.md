# Plan — SCRUM-33 Hello world bash script in a dedicated folder

## Context

SCRUM-33 asks for `hello-world/hello.sh` at the root of the `play1` repository: a script that starts with `#!/bin/bash`, is executable, prints exactly `hello world` and exits 0, and is the only file in `hello-world/` (spec scenarios 1–4). The script and its tests already exist on `main`, so the spec (FR5, assumption A1) and the design limit this story to one `CHANGELOG.md` bullet. That bullet records the delivery and satisfies repo-gate rule 4. The change lands on the work branch `halo/feat/scrum-33-20261119-040915`, which was cut from `main` and merges into `main`. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/SCRUM-33/`.

## Research findings

- **Script (exists, unchanged):** `hello-world/hello.sh:1` is `#!/bin/bash`. `hello-world/hello.sh:2` is `echo "hello world"`. Git index mode is `100755` (blob `2a43bb26`). `hello-world/` tracks only `hello.sh`.
- **Tests (exist, unchanged):** `tests/test_hello_sh.py` covers every acceptance criterion:
  - stdout `== "hello world\n"` and exit 0 (`:10-15`)
  - empty stderr (`:17-21`)
  - exact output (`:23-28`)
  - shebang (`:32-34`)
  - executable bit (`:36-38`)
  - folder holds only `hello.sh` (`:40-43`)
- **Change surface:** only `CHANGELOG.md`. The `## Unreleased` heading is at `CHANGELOG.md:3`. Bullets run from `CHANGELOG.md:5` to `CHANGELOG.md:8`, the last one being `PLAY-175`. They follow the style `- <KEY>: add \`<path>\`, a … script that prints \`<text>\`.`
- **Repo gate:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:17-20`, rule 4: if `CHANGELOG.md` is not touched, the gate raises blocker `PLAY-G4`. Rule 2 (`:15`) applies only to new shell scripts, and this story adds none. Rule 3 (`:16`) caps each file at 200 KB.
- **Test gate:** `.factory/testing.md` declares one required layer, `package-api` (`pytest`, `runBy: canonical-gate`). CI `test` job (`.github/workflows/ci.yml:12-24`) runs `pip install -e ".[test]"`, then `pytest`, on Python 3.12. The `gate` job (`ci.yml:26-38`) fails only if `CI_FAIL` exists at the root. It does not exist on this branch.
- **Other context:** no linter or formatter is configured. No `.factory/memory/` or `.factory/delivery-assets` exists. There are no external data dependencies.
- **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**
- Keep `hello-world/hello.sh` and `tests/test_hello_sh.py` byte-identical. Source: spec FR5/A1, hld §6, work item t1.
- Add exactly one `- SCRUM-33: …` bullet, appended after the existing bullets under `## Unreleased`. Source: spec FR5, hld §5, t1 AC 1.
- The output contract is `hello world\n`; the single terminating newline is allowed. Source: spec A2, `tests/test_hello_sh.py:15`.
- The out-of-scope "documentation files" means files inside `hello-world/`, not the changelog. Source: spec A3.
- Use one work item, t1, with no new test. Source: hld §6.

**Assumptions**
- **Bullet wording:** `- SCRUM-33: deliver the hello-world bash script via the existing \`hello-world/hello.sh\`, which prints \`hello world\`.`
  - Evidence: the existing bullet style and the t1 AC wording.
  - If wrong: only cosmetic. A reviewer can reword it without effect on the gate.

## Solution proposal

The behaviour already exists, so this story adds no code. Append one bullet at the end of the `## Unreleased` list in `CHANGELOG.md`, after `CHANGELOG.md:8`. The bullet states that SCRUM-33 is delivered by the existing `hello-world/hello.sh`, which prints `hello world`. The existing `tests/test_hello_sh.py` proves acceptance criteria 1–4 in the canonical `pytest` gate. The changelog line satisfies repo-gate rule 4.

Appending at the end of the list keeps conflicts with concurrent `## Unreleased` edits to one line.

Alternatives rejected:
- **Rewrite the script or test:** churn with no change in behaviour (spec A1).
- **Add a README in `hello-world/`:** breaks FR4 and fails `test_folder_contains_only_hello_sh`.
- **Close the story with no PR:** contradicts FR5, and every PR needs the changelog line anyway.

## Ordered implementation steps

1. **Verify the baseline without changing it.**
   - Confirm that `git ls-files -s hello-world` shows only `hello-world/hello.sh` at mode `100755`.
   - Confirm that running `./hello-world/hello.sh` gives `hello world\n` on stdout, empty stderr and exit 0.
   - Confirm that `CI_FAIL` is absent at the root.
   - Advances AC 1–4 and t1 ACs 2–3, 5. Test layer: `package-api` (`tests/test_hello_sh.py`).
2. **Append the bullet.** Add the `- SCRUM-33: …` bullet in `CHANGELOG.md` as a new line after the `PLAY-175` bullet, in the style above.
   - Keep existing lines and the trailing newline unchanged.
   - Advances t1 AC 1 and repo-gate rule 4 (`PLAY-G4`).
   - No test layer covers changelog content: the repo gate (`mr-gate` slot) checks it.
3. **Run the gate.** Run `pip install -e ".[test]" && pytest` from the repo root and confirm that it passes, including all six tests in `tests/test_hello_sh.py`.
   - Confirm that `git diff --stat main...HEAD` shows only `CHANGELOG.md` outside `stories/SCRUM-33/`.
   - Advances t1 ACs 2 and 4. Test layer: `package-api`.

Implicit invariants: there is no input, authz, tenancy, concurrency or error path. Dependencies come only from `pip install -e ".[test]"` (pytest, pypdf), with no warm cache assumed. There are no generated deliverables.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Record SCRUM-33 hello-world script delivery in CHANGELOG |
| 2 | t1 | Record SCRUM-33 hello-world script delivery in CHANGELOG |
| 3 | t1 | Record SCRUM-33 hello-world script delivery in CHANGELOG |

Every work item has at least one step.

## Verification and CI gate

- **Canonical gate:** run `pip install -e ".[test]"`, then `pytest`, from the repo root. Run it once on the committed SHA.
  - It runs unprivileged in a pod.
  - The provider CI `test` job at the exact head is the authoritative result (`.factory/testing.md`).
- **Required layers:** `package-api` (`pytest`) only.
- **CI configuration:** no change needed. The `gate` job must stay green, so `CI_FAIL` stays absent.
- **Delivery obligations:** none, because no `.factory/delivery-assets` is needed and no binary is added.
- **What done looks like:**
  - `pytest` is fully green, including the six `tests/test_hello_sh.py` tests.
  - The repo gate passes with no `PLAY-G4`.
  - The diff touches only `CHANGELOG.md`, with one added line.
  - `hello-world/hello.sh` is unchanged at mode `100755`.

## Risks and scope guards

**Risks**
- **The PR carries no product change (spec A1).** Mitigation: the human reviewer can close it if SCRUM-33 was expected to produce new code.
- **Conflict in `## Unreleased`.** Mitigation: append a single line at the end of the list. On conflict, keep both lines.

**Do NOT:**
- modify, rename, move or chmod `hello-world/hello.sh`;
- add any file to `hello-world/`, including a README or `.gitkeep`;
- modify `tests/test_hello_sh.py` or add tests;
- touch `qa/`, `src/`, `.github/workflows/ci.yml`, `.factory/`, `README.md` or other changelog entries;
- create `CI_FAIL`;
- skip, xfail, delete or weaken any test or gate check. A failing check is reported, not silenced.

## Clarification outcomes

None.
