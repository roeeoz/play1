# Implementation plan — SCRUM-109: `qa/s4_marker.sh` prints `QA_S4_MARKER`

## Context

Add one POSIX shell script, `qa/s4_marker.sh`, to `roeeoz/play1` that prints the exact value of the environment variable `QA_S4_MARKER` followed by one newline and exits 0 (an empty value prints a single newline, exit 0), and that prints `QA_S4_MARKER is not set` to stderr and exits 1 when the variable is absent. A sibling shell test, `qa/s4_marker_test.sh`, proves that contract. Nothing outside `qa/s4_*` changes (AC3). The work lands on `halo/feat/scrum-109-20261122-205918`, cut from `qa-20261122-s4-base`. The approved requirement is `spec.md`, the design `hld.md` and the breakdown `work-items.md`, all beside this file in `stories/SCRUM-109/`.

## Research findings

- **Existing pattern (fact).** Every `qa/` helper is `#!/bin/sh`, has a one-line purpose comment on line 2, and is committed with mode `100755` (`git ls-files -s qa`): `qa/s3-hello.sh:1-3`, `qa/20261110-s3/hello.sh:1-3`.
- **Shell-test precedent (fact).** `qa/20261110-s3/test_hello.sh` resolves its own directory (`:3`, `CDPATH= cd -P -- "$(dirname -- "$0")" && pwd`), runs the sibling by absolute path (`:4`), captures stdout plus exit code with an `x` sentinel so trailing newlines survive `$(...)` (`:6-9`), compares against an exact expected string (`:11-21`), writes `FAIL: …` to stderr and exits 1 on mismatch, and prints `PASS: …` on success (`:22`). It does not check stderr; the new test must add that.
- **Change surface.** Two new files: `qa/s4_marker.sh`, `qa/s4_marker_test.sh`. No file exists at either path today. No contract, schema, package or shared constant is touched.
- **Canonical gate (fact).** `.factory/testing.md`: `test-gate: pytest`, `local-test-gate: pip install -q -e ".[test]" && pytest`; one declared layer `package-api` (production-path, `runBy: canonical-gate`). `.github/workflows/ci.yml` runs job `test` (`pip install -e ".[test]"`, then `pytest`) and job `gate` (fails iff `CI_FAIL` exists at the root). No linter, formatter or shellcheck is configured.
- **Pre-existing red check (fact).** `tests/test_qa_20261122_s4_base.py` asserts `1 == 2` on the base, so the `test` job and the local gate fail independently of this change (spec §6).
- **Layout gate (fact).** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rule 2 (`PLAY-G2`): a new shell script is executable and starts with a shebang; rule 3: no file over 200 KB.
- **pytest does not cover `qa/s4_*`.** `tests/test_hello_sh.py` shows pytest can drive a shell script, but a new file in `tests/` would break AC3; the shell test is the coverage (hld §6).
- **Environment (fact).** In this pod `/bin/sh` resolves to `/usr/bin/bash`; `dash` is not installed. No `.gitattributes` exists, so line endings depend on how the file is written.
- **External data.** None. No other system of record is involved.
- **Remaining unknowns.** None blocking.

## Locked decisions and assumptions

**Locked decisions**

- Script path `qa/s4_marker.sh`, executable, run as `./qa/s4_marker.sh` — spec FR1, AC1.
- Set → value plus exactly one `\n` on stdout, nothing else, exit 0 — spec FR2, AC1, AC4.
- Set to empty → single `\n` on stdout, exit 0 — spec FR5, AC5.
- Unset → `QA_S4_MARKER is not set` on stderr, exit 1 — spec FR3, AC2.
- Only `qa/s4_*` files change; `tests/test_qa_20261122_s4_base.py` stays as is — spec FR4, AC3, §6 developer decision (b).
- `#!/bin/sh`, `printf` with a fixed `%s\n` format, no `echo`; test is a sibling `qa/s4_marker_test.sh`, mode `100755` for both, LF endings — hld §5, §6, §7; work item t1.
- No output label, prefix or quoting; arguments ignored — spec §4, hld §5.

