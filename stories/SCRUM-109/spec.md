# Feature Specification Document — QA-20261122-S4: a script that prints the project's QA_S4_MARKER value

> Status: READY_FOR_SPEC — the developer settled the scope question and both edge cases in the intake chat on 2026-11-22.

## 1. Feature Overview

- **What is being built:** one small shell script, `qa/s4_marker.sh`, in `roeeoz/play1`, that prints the value of the environment variable `QA_S4_MARKER`.
- **Problem:** a developer cannot quickly see which environment a pod runs with; the `QA_S4_MARKER` value identifies it.
- **Actor:** a developer with a shell in the pod (or any environment where the repository is checked out).

## 2. Goals & Non-Goals

### Goals
- Running `qa/s4_marker.sh` shows the developer the exact value of `QA_S4_MARKER`.
- When the variable is unset, the developer gets a clear message on stderr and a non-zero exit (1).
- A caller can tell success (exit 0) from the unset case (exit 1).

### Non-Goals
- Any change to a file outside `qa/s4_*` (story scope: "add one file, qa/s4_marker.sh … and only files under qa/s4_*. Do not change anything else.").
- Setting, validating or interpreting `QA_S4_MARKER` (the script only reports it).
- Changes to the Python package, tests, CI workflow or other `qa/` scripts.

## 3. Functional Requirements

- **FR1 — Location and runnability.** The script is `qa/s4_marker.sh`, is executable, and runs directly (`./qa/s4_marker.sh`).
- **FR2 — Variable set.** Input: `QA_S4_MARKER` set in the environment. Output on stdout: exactly the variable's value followed by one newline; nothing else on stdout. Exit status 0.
- **FR3 — Variable unset.** Input: `QA_S4_MARKER` not set. Output on stderr: `QA_S4_MARKER is not set`; exit status 1.
- **FR4 — Scope boundary.** The change adds/edits only files matching `qa/s4_*`.
- **FR5 — Variable set to an empty string.** Treated as set (developer's decision): stdout is an empty line (a single newline), nothing on stderr, exit status 0.

## 4. User Experience & Behavior

- **Flow:** the developer runs `qa/s4_marker.sh` in a shell → sees the marker value on its own line (exit 0; an empty line when the value is empty), or sees `QA_S4_MARKER is not set` on stderr and exit status 1.
- **Output format:** the raw value only — no label, prefix, quoting or trailing text beyond one newline — so it can be piped or captured by other commands.
- No visual, interactive or other sensory requirements were named.

## 5. Acceptance Criteria

1. qa/s4_marker.sh exists, is executable, and prints exactly the value of QA_S4_MARKER followed by a newline.
2. When QA_S4_MARKER is unset, the script prints 'QA_S4_MARKER is not set' to stderr and exits 1.
3. No file outside qa/s4_* is changed.
4. When QA_S4_MARKER is set, the script exits 0.
5. When QA_S4_MARKER is set to an empty string, the script prints an empty line (a single newline) to stdout and exits 0.

## 6. Dependencies & Constraints (product-level)

- **Pre-existing failing test on the target branch.** `qa-20261122-s4-base` head commit `ea6f718` adds `tests/test_qa_20261122_s4_base.py`, whose only test asserts `1 == 2`. The repository's required test gate is `pytest` over the whole suite (`.factory/testing.md`; the `test` job in `.github/workflows/ci.yml`), so this story's pull request is expected to show a red `test` check caused by the base, not by this change.
- **Decision (developer, 2026-11-22): option (b).** The scope stays as written: this story changes only `qa/s4_*` files and does not touch that test. The failure is a known pre-existing one on the base, not this story's to fix; delivery goes ahead, and the developer decides at merge time what to do about the red base test. No exemption from the gate is recorded here; the merge is a person's decision.
- **Repository layout gate** (`.factory/plugins/claims-dev/skills/repo-gate`, rule PLAY-G2): a new shell script must be executable and start with a shebang. This is consistent with acceptance criterion 1.
- A person reviews and merges the pull request; the factory never merges.

## 7. Technical Design (deferred to STRUCTURE)

Shell dialect, how the script is tested, and how the evidence is produced are left to STRUCTURE. Product-imposed constraint: the deliverable lives entirely under `qa/s4_*`.

## 8. Open Questions (if any remain)

None blocking. Settled in the intake chat (2026-11-22):

- **Q1 — Failing base test vs. scope:** (b) — scope stays `qa/s4_*` only; the red base test is the developer's call at merge.
- **Q2 — Exit status on success:** 0.
- **Q3 — Set but empty:** treated as set — prints an empty line, exits 0.
