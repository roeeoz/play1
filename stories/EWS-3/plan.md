## Context

EWS-3 adds one static markdown file, `docs/live-e2e/e2e-w21-x.md`, to `roeeoz/play1`. The file records the verification run `e2e-w21-x` as evidence that the delivery line works end to end. There are three acceptance criteria: (1) the file exists at that exact path with that exact content; (2) no existing file is modified; (3) the change is documentation only, with no runtime change and no added test. The work branch `halo/feat/ews-3-20261118-154958` was cut from `main`, and its pull request targets `main`. The approved requirement (`spec.md`), the design (`hld.md`) and the breakdown (`work-items.md`, a single item `t1`) are in the same folder as this file, `stories/EWS-3/`.

## Research findings

- **Change surface.** The only change is the new file `docs/live-e2e/e2e-w21-x.md`. Neither `docs/live-e2e/` nor the file exists yet; `ls docs` shows only `argo-agent-runs.md` and `plans/`. No module, contract, schema or shared constant is touched.
- **Packaging.** Nothing reads or ships `docs/`. `pyproject.toml:23-24` limits package discovery to `src` (`[tool.setuptools.packages.find] where = ["src"]`), and `pyproject.toml:9` points `readme` at `README.md` only.
- **Ignore rules.** `.gitignore` excludes only `docs/_build/` under `docs/`, so the new path is tracked.
- **Byte-altering tooling.** The repo root has no `.editorconfig`, `.gitattributes`, markdownlint or pre-commit configuration, so nothing in the repo rewrites line endings or whitespace on commit.
- **Gate.** The canonical gate is defined in `.factory/testing.md` and `.github/workflows/ci.yml`. The `test` job runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. `pytest` is limited to `tests/` (`pyproject.toml:26-28`, `testpaths = ["tests"]`). The `gate` job fails only if a root `CI_FAIL` exists (`.github/workflows/ci.yml:31-37`). Neither job reads `docs/`, so this change cannot affect either result.
- **Test layers.** `.factory/testing.md` declares one layer, `package-api` (`pytest`, `runBy: canonical-gate`). No layer checks documentation content. Under FR3 the content is verified by inspecting bytes, not by a test.
- **Repo memory.** There is no `.factory/memory/` directory and no `AGENTS.md` or `CLAUDE.md`.
- **External data.** None.
- **Unknowns remaining.** None. Whether the file ends with a newline was resolved by the spec's working assumption (§8) and by `hld.md` §6: it ends with one LF.

## Locked decisions and assumptions

