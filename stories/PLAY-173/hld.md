# High-level design: PLAY-173, a script that prints "B" after "A"

## 1. What we're building
- **What:** a new script, `qa/20261109-s1/b.sh`. It runs the `qa/20261109-s1/a.sh` that sits next to it (from PLAY-172, already merged to `main`), then prints `B`. A normal run outputs exactly `A\n` then `B\n` and exits 0.
- **Why:** this is the second, dependent story of the epic QA-20261109-S1. It shows the factory can deliver a story that depends on an earlier one, in the right order.
- **What it does:**
  - finds `a.sh` relative to `b.sh`'s own location
  - passes `a.sh`'s output straight through
  - stops before printing `B` if `a.sh` is missing or fails
  - comes with automated tests and one CHANGELOG line

## 2. Architecture
- **One repository:** `roeeoz/play1`. There are no services and no new dependencies.
- **Components:**
  - **`a.sh`** (existing, read-only here): prints `A\n`, writes nothing to stderr, exits 0, and doesn't depend on where it lives (contract in `stories/PLAY-172/hld.md` §5).
  - **`b.sh`** (new): the script that calls `a.sh`.
  - **`tests/test_qa_20261109_s1_b.py`** (new): pytest tests, run by the existing CI `test` job (`pytest`, `testpaths = ["tests"]`).
  - **`CHANGELOG.md`:** one appended line under `## Unreleased` (repo-gate rule 4, PLAY-G4). This is the only existing file allowed to change.
- **Untouched:** `qa/20261109-s1/a.sh`, `qa/s3-a.sh`, `qa/s3-hello.sh`, `hello-world/hello.sh`, all existing tests, `ci.yml` and `pyproject.toml`.

## 3. Data flow (synchronous, one process chain)
1. The user runs `qa/20261109-s1/b.sh` by its path, from any folder.
2. `b.sh` works out its own folder from how it was invoked (`$0`), not from the current folder.
3. If `<folder>/a.sh` is missing or can't be run, `b.sh` writes an error to stderr and exits 1. `B` is not printed.
4. Otherwise `b.sh` runs `<folder>/a.sh`. `a.sh`'s stdout passes straight through, with no capture and no pipe, so the output order stays intact.
5. If `a.sh` exits non-zero, `b.sh` exits with the same code. `B` is not printed.
6. Otherwise `b.sh` prints `B\n` and exits 0.

## 4. Components

| Component | What it does | Inputs / outputs | Repo |
|---|---|---|---|
| `qa/20261109-s1/b.sh` | Runs the sibling `a.sh`, then prints `B` | No arguments. stdout is `A\nB\n`, exit 0. On error: message on stderr, non-zero exit, no `B` | roeeoz/play1 |
| `tests/test_qa_20261109_s1_b.py` | Tests every acceptance scenario and the file's shape | Runs the real scripts and copies in `tmp_path` | roeeoz/play1 |
| `CHANGELOG.md` (one line) | Satisfies the PR gate | — | roeeoz/play1 |

## 5. Interface contracts
- **What `b.sh` consumes:** the `a.sh` contract from PLAY-172. It sits next to `b.sh`, is executable and starts with a shebang. stdout is exactly `A\n`, stderr is empty, exit is 0.
- **What `b.sh` exposes:**
  - **Success:** stdout is exactly `A\nB\n`, stderr is empty, exit is 0, from any current folder.
  - **`a.sh` missing or not executable:** exit 1, stderr is `b.sh: cannot run <path>/a.sh`, and `B` is not on stdout.
  - **`a.sh` exits N (N ≠ 0):** `b.sh` exits N, and `B` is not on stdout.
- **File shape:** the script starts with `#!/bin/sh\n`, is git mode 100755 and contains no `\r`.

## 6. Key technical decisions
- **Interpreter: `#!/bin/sh` (POSIX, dash in CI), not bash.** This matches every `qa/` script and the existing shape tests, and PLAY-172 made the same choice. The PRD glossary's "bash" just means the terminal language. Rejected: bash, which would be inconsistent with the rest of `qa/` and isn't needed.
- **Finding `a.sh`: from `dirname "$0"`.** This works when `b.sh` is run directly, as `sh path/b.sh`, or found through `PATH`. Rejected: looking it up from the current folder or from `PATH`, because that breaks FR3/R4.
- **Running `a.sh`: execute it directly, so its own shebang applies.** Rejected: `sh a.sh`, which would ignore `a.sh`'s declared interpreter.
- **Error for a missing `a.sh`: an explicit check with our own message.** The shell's default "not found" wording varies between shells, so `b.sh` checks first and writes its own message to stderr, exit 1. Tests only check that stderr isn't empty and the exit code isn't 0.
- **Failures stop `b.sh`:** it stops explicitly on `a.sh`'s failure and passes on the exit code (rather than relying on `set -e`). Rejected: capturing `a.sh`'s output and re-printing it, which could hide the exit code or change the output order.
- **Test isolation: per-test copies in pytest's `tmp_path`.**
  - Each test copies `b.sh` next to a stub, a missing `a.sh`, or a real copy of `a.sh`.
  - Copies keep their executable bit (`shutil.copy`), and stubs are made executable.
  - Rejected: permanent fixtures under `tests/fixtures/`, which have no `.sh` precedent and add files.

## 7. Risks and constraints
- **The real dependency could be faked (R3):** if `b.sh` printed `A` itself, the normal-run tests would still pass. Scenario 2 (a stub `a.sh` printing different text) is required to catch this.
- **Failure ignored (R5):** if `b.sh` didn't stop on `a.sh`'s failure, it would still print `B`. Scenarios 4 and 5 catch this.
- **Executable bit and line endings:** a file committed as 100644, or with CRLF line endings, breaks repo-gate rule 2. Mitigated by the shape tests and by checking `git ls-files -s`.
- **Finding `a.sh` (RK2):** if `b.sh` is sourced (`. b.sh`) or run through a symlink, it resolves `a.sh` differently. Both are outside the acceptance criteria and are documented here only.
- **R6 / G4:**
  - Tests never modify the real `a.sh`.
  - Every `subprocess` call has `timeout=10`.
  - No network, clock or environment dependencies.
  - The test suite stays well under 60 seconds.
- **RK3:** `b.sh` never refers to `qa/s3-*.sh`.
- **Size (G3):** the diff is under 100 lines.
- **Process:**
  - A human merges the PR.
  - The PR cites PLAY-173 and the epic PRD.
