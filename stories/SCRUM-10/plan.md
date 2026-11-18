# Implementation plan — SCRUM-10: hello-world bash script in its own folder

## Context

SCRUM-10 asks for a `hello-world/` folder at the root of `play1` that holds only `hello.sh`. The script must have a `#!/bin/bash` shebang and the executable bit, and must print exactly `hello world` and exit 0 (AC1–AC4 in `spec.md` §5). The deliverable already exists on `main`, the target branch. The work branch `halo/feat/scrum-10-20261118-222915` was cut from `main`. The one remaining gap is that the AC2 test ignores hidden files. This plan closes that gap in `tests/test_hello_sh.py` and changes nothing else. `spec.md`, `hld.md` and `work-items.md` are in the same folder as this file (`stories/SCRUM-10/`). The breakdown has one work item, `t1`.

## Research findings

- **Script (exists, unchanged):** `git ls-tree HEAD hello-world/` returns one entry, `100755 blob 2a43bb2… hello-world/hello.sh`. The file is 31 bytes: `#!/bin/bash` and `echo "hello world"`. In the working tree, `hello-world/` contains only `hello.sh`.
- **Existing tests:** `tests/test_hello_sh.py` holds six tests, and all pass on the work branch:
  - `TestHelloShExecution` (`tests/test_hello_sh.py:9-28`) covers stdout `== "hello world\n"`, exit code 0, empty stderr, and `strip()` exactness. These map to AC1 and AC4.
  - `TestHelloShStructure` covers the shebang (`:32-34`, AC3), `S_IXUSR` (`:36-38`, AC3), and folder isolation (`:40-43`, AC2).
  - The scripts are run directly by `subprocess.run([str(SCRIPT)])`, without `bash`, so the shebang path is exercised (AC3).
- **The gap:** `tests/test_hello_sh.py:42` filters entries with `if not f.name.startswith(".")`. A file such as `hello-world/.gitkeep` would break AC2 and the test would still pass. The comparison also relies on `iterdir()` order. That order is harmless for a single entry, but the result is not sorted.
- **Canonical gate:** `.factory/testing.md` declares `test-gate: pytest`, with one required layer, `package-api`, of type `runBy: canonical-gate`. `.github/workflows/ci.yml` runs job `test` (`pip install -e ".[test]"`, then `pytest`, on Python 3.12) and job `gate` (fails only if `CI_FAIL` exists at the repo root). No linter, formatter or type checker is configured. `pyproject.toml` sets `testpaths = ["tests"]` and `addopts = "-q"`.
- **Contracts touched:** none. No API, schema or cross-repo value is involved, and no external data is needed.
- **Unknowns:** none remain.

## Locked decisions and assumptions

**Locked decisions**
- The deliverable is verified against `main`, and only the gap found is filled (spec A1, `hld.md` §6).
- The output is `hello world` followed by a single newline. Existing tests pin it as `"hello world\n"` (spec FR6/A2).
- `t1` may change only `tests/test_hello_sh.py`. It must not touch anything under `hello-world/`, `qa/`, CI workflows, docs or `CHANGELOG.md` (`work-items.md`, t1).
- The `hello.sh` content and its `100755` mode must not change (`work-items.md`, t1; `hld.md` §7).
- The gate is `pip install -e ".[test]" && pytest` on Python 3.12, and no `CI_FAIL` file may exist (`.factory/testing.md`, `.github/workflows/ci.yml`).

**Assumptions**
- *"Every entry" means every name `Path.iterdir()` returns, including dotfiles and subdirectories.*
  - Evidence: the t1 AC says "counting hidden entries … and subfolders".
  - If wrong: the test would be stricter than intended. A developer's local `.DS_Store` would fail it, which `hld.md` §7 accepts as intended.
- *A fixture-based negative test in `tmp_path` is allowed, in addition to the manual demonstration.*
  - Evidence: t1 owns `tests/test_hello_sh.py`, and pytest's built-in `tmp_path` fixture needs no new dependency.
  - If wrong: drop that one test. The manual demonstration recorded in the PR still satisfies the t1 AC.

## Solution proposal

Tighten the existing AC2 test rather than add product code.

1. In `tests/test_hello_sh.py`, add a module-level helper that returns the sorted names of every entry in a folder, with no filtering. Use it in `test_folder_contains_only_hello_sh` and assert that the result equals `["hello.sh"]`. With no filter, hidden files and subfolders count, and sorting makes the comparison independent of `iterdir()` order.
2. Add one regression test in the same class. It builds a `tmp_path` folder holding `hello.sh` and `.gitkeep`, then asserts that the helper's result is not `["hello.sh"]`. This keeps the proof that the check catches hidden extras in CI, without ever putting a file inside the real `hello-world/`.
3. Leave the five other tests and `hello-world/hello.sh` exactly as they are.

