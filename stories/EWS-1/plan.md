# Implementation plan — EWS-1: `e2e-w21-a` live proof document

## Context

EWS-1 adds one static Markdown file, `docs/live-e2e/e2e-w21-a.md`, to `roeeoz/play1`. The file records the live verification run `e2e-w21-a`. The acceptance criteria are: (1) the file exists at that exact path with exactly the bytes `# Live coding proof\n\nRun: e2e-w21-a\n`; (2) no existing file is modified; (3) documentation only, no runtime change and no new test. The work lands on branch `halo/feat/ews-1-20261118-154958`, which was cut from `main` and merges back into it. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/EWS-1/`.

## Research findings

- **Change surface.** `docs/` exists and holds `docs/argo-agent-runs.md` and `docs/plans/`. `docs/live-e2e/` does not exist yet, so the new file creates it. Nothing else in the repository refers to `docs/live-e2e`.
- **Not runtime.** Packaging only includes `src` (`pyproject.toml:27-28`, `where = ["src"]`), and pytest only collects `tests` (`pyproject.toml:31`, `testpaths = ["tests"]`). A file under `docs/` is neither packaged nor collected.
- **Byte-level rules.** The repository root has no `.gitattributes` and no `.editorconfig`, so nothing rewrites line endings or the final newline. `.gitignore` has no rule that matches `docs/live-e2e/` (its only `docs` rule is `docs/_build/`).
- **Contract.** The file's path and bytes are the only contract: `# Live coding proof\n\nRun: e2e-w21-a\n` (36 bytes, LF line endings, one trailing newline). There are no APIs, schemas or cross-repo values.
- **Gate.** `.factory/testing.md` declares the gate `pytest`, run after `pip install -e ".[test]"`. It has one required layer, `package-api` (production-path, `runBy: canonical-gate`). `.github/workflows/ci.yml` runs it in the `test` job. The `gate` job fails only when `CI_FAIL` exists at the repository root. There is no linter, formatter or type checker.
- **Convention not followed.** Earlier stories added a line under `## Unreleased` in `CHANGELOG.md`. The spec's non-goals and AC 2 forbid that here.
- **Branch state.** Compared with `origin/main`, the work branch only adds `stories/EWS-1/{spec,hld,work-items}.md`. Those are pipeline artefacts, not part of the deliverable.
- **Repo memory.** `.factory/memory/` does not exist. The repository has no `AGENTS.md` or `CLAUDE.md`.
- **Unknowns.** None remain.

## Locked decisions and assumptions

**Locked decisions**
- The path is exactly `docs/live-e2e/e2e-w21-a.md` (spec FR1, hld §4).
- The content is exactly `# Live coding proof`, an empty line, then `Run: e2e-w21-a`, ending in a single trailing newline, with no front matter and no trailing whitespace (spec FR2, hld §5, work item t1).
- No existing file is modified. `CHANGELOG.md` and `README.md` stay unchanged, and no index or link to the new file is added (spec non-goals, AC 2, hld §6).
- No test is added (spec AC 3, hld §6).
- A person merges the pull request. The factory never does (spec §6).

**Assumptions**
- The file ends with LF (`\n`), not CRLF. Evidence: the spec writes the bytes with `\n`, and the repository has no `.gitattributes`. If this is wrong, a byte comparison against the specified content fails AC 1.
- One trailing newline is wanted. The spec states this assumption itself (spec §8). If the developer expects no final newline, the file must change by one byte.

## Solution proposal

Add a single new file, `docs/live-e2e/e2e-w21-a.md`, whose bytes are exactly `# Live coding proof\n\nRun: e2e-w21-a\n`. Creating the file also creates the `docs/live-e2e/` directory, because git tracks files, not directories. No other file in the repository changes.

Key decisions:
- **Write the bytes deterministically.** Use `printf '# Live coding proof\n\nRun: e2e-w21-a\n'` or an equivalent exact write, not an editor that might add a BOM, CRLF line endings or trailing whitespace. Then confirm the bytes (step 2).
- **No proof test.** AC 3 forbids adding a test, so the proof of AC 1 and AC 2 is the diff itself together with a byte check during the build.

