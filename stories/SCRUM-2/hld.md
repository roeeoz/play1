# HLD — SCRUM-2: Hello world bash script in a dedicated folder

## 1. System overview
- **What:** a runnable `hello-world/hello.sh` at the root of the play1 repo. It prints exactly `hello world` and exits 0.
- **State of `main` (`b7b5d0a`):** already delivered by WI-220A63:
  - The script is `#!/bin/bash` followed by `echo "hello world"`. It is 31 bytes, LF line endings, git mode 100755.
  - It is the only entry in `hello-world/`.
  - `tests/test_hello_sh.py` holds 6 tests and passes.
- **Responsibility of this story:** show that each AC is met on the target branch, and close the single coverage gap found: the AC2 isolation test ignores dotfiles. The script is not rebuilt.

## 2. Architecture overview
| Component | Path | Owner in this story | Change |
|---|---|---|---|
| Hello script | `hello-world/hello.sh` | none (read-only) | none; content and 100755 mode preserved |
| Existing behavior tests | `tests/test_hello_sh.py` | none (read-only) | none (A3) |
| Strict folder-isolation test | new test module under `tests/` | t1 | added |
| Test gate / CI | `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/testing.md` | none (reused) | none (CI/CD is out of scope) |

External dependencies: `/bin/bash` on the runner, plus Python 3.12 and pytest per `.factory/testing.md`.

## 3. Data flow
- **Runtime:** developer → `./hello-world/hello.sh` → the kernel follows the shebang → `/bin/bash` → stdout `hello world\n`, empty stderr, exit 0. The script is synchronous and stateless, and takes no input.
- **Verification:** PR → the CI `test` job runs `pip install -e ".[test]"` then `pytest`. Collection uses `testpaths = ["tests"]`, so the new module is picked up with no config change. The result at the PR head is the authoritative evidence.

## 4. Component breakdown
- **hello.sh**
  - Input: none.
  - Output: `hello world\n` on stdout, nothing on stderr, exit code 0.
  - Repo: play1. Unchanged.
- **Existing tests (`tests/test_hello_sh.py`)** cover:
  - AC1: direct execution, exit 0, stdout.
  - AC3: shebang, executable bit, and direct execution, which only works through the shebang.
  - AC4: exact output and empty stderr.
  - AC2: only partly, because dotfiles are skipped.
  - Repo: play1. Unchanged.
- **Strict isolation test (new)**
  - Input: the directory listing of `hello-world/`, every entry including hidden files and subdirectories.
  - Output: pass only when the listing is exactly `hello.sh`.
  - Repo: play1. Owned by t1.

## 5. Interface contracts
- **CLI contract:** `./hello-world/hello.sh` from the repo root. stdout is exactly the 12 bytes `hello world\n` (A2), stderr is empty, exit code is 0.
- **Filesystem contract:**
  - `hello-world/` contains exactly one entry, `hello.sh`.
  - `hello.sh` keeps git mode 100755 and LF line endings.
- No APIs, events or cross-repo contracts.

## 6. Key technical decisions
- **Evidence over rebuild (A1):** reuse the existing script, tests and CI gate. Rewriting them would duplicate WI-220A63 and go beyond the spec's non-goals.
- **Close the AC2 gap with a new test module instead of editing `tests/test_hello_sh.py`:** this keeps A3 ("existing tests unchanged") literally true while AC2's "only file present" becomes fully asserted.
  - Alternative considered: change the existing test's dotfile filter. Rejected because it edits the existing tests.
  - Alternative considered: a docs-only PR. Rejected because it would leave AC2 only partly guarded by the gate.
- **No CI, CHANGELOG or README changes:** these are out of scope per the spec.
- **Evidence location:** the PR description maps each AC to its test(s) and to the CI run at the PR head.

## 7. Risks & constraints
- **Executable bit:** any tooling that rewrites `hello.sh` could drop mode 100755 and break AC3. The ticket must not touch the file.
- **Output and test coupling:** if the reading of AC4 ever changes, the script and its asserting test must change in the same PR (spec §7). This story makes no such change.
- **`gate` CI job:** fails if a `CI_FAIL` file exists at the repo root. The delivery must not add one.
- **Scale and performance:** not applicable. The script is trivial and synchronous. There is no security surface beyond file permissions.
