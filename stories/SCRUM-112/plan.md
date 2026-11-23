# Plan — SCRUM-112: add qa/gap-hello.txt

## Context

SCRUM-112 adds one static text file, `qa/gap-hello.txt`, containing exactly `hello from gap\n` (15 bytes). It is a factory QA story. It checks that work started on a non-default base branch is delivered onto that branch. It also checks how the factory handles a base branch that already has a failing test. The acceptance criteria are: AC1, the file exists with that text. AC2, the content is exactly one lowercase line with no quotes and exactly one trailing LF (15 bytes). AC3, compared with the base branch, no other file changes. The change goes into `roeeoz/play1` on the work branch `halo/feat/scrum-112-20261123-053053`, which was cut from the frozen target branch `qa-20261122-s4-base`. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/SCRUM-112/`.

## Research findings

- **Change surface:** `qa/gap-hello.txt` does not exist yet, so it is new. `qa/` currently holds only shell scripts, all at git mode `100755`: `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/hello.sh` and `qa/20261110-s3/test_hello.sh`. No `.txt` file is in `qa/` today.
- **Current diff vs base:** `git diff --stat origin/qa-20261122-s4-base...HEAD` shows only `stories/SCRUM-112/{spec,hld,work-items}.md`. These are platform-owned plan-folder files. No product file has changed.
- **Nothing references the file.** `src/`, `tests/`, `pyproject.toml` and `.github/workflows/ci.yml` do not read it. It has no API, schema or cross-repo contract.
- **Byte handling:** the repo has no `.gitattributes`, so git does no EOL or BOM conversion. `.gitignore:36-37` ignores only `pip-log.txt` and `pip-delete-this-directory.txt`, so the new file is tracked normally.
- **Canonical gate:** `.factory/testing.md` declares `local-test-gate: pip install -q -e ".[test]" && pytest` and one required layer: `package-api`, `pytest`, `runBy: canonical-gate`. In CI, `.github/workflows/ci.yml` runs the `test` job (`pip install -e ".[test]"`, then `pytest` on Python 3.12) and the `gate` job, which fails only if `CI_FAIL` exists at the repo root. The repo configures no linter, formatter or type checker.
- **Pre-existing red:** `tests/test_qa_20261122_s4_base.py:5` runs `assert 1 == 2`. It arrived in commit `ea6f718` on the base branch. `pyproject.toml` sets `testpaths = ["tests"]`, so `pytest` collects this test and fails on any head of this branch.
- **Layout gate:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-16` has three rules. PLAY-G1: Python goes under `src/`, tests under `tests/`. PLAY-G2: a new shell script is executable and has a shebang. PLAY-G3: no file in the diff is over 200 KB. A 15-byte non-script text file meets all three.
- **No unknowns remain.**

## Locked decisions and assumptions

**Locked decisions**
- The path is `qa/gap-hello.txt`. Its bytes are `68 65 6c 6c 6f 20 66 72 6f 6d 20 67 61 70 0a`: no BOM, LF line ending, git mode `100644`. Sources: spec FR1/FR2, AC1/AC2 and HLD §5.
- No other file changes. That includes the existing `qa/` scripts. No test, script, package or CI change is added. Sources: spec §2 Non-Goals, FR3/AC3 and HLD §6.
- `tests/test_qa_20261122_s4_base.py` stays exactly as it is. It is not fixed, skipped, deleted or marked xfail. The red `pytest` gate is the expected QA outcome, and no gate exemption is sought. Sources: spec §6 (developer answer Q1, option c) and HLD §6.
- The base branch is `qa-20261122-s4-base`. The PR targets that branch. Source: the platform's frozen target branch.
- There is one work item, `t1`. Source: `work-items.md`.

**Assumptions**
- AC3 ("changes no other file") excludes the platform-owned plan folder `stories/SCRUM-112/`. Evidence: HLD §8 says so, and the base branch already has plan folders from earlier stories under `stories/`. If this is wrong, a reviewer reading AC3 literally will see `stories/SCRUM-112/*` in the PR. That is platform behaviour, and this work item cannot change it.

## Solution proposal

Create `qa/gap-hello.txt` as a plain, non-executable file holding exactly `hello from gap\n`. Write it with a byte-exact method, such as `printf 'hello from gap\n' > qa/gap-hello.txt`. Do not use an editor that might add CRLF, a BOM or a second newline. Nothing else is touched.

