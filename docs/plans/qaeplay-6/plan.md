# Implementation Plan — Add hello-world bash script in dedicated folder

Work item: **t1** · Tier: T1 · Repository: play1

## Research findings

### Change surface

The ticket adds one new file (`hello-world/hello.sh`) in one new directory (`hello-world/`) at the repository root. No existing files are modified.

### Existing state

Commit `86f36c2` on the current branch already delivers the complete implementation:

| Check | Result |
|---|---|
| `hello-world/` directory exists at repo root | Yes |
| Only file in directory is `hello.sh` | Yes (`ls hello-world/` → `hello.sh`) |
| Shebang line is `#!/bin/bash` | Yes (`head -1` confirms) |
| Executable permissions set | Yes (mode 755) |
| Output is exactly `hello world` | Yes (`od -c` shows `h e l l o   w o r l d \n`, 12 bytes, no leading/trailing whitespace, no extra lines) |
| Exit code is 0 | Yes |

### Repository gate

The canonical gate is `pytest` (per `.factory/testing.md`). No linter, formatter, or type checker is configured. The `hello-world/hello.sh` script is a standalone shell artifact outside the Python package; it has no pytest coverage and the spec explicitly lists CI/CD integration as a non-goal.

### Contracts and dependencies

- No APIs, event schemas, or cross-repo contracts are affected.
- No existing modules are imported or modified.
- No large binary deliverables are introduced; `.factory/delivery-assets` is not needed.
- No `.factory/memory/` directory exists; no repo memories to consult.
- No `CLAUDE.md` or `AGENTS.md` exists.

## Solution proposal

The implementation is a two-line bash script in a new directory — no design decisions beyond what the spec mandates:

1. **Shebang**: `#!/bin/bash` (spec-mandated, FR3).
2. **Output command**: `echo "hello world"` — produces the exact required lowercase string with a single trailing newline and implicit exit code 0.
3. **Permissions**: `chmod +x` sets mode 755 (spec-mandated, FR4).
4. **Folder isolation**: `hello-world/` contains only `hello.sh` (spec-mandated, FR1).

The existing commit `86f36c2` implements all four points correctly. The implement phase should verify the script is still present and unchanged on the branch head, and ensure `pytest` passes (the gate does not cover this script but must remain green).

## Ordered implementation tasks

| # | Work item | Action | Files | AC |
|---|---|---|---|---|
| 1 | t1 | Verify `hello-world/` exists at repo root with only `hello.sh` | `hello-world/hello.sh` (exists) | AC1, AC2 |
| 2 | t1 | Verify shebang is `#!/bin/bash` and permissions are executable | `hello-world/hello.sh` (exists) | AC3, AC4 |
| 3 | t1 | Run `./hello-world/hello.sh` and confirm output is exactly `hello world` with exit code 0 | — | AC5, AC6 |
| 4 | t1 | Run `pytest` to confirm the repository gate is still green | — | Gate integrity |

Since the implementation already exists on this branch, the implement phase validates rather than creates. If the script has been modified or removed between plan and implement, steps 1–3 become corrective: recreate the directory and script as specified.

## Verification

The gate for this change is `pip install -e ".[test]" && pytest`, run from the repo root after the editable install. The script itself is not exercised by pytest; its correctness is verified by direct execution.

| AC | Verification | Expected |
|---|---|---|
| AC1 — folder exists with `hello.sh` | `ls hello-world/` | `hello.sh` (sole entry) |
| AC2 — folder isolation | `ls hello-world/` | exactly one file |
| AC3 — shebang line | `head -1 hello-world/hello.sh` | `#!/bin/bash` |
| AC4 — executable permissions | `stat` or `ls -l` on file | executable bit set |
| AC5 — output exactness | `./hello-world/hello.sh \| od -c` | `h e l l o   w o r l d \n` (12 bytes) |
| AC6 — exit code 0 | `./hello-world/hello.sh; echo $?` | `0` |
| Gate — pytest green | `pip install -e ".[test]" && pytest` | all tests pass |

## Risks and scope guards

- **No new risks.** The change is additive, self-contained, and touches no existing code or configuration.
- **Scope guard — no additional files.** The spec's non-goals explicitly exclude documentation, CI integration, and additional scripts. The `hello-world/` directory must contain only `hello.sh`.
- **Scope guard — no gate changes.** The canonical gate (`pytest`) and CI configuration (`.github/workflows/ci.yml`) must not be modified by this ticket.
- **Scope guard — no `.factory/testing.md` update.** The shell script is not a test layer and CI is a non-goal; `testing.md` stays as-is.

## Clarification outcomes

No clarifications needed. All requirements are fully specified by the spec and work-item acceptance criteria, and the existing implementation satisfies them.