**Locked decisions**
- The path is exactly `docs/live-e2e/e2e-w21-x.md` (spec FR1).
- The content is exactly `# Live coding proof`, LF, LF, `Run: e2e-w21-x`, LF. That is 36 bytes: UTF-8, no BOM, no CRLF, no trailing whitespace, no front-matter (spec FR2; `hld.md` §5).
- The change set is one added product file. No existing file changes, including `README.md`, `CHANGELOG.md`, config and CI files, and no test is added (spec FR3 and non-goals; `hld.md` §6).
- There is one work item, `t1` (`work-items.md`).
- The base and pull-request target are both `main` (the platform's frozen target branch).

**Assumptions**
- **The file ends with a single trailing LF.** Evidence: spec §8 and `hld.md` §6. If wrong, a byte-exact check that expects no final newline fails, and the fix is to drop the last byte.
- **The `stories/EWS-3/` plan documents in the PR diff do not count as product files under FR3.** Evidence: `hld.md` §7. If wrong, the reviewer counts more than one added file. This is not something the implement phase can change, because the platform commits that folder.

## Solution proposal

Create `docs/live-e2e/e2e-w21-x.md` with the 36-byte content above, written so that no editor-inserted CRLF, BOM or trailing whitespace can appear. A `printf '# Live coding proof\n\nRun: e2e-w21-x\n'` redirected into the file is one way to do that. Creating the file also creates the directory. Nothing else changes.

Key decisions:
- **Do not add an index, README link or CHANGELOG entry.** The spec's non-goals forbid touching existing files, and the repo has no docs index.
- **Do not add a test.** FR3 forbids adding one. Acceptance comes from a byte check of the committed blob plus the unchanged gate.

Alternatives considered:
- **A pytest that asserts the file content.** Rejected: it violates FR3 and AC 3.
- **A `.gitattributes` rule to pin LF.** Rejected: it modifies or adds a config file outside scope, and `printf` already guarantees the bytes.

## Ordered implementation steps

1. **Create `docs/live-e2e/e2e-w21-x.md` with the exact 36-byte content.** Advances AC 1. No existing test layer covers documentation content, and FR3 forbids adding one, so this step is verified by the byte check in step 2.
2. **Verify the bytes of the committed file.**
   - `xxd docs/live-e2e/e2e-w21-x.md` (or `od -c`) must show exactly `# Live coding proof\n\nRun: e2e-w21-x\n`.
   - `wc -c` must report `36`.
   - The file must contain no `\r` and must not start with the bytes `ef bb bf` (a BOM).

   Advances AC 1. The layer is a manual byte inspection, not a test layer.
3. **Verify the change set against `main`.** `git diff --name-status main...HEAD -- . ':!stories/EWS-3'` must list exactly `A	docs/live-e2e/e2e-w21-x.md`, with no `M`, `D` or `R` entries. Advances AC 2 and AC 3. The layer is diff inspection.
4. **Run the canonical gate.** Run `pip install -e ".[test]"` and then `pytest` from the repo root. The result must match `main`: all green, with no tests added or removed. Advances AC 3. The layer is `package-api` (the `pytest` canonical gate).

Implicit invariants:
- Authorization, tenancy, concurrency, idempotency and validation are not applicable, because this is a static file with no runtime.
- No dependencies are acquired beyond the gate's own editable install.
- There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add docs/live-e2e/e2e-w21-x.md live proof document |
| 2 | t1 | Add docs/live-e2e/e2e-w21-x.md live proof document |
| 3 | t1 | Add docs/live-e2e/e2e-w21-x.md live proof document |
| 4 | t1 | Add docs/live-e2e/e2e-w21-x.md live proof document |

Every work item has at least one step.

## Verification and CI gate

- **Canonical gate.** Run `pip install -e ".[test]"`, then `pytest`, from the repo root on Python 3.12 (`.factory/testing.md`; `.github/workflows/ci.yml:20-23`). Run it once locally on the committed SHA. Provider CI re-runs it at the PR head, and that provider run is the authoritative result.
- **Required layers.** The only required layer is `package-api` (`pytest`), and it can run in a pod.
- **CI `gate` job.** It must stay green. No root `CI_FAIL` may be created.
- **Provider CI configuration.** None is needed. CI is the repo's own and is not part of this change.
- **Delivery assets.** `.factory/delivery-assets` has no obligation for this change, because no binary is added.
- **Done means all of the following:**
  - the step 2 byte check shows exactly the 36 specified bytes;
  - the step 3 diff shows one added product file and nothing modified;
  - `pytest` passes with the same test count as `main`;
  - both CI jobs, `test` and `gate`, are green at the PR head.

## Risks and scope guards

**Risks**
- **Editor or tool byte drift** (CRLF, BOM, trailing space, missing or doubled final newline). Mitigation: write the file with `printf`, then run the step 2 hex and size check.
- **The reviewer counts the `stories/EWS-3/` plan files as part of the change.** Mitigation: the PR description states that the only product file is `docs/live-e2e/e2e-w21-x.md`.

**Scope guards: the implement phase must NOT do any of the following**
- Modify, rename or delete any existing file, including `README.md`, `CHANGELOG.md`, `pyproject.toml`, `.gitignore` and `.github/workflows/ci.yml`.
- Add a test, a `conftest.py`, a `.gitattributes`, an `.editorconfig` or any lint config.
- Add front-matter, extra headings, links or any other proof files to the document.
- Create a root `CI_FAIL` file.
- Edit `stories/EWS-3/spec.md`, `stories/EWS-3/hld.md` or `stories/EWS-3/work-items.md`.
- Skip, disable or weaken any check. A failing check may be reported as blocked but never made green that way.

## Clarification outcomes

None.

Reviewer note (e2e-w21-x): checked at plan review.
