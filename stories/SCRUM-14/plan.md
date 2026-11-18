# Plan — SCRUM-14: Hello world bash script in a dedicated folder

## Context

SCRUM-14 asks for a runnable `hello-world/hello.sh` at the root of play1. Run directly through its `#!/bin/bash` shebang, it prints exactly `hello world` and exits 0, and it is the only file in its folder (AC1–AC4). The script already exists on `main` and meets every criterion. The story therefore keeps it byte-for-byte (FR5 / A1) and adds only the `CHANGELOG.md` line that the repository gate rule `PLAY-G4` requires on every pull request (A3). The change lands in `play1` on the work branch `halo/feat/scrum-14-20261118-232451`, which merges into `main`. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/SCRUM-14/`.

## Research findings

- **Script (unchanged, fact):** `hello-world/hello.sh` has git mode `100755` (blob `2a43bb26`). It is 31 bytes with LF endings. `hello-world/hello.sh:1` is `#!/bin/bash` and `hello-world/hello.sh:2` is `echo "hello world"`. `ls -a hello-world` shows only `hello.sh`, with no dot-files.
- **Tests (unchanged, fact):** `tests/test_hello_sh.py` checks every criterion:
  - AC1 and AC4: `test_prints_hello_world` (`:10`) and `test_exact_output_no_extra_whitespace` (`:23`) both assert `stdout == "hello world\n"` and exit 0.
  - stderr: `test_no_stderr` (`:17`) asserts that stderr is empty.
  - AC3: `test_shebang_line` (`:32`) and `test_executable_permission` (`:36`). `subprocess.run([str(SCRIPT)])` at `:11` executes the script without `bash`, so AC1 also covers direct execution.
  - AC2: `test_folder_contains_only_hello_sh` (`:40`). It ignores dot-files (`:42`), so the "no dot-files" part of the work item is enforced by review, not by this test.
- **Changelog (to change, fact):** `CHANGELOG.md` has 8 lines.
  - `## Unreleased` is at `CHANGELOG.md:3`.
  - The entries at `:5`–`:8` use the format `- <KEY>: <lowercase verb> \`path\`, <description>.`
  - The last entry, `PLAY-175`, is at `:8`.
  - The file ends with a newline.
- **Gate:**
  - `.factory/testing.md` declares one required layer, `package-api`, with command `pytest` and `runBy: canonical-gate`.
  - `.github/workflows/ci.yml` runs the `test` job (`pip install -e ".[test]"`, then `pytest`, on Python 3.12) and the `gate` job, which fails only if `CI_FAIL` exists at the repository root. No `CI_FAIL` file exists.
  - `pyproject.toml` sets `testpaths = ["tests"]`.
  - No linter, formatter or type checker is configured.
  - The pull-request gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` enforces rule 4 (`PLAY-G4`) and rule 2 (a new shell script must be executable and have a shebang; this change adds no script).
- **Cross-repo and external data:** none.
- **Repo memory:** there is no `.factory/memory/` directory.
- **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**
- Keep `hello-world/hello.sh` as it is, without rewriting it. Source: spec FR5 / A1, hld §6, work item t1.
- The output is `hello world` followed by one newline, written by `echo`. Source: spec A2, hld §6, and the byte-exact assertions at `tests/test_hello_sh.py:15,28`.
- Every pull request adds a line under `## Unreleased` in `CHANGELOG.md`. Source: repo-gate rule 4 (`PLAY-G4`), spec A3.
- Leave out CI/CD integration, additional scripts and documentation files. Source: spec §2 Non-Goals.
- The changelog line uses the existing `- <KEY>: ...` format. Source: work item t1 and `CHANGELOG.md:5-8`.

**Assumptions**
- **The new entry is appended after `CHANGELOG.md:8`.** Evidence: the existing entries are in chronological order. If this is wrong, only the position of the line changes. `PLAY-G4` is still met.
- **The changelog line counts as a gate artefact, not as feature documentation.** Evidence: spec A3. If this is wrong, the story conflicts with `PLAY-G4`. That would be a spec change, not a plan change.

## Solution proposal

Change one file only: add a single SCRUM-14 entry under `## Unreleased` in `CHANGELOG.md`. For example: `` - SCRUM-14: confirm `hello-world/hello.sh`, a hello-world bash script that prints `hello world`, in its own `hello-world/` folder. `` The wording follows the existing entry style and must name both SCRUM-14 and `hello-world/hello.sh`.

