# Implementation Plan — F1: Folder Scaffold

## Context

Git does not track empty directories, so downstream features F2 (script) and F3 (tests + CI) need a committed file in `scripts/hello-world/` before they can write into it. This work item delivers exactly one file — `scripts/hello-world/README.md` — which simultaneously anchors the directory in git history and provides human-readable documentation (purpose, canonical invocation, PDLC context, folder map) for contributors.

## Approach

Single-step commit on a dedicated feature branch (`halo/feat/scaffold-hello-world`). No existing files are modified. The README content is fully dictated by the spec, so there are no design decisions to make: write the four required sections verbatim, commit, open a PR targeting `main`. F2 and F3 branch from or stack on top of this branch once the PR is merged (or while it is open, since the directory is present on the branch).

## Steps

1. **Create `scripts/hello-world/README.md`** (implicitly creates the directory).
   - Section 1 — **Purpose**: state that this directory is the authoritative location for Hello World PDLC smoke-test artifacts, created to validate the Halo platform's end-to-end product development lifecycle pipeline.
   - Section 2 — **Usage**: include the exact fenced shell code block containing `bash scripts/hello-world/hello_world.sh` — no variation in path or command name.
   - Section 3 — **PDLC Note**: state that this folder and its contents exist as a platform test case, not a general-purpose scripting framework.
   - Section 4 — **Folder Map**: table listing `hello_world.sh` (F2, prints Hello World), `test/hello_world.bats` (F3, bats assertion), and `.github/workflows/hello-world.yml` (F3, CI pipeline) with brief descriptions.
2. **Commit** the single file with a conventional-commit message, e.g. `feat(scaffold): add scripts/hello-world/ directory with README.md`.
3. **Open a pull request** from `halo/feat/scaffold-hello-world` into `main`.

## Verification

| Check | Command / method | Expected result |
|-------|------------------|-----------------|
| AC1 — directory committed | `git ls-files scripts/hello-world/` | Returns `scripts/hello-world/README.md` |
| AC2 — README committed | `git show HEAD:scripts/hello-world/README.md` | File contents printed |
| AC3 — Purpose statement present | `grep -i 'authoritative location' scripts/hello-world/README.md` | Match found |
| AC4 — Exact usage command | `grep 'bash scripts/hello-world/hello_world.sh' scripts/hello-world/README.md` | Match found inside fenced block |
| AC5 — PDLC note present | `grep -i 'platform test case' scripts/hello-world/README.md` | Match found |
| AC6 — Folder map present | Visually confirm table lists `hello_world.sh`, `test/hello_world.bats`, `.github/workflows/hello-world.yml` | All three entries present |
| AC7 — No extra files | `git ls-files scripts/hello-world/` | Only `README.md` listed |
| AC8 — No pre-existing files modified | `git diff main -- .github/workflows/ci.yml` | Empty diff |

All checks pass on the current branch (`halo/feat/scaffold-hello-world`, commit `2f758fe`). The existing Python CI jobs in `.github/workflows/ci.yml` are unaffected by this documentation-only commit.

## Risks & Open Points

- **Forward-reference in folder map:** The README lists `hello_world.sh`, the bats test file, and the CI workflow — none of which exist yet. This is intentional per spec and cosmetic; no action required.
- **Branch sequencing:** F2 and F3 must not branch from `main` before this PR merges, or they lose the directory guarantee. The platform's `dependsOn` enforcement is the mitigation; no code change needed here.
- **No new risks introduced:** This is a documentation-only commit; there are no runtime, security, or dependency concerns.