**Assumptions**

- "Set" means present in the script's process environment, detected with the POSIX `${QA_S4_MARKER+set}` expansion. Evidence: hld §5. If wrong (e.g. a non-exported caller variable was meant to count), no script can observe it anyway.
- Unset is produced in the test with `unset QA_S4_MARKER` inside a subshell rather than `env -u`, which is not POSIX. If wrong, only the test's portability changes.
- The dash check runs only where `dash` is installed (work item t1: "where dash is available"). In this pod it is skipped with a note line. If a reviewer requires dash evidence, it must be produced on a host that has dash.
- The test is not wired into CI (hld §8). Consequence if wrong: a CI change outside `qa/s4_*`, which AC3 forbids.

## Solution proposal

Two standalone POSIX `sh` files under `qa/`, following the existing `qa/` helpers.

- **`qa/s4_marker.sh`.** Shebang `#!/bin/sh`, purpose comment, then one branch: if `"${QA_S4_MARKER+set}" = set`, run `printf '%s\n' "$QA_S4_MARKER"` and exit 0; otherwise `printf 'QA_S4_MARKER is not set\n' >&2` and exit 1. Using `+set` (not `-z`) separates unset from empty (FR5). A fixed `%s\n` format prints `-n`, backslashes, `%` sequences, spaces and embedded newlines unchanged in both bash and dash; `echo` would not. Arguments are never read.
- **`qa/s4_marker_test.sh`.** Shebang `#!/bin/sh`, purpose comment, directory resolution copied from `qa/20261110-s3/test_hello.sh:3`. One helper function runs the target in a subshell with a given environment state (exported value, or `unset`), captures stdout with the `x` sentinel, captures stderr separately (redirect to a file from `mktemp`, removed by a `trap` on exit), and compares stdout, stderr and exit code with the expected triple. Cases: non-empty value; empty value; unset; the verbatim values `-n`, `a\nb\c` (literal backslashes), `%s %d`, ` sp `, and a two-line value; a run with extra arguments. The cases run once through the shebang (`"$target"`) and once more via `dash "$target"` when `command -v dash` succeeds; otherwise it prints a `SKIP: dash not installed` line. The first mismatch prints `FAIL: <case> …` on stderr and the script exits 1; when all pass it prints `PASS: …` and exits 0.

**Alternatives rejected.** A pytest file in `tests/` (as `tests/test_hello_sh.py` does) — violates AC3. `#!/bin/bash` (as `hello-world/hello.sh`) — adds a bash dependency on minimal pods. `[ -z "$QA_S4_MARKER" ]` — treats empty as unset, breaks AC5. `echo "$QA_S4_MARKER"` — mangles `-n` and, under dash, backslashes.

## Ordered implementation steps

1. **Create `qa/s4_marker.sh`** with the shebang, purpose comment and the set/unset branch described above; LF endings; `chmod +x` so git records mode `100755`. Advances AC1, AC2, AC4, AC5. Covered by `qa/s4_marker_test.sh` (step 2); the `pytest` layer does not reach it.
2. **Create `qa/s4_marker_test.sh`** with the directory resolution, the case helper (stdout via sentinel, stderr via `mktemp` file with `trap` cleanup, exit code), all cases from the Solution proposal, the optional dash pass, and `PASS`/`FAIL:` output; LF endings; `chmod +x`. Advances AC1, AC2, AC4, AC5 (proof). Test layer: this shell test itself, run as `./qa/s4_marker_test.sh` from the repo root and from another directory (e.g. `cd /tmp && /workspace/…/qa/s4_marker_test.sh`).
3. **Confirm the change boundary and file modes.** `git diff --name-only qa-20261122-s4-base...HEAD` lists only `qa/s4_marker.sh`, `qa/s4_marker_test.sh` and the platform's `stories/SCRUM-109/` files; `git ls-files -s qa/s4_*` shows `100755` for both; `head -c 9` of each is `#!/bin/sh`; neither contains `\r`. Advances AC3 and PLAY-G2. Layer: repo-gate review (`PLAY-G2`, `PLAY-G3`).
4. **Note the base failure for the PR description.** State that the red `test` check comes from `tests/test_qa_20261122_s4_base.py` on `qa-20261122-s4-base` (spec §6, decision b), not from this change. Advances no AC; required by work item t1.

