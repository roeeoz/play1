## Context

Story QA20261110-2 "QA-20261110-S4 hello.sh prints hello s4" (epic QA-20261110-S4) adds a QA sanity script `qa/20261110-s4/hello.sh` to roeeoz/play1. The script prints exactly `hello s4` and exits 0. Next to it goes a self-contained shell test `qa/20261110-s4/test_hello.sh` that runs the script and reports PASS or FAIL through a message and its exit code. One line under `## Unreleased` in `CHANGELOG.md` is also added, because play1's PR gate requires it. The acceptance criteria are scenarios 1–5 in `spec.md` §5: exact output and exit 0; the test passes; the test fails on wrong output or a failed exit; the same result from any directory with no network; and only the agreed files change while all required checks stay green. The work lands on the work branch cut from `qa-20261110-s4-base`, and the PR merges back into that branch. `spec.md`, `hld.md` and `work-items.md` sit next to this file in `stories/QA20261110-2/`.

## Research findings

- **Target folder exists.** `qa/20261110-s4/` already holds only `BASE_MARKER.txt` (mode 100644, one line: "QA-20261110-S4 base marker: this file exists only on qa-20261110-s4-base"). `hello.sh` and `test_hello.sh` do not exist yet and must be created.
- **Existing `qa/` script convention (fact):** `qa/s3-hello.sh:1-3` and `qa/20261109-s1/a.sh:1-3` each have a `#!/bin/sh` shebang, a one-line `#` comment describing the purpose, and a single `printf '...\n'`. `git ls-files -s qa` shows them at mode `100755`.
- **CHANGELOG contract:** `CHANGELOG.md:3` is `## Unreleased`. Entries at `CHANGELOG.md:5-7` follow the format ``- <KEY>: add `<path>`, a <kind> script that prints `<text>`.``, and the file ends after line 7.
- **PR layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-20`):
  - Rule 1: Python goes under `src/`, tests under `tests/`. It does not apply to shell (the developer's ruling is recorded in `spec.md` §6).
  - Rule 2: a new shell script must be executable and start with a shebang.
  - Rule 3: no file over 200 KB.
  - Rule 4: a line must be added under `## Unreleased` in `CHANGELOG.md`, or the gate raises blocker `PLAY-G4`.
- **Canonical gate** (`.factory/testing.md`, `.github/workflows/ci.yml:12-24`): job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. Its single declared layer is `package-api` (`pytest`, required, `runBy: canonical-gate`). Job `gate` (`ci.yml:26-36`) fails only if `CI_FAIL` exists at the repo root. No linter, formatter or coverage tool is configured.
- **pytest does not see `qa/`:** `pyproject.toml` sets `testpaths = ["tests"]`, and `test_hello.sh` is not a pytest file. As the PRD's RK1 accepts, CI will not run the new test.
- **Existing shell-script test pattern:** `tests/test_hello_sh.py:1-30` drives `hello-world/hello.sh` through `subprocess` with byte-exact stdout and stderr assertions. A matching pytest test for the new script is out of scope: `spec.md` §2 Non-Goals rules out changing `tests/`, and `work-items.md` criterion 7 lists `tests/` as untouched.
- **External data:** none. There are no cross-repo contracts and no dependencies.
- **Remaining unknowns:** none.

## Locked decisions and assumptions

**Locked decisions**

- **File paths:** `qa/20261110-s4/hello.sh` and `qa/20261110-s4/test_hello.sh` (Epic PRD R1/R3, `spec.md` FR1–FR5).
- **`hello.sh` output contract:** stdout is exactly `hello s4\n`, stderr is empty, the exit code is 0, and the script takes no input (`hld.md` §5, `work-items.md` t1 criterion 1).
- **`test_hello.sh` result:** it exits 0 if and only if the sibling `hello.sh` exits 0 and its stdout is exactly `hello s4\n`. Otherwise it exits non-zero and prints a message that says what was wrong (`hld.md` §5).
- **Locating the script:** the test finds `hello.sh` from its own `$0` directory and is not affected by the current directory or `CDPATH` (`hld.md` §6, FR5).
- **Shell and file format:** POSIX `#!/bin/sh`, git mode `100755`, LF only, no test-only override variable (`hld.md` §6).
- **CHANGELOG:** exactly one added line under `## Unreleased` naming QA20261110-2 and `qa/20261110-s4/hello.sh`, with no other line changed (`spec.md` FR6, gate rule 4).
- **Scope:** `BASE_MARKER.txt`, `src/`, `tests/`, `.github/workflows/ci.yml` and `pyproject.toml` are untouched (`spec.md` FR7, `work-items.md` criterion 7).
- **No CI wiring for `test_hello.sh`:** it is accepted as RK1, and scenarios 1–4 are verified by hand and recorded in the PR description (PRD §6, `work-items.md` criterion 9).

**Assumptions**

