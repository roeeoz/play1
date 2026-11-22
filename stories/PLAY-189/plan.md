# PLAY-189 — Implementation plan: add qa/s7_greeting.txt

## Context

PLAY-189 adds a single static text file, `qa/s7_greeting.txt`, to `roeeoz/play1`. The file holds the one line `hello again from s7`, and QA uses it to exercise the factory's go-back flow. The acceptance criteria: the file exists under the root `qa/` folder (AC1); it holds exactly that one line (AC2, with the line set by the developer's change request in place of the spec's `hello from s7`); and the pull request changes nothing else except the factory plan folder `stories/PLAY-189/` (AC3). The change goes on the work branch `halo/feat/play-189-20261122-205349`, which was cut from `main`. The approved requirement (`spec.md`), the design (`hld.md`) and the breakdown (`work-items.md`, one work item `t1`) are in the same folder as this file.

## Research findings

- **Change surface:** one new file, `qa/s7_greeting.txt`. No source, test, config or CI file is touched.
- **`qa/` on `main`** (`git ls-tree origin/main qa/`): `qa/20261109-s1/`, `qa/20261110-s3/`, `qa/s3-a.sh` (mode `100755`), `qa/s3-hello.sh` (mode `100755`). `qa/s7_greeting.txt` exists neither on `main` nor at work-branch `HEAD` (`c856e65`).
- **Contracts:** the only contract is the file contract in `hld.md` §5: path `qa/s7_greeting.txt`, bytes exactly `hello again from s7\n` (20 bytes, LF, no BOM/CR/extra whitespace), git mode `100644`, no shebang. No API, schema or cross-repo value is involved.
- **Consumers:** nothing reads `qa/*.txt`. Nothing under `tests/` or `src/` refers to `qa/` text files. `pyproject.toml:27-29` limits pytest to `testpaths = ["tests"]`, so the suite never collects anything from `qa/`.
- **Ignore rules:** `.gitignore:36-37` ignores only `pip-log.txt` and `pip-delete-this-directory.txt`, so the new file is tracked.
- **Canonical gate** (`.factory/testing.md`, `.github/workflows/ci.yml`): job `test` runs `pip install -e ".[test]"` then `pytest` on Python 3.12. Job `gate` fails if and only if `CI_FAIL` exists at the repo root (none exists now). The repo has no linter, formatter or type checker. The one declared layer is `package-api` (`pytest`, `runBy: canonical-gate`).
- **MR gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): PLAY-G1 (Python in `src/`, tests in `tests/`) does not apply; PLAY-G2 (shell scripts executable with a shebang) does not apply to a `.txt` file; PLAY-G3 (no file over 200 KB) passes at 20 bytes.
- **Test precedent:** QA *scripts* get a pytest module (`tests/test_qa_s3_greeting.py`, `tests/test_qa_20261109_s1_a.py`). AC3 forbids such a module for this story (see locked decisions).
- **Repo memory / delivery assets:** the repo has no `.factory/memory/` and no `.factory/delivery-assets`.
- **Unknowns remaining:** none.

## Locked decisions and assumptions

**Locked decisions**
- The only product file added is `qa/s7_greeting.txt`, and nothing else changes except `stories/PLAY-189/` (spec FR3, AC3; developer answer Q2 in spec §8).
- Content is the single line `hello again from s7`. Source: the developer's plan change request, which replaces the line `hello from s7` in spec FR2 and AC2; `hld.md` §1/§5 and `work-items.md` `t1` already carry the new line. The rest of the spec stands.
- The file ends with exactly one LF: 20 bytes, mode `100644`, no shebang (`hld.md` §5–§6, which settles the open point in spec §8).
- No new test module is added. Verification is the byte-exact check plus the unchanged `pytest` gate (`hld.md` §6, required by AC3).
- `roeeoz/play2` is out of scope (spec §2, developer answer Q1).

**Assumptions**
- The implement turn writes the file with a byte-exact method (for example `printf 'hello again from s7\n' > qa/s7_greeting.txt`), not an editor that could add a BOM or CRLF. Evidence: the repo has no `.gitattributes` forcing EOL conversion. If wrong, the `cmp` check in step 2 fails and the file is rewritten.

## Solution proposal

Add `qa/s7_greeting.txt` as a plain, non-executable data file whose contents are exactly `hello again from s7\n`. No runtime component reads it, so the change does not touch the package, the tests or CI.

