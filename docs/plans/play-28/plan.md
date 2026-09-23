# Implementation Plan: Add a Hello World bash script in a new folder

| Field | Value |
|---|---|
| Work item | t1 — Add executable `scripts/hello-world/hello_world.sh` printing `Hello, World!` |
| Repository | roeeoz/play1 (`main`, head `f8098c5b`) |
| Tier | T1, junior, very low effort |
| Traces to | Epic R1, R2; spec FR1–FR5; acceptance criteria 1–6 |

## 1. Context

The team wants a minimal, zero-risk change that exercises the repository's branch → PR → CI → review pipeline end to end. The vehicle is one new folder, `scripts/hello-world/`, containing one executable bash script, `hello_world.sh`, that prints `Hello, World!` and exits 0. Nothing else in the repository changes.

## 2. Approach

There is one work item with no dependencies, so the work is a single linear pass: create the file, set its mode, verify behaviour and committed mode locally, open the PR with the verification evidence in the description. No existing code is reused; the repo is a Python `src/` package with no shell scripts, no `.gitattributes`, no `.editorconfig`, and no shell linting, so the shebang, LF endings, and executable bit are entirely the implementer's responsibility.

The only non-trivial concern is the git file mode. Nothing in CI runs the script, so a `100644` commit or CRLF endings would pass CI green. The plan therefore front-loads explicit mode and byte-level checks before push and records them in the PR description, as required by the work item.

## 3. Steps

All steps belong to work item **t1**.

1. **Branch.** From up-to-date `main`, create a feature branch (e.g. `halo/feat/hello-world-script`). Do not create a file named `CI_FAIL` at the repo root at any point; the `gate` CI job fails if it exists.

2. **Create the folder and script.** Add `scripts/hello-world/hello_world.sh` with exactly this content, LF line endings, trailing newline after the last line:

   ```bash
   #!/bin/bash
   echo "Hello, World!"
   ```

   Rationale: the shebang is fixed by spec assumption A4; a fixed-string `echo` behaves identically on bash 3.2 (macOS) and bash 5 (ubuntu-latest), so `printf` is not needed. No `set -e`, comments, or blank lines are required; keep it to these two lines so the diff is trivially reviewable.

3. **Set the executable bit.** Run `chmod +x scripts/hello-world/hello_world.sh`. Then `git add scripts/hello-world/hello_world.sh` and confirm the index mode with:

   ```bash
   git ls-files -s scripts/hello-world/hello_world.sh
   ```

   The first field must be `100755`. If it shows `100644` (e.g. `core.fileMode` is false in the checkout, or the file was created by tooling that ignores mode), run `git update-index --chmod=+x scripts/hello-world/hello_world.sh` and re-check.

4. **Confirm LF endings and shebang bytes.** Run:

   ```bash
   head -c 12 scripts/hello-world/hello_world.sh | od -c   # expect '#!/bin/bash\n'
   grep -c $'\r' scripts/hello-world/hello_world.sh          # expect 0
   ```

5. **Commit.** Single commit touching only the new file, e.g. `feat(scripts): add hello-world bash script`. Confirm the diff scope with `git diff --stat main...HEAD` — exactly one file added, no modifications or deletions elsewhere. End the commit message with the required attribution trailer.

6. **Open the PR** against `main`. The description must include, verbatim, the commands from Section 4 and their observed output: stdout bytes, exit codes for both invocations, and the `git ls-files -s` line showing `100755`. Reference work item t1 and the story for traceability. Do not add a README, a bats test, a shellcheck workflow, or `.factory/testing.md` changes; all are excluded by the spec's non-goals.

## 4. Verification

No automated tests are added (spec non-goal); the repo's CI (`pytest` plus the `CI_FAIL` gate) will run and must stay green, but it does not exercise the script. Acceptance is proven manually from the repository root on the feature branch:

| Criterion | Command | Expected |
|---|---|---|
| 1, 2 | `ls -l scripts/hello-world/` | one entry `hello_world.sh`, mode string starts `-rwx` |
| 3, 4 (direct) | `./scripts/hello-world/hello_world.sh; echo "exit=$?"` | `Hello, World!` then `exit=0` |
| 3, 4 (via bash) | `bash scripts/hello-world/hello_world.sh; echo "exit=$?"` | `Hello, World!` then `exit=0` |
| 3 (exact bytes, empty stderr) | `./scripts/hello-world/hello_world.sh 2>/tmp/err \| od -c; wc -c </tmp/err` | od shows `H e l l o ,   W o r l d ! \n`; stderr byte count `0` |
| 5 (committed mode) | `git ls-files -s scripts/hello-world/hello_world.sh` | line begins `100755` |
| 6 (scope) | `git diff --stat main...HEAD` | `1 file changed`, only the new path listed |

After push, re-check criterion 5 in the PR's "Files changed" view (GitHub shows `new file mode 100755` in the diff header) to confirm the platform's commit path did not drop the bit.

## 5. Risks & open points

- **Executable bit dropped by platform tooling.** No file in this repo's history has ever been `100755`, so there is no precedent that the implement pod's commit path preserves mode. Step 3's index check and the post-push diff-header check are the only guards; CI cannot catch this.
- **Criterion 6 vs. platform PR convention.** Recent Halo feature PRs in this repo (#71, #73, #75) bundle `docs/plans/...` files and sometimes `.factory/testing.md` edits into the feature diff. The spec's criterion 6 says "no files outside `scripts/hello-world/hello_world.sh`". This plan assumes the criterion applies to repository content and that any platform-generated `docs/plans/` files are outside its intent; the reviewer should confirm, and the implementer should not hand-add any docs or `.factory` changes.
- **Open PR #65 conflicts on the same folder.** It adds `scripts/hello-world/README.md` from an earlier decomposition, promising a `test/hello_world.bats` file and a `hello-world.yml` workflow that this spec explicitly excludes. If #65 merges first, this PR adds one file into an existing folder (still satisfying criteria 1–6), but the README will describe files that never arrive. Recommend closing #65 as superseded, or explicitly accepting the stale README as out of scope for this story.
- **Shebang portability.** `#!/bin/bash` is fixed by the spec; `#!/usr/bin/env bash` would be more portable but is out of scope to change. Both target hosts (macOS, ubuntu-latest) have `/bin/bash`.
- **Repository id mismatch across planning docs** (`0fcb6992-...` in the HLD vs. other ids in older plans) is a dev-stack registration detail and has no effect on this change; noted for traceability only.
