# High-Level Design — SCRUM-127: QA-20261124-N1 a helper that doubles a number

## 1. System Overview

- **What:** a pure helper `double(n)` returning `n * 2`, in a new module `src/testbed_utils/doubler.py`, re-exported from the package root `testbed_utils`, with a pytest file `tests/test_doubler.py`.
- **Problem:** the `testbed_utils` package (`src/testbed_utils/__init__.py`) has numeric helpers (`numutils.mean/median/percentile`) but no doubling helper.
- **Responsibilities:** return the doubled value; be importable from `testbed_utils.doubler` and `testbed_utils`; be covered by the repo's `pytest` gate.
- Spec and code agree: every path the spec names exists as described (package root, `src/` layout, `tests/` suite, `.factory/testing.md`, `.github/workflows/ci.yml`).

## 2. Architecture Overview

- One repository, `roeeoz/play1`; one Python package, `testbed_utils` (setuptools `src/` layout, `pyproject.toml` `[tool.setuptools.packages.find] where = ["src"]`).
- New module `src/testbed_utils/doubler.py` sits beside the existing single-purpose helper modules (`numutils.py`, `textutils.py`, `dateutils.py`, `hello.py`) and follows their pattern: module docstring, `from __future__ import annotations`, type-hinted function with a docstring carrying a `>>>` doctest example (see `src/testbed_utils/numutils.py:1-23`).
- Package root `src/testbed_utils/__init__.py` gains one import line and one `__all__` entry (alphabetical, as the existing list is).
- No external dependencies, no runtime state, no CLI/entry point (`pyproject.toml` `[project.scripts]` is untouched), so the `qa/` script standing rule does not apply.

## 3. Data Flow Design

- Synchronous, in-process: caller → `testbed_utils.double(n)` (re-export of `testbed_utils.doubler.double`) → returns `n * 2`. Nothing is printed, logged, stored or raised by the helper itself.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `src/testbed_utils/doubler.py` (new) | Defines `double(n)` | int `n` → int `n * 2` | `roeeoz/play1` |
| `src/testbed_utils/__init__.py` (edit) | Re-export `double`, list it in `__all__` | — | `roeeoz/play1` |
| `tests/test_doubler.py` (new) | Prove FR2 / FR4 through the installed package | — | `roeeoz/play1` |

## 5. Interface Contracts

- Public Python API: `double(n)` — one positional parameter named `n`; for any `int`, returns the `int` `n * 2`. Importable as `from testbed_utils.doubler import double` and `from testbed_utils import double`; `"double"` is in `testbed_utils.__all__`.
- Integers are arbitrary-precision in Python, so very large values double exactly (verified on the CI runtime, Python 3.12: `2**100 * 2` is exact) — no overflow case exists.
- Non-integer input (float, str, `None`, `bool`): deliberately unspecified by the spec. The helper does no type check and no rejection; whatever `n * 2` does is what happens. No test asserts any of it.
- No cross-repo contracts, no events.

## 6. Key Technical Decisions

- **Separate module `doubler.py`** rather than adding to `numutils.py`: the spec names the path, and it leaves `numutils` untouched (spec non-goal).
- **No input validation:** the developer settled at intake that only integers are in contract and nothing is rejected; adding an `isinstance` check would invent behaviour.
- **Doctest in the docstring** is optional style, matching sibling modules; if present it must pass (existing tests such as `tests/test_numutils.py:88-96` run module doctests, and `tests/test_doubler.py` may do the same).
- **One work item:** the change is three small files; splitting would produce non-shippable fragments.

## 7. Risks & Constraints

- **Pre-existing red test on the base branch:** `tests/test_qa_20261122_s4_base.py` asserts `1 == 2` on `qa-20261122-s4-base`, so the full `pytest` run (and the CI `test` job) is red before this story begins. This story must not edit or delete that file (spec non-goal: no change to existing code); its done-signal is that the new tests pass and the only failing test in the suite is that pre-existing one.
- Repo gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): source under `src/`, tests under `tests/`, no file > 200 KB — the planned paths comply; no shell script is added.
- Test gate (`.factory/testing.md`): tests import only through the installed package — no `conftest.py`, no `sys.path` manipulation.
- No scale, performance or security surface: pure arithmetic, no I/O.

## 8. Assumptions

- Placement of `double` in `__all__` follows the existing alphabetical order (between `"days_between"` and `"extract_fields"`). Risk if wrong: cosmetic only.
- The pre-existing failing test is out of this story's scope and is handled by whoever owns the QA base. Risk: the PR's CI `test` job shows red for a reason unrelated to this change; the reviewer must read the failure, not just the status.