Key decisions:
- **Trailing LF.** This is a POSIX-terminated single line: `wc -l` reports 1 and the diff shows no "No newline at end of file" marker (`hld.md` §6).
- **No pytest module.** Adding `tests/test_qa_s7_greeting.py` would follow the QA-script precedent, but it would break AC3. AC1 and AC2 are proven instead by a byte-exact `cmp` and a `git ls-files -s` mode check, recorded in the implement evidence. The existing `pytest` suite stays green unchanged, which proves the change is inert.
- **Mode `100644`.** The file must not copy the exec bit of the neighbouring `.sh` files. PLAY-G2 does not apply to it, and an exec bit on a data file would be misleading.

Alternatives rejected: a test module (breaks AC3); no trailing newline (non-POSIX and a noisy diff); placing the file anywhere other than root `qa/` (breaks AC1).

## Ordered implementation steps

1. **Create the file.** Write `qa/s7_greeting.txt` with exactly the bytes `hello again from s7\n`, mode `100644`. Advances AC1 and AC2. Test layer: no existing layer covers a static data file, and AC3 forbids adding one. Coverage is the byte-exact check in step 2.
2. **Verify the file contract.** Before committing, run `printf 'hello again from s7\n' | cmp - qa/s7_greeting.txt` (must exit 0) and `git ls-files -s qa/s7_greeting.txt` after staging (must show `100644`). Record both results in the implement evidence. Advances AC1 and AC2. Test layer: manual/evidence check. No repo test layer applies.
3. **Verify scope.** After committing, check that `git diff --name-only main...HEAD` lists only `qa/s7_greeting.txt` and paths under `stories/PLAY-189/`. Check that no `CI_FAIL` file exists at the root. Advances AC3. Test layer: evidence check, plus the `gate` CI job for `CI_FAIL`.
4. **Gate.** The gate's own run (`run-tests-gate.sh --run` on the committed SHA, which runs `local-test-gate:` from `.factory/testing.md`) must be green. Advances AC3 (proves nothing else broke). Test layer: `package-api` (`pytest`).

Implicit invariants: authorization, tenancy, concurrency and input validation do not apply, because this is a static file with no code path. The gate's `pip install` fetches dependencies from `pyproject.toml` without relying on a warm cache. There are no generated deliverables.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–4 | `t1` — Add qa/s7_greeting.txt containing the line "hello again from s7" |

`t1`, the only work item, is covered.

## Verification and CI gate

- **Canonical gate** (`.github/workflows/ci.yml`, job `test`, Python 3.12): `pip install -e ".[test]"`, then `pytest`. Job `gate` must pass, which means no `CI_FAIL` at the root.
- **One local run:** the gate's own, `run-tests-gate.sh --run` on the committed SHA. Do not also run `pytest` by hand or add a second worktree.
- **Required layers:** `package-api` (`pytest`), which can run in a pod. It is credited from the provider run at the exact head.
- **MR gate:** play1 layout gate PLAY-G1..G3 must pass (it will: 20-byte non-script text file).
- **Provider CI changes:** none.
- **`.factory/delivery-assets`:** not applicable, since the file is 20 bytes and not a binary.
- **Done means:** the provider `test` and `gate` jobs are green at the exact head, the layout gate passes, the `cmp` check exits 0, the mode is `100644`, and the PR diff holds only `qa/s7_greeting.txt` plus `stories/PLAY-189/`.

## Risks and scope guards

Risks:
- An editor or OS adds CRLF, a BOM or a missing or extra newline, and AC2 fails. Mitigation: write the file with `printf` and run the step 2 `cmp` check.
- The exec bit is copied from the `.sh` neighbours. Mitigation: the step 2 mode check.

The implement phase must NOT:
- Add a test module (for example `tests/test_qa_s7_greeting.py`) or edit any existing test.
- Touch `README.md`, `.gitignore`, `pyproject.toml`, `.github/`, `.factory/`, `src/`, or any existing `qa/` file.
- Create `CI_FAIL` or any other root file.
- Touch `roeeoz/play2`.
- Edit `spec.md`, `hld.md` or `work-items.md`.
- Skip, delete or weaken any check to get green. A failing check is reported as blocked.

## Clarification outcomes

No clarifying question was raised. Developer change request on the previous plan: the file content is the single line `hello again from s7` instead of `hello from s7`, and everything else stays. Folded into the locked content decision, the file contract (20 bytes with the LF), steps 1–2 and the `cmp` check. `spec.md` still reads `hello from s7`; per the platform rule it is not edited here, and the change request takes precedence for AC2.
