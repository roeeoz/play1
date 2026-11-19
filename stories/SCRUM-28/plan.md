# Plan — SCRUM-28 Hello world bash script in a dedicated folder

## Context

SCRUM-28 asks for a bash script `hello-world/hello.sh` at the repository root that runs directly (shebang `#!/bin/bash` plus executable bit), prints exactly `hello world` and exits 0, alone in its folder (four Given/When/Then criteria, AC1–AC4 in `spec.md` §5). The change lands in `play1` on the work branch `halo/feat/scrum-28-20261119-024453`, merging into `main`. The script and its test already exist on `main` and meet every criterion, so the story is delivered as a verification pull request whose only diff is the `CHANGELOG.md` line gate `PLAY-G4` requires (spec A1, `hld.md` §1). `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-28/`.

## Research findings

Facts read from the checkout at `4102b0c`:

- **Script.** `hello-world/hello.sh:1` is `#!/bin/bash`; `hello-world/hello.sh:2` is `echo "hello world"`. Git index mode is `100755` (`git ls-files -s hello-world`). `ls -a hello-world` lists only `hello.sh`. Running `./hello-world/hello.sh` emits the bytes `hello world\n` (`od -c`). Introduced in `65938b5`; tests in `a2ec96d`.
- **Test.** `tests/test_hello_sh.py` runs the script as a subprocess with no `bash` prefix and asserts: return code 0 and stdout `"hello world\n"` (`tests/test_hello_sh.py:10-15`), empty stderr (`:17-21`), stripped and exact output (`:23-28`), first line `#!/bin/bash` (`:32-34`), `S_IXUSR` set (`:36-38`), non-dot folder contents `== ["hello.sh"]` (`:40-43`).
- **Changelog.** `CHANGELOG.md:3` is `## Unreleased`; entries `CHANGELOG.md:5-8` use the form `- <KEY>: add \`<path>\`, a ... script that prints \`<text>\`.` No line mentions `hello-world/`.
- **Gate rules.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rule 2 (new shell script executable + shebang) already holds; rule 4 (`PLAY-G4`) blocks a PR whose diff does not add a line under `## Unreleased` in `CHANGELOG.md`; rule 3 caps files at 200 KB.
- **Canonical gate.** `.factory/testing.md`: `pip install -e ".[test]"` then `pytest` (Python 3.12), one required layer `package-api` (`runBy: canonical-gate`). `.github/workflows/ci.yml` jobs `test` (install + `pytest`) and `gate` (fails iff `CI_FAIL` exists at root). `pyproject.toml` sets `testpaths = ["tests"]`, so `tests/test_hello_sh.py` is collected. No linter, formatter or type checker is configured.
- **Change surface.** One file: `CHANGELOG.md`. No API, schema, cross-repo or external data dependency. `README.md` and `docs/` do not reference `hello-world/`.
- **Remaining unknowns.** None. `core.fileMode` is `true` in this checkout, so a mode change would be visible in the diff.

## Locked decisions and assumptions

Locked decisions:

- Script path, name, shebang, executable bit, exact output and folder isolation — `spec.md` §3 FR1–FR4, §5 AC1–AC4.
- Output contract is `hello world\n` (one terminating newline) — spec A2, `hld.md` §6.
- Delivery is a verification PR; script and test stay unchanged unless a criterion is found unmet — spec A1, `hld.md` §6, work item `t1`.
- `CHANGELOG.md` gains one line under `## Unreleased` — gate `PLAY-G4`, spec A3.
- One work item, `t1` — `work-items.md`.

Assumptions:

- The changelog line counts as gate-required, not as "documentation files" excluded by the story (spec A3). Evidence: `PLAY-G4` admits no exemption. If wrong: reviewer asks to drop it, and the gate then blocks — conflict goes back to the PO.
- The folder-isolation test ignoring dotfiles is acceptable (`hld.md` §8). Evidence: no dotfiles exist in `hello-world/`. If wrong: a hidden file added later would not be caught; no impact on this PR.

## Solution proposal

Add a single line to `CHANGELOG.md` under `## Unreleased`, after the last existing entry (`CHANGELOG.md:8`), in the house style: `- SCRUM-28: add \`hello-world/hello.sh\`, a bash script that prints \`hello world\`.` Leave `hello-world/hello.sh` and `tests/test_hello_sh.py` byte- and mode-identical; they already prove AC1–AC4 through the canonical `pytest` layer, which executes the real file as a developer would.

Key decisions:

- **Reuse the existing test as evidence** instead of writing a new one: it already covers every criterion at the repo's only test layer; a duplicate adds churn.
- **Append, not reorder**: entries in `## Unreleased` are chronological; appending keeps the diff to one added line.

Alternatives rejected:

