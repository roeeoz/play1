# Feature Specification Document — SCRUM-127: QA-20261124-N1 a helper that doubles a number

> Status: READY_FOR_SPEC — intake questions settled by the developer on 2026-11-24 (see §8).

## 1. Feature Overview

- **What is being built:** a new helper module `src/testbed_utils/doubler.py` in the existing `testbed_utils` package, holding one function `double(n)` that returns `n * 2`, plus a pytest test file `tests/test_doubler.py`. The function is also exported from the package root.
- **Problem statement:** the `testbed_utils` package (see `src/testbed_utils/__init__.py`, `src/testbed_utils/numutils.py`) has no doubling helper; this story adds a small, well-tested one.
- **Target users / actors:** internal developers who import `testbed_utils` in Python code (the package's public import surface). No CLI or script is part of this story.
- **Name as filed:** the ticket shows `double👎`; the developer confirmed this is Jira wiki markup rendering `(n)` as an emoticon. The function's name is `double` and its parameter is `n`.

## 2. Goals & Non-Goals

### Goals
- A developer can call `double(n)` — from `testbed_utils.doubler` or from the package root `testbed_utils` — with an integer `n` and get `n * 2` back.
- `tests/test_doubler.py` covers positive, zero and negative integer inputs, and runs in the repository's `pytest` gate (`.factory/testing.md`, `.github/workflows/ci.yml`).

### Non-Goals
- No CLI, console entry point or `qa/` script (so the `qa/` script standing rule does not apply).
- No change to existing helpers (`numutils`, `textutils`, `dateutils`, etc.) or to the guestbook app, beyond adding `double` to the package root's imports and `__all__`.
- No behaviour is promised for non-integer inputs (floats, strings, `None`, `bool`): no rejection, no error, and no test for them (developer decision, 2026-11-24).

## 3. Functional Requirements

- **FR1** — `src/testbed_utils/doubler.py` defines a function `double` taking one argument `n`.
- **FR2** — For any integer `n` (positive, zero, negative), `double(n)` returns `n * 2` (e.g. `double(3) == 6`, `double(0) == 0`, `double(-4) == -8`).
- **FR3** — `tests/test_doubler.py` exists under `tests/` and asserts FR2 for at least one positive, zero and one negative input.
- **FR4** — `double` is exported from the package root: `from testbed_utils import double` works and `"double"` is listed in `testbed_utils.__all__`, as every existing helper is (`src/testbed_utils/__init__.py`).
- **Edge cases** — integers only are in contract; non-integer input is deliberately unspecified and untested.

## 4. User Experience & Behavior

- **Flow:** a developer imports `double` from `testbed_utils` (or `testbed_utils.doubler`) and calls it with an integer; they receive the doubled integer. Nothing is printed.
- **States / messages:** none user-facing; the function is a pure return-value helper.
- No look-and-feel, output-format or performance qualities were named by the story.

## 5. Acceptance Criteria

1. double(n) returns n * 2 for integers.
2. A pytest test under tests/ covers positive, zero and negative inputs.
3. double is exported from the package root: `from testbed_utils import double` works and "double" is listed in `testbed_utils.__all__`.

## 6. Dependencies & Constraints (product-level)

- Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): Python source under `src/`, tests under `tests/`, no file over 200 KB — the requested paths already comply.
- Test gate (`.factory/testing.md`): `pip install -e ".[test]" && pytest`; tests must import through the installed package (no `sys.path` tricks).
- The story stands alone; it depends on no sibling story.

## 7. Technical Design (deferred to STRUCTURE)

Implementation details (type hints, docstring, test structure, placement in `__all__`) are left to STRUCTURE. Product-imposed constraints: the public name is `double` with parameter `n`, and it is importable from both `testbed_utils.doubler` and `testbed_utils`.

## 8. Open Questions

No open product questions. Settled at intake (developer, 2026-11-24):

- **Name** — `double(n)`; the `👎` in the ticket is Jira wiki markup rendering `(n)` as an emoticon. Criterion 1 is reworded accordingly.
- **Non-integer input** — integers only; no rejection and no test for other inputs.
- **Package-root export** — yes, from `testbed_utils` and in `__all__`; added as criterion 3.
