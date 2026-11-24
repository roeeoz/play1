# Implementation plan — SCRUM-127: QA-20261124-N1 a helper that doubles a number

## Context

SCRUM-127 adds a pure helper `double(n)` that returns `n * 2` for integers. It lives in a new module `src/testbed_utils/doubler.py`, is re-exported from the package root `testbed_utils` and listed in `__all__`, and is covered by a new `tests/test_doubler.py`. There are three acceptance criteria: AC1, `double(n)` returns `n * 2` for integers. AC2, a pytest test under `tests/` covers positive, zero and negative inputs. AC3, `double` is exported from the package root and listed in `__all__`. The change lands in `roeeoz/play1` on the work branch `halo/feat/scrum-127-20261124-084351`, which was cut from `qa-20261122-s4-base`. `spec.md`, `hld.md` and `work-items.md` sit in this folder (`stories/SCRUM-127/`), beside this file.

## Research findings

- **Package layout.** `pyproject.toml` declares a setuptools `src/` layout (`[tool.setuptools.packages.find] where = ["src"]`) with `testpaths = ["tests"]` and `addopts = "-q"`. Its runtime dependencies are `pypdf` and `flask>=3`, and its test extra is `pytest>=8`. The change needs no new dependency.
- **Package root.** In `src/testbed_utils/__init__.py:8-12`, each line imports names from one sibling module, sorted by module name. `__all__` at `src/testbed_utils/__init__.py:14-26` is alphabetical. `"double"` belongs between `"days_between"` (line 15) and `"extract_fields"` (line 16). By module order, the new `from testbed_utils.doubler import double` belongs between the `dateutils` import (line 8) and the `hello` import (line 9).
- **Module style pattern.** `src/testbed_utils/numutils.py:1-23` sets the pattern: a module docstring, `from __future__ import annotations`, type-hinted functions, and a docstring with a `>>>` example.
- **Test style pattern.** `tests/test_numutils.py` has three kinds of tests:
  - class-grouped behaviour tests (lines 11-20);
  - a root-export test that checks object identity and membership in `testbed_utils.__all__` (around lines 55-64);
  - `TestDocstringExamples` (lines 77-100), which uses `public_functions()` (lines 67-74) to check that each public function has a `>>>` example and runs `doctest.testmod(numutils)` with `attempted > 0` and `failed == 0`.
- **Existing files.** `src/testbed_utils/doubler.py` and `tests/test_doubler.py` do not exist yet; both are new. No existing code defines `double`.
- **Test gate.**
  - `.factory/testing.md` declares `local-test-gate: pip install -q -e ".[test]" && pytest` and one required layer, `package-api` (production-path, `pytest`, `runBy: canonical-gate`).
  - In `.github/workflows/ci.yml`, the `test` job runs `pip install -e ".[test]"` and then `pytest` on Python 3.12. The `gate` job fails only if a `CI_FAIL` file exists at the repo root.
  - No linter, formatter or type checker is configured.
  - There is no `conftest.py` and no `sys.path` manipulation, so tests can import the package only through the editable install.