Key decisions:
- **No automated test for the file.** A test would add a second changed file, which breaks FR3/AC3, and the spec puts tests out of scope. AC1–AC3 are checked by byte and diff checks during implementation and review, not by a test in the suite.
- **Leave the base failure alone.** The point of the run is to see how the factory handles an inherited red gate. "Fixing" it would defeat the QA purpose and go against the developer's Q1 answer.

Alternatives rejected:
- Adding a pytest check for the file: out of scope, and it breaks AC3.
- Fixing or xfail-ing `tests/test_qa_20261122_s4_base.py`: explicitly out of scope (Q1).
- Making the file a script: the spec says it is a text file, and the standing script rule does not apply to it.

## Ordered implementation steps

1. **Create `qa/gap-hello.txt`** (new) with exactly `hello from gap` and one LF. Use mode `100644`, not executable. Advances AC1 and AC2. Test layer: none in the suite, by design. Verify inline as follows:
   - `wc -c qa/gap-hello.txt` reports `15`.
   - `od -c qa/gap-hello.txt` shows no `\r`, no BOM and a single trailing `\n`.
   - `cat qa/gap-hello.txt` prints `hello from gap`.
   - `git ls-files -s qa/gap-hello.txt` shows `100644`.
2. **Confirm isolation.** `git diff --name-status origin/qa-20261122-s4-base...HEAD` must show `A qa/gap-hello.txt` plus only `stories/SCRUM-112/*`. No `CI_FAIL` may be at the root. Advances AC3. Test layer: none, as this is a diff check. The `gate` CI job covers the `CI_FAIL` invariant.
3. **Run the gate and report its result honestly.** The gate's own run is expected to be red, with exactly one failure: `tests/test_qa_20261122_s4_base.py::test_pre_existing_failure_on_the_qa_base`. Record this in the PR or run summary as the expected, pre-existing base failure, not a story failure. Covers the work item's gate criterion. Test layer: `package-api` (`pytest`).

Implicit invariants: there is no authz, tenancy, concurrency or input validation surface, because the change is a static file. Dependencies come only from the gate's own `pip install -e ".[test]"`. Nothing is generated, and no binary or delivery asset is added.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add qa/gap-hello.txt containing 'hello from gap' |
| 2 | t1 | Add qa/gap-hello.txt containing 'hello from gap' |
| 3 | t1 | Add qa/gap-hello.txt containing 'hello from gap' |

Every work item is covered: `t1` is the only one.

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"`, then `pytest`. Provider CI runs this as the `test` job in `.github/workflows/ci.yml` at the exact PR head. The `gate` job runs alongside it (no `CI_FAIL` at the root).
- **The one local run** is the gate's own: `run-tests-gate.sh --run` on the committed SHA. It runs `.factory/testing.md`'s `local-test-gate`. Do not also run `pytest` by hand or in a second worktree.
- **Required layer:** `package-api` (`pytest`, required, `runBy: canonical-gate`). It can run unprivileged in a pod.
- **What "done" looks like:**
  - `qa/gap-hello.txt` matches the 15-byte contract.
  - The diff against the base is that file plus the plan folder.
  - The `gate` job is green.
  - The `test` job is red, with exactly one failure: the pre-existing `tests/test_qa_20261122_s4_base.py` assertion. Every other test passes, which proves the change broke nothing.
  - The red result is reported as is. It must never be presented as green.
- **Layout gate** (`repo-gate`, mr-gate slot): expected to pass PLAY-G1 through PLAY-G3.
- **No CI configuration changes.** `.factory/delivery-assets` does not apply: no binary of 1 MiB or more is added.

## Risks and scope guards

**Risks**
- **Byte drift:** CRLF, a BOM, a missing newline or a double newline would break AC2. Mitigation: write with `printf` and check with `wc -c` and `od -c` (step 1).
- **Red gate read as a story failure.** Mitigation: the PR and summary name the single pre-existing failing test and its base commit `ea6f718`.

**Do NOT**
- Do not modify, delete, skip, xfail or otherwise weaken `tests/test_qa_20261122_s4_base.py`. Do not add a `conftest.py`, pytest options or a CI step to hide the failure.
- Do not touch any existing `qa/` file, `src/`, `tests/`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/`, `README.md` or `.gitignore`.
- Do not add a test, script, `.gitattributes` or README mention for the new file.
- Do not make the file executable, and do not add a shebang.
- Do not create `CI_FAIL`.
- Do not rebase onto or merge any branch other than `qa-20261122-s4-base`.

## Clarification outcomes

None. The intake already settled Q1–Q3 (spec §8), and no new blocker came up.
