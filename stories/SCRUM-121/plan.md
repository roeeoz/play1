# SCRUM-121 — Implementation plan: `marker()` helper that reads `QA_S4_MARKER`

## Context

SCRUM-121 adds a function `marker()` to the `testbed_utils` package. It returns the process environment's `QA_S4_MARKER` value verbatim, or `""` when the variable is unset. The package root re-exports it. A pytest file covers both cases. In a factory run only, the same file also asserts that `QA_S4_MARKER` is set to a non-empty value. A run counts as a factory run when `HALO_PROJECT_ENV_NAMES` lists `QA_S4_MARKER`. The change lands in `roeeoz/play1` on the work branch `halo/feat/scrum-121-20261124-054329`, cut from `qa-20261122-s4-base`. The approved requirement is `spec.md` (AC 1–6, FR1–FR9). The design is `hld.md`. The breakdown is `work-items.md`, which has one work item, `t1`, with criteria t1-AC1 to t1-AC10. All three files sit beside this file in `stories/SCRUM-121/`.

## Research findings

**Change surface (facts):**
- `src/testbed_utils/__init__.py:8-12` imports one public name per module, in alphabetical order by module (`dateutils`, `hello`, `numutils`, `pdfutils`, `textutils`). `__init__.py:14-26` lists `__all__` alphabetically. The new import line goes after `numutils` and before `pdfutils`, because `s4_marker` sorts there. `"marker"` goes into `__all__` between `"is_weekend"` and `"mean"`.
- `src/testbed_utils/hello.py:1-17` is the reference pattern: a module docstring, `from __future__ import annotations`, and a small typed public function with a `>>>` docstring example. `marker()` depends on the environment, so its docstring cannot carry a deterministic doctest. Plain prose is the right form here.
- `src/testbed_utils/s4_marker.py` does not exist yet and is **new**.
- `tests/test_hello.py:1-14` is the reference test style. It groups tests in classes, imports through the installed package, and checks the root export with `testbed_utils.hello_world is hello.hello_world` and `"hello_world" in testbed_utils.__all__`.
- `tests/test_s4_marker.py` does not exist yet and is **new**.
- Nothing in the repository mentions `QA_S4_MARKER` or `HALO_PROJECT_ENV_NAMES` today, outside the story folder.
- The repository has no `tests/conftest.py`. Tests import `testbed_utils` only through the editable install (`.factory/testing.md`, "What the gate proves").

**Contracts:**
- The public API is `testbed_utils.marker` and `testbed_utils.s4_marker.marker`. Both are the same object. The function takes no arguments and returns `str` (`hld.md` §5).
- The environment variables are named exactly `QA_S4_MARKER` and `HALO_PROJECT_ENV_NAMES`. The second is a comma-separated list. Each item is stripped of whitespace, and matching is exact and case-sensitive (`hld.md` §5).
- There are no cross-repo contracts.

**Gate (facts):**
- `.factory/testing.md` declares `test-gate: pytest` and `local-test-gate: pip install -q -e ".[test]" && pytest`. Its one required layer is `package-api` (production-path, `runBy: canonical-gate`).
- `.github/workflows/ci.yml` runs `pip install -e ".[test]"` and then `pytest` on Python 3.12 in the `test` job. The `gate` job fails only when a `CI_FAIL` file exists.
- No linter, formatter or type checker is configured.
- `pyproject.toml` sets `requires-python = ">=3.10"`, `test = ["pytest>=8"]` and `addopts = "-q"`.