- **Pre-existing red test.** `tests/test_qa_20261122_s4_base.py:4-5` asserts `1 == 2` on the base branch. The full `pytest` run is therefore red before this story starts.
- **Repo gate.** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` requires Python source under `src/`, tests under `tests/`, executable shebang-led shell scripts, and no file over 200 KB. The planned files comply, and no shell script is added.
- **Product memory.** No `.factory/memory/` directory exists. The `qa/` script standing rule does not apply, because this story adds no script or entry point (spec §2 Non-Goals).
- **External data.** None.
- **Unknowns remaining.** None.

## Locked decisions and assumptions

**Locked decisions**

- The public name is `double`, with one parameter named `n`. It is importable from `testbed_utils.doubler` and from `testbed_utils` (spec §1, §7; FR1, FR4).
- Integers are the only inputs in contract. The helper does no type check and rejects nothing, and no non-integer input is tested (spec §2 Non-Goals, §8; hld §6).
- The helper goes in a separate module, `doubler.py`, and `numutils.py` stays untouched (hld §6; spec §2 Non-Goals).
- The only edit to `__init__.py` is one import line plus one `__all__` entry, kept alphabetical (work-items t1 "Owns").
- `tests/test_qa_20261122_s4_base.py` must not be modified or deleted (hld §7; work-items t1 "Must not modify").
- Tests import only through the installed package: no `conftest.py` and no `sys.path` changes (`.factory/testing.md`).

**Assumptions**

- The type hint is `def double(n: int) -> int`.
  - Evidence: the integer-only contract and the type-hinted siblings.
  - If wrong: the effect is cosmetic, because hints are not enforced at runtime.
- The docstring carries a `>>> double(3)` / `6` doctest, and `tests/test_doubler.py` runs `doctest.testmod(doubler)`. This mirrors `tests/test_numutils.py:95-98` and covers work-item AC6.
  - If wrong: only one style check is lost.

## Solution proposal

Add a one-function module that follows the existing single-purpose helper pattern, re-export it from the package root, and prove it with a pytest file shaped like `tests/test_numutils.py`.

- **`src/testbed_utils/doubler.py` (new).**
  - It starts with a module docstring and `from __future__ import annotations`.
  - It defines `double(n: int) -> int`, whose body returns `n * 2`.
  - The function's docstring includes a `>>>` example.
  - The module does no validation, no printing and no I/O.
- **`src/testbed_utils/__init__.py` (edit).**
  - Add `from testbed_utils.doubler import double` after the `dateutils` import.
  - Add `"double"` to `__all__` after `"days_between"`.
- **`tests/test_doubler.py` (new).** It has three test groups:
  - behaviour: `double(3) == 6`, `double(0) == 0`, `double(-4) == -8`, plus one large integer such as `2**100` to document exact doubling;
  - signature: `inspect.signature(double).parameters` holds exactly one parameter, `n`;
  - root export: `testbed_utils.double is testbed_utils.doubler.double`, `"double"` is in `testbed_utils.__all__`, and the pre-existing names are still present.

  A doctest check also runs `doctest.testmod(doubler)`.

**Alternatives rejected**

- Adding `double` to `numutils.py`: the spec names `doubler.py` and keeps `numutils` unchanged.
- An `isinstance` guard: it would invent rejection behaviour that the developer explicitly declined.

## Ordered implementation steps

1. **Create the module.** Create `src/testbed_utils/doubler.py` with the module docstring, `from __future__ import annotations`, and `double(n: int) -> int`, which returns `n * 2`. Give the function a docstring with a passing `>>>` example. Do not add validation, printing or I/O.
   - Advances: AC1 (work-item AC1, AC2, AC5, AC6).
   - Test layer: `package-api` (pytest), through step 3.
2. **Export from the package root.** Edit `src/testbed_utils/__init__.py`:
   - insert `from testbed_utils.doubler import double` between line 8 (`dateutils`) and line 9 (`hello`);
   - insert `"double",` in `__all__` between `"days_between"` and `"extract_fields"`;
   - change nothing else.
   - Advances: AC3 (work-item AC3).
   - Test layer: `package-api` (pytest).
3. **Add the tests.** Create `tests/test_doubler.py`. It imports `testbed_utils`, `from testbed_utils import doubler` and `from testbed_utils.doubler import double`, with no `conftest.py` and no `sys.path` changes. Include:
   - (a) behaviour tests for a positive, zero and negative integer (`3 → 6`, `0 → 0`, `-4 → -8`), plus one large integer;
   - (b) a signature test asserting that the only parameter is `n`;
   - (c) a root-export test asserting object identity with `testbed_utils.double`, `"double"` in `__all__`, and that the original eleven names are still in `__all__`;
   - (d) a doctest test, `doctest.testmod(doubler)`, with `attempted > 0` and `failed == 0`.

   Do not test any non-integer input.
   - Advances: AC1, AC2 and AC3 (work-item AC1–AC4, AC6).
   - Test layer: `package-api` (pytest).

Invariants:

- **Authorization, tenancy, concurrency and idempotency:** not applicable. The helper is a pure, stateless function.
- **Validation and error paths:** deliberately none, per the spec.
- **Dependencies:** acquired only by the gate's `pip install -q -e ".[test]"`; no new ones.
- **Generated deliverables:** none.

## Work-item mapping

| Step | Work item |
|---|---|
| 1 | t1 — Add double(n) helper in testbed_utils.doubler, export it from the package root, with pytest tests |
| 2 | t1 — Add double(n) helper in testbed_utils.doubler, export it from the package root, with pytest tests |
| 3 | t1 — Add double(n) helper in testbed_utils.doubler, export it from the package root, with pytest tests |

## Verification and CI gate

- **Canonical gate.** This is the `test` job in `.github/workflows/ci.yml`: `pip install -e ".[test]"`, then `pytest` from the repo root on Python 3.12, at the exact PR head. The `gate` job must stay green, so no `CI_FAIL` file is added.
- **Local run.** The one local run is the gate's own: `run-tests-gate.sh --run` on the committed SHA, which runs the `local-test-gate:` from `.factory/testing.md`, `pip install -q -e ".[test]" && pytest`.
- **Required layer.** `package-api` (production-path, `pytest`). It runs unprivileged in a pod, but the provider run is authoritative (`runBy: canonical-gate`).
- **What done means.** The run must show:
  - every test in `tests/test_doubler.py` passes;
  - every previously passing test still passes;
  - the single failure is the pre-existing `tests/test_qa_20261122_s4_base.py::test_pre_existing_failure_on_the_qa_base`.

  The CI `test` job will therefore report red for that unrelated reason. Report that, and do not hide it.
- **Configuration obligations.** None of the following is needed:
  - CI configuration changes;
  - `.factory/testing.md` updates, because the layer set is unchanged;
  - `.factory/delivery-assets` entries, because no binary is added.

## Risks and scope guards

**Risks**

- The CI `test` status is red because of the pre-existing base-branch failure.
  - Mitigation: state in the PR description that it is the only failure and that this change does not touch it. The reviewer reads the failure detail, not just the status.

**Scope guards.** The implement phase must NOT:

- edit or delete `tests/test_qa_20261122_s4_base.py`, or skip, xfail or deselect it in any way, including through `pyproject.toml` `addopts`;
- touch `numutils.py`, any other module under `src/`, `src/guestbook/`, `pyproject.toml`, `.github/`, `qa/` or `README.md`;
- change anything in `__init__.py` beyond the one import line and the one `__all__` entry;
- add input validation, a CLI entry point, a `qa/` script, a `conftest.py` or a `sys.path` change;
- add tests for float, str, `None` or `bool` inputs;
- add a dependency.

## Clarification outcomes

None.