- **The new CHANGELOG line goes last under `## Unreleased`** (after `CHANGELOG.md:7`) and uses the story key as its prefix: ``- QA20261110-2: add `qa/20261110-s4/hello.sh`, a QA script that prints `hello s4`, with its test `qa/20261110-s4/test_hello.sh`.``
  - Evidence: the existing entries are appended in order and prefixed with their tracker key.
  - If wrong: cosmetic only. Gate rule 4 checks only that a line was added.
- **`test_hello.sh` uses `printf` and `[`/`test` only**, with no `mktemp`, `diff` or `cmp`. To keep trailing newlines in the comparison, it appends a sentinel character inside the command substitution and checks it.
  - Evidence: `hld.md` §6 asks for a newline-preserving comparison, and builtin-only code removes any toolchain dependency.
  - If wrong: an alternative comparison is equally valid as long as criterion 3's cases (extra line, extra blank line, missing newline) fail.

## Solution proposal

Add two standalone POSIX `sh` scripts in the existing `qa/20261110-s4/` folder, plus one CHANGELOG line. Nothing in `src/`, `tests/` or CI changes.

**`hello.sh`** follows the existing `qa/` convention exactly:
- a shebang;
- a one-line purpose comment naming epic QA-20261110-S4;
- `printf 'hello s4\n'`.

Use `printf` rather than `echo`, because it has defined byte behaviour across `sh` implementations. The script ignores arguments and stdin, and the exit status is that of `printf` (0).

**`test_hello.sh`** works in these steps:
1. Resolve its own directory without `cd` side effects from `CDPATH`: `dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)`.
2. Run `"$dir/hello.sh"`, capturing stdout plus a sentinel (for example `out=$("$dir/hello.sh"; rc=$?; printf x; exit $rc)`), and record the exit status. Use `set -u`, but not `set -e`, so a failed `hello.sh` is reported instead of aborting the test silently.
3. Strip the sentinel, then compare the result with the expected value `hello s4` plus a newline. The expected value is built with `printf 'hello s4\nx'` and the same stripping, so both sides are treated identically.
4. If the exit status is 0 and the output matches, print `PASS: hello.sh printed "hello s4"` and exit 0.
5. Otherwise print a `FAIL:` line that gives the exit status or the output that came back, and exit 1. It is fine for the FAIL message to go to stdout or stderr. The visible text and the exit code carry the result.

Keep each script at a few lines plus comments.

**Scenario 3 check, done by hand:** copy both scripts to a temporary directory and change the copy of `hello.sh`. Try different text, an extra line, a missing newline, and correct output followed by `exit 3`. Run the copied `test_hello.sh` each time and expect a non-zero exit. The committed files are never edited.

**Alternatives rejected:**
- **A `HELLO_SH` override variable:** it adds surface the spec did not ask for (`hld.md` §6).
- **A pytest wrapper under `tests/`:** it would change `tests/`, which is out of scope (FR7, RK1 accepted).
- **`#!/bin/bash`:** it works, but is inconsistent with the other `qa/` scripts.
- **Comparing `$(...)` output directly:** it silently strips trailing newlines, so it would miss criterion 3's extra-blank-line and missing-newline cases.

## Ordered implementation steps

1. **Create `qa/20261110-s4/hello.sh`** (new): shebang `#!/bin/sh`, a one-line purpose comment, and `printf 'hello s4\n'`. LF line endings. Set git mode `100755` (`chmod +x`; confirm with `git ls-files -s` after staging).
   - Advances: scenario 1 / t1 criteria 1 and 5.
   - Covered by: the manual shell check (no existing automated layer runs `qa/`, RK1). Run `./qa/20261110-s4/hello.sh | od -c` and expect `h e l l o   s 4 \n`. Expect `$?` to be 0 and stderr to be empty (`2>&1 >/dev/null` gives nothing).
2. **Create `qa/20261110-s4/test_hello.sh`** (new), as described in the Solution proposal: resolve its own directory with `CDPATH` cleared, run the sibling `hello.sh`, use the sentinel comparison with a separately captured exit status, print PASS/FAIL, and exit 0 or 1. Use `#!/bin/sh`, LF only, mode `100755`. Handle the error path where `hello.sh` exits non-zero or is missing or not executable: that is a FAIL, never a crash that exits 0.
   - Advances: scenarios 2–4 / t1 criteria 2–5.
   - Covered by: manual runs.
     - Scenario 2: `qa/20261110-s4/test_hello.sh` exits 0 and prints `PASS`.
     - Scenario 4: run it from the repo root, from `qa/20261110-s4/` (`./test_hello.sh`), from `/tmp` using the absolute path, and with `CDPATH=/tmp` exported. All give PASS and exit 0. No network or clock is used.
     - Scenario 3: in a `mktemp -d` copy, run four mutations (text `hello`, extra line, `printf 'hello s4'` with no newline, correct output then `exit 3`). Each gives FAIL and a non-zero exit. Then delete the temporary directory.