Alternatives rejected:
- Adding a `CHANGELOG.md` entry, following earlier stories. Rejected because it violates AC 2.
- Adding a pytest that asserts the file's content. Rejected because it violates AC 3, and because `docs/` is outside the shipped package.
- Linking the file from `README.md` or `docs/`. Rejected because the spec's non-goals forbid it.

## Ordered implementation steps

1. **Create the file.** Create `docs/live-e2e/e2e-w21-a.md` (new, in a new directory) with exactly `# Live coding proof\n\nRun: e2e-w21-a\n`.
   - Advances AC 1.
   - Test layer: none. AC 3 forbids a new test, so proof comes from the byte check in step 2 and the PR diff.
2. **Check the bytes.** Confirm the file is exactly 36 bytes, uses LF only, has no BOM and no trailing spaces, and ends with one `\n`. For example, compare `od -c docs/live-e2e/e2e-w21-a.md` against the expected sequence, or run `cmp` against a `printf` of the same string.
   - Advances AC 1.
   - Test layer: none. This is a build-time check and is not committed.
3. **Check the scope.** Run `git status` / `git diff --stat` and confirm the only change outside `stories/EWS-1/` is the added `docs/live-e2e/e2e-w21-a.md`. `CHANGELOG.md`, `README.md`, `src/`, `tests/`, `pyproject.toml` and `.github/` must show no change.
   - Advances AC 2 and AC 3.
   - Test layer: none. This is a diff review.
4. **Run the gate.** Run the canonical gate once to confirm the existing suite is unaffected (see Verification and CI gate).
   - Advances AC 3 ("the existing `pytest` suite still passes unchanged").
   - Test layer: `package-api` (`pytest`).

Implicit invariants (authorization and tenancy, concurrency, validation and error paths) do not apply: the change is a static document with no runtime path. The step needs no dependencies, and the gate's install step resolves dependencies itself. The change produces no generated deliverables and no binary, so there is no `.factory/delivery-assets` obligation.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add docs/live-e2e/e2e-w21-a.md live coding proof document |
| 2 | t1 | Add docs/live-e2e/e2e-w21-a.md live coding proof document |
| 3 | t1 | Add docs/live-e2e/e2e-w21-a.md live coding proof document |
| 4 | t1 | Add docs/live-e2e/e2e-w21-a.md live coding proof document |

Work item t1 is the story's only work item, and every step maps to it.

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"`, then `pytest` from the repository root (`.factory/testing.md`, `.github/workflows/ci.yml` job `test`). Run it once locally on the committed SHA. Provider CI runs it again at the PR head, and that result is the authoritative one for layer `package-api` (`runBy: canonical-gate`).
- **Required layers:** `package-api` (`pytest`). It runs unprivileged in a pod. No layer needs another environment.
- **`gate` job:** stays green because no `CI_FAIL` file is created.
- **Provider CI configuration:** no change needed.
- **`.factory/testing.md` obligations:** none beyond running the declared layer. The change adds no layer.
- **`.factory/delivery-assets` obligations:** none, because the change adds no binary.
- **What "done" requires:** `pytest` passes with the same tests as on `main`, none added or removed. The CI `test` and `gate` jobs are green. The PR diff, excluding the pipeline's `stories/EWS-1/` files, shows exactly one added file, `docs/live-e2e/e2e-w21-a.md`, with the 36 specified bytes.

## Risks and scope guards

**Risks**
- **Byte drift.** An editor may add CRLF line endings, a BOM, trailing whitespace or a second newline, or drop the final newline. Mitigation: write the file with `printf` and run the byte check in step 2.
- **Habitual scope creep.** Mitigation: the scope check in step 3.
- **Pipeline files in the diff.** The PR also shows the `stories/EWS-1/` files. They are expected and are not part of the deliverable.

**The implement phase must NOT:**
- Edit `CHANGELOG.md`, `README.md`, `docs/argo-agent-runs.md` or any other existing file.
- Add an index, link, front matter or additional content to the new file.
- Add, change or remove any test, source file, `pyproject.toml`, CI workflow or dependency.
- Create `CI_FAIL`.
- Edit `stories/EWS-1/spec.md`, `hld.md` or `work-items.md`.
- Skip, disable or weaken `pytest` or either CI job to get a green result. A failure that has nothing to do with this change is reported as blocked, not suppressed.

## Clarification outcomes

None.