**Repository layout gate:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` requires Python source under `src/`, tests under `tests/`, and no file in the diff over 200 KB.

**Pre-existing red:** `tests/test_qa_20261122_s4_base.py:4-5` (`assert 1 == 2`) fails on the base branch. The overall `pytest` result and the CI `test` job therefore stay red no matter what this story does.

**External data:** the only external input is the factory runtime's environment (`HALO_PROJECT_ENV_NAMES`, `QA_S4_MARKER`). Nothing is read from another system of record.

**Unknowns left after research:** none that block the work. Q4, whitespace around names, is settled as an assumption below.

## Locked decisions and assumptions

**Locked decisions:**
1. The module is `src/testbed_utils/s4_marker.py` and the function is `marker()`. It returns the value verbatim, `""` when the variable is unset, and never raises (spec FR1–FR3; `hld.md` §1, §5).
2. `marker` is exported from `testbed_utils/__init__.py` and listed in `__all__` (spec FR9, AC 6, Q3).
3. The value is read at call time, with no module-level cache (`hld.md` §6; t1-AC3).
4. A factory run is detected by `HALO_PROJECT_ENV_NAMES`. Outside a factory run, the factory check is skipped with a reason (spec FR5, FR7, Q1).
5. An empty value counts as "not set". A whitespace-only value counts as set (spec FR6, Q2; `hld.md` §5).
6. The marker value never appears in output. The factory check fails with a fixed message and does not use a bare `assert` on the real value (spec FR8; `hld.md` §5; t1-AC9).
7. The change adds no `conftest.py`, no `sys.path` edits, no CI change and no new dependency (`hld.md` §6; `work-items.md` t1 "Must not modify").
8. The test file is `tests/test_s4_marker.py` and the unit tests use `monkeypatch` (spec FR4; `hld.md` §6).

**Assumptions:**
- **A1 (spec Q4):** whitespace around names in `HALO_PROJECT_ENV_NAMES` is ignored, and matching is case-sensitive. *Evidence:* the spec's working assumption and `hld.md` §8. *If wrong:* a factory run whose list uses an unusual format would skip the check instead of running it. The effect is low.
- **A2:** the factory check does its gating inside the test body. It calls a small private detection helper, defined in the test file, against the environment at run time. *Evidence:* `hld.md` §6 allows either this or `skipif`. Running the check inside the test body lets the same helper be unit-tested with values the test sets itself (t1-AC6). *If wrong:* nothing breaks. A `skipif` would be equally valid.
- **A3:** the factory-detection logic lives in the test file, not in `src/`. *Evidence:* the spec scopes the product surface to `marker()` alone, and the HLD names no detection API. *If wrong:* a reviewer could ask to move it into `src/`. That would widen the public surface beyond the spec.

## Solution proposal

**Helper.** Add one small module, following the one-module-per-concern pattern in `hello.py`. It has a module docstring, `from __future__ import annotations`, `import os`, and `def marker() -> str` returning `os.environ.get("QA_S4_MARKER", "")`. That covers t1-AC1 to t1-AC3:
- `os.environ.get` returns the value as stored, with no trimming.
- The `""` default covers the unset case.
- The lookup runs on each call, so a `monkeypatch` change between calls is seen.

Keep the variable name in a module constant only if it reads more clearly; it must still be looked up at call time.

**Export.** Edit `__init__.py` in two places only: one import line and one `__all__` entry, both in alphabetical position.

**Tests.** Put them in `tests/test_s4_marker.py`, grouped in classes like `test_hello.py`:
- `TestMarker` covers t1-AC1 to t1-AC3:
  - A set value comes back unchanged: `"  a=b ü  "`, plus a plain value.
  - With the variable deleted (`delenv(..., raising=False)`), the result is `""` and nothing is raised.
  - A value set to `""` returns `""`.
  - Two calls with a `setenv` between them return different results.
- `TestExport` covers t1-AC4: `testbed_utils.marker is s4_marker.marker`, `"marker" in testbed_utils.__all__`, and the previous eleven names are still present.
- `TestFactoryDetection` covers t1-AC6. It runs a private `_is_factory_run()` helper under the `HALO_PROJECT_ENV_NAMES` values that `work-items.md` t1-AC6 lists: unset, `""`, `","`, `"qa_s4_marker"`, `"QA_S4_MARKER_X"`, `"QA_S4_MARKER"` and `"A, QA_S4_MARKER"`. Parametrisation is a good fit here.
- `test_factory_run_has_marker_set` covers t1-AC7 to t1-AC9. It calls `pytest.skip("not a factory run: HALO_PROJECT_ENV_NAMES does not list QA_S4_MARKER")` when the helper returns false. Otherwise, if `marker() == ""`, it calls `pytest.fail("QA_S4_MARKER is not set in the run's environment")`. It never asserts on the value, never prints it, and uses no `monkeypatch`, so it sees the real environment. `monkeypatch` in the other tests restores the environment, so test order does not matter.

**Alternatives rejected:**
- A module-level constant read at import time breaks the `monkeypatch` tests and t1-AC3.
- `assert marker() != ""` lets pytest introspection print the value on failure, which breaks FR8.
- Putting the detection in `src/` widens the public API beyond the spec (A3).
- Adding a `conftest.py` fixture is forbidden by `hld.md` §6.
- A CI change is not needed (`hld.md` §6).

## Ordered implementation steps

1. **Create `src/testbed_utils/s4_marker.py`** with `marker()` as described in the solution proposal.
   - Advances: AC 1, AC 2; t1-AC1, t1-AC2, t1-AC3.
   - Test layer: `package-api` (pytest), through step 3.
   - Invariants: no raise when the variable is unset; no caching; no print or log; standard library only.
2. **Edit `src/testbed_utils/__init__.py`.** Add `from testbed_utils.s4_marker import marker` between the `numutils` and `pdfutils` imports. Add `"marker"` to `__all__` between `"is_weekend"` and `"mean"`. Change nothing else.
   - Advances: AC 6; t1-AC4.
   - Test layer: `package-api`, through step 3.
3. **Create `tests/test_s4_marker.py`** with these classes and tests:
   - `TestMarker`: the verbatim value, unset → `""`, empty → `""`, read at call time. Advances AC 1, AC 2, AC 3 and t1-AC1 to t1-AC3, t1-AC5.
   - `TestExport`: identity across both import paths, `__all__` membership, and the prior exports retained. Advances AC 6 and t1-AC4.
   - A private `_is_factory_run()` helper with `TestFactoryDetection`, parametrised over the t1-AC6 value table. Advances AC 4 and t1-AC6.
   - `test_factory_run_has_marker_set`: skip with a reason outside a factory run; `pytest.fail` with a fixed message when the real value is `""`; pass when it is non-empty. Advances AC 3, AC 4, AC 5 and t1-AC7 to t1-AC9.

   Use `monkeypatch.setenv` and `monkeypatch.delenv(raising=False)` for every test that sets values, never `os.environ` directly. Import only through the installed package.
   - Test layer: `package-api` (pytest). This step is the test layer itself.
4. **Gate check (no code).** Confirm the canonical gate's result, described under "Verification and CI gate". Advances t1-AC10.

Dependency acquisition: `pip install -e ".[test]"` from `pyproject.toml`, which is already part of `local-test-gate` and the CI job. Nothing is cached or vendored. There are no generated deliverables and no binaries, so `.factory/delivery-assets` does not apply.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add testbed_utils.marker() reading QA_S4_MARKER, its root export, and tests/test_s4_marker.py with the factory-run check |
| 2 | t1 | (same) |
| 3 | t1 | (same) |
| 4 | t1 | (same) |

The single work item `t1` covers every step. No work item is left without a step.

## Verification and CI gate

**Canonical gate.** The `test` job in `.github/workflows/ci.yml` runs on Python 3.12 at the exact head:
1. `pip install -e ".[test]"`
2. `pytest`

The provider run is authoritative (`.factory/testing.md`, `runBy: canonical-gate`). The `gate` job must stay green, so no `CI_FAIL` file may be added.

**Local run.** There is one local run: the gate's own `run-tests-gate.sh --run` on the committed SHA, which executes `local-test-gate: pip install -q -e ".[test]" && pytest`. Do not also run the command by hand, and do not do a separate pre-commit run of the new tests.

**Required layer.** `package-api` (pytest, production-path) is the only required layer, and it runs in a pod. No layer needs another environment.

**What the gate must show:**
- Every test in `tests/test_s4_marker.py` passes.
- In a factory pod, where `HALO_PROJECT_ENV_NAMES` lists `QA_S4_MARKER` and the variable is non-empty, `test_factory_run_has_marker_set` **passes**.
- In GitHub Actions, where `HALO_PROJECT_ENV_NAMES` is unset, that test is reported **skipped** with the not-a-factory-run reason.
- The only failing test in the suite is the pre-existing `tests/test_qa_20261122_s4_base.py::test_pre_existing_failure_on_the_qa_base`. The overall run is therefore red, for that reason alone. Report it as pre-existing; do not count it as caused by this change.
- No test output contains the `QA_S4_MARKER` value.
- The layout gate holds: source under `src/`, tests under `tests/`, every file under 200 KB.

**Other obligations.** No change to the provider CI configuration is needed. `.factory/testing.md` needs no update because no new layer is added. `.factory/delivery-assets` does not apply.

## Risks and scope guards

**Risks and mitigations:**
- **The value leaks into output.** Mitigation: fail with the fixed-message `pytest.fail`, never compare the real value in an `assert`, and never print. Skip reasons mention variable names only, never values.
- **The environment leaks between tests.** Mitigation: every test that sets values uses `monkeypatch`, which restores the environment. The factory check does not use `monkeypatch`.
- **The suite is red overall because of the pre-existing failure.** Mitigation: judge the change by the per-test result described above.
- **The factory stops listing `QA_S4_MARKER` in `HALO_PROJECT_ENV_NAMES`.** The factory check would then skip silently. This is accepted, per spec FR5.

**Scope guards. The implement phase must NOT:**
- touch other `src/testbed_utils/` modules, `src/guestbook/`, `qa/`, `pyproject.toml`, `.github/workflows/ci.yml`, `.factory/` or `README.md`;
- change anything in `__init__.py` beyond the one import line and the one `__all__` entry;
- modify, skip, xfail or delete `tests/test_qa_20261122_s4_base.py`, or any other existing test, to make the suite green;
- add a `conftest.py`, edit `sys.path`, or add a dependency;
- set, print or log `QA_S4_MARKER` or `HALO_PROJECT_ENV_NAMES` in product code or tests, except setting values through `monkeypatch` in the unit tests;
- trim or normalise the value in `marker()`;
- add a `qa/` script or a CI step that sets `QA_S4_MARKER`.

A required check may be reported blocked, but it is never made green by weakening it.

## Clarification outcomes

None. Spec Q1–Q3 were settled at intake. Q4 is carried as assumption A1.
