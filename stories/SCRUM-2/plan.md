# Plan — SCRUM-2: Hello world bash script in a dedicated folder

## Context

SCRUM-2 asks for a `hello-world/` folder at the play1 repo root. The folder holds only `hello.sh`, a `#!/bin/bash` script with the executable bit that prints exactly `hello world` and exits 0 (AC1–AC4). The target branch `main` already delivers the script and six tests. This change is one new pytest module that closes the remaining gap: AC2 isolation is checked today with dotfiles skipped. The PR description then records the evidence for each AC. The change lands in `play1` on `halo/feat/scrum-2-20261118-212149`, cut from `main`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-2/`.

## Research findings

**Change surface (facts)**
- `hello-world/hello.sh` is 31 bytes with LF endings: `#!/bin/bash\necho "hello world"\n`. Its index mode is `100755` (`git ls-files -s`). It is the only entry in `hello-world/`, hidden entries included (`ls -la`).
- `tests/test_hello_sh.py:1-43` holds 6 tests and finds the script through `REPO_ROOT = Path(__file__).resolve().parent.parent` (`:5`) and `SCRIPT` (`:6`).
  - AC1, AC3: `test_prints_hello_world` (`:10`) runs `[str(SCRIPT)]` directly, without a `bash` prefix, and checks exit code 0 and stdout.
  - AC3: `test_shebang_line` (`:32`) and `test_executable_permission` (`:36`).
  - AC4: `test_no_stderr` (`:17`) and `test_exact_output_no_extra_whitespace` (`:23`).
  - AC2, partial: `test_folder_contains_only_hello_sh` (`:40-43`) filters out names that start with `.` (`:42`). A dotfile such as `.keep` or a hidden subdirectory passes this check unnoticed.
- No module named `tests/test_hello_world_folder.py` exists yet. The `tests/` directory has no `conftest.py`, and none is needed.

**Gate (facts)**
- `.factory/testing.md` declares one layer, `package-api`, with command `pytest`, `runBy: canonical-gate`, `required: true`.
- `.github/workflows/ci.yml`: the `test` job runs on Python 3.12, `pip install -e ".[test]"` then `pytest`. The `gate` job fails only if `CI_FAIL` exists at the repo root.
- `pyproject.toml`: `testpaths = ["tests"]`, `addopts = "-q"`, and `test = ["pytest>=8"]`. A new `tests/test_*.py` module is collected with no configuration change.
- No linter, formatter or type checker is configured.

**Contracts**
- CLI contract: stdout is exactly `hello world\n`, stderr is empty, exit code is 0.
- Filesystem contract: `hello-world/` contains exactly `hello.sh`, mode `100755`. There are no APIs, schemas or cross-repo values.

**Exists vs new**
- Already exists: the script, the 6 tests and the CI gate.
- New: one test module.

**Unknowns**
- None blocking.

## Locked decisions and assumptions

