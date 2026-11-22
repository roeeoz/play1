## Context

SCRUM-110 (factory QA story `QA-20261122-S3`) adds a pure `farewell` greeting to two independent repositories. Each returns `"goodbye, <name>"`, with the name stripped and an empty or blank name replaced by `world`. In `roeeoz/play2`, `farewell` goes beside `greet` in `greetlib` and gets a new pytest file (AC1). In `roeeoz/play1`, a new standalone module `testbed_utils.s3_greeting` defines `FAREWELL_FORMAT` and `farewell` without importing greetlib, and gets a new pytest file (AC2). No other file changes in either repository (AC3). Both changes land on the work branch `halo/feat/scrum-110-20261122-210129`, cut from `main` in each repository. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/SCRUM-110/` of the play1 checkout.

## Research findings

**play2 (`/workspace/play2-ec10e24acf`)**
- `src/greetlib/greet.py:5-8` defines `greet(name: str = "world") -> str` as `name = name.strip() or "world"` followed by `return f"hello, {name}"`. `main` follows at `:11-14` and the `__main__` guard at `:17-18`. The module docstring is at `:1` and `import sys` at `:2`.
- `src/greetlib/__init__.py:2-4` imports and exports only `greet`. It stays unchanged, so `farewell` is reached through `greetlib.greet`.
- `tests/test_greet.py` is the only test file. It uses plain functions (`def test_...`) and imports `from greetlib import greet` and `from greetlib.greet import main`.
- `pyproject.toml` has no runtime dependencies, a `greet = "greetlib.greet:main"` script, `test = ["pytest>=8"]`, `testpaths = ["tests"]` and `addopts = "-q"`. It uses the setuptools `src/` layout.
- Gate (`.factory/testing.md`, `.github/workflows/ci.yml`): `local-test-gate: pip install -q -e ".[test]" && pytest`. CI job `test` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. Job `gate` fails only if `CI_FAIL` exists at the root. The one declared layer is `package-api` (production-path, `runBy: canonical-gate`). There is no linter, formatter, type checker or `conftest.py`.
- play2 has no repository-gate plugin and no `CLAUDE.md` or `AGENTS.md`.

**play1 (`/workspace/play1-79db628f23`)**
- `src/testbed_utils/` holds `__init__.py`, `dateutils.py`, `hello.py`, `numsummary.py`, `numutils.py`, `pdfutils.py` and `textutils.py`. `s3_greeting.py` does not exist yet and must be created.
- `src/testbed_utils/__init__.py:8-12` eagerly imports five submodules, including `pdfutils`, which imports `pypdf`. Importing `testbed_utils.s3_greeting` therefore runs that file. `pypdf` (and `flask>=3`) are declared runtime dependencies in `pyproject.toml`, so the gate installs them.
- Module style, from `src/testbed_utils/hello.py`: a module docstring, `from __future__ import annotations`, type-hinted functions and docstrings. Tests use pytest classes (`class TestHelloWorld:`) and import from the submodule path (`tests/test_hello.py:1-4`).
- `tests/test_qa_s3_greeting.py` already exists and tests `qa/s3-hello.sh`. The new `tests/test_s3_greeting.py` is a different file, and neither the existing file nor `qa/` is touched.
- No test enumerates package modules or requires every module to be in `__all__`. The only `__all__` checks are `tests/test_hello.py:13-15` and `tests/test_numutils.py:64`, and both cover specific names. A non-exported module therefore breaks no existing test.
- Layout gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): rule 1 puts source under `src/` and tests under `tests/`. Rule 2 covers new shell scripts, and this change adds none. Rule 3 caps files at 200 KB.
- The gate is the same as play2's: `.factory/testing.md` sets `local-test-gate: pip install -q -e ".[test]" && pytest`, CI job `test` runs on Python 3.12, and the `CI_FAIL` job is the same. `pyproject.toml` sets `testpaths = ["tests"]`.
- play1 has no `.factory/memory/`, `CLAUDE.md` or `AGENTS.md`.

**Contracts:** `"goodbye, " + stripped name`, with `"world"` as the fallback. play1 adds `FAREWELL_FORMAT == "goodbye, {name}"`. The behavior table is in hld.md §5. There is no contract between the repositories and no external data.

**Unknowns remaining:** none that block the work.

## Locked decisions and assumptions

**Locked decisions**
- play2's signature is `farewell(name: str = "world") -> str` in `src/greetlib/greet.py`. It strips the name and falls back to `"world"` (spec FR1; hld.md §4).
- `src/greetlib/__init__.py` is unchanged and there is no re-export (spec Q3).
- play2's test is the new file `tests/test_farewell.py`, and `tests/test_greet.py` is untouched (hld.md §2 and §6; spec AC3).
- play1's module is `src/testbed_utils/s3_greeting.py` and its test is `tests/test_s3_greeting.py`. play1 only adds files: no `__init__.py`, `pyproject.toml`, CI or `qa/` edit (spec FR3-FR5 and Q1).
- play1's `farewell` builds its result through `FAREWELL_FORMAT.format(name=...)` and defaults `name` to `"world"` (hld.md §6).
- play1 never imports greetlib, and the repositories share no package (spec Non-Goals).
- Non-`str` input gets no validation. It fails like `greet` does and is not tested (hld.md §5).
- Each repository's canonical gate is `pip install -e ".[test]"` followed by `pytest` (each repository's `.factory/testing.md`).

**Assumptions**
- play1's test uses a class-based layout like `tests/test_hello.py`, and play2's test uses plain functions like `tests/test_greet.py`. Evidence: existing conventions in each repository. If this is wrong, it is cosmetic and the behavior is unaffected.
- `str.format` with a keyword argument does not re-expand braces in the substituted value, so `"{x}"` comes back as `"goodbye, {x}"`. Evidence: Python's format semantics, as verified in hld.md §5. If this is wrong, the brace test fails at the gate and the implementation must change to concatenation.

## Solution proposal

Add one small pure function per repository, each in the style of the module it sits in. There is no shared code and no new dependency.

- **play2:** insert `farewell` directly after `greet` in `src/greetlib/greet.py`, mirroring its two lines with `goodbye` in place of `hello`. Give it a one-line docstring like `greet`'s. `main`, the console script and `__init__.py` stay as they are, which keeps the diff to one added function. Add `tests/test_farewell.py`, which imports `from greetlib.greet import farewell` and asserts every case in the work item t1 criteria.
- **play1:** create `src/testbed_utils/s3_greeting.py` with a module docstring, a module-level `FAREWELL_FORMAT = "goodbye, {name}"`, and `farewell(name: str = "world") -> str`. The function strips the name, falls back to `"world"`, and returns `FAREWELL_FORMAT.format(name=name)`. The module imports nothing outside the standard library and needs no imports at all. Add `tests/test_s3_greeting.py`, which imports `from testbed_utils.s3_greeting import FAREWELL_FORMAT, farewell` and asserts every case in the work item t2 criteria. That includes the constant's value, the brace-literal case, and a check that greetlib is not imported. To keep that check deterministic, the test reads the module source with `inspect.getsource` and asserts that `greetlib` does not appear in it. A `sys.modules` check is weaker, because it depends on what else the environment imported.

**Alternatives rejected**
- Extending `tests/test_greet.py`: spec AC3 forbids changes to existing tests.
- Re-exporting from either `__init__.py`: forbidden by spec Q3 and FR5.
- Hard-coding the string in play1 instead of using `FAREWELL_FORMAT`: rejected by hld.md §6, because the constant must be the real source of the text.
- play1 importing greetlib, or a shared package: forbidden by the spec.

## Ordered implementation steps

The two work items are independent and can run in either order.

1. **play2: add `farewell`.** In `src/greetlib/greet.py`, add `farewell(name: str = "world") -> str` right after `greet` (`:8`). It strips the name, falls back to `"world"`, and returns `"goodbye, <name>"` with a docstring. Leave `greet`, `main` and the imports untouched. Advances AC1. Covered by the `package-api` layer (pytest).
2. **play2: add `tests/test_farewell.py`** (new). Import `from greetlib.greet import farewell` and assert:
   - `farewell() == "goodbye, world"`
   - `farewell("Ada") == "goodbye, Ada"`
   - `farewell("  ") == "goodbye, world"` and `farewell("") == "goodbye, world"`
   - `farewell("  Ada  ") == "goodbye, Ada"`
   - optionally `farewell("\tAda\n") == "goodbye, Ada"`

   Each exact-equality assert also proves there is no trailing newline or punctuation. Do not test non-`str` input. Advances AC1 and AC3. Covered by `package-api`.
3. **play1: create `src/testbed_utils/s3_greeting.py`** (new). Give it a module docstring, `FAREWELL_FORMAT = "goodbye, {name}"`, and `farewell(name: str = "world") -> str`, which strips, falls back to `"world"`, and returns `FAREWELL_FORMAT.format(name=name)`. Do not import greetlib or any third-party package. Do not edit `src/testbed_utils/__init__.py`. Advances AC2 and AC3. Covered by `package-api`.
4. **play1: create `tests/test_s3_greeting.py`** (new). Import `from testbed_utils.s3_greeting import FAREWELL_FORMAT, farewell` and assert:
   - `FAREWELL_FORMAT == "goodbye, {name}"`
   - `farewell("Ada") == "goodbye, Ada"`
   - `farewell("  ") == "goodbye, world"` and `farewell("") == "goodbye, world"`
   - `farewell("  Ada  ") == "goodbye, Ada"`
   - `farewell() == "goodbye, world"`
   - `farewell("{x}") == "goodbye, {x}"`
   - the source of `testbed_utils.s3_greeting` (via `inspect.getsource`) does not contain `greetlib`

   Leave `tests/test_qa_s3_greeting.py` and `qa/` untouched. Advances AC2 and AC3. Covered by `package-api`.

**Invariants**
- Authorization, tenancy, concurrency and idempotency do not apply: both functions are pure, stateless and do no I/O.
- Validation and error paths: the blank-name fallback is the only branch, and both steps test it. Non-`str` input is out of contract.

**Dependencies:** none are added. The gate's `pip install -e ".[test]"` installs everything from each repository's `pyproject.toml` without relying on a warm cache.

**Generated deliverables:** none. No binary is added, so there is no `.factory/delivery-assets` entry.

## Work-item mapping

| Step | Work item | Repo |
|---|---|---|
| 1, 2 | t1 — play2: add farewell to greetlib with pytest coverage | roeeoz/play2 |
| 3, 4 | t2 — play1: add standalone s3_greeting farewell module with pytest coverage | roeeoz/play1 |

Every work item has at least one step.

## Verification and CI gate

**Canonical gate per repository**, as the `test` job in `.github/workflows/ci.yml` runs it on Python 3.12 at the exact head:
1. `pip install -e ".[test]"`
2. `pytest` (`testpaths = ["tests"]`, `-q`)

The `gate` job passes as long as no `CI_FAIL` file exists at the root.

**Local run:** the implement turn runs the gate itself once per repository: `run-tests-gate.sh --run` on the committed SHA, which runs `local-test-gate: pip install -q -e ".[test]" && pytest` from `.factory/testing.md`. Do not run the canonical command by hand as well, and do not do a narrower pre-commit run of the new tests.

**Required layer:** `package-api` (production-path, `runBy: canonical-gate`) in each repository. It runs unprivileged in a pod, and the provider run at the exact head is the authoritative result. No CI configuration change is needed. `.factory/testing.md` stays unchanged, because the new tests fall under the existing layer.

**Done means:**
- In play2, `pytest` passes, including every test in `tests/test_farewell.py`, and every existing test in `tests/test_greet.py` still passes.
- In play1, `pytest` passes, including every test in `tests/test_s3_greeting.py`, and the full existing suite still passes. That includes `tests/test_qa_s3_greeting.py`, `tests/test_hello.py` and `tests/test_numutils.py`.
- Both `gate` jobs are green.
- The play1 layout gate passes (PLAY-G1/G2/G3).
- The diffs are exactly:
  - play2: `src/greetlib/greet.py` (modified) and `tests/test_farewell.py` (new).
  - play1: `src/testbed_utils/s3_greeting.py` and `tests/test_s3_greeting.py` (both new).

## Risks and scope guards

**Risks**
- Importing `testbed_utils.s3_greeting` triggers the eager imports in `src/testbed_utils/__init__.py:8-12`, which pull in `pypdf`. Mitigation: `pypdf` is a declared dependency that the gate installs, so this risk already exists today and the change adds nothing new.
- Test-file confusion in play1: `test_s3_greeting.py` and `test_qa_s3_greeting.py` have similar names. Mitigation: create the new file. Never rename or edit the existing one.
- The diff could drift outside the spec's allowed files, which would violate AC3. Mitigation: before committing, check that the changed paths are exactly the four files listed under Verification and CI gate.

**Scope guards: the implement phase must NOT**
- edit `src/greetlib/__init__.py`, `greet`, `main`, `tests/test_greet.py` or either `pyproject.toml`;
- edit `src/testbed_utils/__init__.py`, `tests/test_qa_s3_greeting.py`, anything under `qa/`, or any existing play1 file;
- add a `farewell` CLI or console script, or a `conftest.py`;
- add validation for non-`str` input;
- make play1 import or depend on greetlib, or create a shared package;
- touch `.github/workflows/ci.yml` or `.factory/`, or add a `CI_FAIL` file;
- make a failing check green by skipping, deleting, `xfail`-ing or weakening a test. A failing check may be reported blocked, never weakened;
- do adjacent cleanups, such as reformatting `greet.py` or tidying play1 imports.

## Clarification outcomes

None. The spec's intake questions (Q1-Q3) were already answered by the developer on 2026-11-22, and this stage raised no new question.