3. **Append one line to `CHANGELOG.md`** after line 7, under `## Unreleased`, in the existing entry format and naming QA20261110-2 and `qa/20261110-s4/hello.sh` (see Assumptions). Change no other line, and keep the trailing newline.
   - Advances: t1 criterion 6 / gate rule 4.
   - Covered by: `git diff CHANGELOG.md` shows exactly one `+` line and no `-` lines.
4. **Check the scope boundary:** `git diff --name-only qa-20261110-s4-base...HEAD` must list only `qa/20261110-s4/hello.sh`, `qa/20261110-s4/test_hello.sh`, `CHANGELOG.md` and files under `stories/QA20261110-2/`. Also confirm that neither script contains a CR character (`grep -c $'\r'` gives 0, or the `od -c` check) and that both are well under 200 KB.
   - Advances: scenario 5 / t1 criteria 5 and 7.
   - Covered by: the git diff check.
5. **Run the canonical gate** (see Verification) and confirm `pytest` is green and no `CI_FAIL` exists.
   - Advances: scenario 5 / t1 criterion 8.
   - Covered by: the `package-api` layer (`pytest`).
6. **Write the PR description** to cite story QA20261110-2 "QA-20261110-S4 hello.sh prints hello s4" and the Epic PRD "סקריפט hello s4 (בדיקת שפיות של QA)". Record the manual results of scenarios 1–4 from steps 1–2, and state that CI does not run `test_hello.sh` (RK1).
   - Advances: t1 criterion 9.
   - Covered by: no test layer applies, because this is PR metadata.

**Invariants:**
- Authorization, tenancy and concurrency do not apply: these are stateless local scripts with no input.
- The validation and error path is step 2's handling of a non-zero `hello.sh` exit.
- No dependencies are acquired.
- There are no generated deliverables.

## Work-item mapping

| Step | Work item |
| --- | --- |
| 1 — create `hello.sh` | t1 — QA-20261110-S4 hello.sh prints hello s4 |
| 2 — create `test_hello.sh` | t1 — QA-20261110-S4 hello.sh prints hello s4 |
| 3 — CHANGELOG line | t1 — QA-20261110-S4 hello.sh prints hello s4 |
| 4 — scope and format check | t1 — QA-20261110-S4 hello.sh prints hello s4 |
| 5 — canonical gate | t1 — QA-20261110-S4 hello.sh prints hello s4 |
| 6 — PR description | t1 — QA-20261110-S4 hello.sh prints hello s4 |

t1 is the only work item, and every step belongs to it.

## Verification and CI gate

**Canonical gate**, run once locally on the committed SHA from the repo root:
1. `pip install -e ".[test]"`
2. `pytest`

This mirrors job `test` in `.github/workflows/ci.yml`. Job `gate` needs no `CI_FAIL` at the repo root.

**Required layer:** `package-api` (`pytest`, `runBy: canonical-gate`). It runs in a pod, but the provider CI run at the PR head is the authoritative result (`.factory/testing.md`). The change adds no Python, so `pytest` must stay green with the same test count as on the base branch.

**Not a declared layer:** `test_hello.sh` is not part of the canonical gate (RK1, accepted). It runs by hand per steps 1–2, and its results go into the PR description.

**PR layout gate (`repo-gate`):**
- Rule 2: both scripts are `100755` and start with `#!/bin/sh`.
- Rule 3: all files are under 200 KB.
- Rule 4: the `CHANGELOG.md` line has been added.

**Provider CI changes:** none.

**`.factory/delivery-assets`:** not applicable, because no binary is added.

**Done means:**
- `pytest` is green and both CI jobs are green at the PR head.
- The repo-gate verdict passes.
- The manual run of scenarios 1–4 matches the expected results.
- The diff is limited to the three product files plus `stories/QA20261110-2/`.

## Risks and scope guards

**Risks**

- **RK1:** CI never runs `test_hello.sh`, so a broken script could merge green.
  - Mitigation: the manual scenario 1–4 run is recorded in the PR (accepted by the PRD).
- **Missing executable bit:** a missing exec bit breaks rule 2, and the script cannot be run by path.
  - Mitigation: verify `100755` with `git ls-files -s qa/20261110-s4`.
- **CRLF line endings:** these break the shebang.
  - Mitigation: the CR check in step 4.
- **Newline-stripping comparison:** this would make criterion 3's edge cases pass wrongly.
  - Mitigation: the sentinel comparison and the four-mutation check in step 2.

**Scope guards.** The implement phase must NOT:
- Modify `qa/20261110-s4/BASE_MARKER.txt`, `src/`, `tests/`, `.github/workflows/ci.yml`, `pyproject.toml`, `README.md`, `.factory/`, or any existing `qa/` script.
- Change, reorder or reformat any existing line of `CHANGELOG.md`.
- Add a pytest wrapper, wire `test_hello.sh` into CI, or add a `--help` option, an environment override or documentation.
- Leave a modified `hello.sh` or temporary files in the tree after the scenario 3 check.
- Create `CI_FAIL`.
- Add any dependency.
- Make a failing check green by deleting, skipping, disabling or weakening it. A check that is blocked is reported as blocked.

## Clarification outcomes

None.