- Rewriting the script with `printf` — diverges from the test and spec A2.
- Adding a README in `hello-world/` — violates FR3 and the story's non-goals.
- A shell-level test under `qa/` (like `qa/20261110-s3/test_hello.sh`) — not part of the canonical gate; pytest already covers it.

## Ordered implementation steps

1. **Verify AC1–AC4 on the work branch before editing.** Confirm `git ls-files -s hello-world` shows only `hello.sh` at `100755`, `head -1 hello-world/hello.sh` is `#!/bin/bash`, and `./hello-world/hello.sh` prints `hello world\n` with exit 0 and empty stderr. Files: `hello-world/hello.sh` (read only). Advances AC1–AC4. Covered by `tests/test_hello_sh.py` (layer `package-api`). If any check fails, fix only the failing aspect in `hello-world/hello.sh` (content or mode) — not expected.
2. **Add the changelog entry.** Append `- SCRUM-28: add \`hello-world/hello.sh\`, a bash script that prints \`hello world\`.` as a new line directly after `CHANGELOG.md:8`, keeping `## Unreleased` as its heading and the file's trailing newline. Advances gate `PLAY-G4` (work-item `t1` criterion). No test layer covers changelog content; the PR gate `repo-gate` rule 4 is its check.
3. **Run the canonical gate.** `pip install -e ".[test]"` then `pytest` from the repo root; dependencies are acquired by that install from PyPI (no warm cache assumed). Confirm no `CI_FAIL` exists at the root. Advances AC1–AC4 (evidence). Layer `package-api`.
4. **Check the diff scope.** `git diff --stat main...HEAD` (excluding `stories/SCRUM-28/`) shows only `CHANGELOG.md`, one added line; `git diff main...HEAD -- hello-world` is empty (no mode change). Advances work-item `t1` scope criterion. No test layer; reviewed by diff inspection.

Implicit invariants: no authz, tenancy, concurrency or input-validation surface exists (the script takes no input). No generated deliverables; no binary assets, so `.factory/delivery-assets` is not touched.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Verify hello-world/hello.sh against SCRUM-28 criteria and add CHANGELOG entry |
| 2 | t1 | Verify hello-world/hello.sh against SCRUM-28 criteria and add CHANGELOG entry |
| 3 | t1 | Verify hello-world/hello.sh against SCRUM-28 criteria and add CHANGELOG entry |
| 4 | t1 | Verify hello-world/hello.sh against SCRUM-28 criteria and add CHANGELOG entry |

AC coverage: AC1 → `test_prints_hello_world`, `test_no_stderr`; AC2 → `test_folder_contains_only_hello_sh`; AC3 → `test_shebang_line`, `test_executable_permission`, plus every subprocess test invoking the script without `bash`; AC4 → `test_exact_output_no_extra_whitespace`.

## Verification and CI gate

- Canonical gate, in order, run once locally on the committed SHA: `pip install -e ".[test]"` then `pytest` (repo root, Python ≥3.10; CI uses 3.12). Runs unprivileged in a pod.
- Required layer: `package-api` (`pytest`), `runBy: canonical-gate` — the provider run of `.github/workflows/ci.yml` job `test` at the PR head is authoritative per `.factory/testing.md`.
- The `gate` job must be green: no `CI_FAIL` file at the root.
- PR gate `repo-gate`: rule 4 satisfied by the `CHANGELOG.md` line; rules 1–3 unaffected.
- No provider CI configuration change is needed (CI is out of scope per the story). No `.factory/delivery-assets` obligation.
- Done means: `pytest` passes in full including all six tests in `tests/test_hello_sh.py`, both CI jobs are green at the head, and the diff outside `stories/SCRUM-28/` is the single `CHANGELOG.md` line.

## Risks and scope guards

Risks:

- **Mode drift.** An editor or filesystem without exec bits could commit `hello-world/hello.sh` as `100644`, breaking AC3 and `test_executable_permission`. Mitigation: step 4 diff check on `hello-world/`.
- **Changelog merge conflict** with another story appending to `## Unreleased`. Mitigation: append at the end; resolve by keeping both lines.

Do NOT:

- Modify `hello-world/hello.sh` or `tests/test_hello_sh.py` unless step 1 finds a criterion unmet.
- Add any file to `hello-world/` (README, `.gitkeep`, etc.) or any documentation for the script.
- Edit or reorder existing `CHANGELOG.md` entries, `README.md`, `docs/`, `qa/`, `src/`, `pyproject.toml` or `.github/workflows/ci.yml`.
- Add CI/CD integration, extra scripts, or a new test harness.
- Skip, delete, weaken or `xfail` any test (including the dotfile filter in `test_folder_contains_only_hello_sh`) to make the gate green; a failing check is reported blocked.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