**Alternatives rejected:**
- Rewriting or touching `hello.sh` risks losing the `100755` mode or the trailing newline.
- Using `git ls-tree` inside the test would check what git tracks rather than the folder contents AC2 describes ("lists its contents"), and it adds a dependency on git in the test.
- Adding a test file or `.gitkeep` under `hello-world/` would itself break AC2.
- An empty breakdown would leave the AC2 gap open (`hld.md` §6).

## Ordered implementation steps

1. **Add the unfiltered entry-listing helper.** In `tests/test_hello_sh.py`, add a small module-level function that lists all entry names in a given folder, sorted, with no dot-file filter.
   - AC: AC2 / t1 AC 1.
   - Test layer: `package-api` (pytest).
2. **Rewrite `test_folder_contains_only_hello_sh`.** In `tests/test_hello_sh.py:40-43`, assert that the helper applied to `SCRIPT.parent` equals `["hello.sh"]`. Remove the `startswith(".")` filter.
   - AC: AC2 / t1 AC 1.
   - Test layer: `package-api`.
3. **Add the negative regression test.** In `TestHelloShStructure`, use pytest's `tmp_path`: write `hello.sh` and `.gitkeep`, then assert that the helper's result is not `["hello.sh"]` and includes `.gitkeep`.
   - AC: t1 AC 2 (proof that the check fails on an extra entry).
   - Test layer: `package-api`.
4. **Demonstrate the failure manually.**
   - Run `touch hello-world/.gitkeep && pytest tests/test_hello_sh.py` and confirm that `test_folder_contains_only_hello_sh` fails.
   - Run `rm hello-world/.gitkeep && pytest tests/test_hello_sh.py` and confirm that all tests pass.
   - Record both results in the PR description, and confirm that `git status` shows no stray file.
   - AC: t1 AC 2.
   - Test layer: `package-api`, run locally.
5. **Confirm nothing under `hello-world/` changed.**
   - `git ls-tree HEAD hello-world/` must still show only `100755 … hello-world/hello.sh`.
   - `git diff main -- hello-world/` must be empty.
   - No `CI_FAIL` file may exist at the repo root.
   - AC: t1 AC 3–5 (AC1, AC3 and AC4 remain covered by the unchanged tests at `tests/test_hello_sh.py:9-38`).
   - Test layer: none; this is a repository-state check.
6. **Run the canonical gate.** Run `pip install -e ".[test]" && pytest` from the repo root.
   - AC: t1 AC 5.
   - Test layer: `package-api`.

**Invariants:**
- Authorization, tenancy, concurrency and validation do not apply: this is a static script with no input.
- Dependencies come from `pip install -e ".[test]"` (only `pytest>=8` is needed for tests), with no reliance on a cache.
- Nothing is generated.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–6 | `t1`: Make the hello-world folder-isolation test count hidden files (AC2) |

The only work item, `t1`, is covered by these steps.

## Verification and CI gate

- **Canonical gate:** run `pip install -e ".[test]"`, then `pytest`, from the repo root on Python 3.12. Run it once locally on the committed SHA. Provider CI (`test` job) runs it again at the PR head, and that run is the authoritative result for the `package-api` layer (`.factory/testing.md`).
- **The gate must show:**
  - The whole suite passes, including all seven tests in `tests/test_hello_sh.py` (the six existing tests, one of them rewritten, plus the new negative test).
  - The `gate` job is green, because no `CI_FAIL` file exists.
- **Additional evidence for the PR description:**
  - The fail-then-pass demonstration from step 4.
  - `git ls-tree HEAD hello-world/` showing the single `100755` entry.
- **Pod limits:** none. The only layer, `package-api`, runs unprivileged in a pod.
- **No change needed to:** provider CI configuration, `.factory/testing.md`, or `.factory/delivery-assets` (no binaries).

## Risks and scope guards

**Risks**
- *A developer's local dotfile (for example `.DS_Store`) in `hello-world/` fails the test.* This is intended (AC2), and CI checks out a clean tree.
- *The manual `.gitkeep` from step 4 gets committed by mistake.* Mitigation: step 5 checks `git status` and `git ls-tree`, and the PR diff must show no path under `hello-world/`.
- *The executable bit or trailing newline is lost.* Mitigation: `hello.sh` is not opened for editing at all.

**Scope guards (the implement phase must NOT):**
- Modify, re-create, re-format or `chmod` `hello-world/hello.sh`, or add any file under `hello-world/`.
- Change or delete the five unchanged tests in `tests/test_hello_sh.py`, or weaken the `"hello world\n"` assertions.
- Touch `qa/` (including `qa/20261110-s3/hello.sh`), `.github/workflows/ci.yml`, `README.md`, `CHANGELOG.md`, `pyproject.toml` or `.factory/`.
- Add a linter, a new test framework, a `conftest.py` or a CI step.
- Create `CI_FAIL`, or skip, xfail or delete any test to make the gate green. A failing check is reported blocked, never weakened.

## Clarification outcomes

None.
