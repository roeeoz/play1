# Implementation plan — PLAY-167: farewell script `qa/20261109-s3/bye.sh`

## Context

PLAY-167 adds one executable bash script, `qa/20261109-s3/bye.sh`. With no argument, or an empty first argument, it prints `bye`. With a non-empty first argument it prints `bye`, then `bye <first argument>` exactly as given; later arguments are ignored. It always exits 0. The spec's acceptance criteria 1–9 cover the no-name, name, multi-word, `--help`, empty, spaced-name and shebang/executable cases, plus the scope check (only the script and one CHANGELOG line) and the existing CI staying green. The change lands in `roeeoz/play1` on the work branch `halo/feat/play-167-20261109-101240`, cut from and merging into `qa-20261109-s3-base`. `spec.md` (approved requirement, Hebrew), `hld.md` (design) and `work-items.md` (one work item, `t1`) sit next to this file in `stories/PLAY-167/`.

## Research findings

**Change surface**
- `qa/20261109-s3/` exists on the base branch and holds only `BASE_MARKER.md` (`git ls-files -s`: mode `100644`). `bye.sh` is **new**.
- Neighbouring scripts follow one convention: `qa/s3-a.sh:1-3` and `qa/s3-hello.sh:1-3` are a shebang (`#!/bin/sh`), a one-line `#` purpose comment, then a `printf` with a literal format. Both are tracked as `100755`.
- `CHANGELOG.md:3-6` has `## Unreleased` with two entries in the form ``- PLAY-<n>: add `<path>`, a helper script that prints `<x>`.``; the last is the PLAY-156 line at `CHANGELOG.md:6`.
- No `.gitattributes` exists, so line endings depend on the editor; the file must be written with LF.