**Locked decisions**
- AC1–AC4 and FR1–FR5 (`spec.md` §3, §5).
- Out of scope: extra scripts, CI/CD changes and documentation files, including any README in `hello-world/` and any CHANGELOG entry (`spec.md` §2).
- A1, evidence over rebuild: the script and existing tests are not rewritten (`spec.md` §8, `hld.md` §6).
- A2: the single trailing newline is allowed (`spec.md` §8).
- A3: `tests/test_hello_sh.py` stays unchanged (`spec.md` §8, `hld.md` §6).
- The AC2 gap is closed by a new test module, not by editing the existing filter (`hld.md` §6).
- The following files must stay byte-identical and keep their git mode (`work-items.md` t1 "Consumes"): `hello-world/hello.sh`, `tests/test_hello_sh.py`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/testing.md`, `CHANGELOG.md`.
- The canonical gate is `pip install -e ".[test]"` then `pytest` on Python 3.12, and the CI `test` job at the PR head is authoritative (`.factory/testing.md`).

**Assumptions**
- AC2 "lists its contents" means the working-tree listing of `hello-world/`: every entry `os.listdir`/`Path.iterdir` returns, hidden files and subdirectories included.
  - Evidence: `spec.md` §4 says "`ls hello-world` shows only `hello.sh`", and the t1 criterion asks for the complete listing.
  - If wrong (for example, "tracked files only" was meant), the test is stricter than required. Untracked local clutter such as `.DS_Store` would fail it locally, but never in CI, which uses a clean checkout.
- To prove that the new test "fails if any extra entry is present", the isolation check runs as a module-local helper against temporary directories, not by mutating the real `hello-world/`.
  - Evidence: the t1 criterion requires the failure behaviour, and the t1 scope forbids touching `hello-world/`.
  - If wrong, the negative cases are still observable through the helper. Nothing in the repository changes.

## Solution proposal

Add one pytest module, `tests/test_hello_world_folder.py` (new). It holds a small pure helper and two kinds of test:

1. **Helper.** `_folder_entries(path)` returns the sorted names of every entry in a directory, with no filter on hidden names and no type filter. Directories count as entries.
2. **Real-repo test, AC2 strict.** Resolve `REPO_ROOT` the same way `tests/test_hello_sh.py:5` does. Assert that `REPO_ROOT / "hello-world"` exists and is a directory (FR1). Then assert that `_folder_entries(...) == ["hello.sh"]`.
3. **Helper self-tests with `tmp_path`.** Use a parametrized negative case and one positive case:
   - Positive: a directory holding only `hello.sh` gives `["hello.sh"]`.
   - Negative: `hello.sh` plus each extra entry in turn: a dotfile (`.keep`), a `README.md`, a visible subdirectory and a hidden subdirectory. Each case's listing must differ from `["hello.sh"]`. This shows the strict check would reject them, which the filter at `tests/test_hello_sh.py:42` does not do for hidden entries.

Key decisions:
- **Working-tree listing, not `git ls-files`.** It matches what a developer sees (`spec.md` §4), needs no `git` binary in the test, and also catches untracked or ignored files left in the folder.
- **Duplicate the 2-line `REPO_ROOT` idiom; don't import from `tests/test_hello_sh.py`.** `tests/` is not a package. Importing sibling test modules would make the suite depend on collection order, and editing the existing file is forbidden by A3.
- **No change to the script, the configuration or CI.** pytest's `testpaths` collects the module automatically.

Alternatives rejected:
- Editing the dotfile filter at `tests/test_hello_sh.py:42`: this breaks A3 (`hld.md` §6).
- A docs-only PR: AC2 would stay only partly guarded by the gate (`hld.md` §6).
- Creating a real dotfile in `hello-world/` during a test to watch it fail: this mutates the deliverable folder and risks leaving debris if the test aborts.

AC evidence for the PR description (no code):

| AC | Asserting test(s) |
|---|---|
| AC1 | `tests/test_hello_sh.py::TestHelloShExecution::test_prints_hello_world` |
| AC2 | `tests/test_hello_sh.py::TestHelloShStructure::test_folder_contains_only_hello_sh` and the new strict test in `tests/test_hello_world_folder.py` |
| AC3 | `test_shebang_line`, `test_executable_permission`, and `test_prints_hello_world`, which runs the script without `bash` |
| AC4 | `test_exact_output_no_extra_whitespace`, `test_no_stderr` |

The description also records one manual run of `./hello-world/hello.sh` from the repo root: stdout `hello world`, empty stderr, exit status `0`. A byte check such as `./hello-world/hello.sh | od -c` shows the 12 bytes `hello world\n`.

## Ordered implementation steps

1. **Acquire dependencies.** Run `pip install -e ".[test]"` from the repo root on Python ≥3.10 (CI uses 3.12). Don't rely on a warm cache. Then run `pytest tests/test_hello_sh.py` as a baseline: all 6 pass. Covers AC1, AC3 and AC4 through the existing `package-api` layer.
2. **Create `tests/test_hello_world_folder.py` (new).**
   - Add the `REPO_ROOT` / `FOLDER` constants and the `_folder_entries` helper. Don't filter on names starting with `.`, and don't drop directories.
   - Add the real-repo strict test: the folder exists, is a directory, and its listing is exactly `["hello.sh"]`.
   - Covers AC2 and FR1 in the `package-api` layer (pytest).
3. **Add the helper self-tests in the same module**, using the `tmp_path` fixture:
   - Positive case: `["hello.sh"]` only.
   - Parametrized negative cases: `.keep`, `README.md`, subdirectory `sub/`, hidden subdirectory `.hidden/`. Each must produce a listing that is not equal to `["hello.sh"]`.
   - Use only the standard library and pytest. No new dependency.
   - Covers the t1 criterion "fails if any extra entry is present" for AC2, in the `package-api` layer.
4. **Verify the scope invariants locally.**
   - `git diff --stat main...HEAD` lists only `tests/test_hello_world_folder.py` outside `stories/SCRUM-2/`.
   - `git ls-files -s hello-world` still shows `100755` for `hello.sh` and nothing else.
   - There is no `CI_FAIL` at the repo root.
   - Covers AC2 and AC3 preservation. No test layer applies: this is a diff inspection.
5. **Run the gate:** `pytest` from the repo root, covering the full suite. Expect the 6 existing tests in `tests/test_hello_sh.py` plus the new tests to pass, with no other test regressing. Covers AC1–AC4 through the `package-api` layer.
6. **Record the evidence.** Run `./hello-world/hello.sh; echo "exit=$?"` and `./hello-world/hello.sh | od -c` from the repo root. Put the output and the AC→test table from the Solution proposal into the PR description. Covers AC1, AC3 and AC4. No test layer applies: this is documentary evidence, and the CI `test` job at the PR head is authoritative.

Invariants:
- Authorization and tenancy, concurrency and idempotency: not applicable. The work is a stateless script and read-only tests.
- Idempotency of the tests: the self-tests write only under `tmp_path`, and the real-repo test only reads.
- Validation and error paths: the real-repo test fails with a clear message if the folder is missing, is not a directory, or holds extra entries. Use plain `assert` with the listing in the message.
- Generated deliverables: none. Binaries: none, so there is no `.factory/delivery-assets` obligation.

## Work-item mapping

| Step | Work item |
|---|---|
| 1–6 | t1 — Assert strict hello-world folder isolation (including hidden entries) and record AC evidence |

t1 is the only work item, and every step belongs to it.

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"`, then `pytest` from the repo root. Run it once locally on the committed SHA. The CI `test` job (Python 3.12) at the PR head is the authoritative run. The `gate` job must also be green, which means no `CI_FAIL` file.
- **Test layers:** one, `package-api` (pytest). It runs unprivileged in a pod. `/bin/bash` must be present for the existing execution tests, and it is on `ubuntu-latest` and in standard pods.
- **Provider CI configuration:** none needed. `.github/workflows/ci.yml` is unchanged.
- **`.factory/testing.md`:** no change. The new module falls under the existing `pytest` layer.
- **`.factory/delivery-assets`:** not applicable, because no binaries are added.
- **What the gate must show to call the change done:** `pytest` exits 0 with these tests all passing, and every other existing test still passing:
  - all 6 tests in `tests/test_hello_sh.py`;
  - the new strict real-repo isolation test;
  - every negative and positive self-test case.

## Risks and scope guards

**Risks**
- *Executable bit loss.* Any tool that rewrites `hello-world/hello.sh` could drop mode `100755` and break AC3. Mitigation: don't open or rewrite the file, and check `git ls-files -s` in step 4.
- *Local clutter.* An untracked `.DS_Store` or editor swap file inside `hello-world/` makes the strict test fail locally. This is intended (AC2). CI uses a clean checkout, so it is unaffected.
- *Coupling to output wording.* If the reading of AC4 changes later, the script and its assertions must change in one PR (`spec.md` §7). This story makes no such change.

**Scope guards: the implement phase must NOT:**
- touch anything under `hello-world/`, including adding a README, a `.gitkeep` or any other file;
- edit `tests/test_hello_sh.py`, including its dotfile filter at `:42`;
- edit `pyproject.toml`, `.github/workflows/`, `.factory/testing.md`, `CHANGELOG.md` or `README.md`;
- add a `conftest.py`, a new dependency, a linter or any CI step;
- add a `CI_FAIL` file;
- add more scripts;
- edit `spec.md`, `hld.md` or `work-items.md`.

A failing check may be reported as blocked. It must never be made green by deleting, skipping, `xfail`-ing or loosening any assertion, new or existing.

## Clarification outcomes

None.