Implicit invariants: no authorization, tenancy, concurrency or persistence surface — the script reads one variable and writes to the caller's own streams. Error path: the unset branch is the only one and is covered by step 2. Dependencies: none beyond a POSIX `sh`, `printf`, `mktemp`, `dirname`; nothing is installed. No generated deliverables; no file approaches 1 MiB, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add qa/s4_marker.sh that prints QA_S4_MARKER, with its shell test |
| 2 | t1 | Add qa/s4_marker.sh that prints QA_S4_MARKER, with its shell test |
| 3 | t1 | Add qa/s4_marker.sh that prints QA_S4_MARKER, with its shell test |
| 4 | t1 | Add qa/s4_marker.sh that prints QA_S4_MARKER, with its shell test |

## Verification and CI gate

- **Canonical gate, in order** (`.github/workflows/ci.yml`, `.factory/testing.md`): job `test` — `pip install -e ".[test]"` then `pytest` on Python 3.12; job `gate` — fails iff `CI_FAIL` exists at the root. Provider CI runs both at the exact head; that run is authoritative.
- **The one local run** is the gate's own: `run-tests-gate.sh --run` on the committed SHA, which executes `local-test-gate:` (`pip install -q -e ".[test]" && pytest`). Do not run `pytest` by hand beside it.
- **Expected gate result.** `pytest` is red with exactly one failure, `tests/test_qa_20261122_s4_base.py::test_pre_existing_failure_on_the_qa_base`, which is pre-existing on the base; every other test passes, and no failure is attributable to this change. `gate` is green (no `CI_FAIL`). Report the red check as blocked by the base, per spec §6 — not as passing.
- **Story proof outside the declared layer.** `./qa/s4_marker_test.sh` exits 0 with a `PASS` line, run in the pod; it is the test-per-AC evidence for AC1, AC2, AC4, AC5. The dash pass is skipped in this pod (dash not installed) and says so.
- **Layout gate.** repo-gate `PLAY-G2` (executable + shebang) and `PLAY-G3` (size) pass for both files; AC3 proven by the `git diff --name-only` check in step 3.
- No provider CI configuration change is needed or allowed. `.factory/testing.md` declares no layer that would cover `qa/` scripts, and it is not to be edited (outside `qa/s4_*`).

## Risks and scope guards

**Risks**

- Executable bit lost → AC1 and `PLAY-G2` fail. Mitigation: `chmod +x` and the mode check in step 3.
- CRLF endings break the shebang. Mitigation: the `\r` check in step 3.
- bash-only behaviour slipping in unnoticed, since `/bin/sh` is bash here and dash is absent. Mitigation: use only POSIX constructs (`[ ]`, `${var+set}`, `printf`, no `local`, no `[[ ]]`, no `$'…'`); build the embedded-newline value with a literal newline inside quotes.
- A secret placed in `QA_S4_MARKER` would be printed; that is the script's purpose and outside this story's control (hld §7).

**Scope guards — the implement phase must NOT**

- Change any file outside `qa/s4_*`: not `tests/` (including `tests/test_qa_20261122_s4_base.py`), `src/`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/`, `README.md`, or other `qa/` scripts.
- Add a pytest test, wire the shell test into CI, or add a `.gitattributes`.
- Make the `test` check green by deleting, skipping, marking `xfail` or editing the base's failing test; it is reported blocked by the base.
- Add a label, prefix, argument handling, validation or defaulting of `QA_S4_MARKER`.
- Create `CI_FAIL`.

## Clarification outcomes

None. The scope question (failing base test) and both edge cases (exit 0 on success, empty value counts as set) were settled by the developer in the intake chat on 2026-11-22 (spec §6, §8); no new blocker arose in planning.
