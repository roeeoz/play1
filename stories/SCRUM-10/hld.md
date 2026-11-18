# High-Level Design: SCRUM-10, hello-world bash script in its own folder

## 1. System overview
- **What is being built:** a `hello-world/` folder at the root of `play1` that holds exactly one executable bash script, `hello.sh`. Run directly, the script prints `hello world` and exits with code 0.
- **Current state:** this is already done on `main`, the base branch.
  - Commit `65938b5` added `hello-world/hello.sh` with mode `100755` (executable). It is 2 lines: `#!/bin/bash` and `echo "hello world"`.
  - `tests/test_hello_sh.py` (6 tests, all passing) checks the output `"hello world\n"`, the exit code 0, that nothing is written to stderr, the shebang line, the executable bit, and that the folder holds only `hello.sh`.
- **What's left:** the folder-isolation test ignores hidden files (`if not f.name.startswith(".")`). So AC2, "the only file present is `hello.sh`", is not fully enforced: a hidden file added to `hello-world/` would break AC2 and CI would still pass. Per assumption A1, this is the only gap to fill.

## 2. Architecture overview
- **Script:** `hello-world/hello.sh`, a standalone bash script with no dependencies beyond `/bin/bash`. It already exists and is not changed.
- **Test layer:** `tests/test_hello_sh.py`, run by the repo's required check (`pip install -e ".[test]" && pytest` on Python 3.12, in `.github/workflows/ci.yml`). It is the only file that changes.
- **No external dependencies, services or integrations.** CI, `qa/` and documentation are out of scope and untouched.

## 3. Data flow
- A developer, or the pytest subprocess, runs `./hello-world/hello.sh`. The kernel follows the shebang to `/bin/bash`, which writes `hello world\n` to stdout and exits 0. Everything is synchronous, with no state and no events.

## 4. Components
| Component | Responsibility | Inputs / outputs | Repo |
|---|---|---|---|
| `hello-world/hello.sh` | Prints the exact greeting | No input → stdout `hello world\n`, exit 0, empty stderr | play1 (exists, unchanged) |
| `tests/test_hello_sh.py` | Checks AC1–AC4 on every PR | Reads the script and folder → pytest pass/fail | play1 (t1 tightens the AC2 check) |

## 5. Interface contracts
- **What the script guarantees:** run directly as `./hello-world/hello.sh`, without calling `bash`, it writes exactly `hello world` followed by one newline (A2/FR6) to stdout, nothing to stderr, and exits 0.
- **What the folder guarantees:** `hello-world/` contains exactly one entry, `hello.sh`, counting hidden entries too.
- No APIs, events or cross-repo contracts are involved.

## 6. Key technical decisions
- **Check, don't rebuild (A1).** The script already meets FR1–FR6, so rewriting it would only risk losing its executable mode (`100755`) or its trailing newline, which CI depends on.
- **Close the gap in the tests, not in the product.** The only shortfall is a test that is too lenient for AC2, so the fix goes there. No test file goes inside `hello-world/`, because that would itself break AC2.
- **Considered and rejected:**
  - An empty breakdown: it would leave the AC2 gap open.
  - Adding a README or a CI step: out of scope by the spec.

## 7. Risks and constraints
- **Losing the executable bit:** any tool that rewrites `hello.sh` can drop it. t1 does not touch `hello.sh`. `core.fileMode=true` keeps git tracking the mode.
- **Trailing newline:** the existing tests require exactly `"hello world\n"`. Changing to `printf` without a newline would fail CI. Out of scope.
- **Hidden files on developer machines:** the stricter test fails if a local hidden file appears in `hello-world/`. That is intended (AC2), and CI checks out a clean tree.
- No scale, performance or security concerns. It is a static script with no input.