**Contracts**
- The only contract is the CLI table in `hld.md` §5 / `spec.md` §4: stdout lines each end in LF, nothing on stderr, exit 0.
- Repo-gate rules (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md:14-20`):
  - Rule 2: a new shell script is executable and has a shebang.
  - Rule 3: no file is 200 KB or larger.
  - Rule 4 / `PLAY-G4`: a PR that doesn't add a line under `## Unreleased` in `CHANGELOG.md` is a blocker.

**Tests and gate**
- The gate is defined in `.factory/testing.md:3-10`: `pip install -e ".[test]"` then `pytest`, as the `test` job of `.github/workflows/ci.yml:12-24` on Python 3.12. The second CI job, `gate` (`.github/workflows/ci.yml:26-38`), fails only if a `CI_FAIL` file exists at the repo root.
- There is no linter, formatter or type checker. The only declared test layer is `package-api` (`pytest`, `runBy: canonical-gate`).
- `pyproject.toml:26-28` sets `testpaths = ["tests"]`. No test touches `qa/20261109-s3/`: `tests/test_qa_s3_greeting.py:4` targets only `qa/s3-hello.sh`, and `tests/test_hello_sh.py:35,69-72` asserts only on `hello-world/`. The new file therefore can't break an existing test, and no CI layer runs it.

**Environment and external data**
- Local `/usr/bin/bash` is 5.2.15; CI runs on `ubuntu-latest`, which ships bash 5.x.
- The change depends on no external system's data.

**Unknowns**
- None remain. The spec's §8 records all PO and developer decisions.

## Locked decisions and assumptions

**Locked decisions**
- Path is `qa/20261109-s3/bye.sh` (spec FR1, R1).
- First line is exactly `#!/bin/bash`, and the file is executable (spec FR1, AC9; PO decision P1). This is a deliberate departure from the `#!/bin/sh` convention of `qa/s3-*.sh`.
- No argument or `""` prints only `bye` (spec FR2, FR5).
- A non-empty `$1` prints `bye`, then `bye $1` exactly as given, including spaces and a leading `-` (spec FR3, FR6, FR7).
- Arguments after the first are ignored (spec FR4).
- The script exits 0 (spec FR8).
- No help text and no input validation; `--help` is an ordinary name (spec Non-Goals, FR7).
- No pytest test for the script (spec Non-Goals; `hld.md` §6; epic risk RK2).
- Outside `stories/PLAY-167/`, the diff is exactly the new `bye.sh` plus one added PLAY-167 line under `## Unreleased` in `CHANGELOG.md` (spec FR9, AC5; P0-1, P0-2; repo-gate rule 4).
- `qa/s3-a.sh`, `qa/s3-hello.sh` and `qa/20261109-s3/BASE_MARKER.md` stay unchanged (spec AC5).
- The PR cites PLAY-167 and the epic PRD, Confluence pageId 34013185 (Compliance R7; `work-items.md` AC15).

**Assumptions**
- *The name is printed through `printf` with a fixed format and the name as a separate argument.* Evidence: `hld.md` §6 reports this was prototyped on bash 5.2, and it matches `qa/s3-*.sh`. If wrong (for example, if `echo` is used), names like `-n`, `-e` or ones containing `\` print incorrectly, which breaks `work-items.md` AC7.
- *The line-2 purpose comment is included,* following the `qa/` convention (`hld.md` §6 calls it optional). If it's unwanted, the file is one line shorter and behaviour is unchanged.
- *The CHANGELOG wording follows the existing pattern,* for example ``- PLAY-167: add `qa/20261109-s3/bye.sh`, a helper script that prints `bye` (and `bye <name>` when a name is given).`` Evidence: `CHANGELOG.md:5-6`. The wording isn't contractual; rule 4 only needs the line to exist.

## Solution proposal

**Approach.** Add a standalone three- or four-line bash script. It is separate from the Python package, so `pyproject.toml`, `src/` and `tests/` are untouched. The script body:
1. Print `bye` with a fixed `printf` format.
2. If `$1` is non-empty (an `-n "${1-}"`-style test, which also treats an unset `$1` as empty), print `bye ` followed by `"$1"`, passing the name as a `%s` argument and never as part of the format string.
3. End explicitly with `exit 0`.

**Key design decisions**
- **`printf '%s\n'`-style output with the name as data.** Names containing `%`, `\`, spaces or a leading `-` (including `--help` and `-n`) then print literally. Quoting `"$1"` keeps `"Alice Smith"` whole.
- **Explicit `exit 0`, or an `if … fi` block as the last statement.** A trailing `[ -n "$1" ] && printf …` leaves exit status 1 when no name is given, which would break FR8 and AC1/AC7. This is the one real correctness trap in the change.
- **Ignore `$2` and later arguments** by never reading them, which satisfies FR4.
- **No `set -u`/`-e` pitfalls:** if strict mode is used, read `$1` as `${1-}` so an unset `$1` doesn't abort.

**Alternatives rejected**
- A Python console script in `src/`: it touches the package and breaks FR9.
- `echo "bye $1"`: bash `echo` treats a leading `-n` or `-e` as options.
- Interpolating the name into the format string: `%` and `\` in the name would be interpreted.
- Adding a pytest test in `tests/`: excluded by the spec and RK2.
- Putting the CHANGELOG line in a separate PR: each PR must pass rule 4 on its own (`hld.md` §6).

## Ordered implementation steps

1. **Create `qa/20261109-s3/bye.sh` (new).**
   - Content: line 1 is exactly `#!/bin/bash`; line 2 is a one-line `#` purpose comment; then the body described in the Solution proposal.
   - Use LF line endings with a trailing newline. Keep it ASCII only.
   - Implicit invariants:
     - No file I/O, no network, no environment reads.
     - Empty or unset `$1` prints one line.
     - Exit status is 0 on every path; there are no error paths to handle.
     - No authorization, tenancy or concurrency concerns apply.
   - Advances spec AC1–4, AC7–9 and `work-items.md` AC1–9 and AC13.
   - Test layer: none exists for `qa/20261109-s3/`, and the spec forbids adding one. Verify by the manual runs in step 3.
2. **Make the script executable in git.** Run `chmod 755 qa/20261109-s3/bye.sh` so the tracked mode is `100755`. Confirm with `git ls-files -s qa/20261109-s3/bye.sh` once the build stages it.
   - Advances spec AC9 and `work-items.md` AC10 (repo-gate rule 2).
   - Test layer: none; checked by the `git ls-files -s` output.
3. **Run the script by hand and record the transcript for the PR description.** Run each invocation from the repo root, capturing stdout, stderr and `$?`. A `| od -c` check shows the exact bytes and LF endings.
   - No arguments → `bye\n`.
   - `""` → `bye\n`.
   - `Alice` → `bye\nbye Alice\n`.
   - `Alice Bob` → `bye\nbye Alice\n`, with no `Bob`.
   - `"Alice Smith"` → `bye\nbye Alice Smith\n`.
   - `--help` → `bye\nbye --help\n`.
   - `-n`, `'%s'` and `'a\b'` → each printed literally after `bye `.
   - Every run: empty stderr and exit 0. Also check `head -1` shows `#!/bin/bash` and `grep -c $'\r'` returns 0.
   - Advances spec AC1–4, AC7–9 and `work-items.md` AC1–9 and AC16.
   - Test layer: manual evidence only (stated gap; see Risks).
4. **Add the CHANGELOG entry.** Insert one line in `CHANGELOG.md` directly after the PLAY-156 line (`CHANGELOG.md:6`), under `## Unreleased`, in the existing format. Change nothing else in the file.
   - Advances spec AC5 and `work-items.md` AC11 (repo-gate rule 4, `PLAY-G4`).
   - Test layer: none; checked by the diff in step 5.
5. **Check the scope of the diff.** Run `git diff --stat qa-20261109-s3-base...HEAD -- . ':!stories/PLAY-167'`. It must list only `qa/20261109-s3/bye.sh` (added) and `CHANGELOG.md` (+1 line). There must be no `CI_FAIL`, and no change to `tests/`, `.github/`, `pyproject.toml`, `qa/s3-a.sh`, `qa/s3-hello.sh` or `qa/20261109-s3/BASE_MARKER.md`.
   - Advances spec AC5 and `work-items.md` AC11–12.
   - Test layer: none; checked by the diff.
6. **Run the canonical gate** (see Verification and CI gate).
   - Advances spec AC6 and `work-items.md` AC14.
   - Test layer: `package-api` (`pytest`).

No dependencies are acquired. The script needs only bash, and the gate uses `pip install -e ".[test]"` from a cold cache, exactly as CI does. There are no generated deliverables, and no binary of 1 MiB or more, so `.factory/delivery-assets` doesn't apply.

## Work-item mapping

| Step | Work item | Title |
| --- | --- | --- |
| 1–6 | `t1` | PLAY-167: add qa/20261109-s3/bye.sh farewell script and CHANGELOG entry |

`t1` is the only work item, and every step maps to it.

## Verification and CI gate

- **Canonical gate** (`.factory/testing.md:5-10`), run once locally from the repo root on the committed SHA: `pip install -e ".[test]"`, then `pytest`. It must pass with no failures and no new skips. The suite is unchanged, so its duration stays well under 60 s (G4). The provider CI run on the PR head is the authoritative result for `package-api`.
- **Required layers:** only `package-api` (`pytest`). It runs unprivileged in a pod. No layer runs `bye.sh`, so the script's behaviour is proven by the step-3 transcript in the PR description (`work-items.md` AC16).
- **Provider CI:** the `test` and `gate` jobs in `.github/workflows/ci.yml` must both be green. `gate` stays green because no `CI_FAIL` is added. No CI configuration change is needed or allowed.
- **`.factory/testing.md`:** no update needed, because no layer is added. `.factory/delivery-assets` doesn't apply.
- **Done means:**
  - `pytest` and both CI jobs are green.
  - `git ls-files -s` shows `100755` for `bye.sh`.
  - The scope diff in step 5 is exact.
  - The manual transcript matches every row of the `hld.md` §5 table.
  - The PR body cites PLAY-167 and Confluence pageId 34013185.

## Risks and scope guards

**Risks**
- *The executable bit is lost* (for example, `core.fileMode=false`, or the file is written without `chmod`). Repo-gate rule 2 fails, and CI doesn't catch it. Mitigation: step 2 plus the `git ls-files -s` check.
- *A false test is the last command* and leaves exit status 1 when there is no name. Mitigation: end with `exit 0` or an `if … fi` block; step 3 checks `$?` for the no-argument and `""` cases.
- *CRLF line endings or a BOM* break the shebang. Mitigation: write with LF; step 3 checks for `\r`.
- *The script has no automated coverage.* It's an accepted, spec-sanctioned gap (RK2); the evidence is manual.
- *Reviewers ask for a test or `--help` text* (epic RK1/RK2). Point to spec Non-Goals and §8; don't expand scope.

**Scope guards: the implement phase must NOT**
- Add a test under `tests/`, or change `pyproject.toml`, `.github/`, `src/`, `docs/`, `README.md` or `.factory/`.
- Change `qa/s3-a.sh`, `qa/s3-hello.sh` or `qa/20261109-s3/BASE_MARKER.md`, or "align" the `qa/s3-*.sh` shebangs.
- Edit, reorder or reformat existing `CHANGELOG.md` lines; only one line is added.
- Add a `CI_FAIL` file, help text, input validation, colour, or stderr output.
- Change `spec.md`, `hld.md` or `work-items.md`.
- Make any check green by deleting, skipping, disabling or weakening it. A blocked check is reported as blocked.

## Clarification outcomes

None.