The existing tests in `tests/test_hello_sh.py` serve as the proof for AC1–AC4, so no product code and no tests are added.

Alternatives rejected:
- **A rewritten script (e.g. `printf`):** this violates FR5 and risks breaking the byte-exact tests.
- **New or extra tests:** this duplicates existing coverage at the only layer the repository has.
- **An empty pull request:** it fails `PLAY-G4`.

## Ordered implementation steps

1. **Verify the baseline (read-only).**
   - Confirm `git ls-files -s hello-world` lists only `100755 … hello-world/hello.sh`.
   - Confirm `git diff main -- hello-world tests/test_hello_sh.py` is empty.
   - Confirm `ls -a hello-world` shows only `hello.sh`.
   - Confirm `CI_FAIL` is absent.
   - Advances AC1–AC4 (the deliverable is unchanged). Covered by the `package-api` (`pytest`) layer through `tests/test_hello_sh.py`.
2. **Add the changelog entry.** Add one line to `CHANGELOG.md` directly after `CHANGELOG.md:8`, under `## Unreleased`.
   - Keep the trailing newline at the end of the file.
   - Do not touch any other line.
   - Advances the gate obligation (`PLAY-G4`, spec A3) in support of every AC. No test layer covers the changelog; repo-gate rule 4 checks it at pull-request review.
3. **Run the gate.** Run `pip install -e ".[test]"`, then `pytest`, from the repository root.
   - Confirm all six tests in `tests/test_hello_sh.py` pass, along with the rest of the suite.
   - Advances AC1–AC4. Layer: `package-api`.
4. **Write the pull request description.** State that the pull request confirms the existing `hello-world/hello.sh` meets the SCRUM-14 acceptance criteria (A1) and that the only change is the `PLAY-G4` changelog line. Work-item acceptance criterion; no test layer applies.

Implicit invariants:
- Authorization, tenancy, concurrency and input validation do not apply: the script is static and takes no input.
- The editable install fetches the dependencies (`pypdf`, `flask>=3`, `pytest>=8`) and does not rely on a warm cache.
- No generated deliverables and no binaries are added, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item |
|---|---|
| 1, 2, 3, 4 | t1 — Confirm hello-world/hello.sh meets SCRUM-14 and record it in CHANGELOG.md |

Every work item in `work-items.md` (t1 only) is covered.

## Verification and CI gate

- **Canonical gate, in order, run once on the committed SHA:**
  1. `pip install -e ".[test]"`
  2. `pytest`
- **Required layer:** `package-api` (`pytest`, `runBy: canonical-gate`). It runs unprivileged in a pod. The authoritative result is the `test` job of `.github/workflows/ci.yml` at the pull-request head.
- **The `gate` job** must stay green, which means no `CI_FAIL` at the repository root.
- **Pull-request gate:** repo-gate must report no `PLAY-G4`, because `CHANGELOG.md` is in the diff. Rules 1–3 are unaffected.
- **The change is done when:**
  - `pytest` passes in full, including all six tests in `tests/test_hello_sh.py`.
  - The diff against `main`, outside `stories/SCRUM-14/`, is exactly one added line in `CHANGELOG.md`.
  - `hello-world/hello.sh` is unchanged and keeps mode `100755`.
- **CI configuration:** no provider CI change is needed.

## Risks and scope guards

**Risks**
- A changelog-only pull request may be read as having no product change. Mitigation: step 4's description states that the pull request confirms delivery (A1).
- An editor could normalise line endings or the file mode of `hello.sh`. Mitigation: do not open or write that file, and check the baseline in step 1.

**The implement phase must NOT:**
- Modify, re-create, reformat or `chmod` `hello-world/hello.sh`.
- Add any file, including dot-files and a README, under `hello-world/`.
- Edit `tests/test_hello_sh.py`, `.github/workflows/ci.yml`, `.factory/`, `pyproject.toml` or any existing `CHANGELOG.md` line.
- Add `CI_FAIL`, new scripts, CI integration or documentation files.
- Make the gate green by deleting, skipping, `xfail`-marking or weakening any test. A failing check is reported, not suppressed.
- Edit `spec.md`, `hld.md` or `work-items.md`.

## Clarification outcomes

None.
