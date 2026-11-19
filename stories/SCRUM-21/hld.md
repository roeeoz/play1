# HLD — SCRUM-21: Hello world bash script in a dedicated folder

## 1. System Overview

- **What:** a bash script `hello-world/hello.sh` in its own folder that prints
  `hello world` and exits 0 (spec FR1–FR5).
- **Verified state of `main` (read from the checkout, not assumed):**
  - `hello-world/hello.sh` is tracked with mode `100755` (`git ls-files -s`), added
    by commit `65938b5`; its content is exactly two lines: `#!/bin/bash` and
    `echo "hello world"`. It is the only file in `hello-world/`.
  - Running `./hello-world/hello.sh` emits the 12 bytes `hello world\n`, exit 0.
  - `tests/test_hello_sh.py` already asserts output `== "hello world\n"`, empty
    stderr, exit code 0, shebang line, executable bit, and folder contents
    `== ["hello.sh"]`; it passes (6 tests) on the current tree.
  - `CHANGELOG.md` `## Unreleased` has **no** entry for the hello-world script.
- **Problem left to solve:** the code already meets the four acceptance criteria;
  per spec FR6/A1 the story is delivered as a verification of that state. The only
  change any PR may carry is the `CHANGELOG.md` line the layout gate requires
  (rule 4, `PLAY-G4`).

## 2. Architecture Overview

- One repository: `play1` (target branch `main`). No services, no runtime deps.
- Components (all existing):
  - `hello-world/hello.sh` — the deliverable. **Kept unchanged** (A1).
  - `tests/test_hello_sh.py` — verification of AC 1–4, run by the `pytest` gate.
  - `CHANGELOG.md` — receives one traceability line under `## Unreleased`.
- Gates on every PR: `.github/workflows/ci.yml` (`test` job: `pip install -e
  ".[test]"` + `pytest`; `gate` job: fails iff `CI_FAIL` exists), and the layout
  gate `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` (rules 1–4).

## 3. Data Flow Design

- Synchronous only: developer (or pytest via `subprocess.run`) executes
  `./hello-world/hello.sh` → kernel honours the `#!/bin/bash` shebang →
  `echo` writes `hello world\n` to stdout → exit code 0.
- No input, no state, no files read or written, no network.

## 4. Component Breakdown

| Component | Responsibility | In / Out | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Print the greeting | none / `hello world\n`, exit 0 | play1 (unchanged) |
| `tests/test_hello_sh.py` | Assert AC 1–4 | script / pass-fail | play1 (unchanged; extended only if a gap is found) |
| `CHANGELOG.md` | Trace SCRUM-21 for gate rule 4 | — / one new bullet | play1 (t1) |

## 5. Interface Contracts

- CLI contract: `./hello-world/hello.sh` (no args) → stdout exactly
  `hello world\n` (single terminating newline allowed, A2), stderr empty, exit 0.
- File contract: `hello-world/` contains exactly `hello.sh`, mode `100755`, first
  line `#!/bin/bash`.
- No cross-repo contracts.

## 6. Key Technical Decisions

- **Verify, don't rewrite (A1).** The script already satisfies FR1–FR5; rewriting
  it would add risk and churn with no behaviour change.
- **Single PR = one CHANGELOG bullet** tracing SCRUM-21. Required by gate rule 4
  (a PR without a `CHANGELOG.md` change is a `PLAY-G4` blocker); it is an entry in
  an existing file, not a new documentation file, so it respects the non-goal.
- **Existing test is the verification.** `tests/test_hello_sh.py` already covers
  all four scenarios; no new test file, no CI change (CI is a non-goal).
- Alternative considered: close the story without a PR — remains the human's
  option (spec A1); not chosen because the factory delivers per work item.

## 7. Risks & Constraints

- **No-op risk (A1):** the PR has no user-visible effect; if the requester meant a
  different folder/name/content, this story doesn't deliver it.
- **Byte-exactness (A2):** output is `hello world\n`; a consumer comparing raw
  bytes to the 11-byte `hello world` would mismatch. Accepted per spec.
- **Portability:** requires `/bin/bash` (present on `ubuntu-latest` CI and typical
  dev hosts). Executable bit relies on git mode `100755`; checkouts on
  filesystems ignoring modes (e.g. some Windows setups) could lose it — out of
  scope.
- **Folder-isolation test ignores dotfiles** (`tests/test_hello_sh.py`
  filters names starting with `.`); acceptable as no dotfile exists in the folder.
- Scale / performance / security: not applicable (static, input-free script).
