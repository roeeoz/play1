# Feature Specification Document — SCRUM-127: QA-20261124-N1 a helper that doubles a number

> Status: in-progress intake draft (NOT_READY) — see §8.

## 1. Feature Overview

- **What is being built:** a new helper module `src/testbed_utils/doubler.py` in the existing `testbed_utils` package, holding one function that returns its argument multiplied by 2, plus a pytest test file `tests/test_doubler.py`.
- **Problem statement:** the `testbed_utils` package (see `src/testbed_utils/__init__.py`, `src/testbed_utils/numutils.py`) has no doubling helper; this story adds a small, well-tested one.
- **Target users / actors:** internal developers who import `testbed_utils` in Python code (the package's public import surface). No CLI or script is part of this story.
- **Blocking ambiguity:** the function's name as filed is `double👎`. That is not a valid Python identifier, so the name a developer imports cannot be taken from the ticket as written (see §8, Q1).

## 2. Goals & Non-Goals

### Goals
- A developer can call the doubling function from `testbed_utils.doubler` with an integer `n` and get `n * 2` back.
- `tests/test_doubler.py` covers positive, zero and negative integer inputs, and runs in the repository's `pytest` gate (`.factory/testing.md`, `.github/workflows/ci.yml`).

### Non-Goals
- No CLI, console entry point or `qa/` script (so the `qa/` script standing rule does not apply).
- No change to existing helpers (`numutils`, `textutils`, `dateutils`, etc.) or to the guestbook app.
- Behaviour for non-integer inputs (floats, strings, `None`, `bool`) is not stated by the story — pending Q2.

## 3. Functional Requirements

- **FR1** — `src/testbed_utils/doubler.py` defines a function (name pending Q1) taking one argument `n`.
- **FR2** — For any integer `n` (positive, zero, negative), the function returns `n * 2` (e.g. `3 → 6`, `0 → 0`, `-4 → -8`).
- **FR3** — `tests/test_doubler.py` exists under `tests/` and asserts FR2 for at least one positive, zero and one negative input.
- **FR4 (pending Q3)** — Whether the function is also re-exported from the package root (`from testbed_utils import …`, listed in `__all__`) as every existing helper is.
- **Edge cases (pending Q2)** — non-integer input: unspecified.

## 4. User Experience & Behavior

- **Flow:** a developer imports the function from `testbed_utils.doubler` and calls it with an integer; they receive the doubled integer. Nothing is printed.
- **States / messages:** none user-facing; the function is a pure return-value helper.
- No look-and-feel, output-format or performance qualities were named by the story.

## 5. Acceptance Criteria

1. double👎 returns n * 2 for integers.
2. A pytest test under tests/ covers positive, zero and negative inputs.

## 6. Dependencies & Constraints (product-level)

- Repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): Python source under `src/`, tests under `tests/`, no file over 200 KB — the requested paths already comply.
- Test gate (`.factory/testing.md`): `pip install -e ".[test]" && pytest`; tests must import through the installed package (no `sys.path` tricks).
- The story stands alone; it depends on no sibling story.

## 7. Technical Design (deferred to STRUCTURE)

Implementation details (type hints, docstring, test structure) are left to STRUCTURE. The only product-imposed constraint is that the function name must be a valid Python identifier.

## 8. Open Questions

- **Q1 (P0)** — The function is named `double👎` in the title, description and criterion 1. A Python function cannot carry that name. What exact name should developers import? Recommendation: `double(n)`, because the emoji reads like a mangled `(n)` and `n` is the parameter the criteria use. If the emoji is deliberate, the story has to change its scope, since no valid Python function can have that name.
- **Q2 (P1)** — What should happen for non-integer input (float, `bool`, string, `None`)? Recommendation: keep integers as the only contract and leave other inputs unspecified, with no rejection and no test, because criterion 1 says "for integers" only. If you want floats doubled or non-numbers rejected with an error, say so and it becomes a criterion.
- **Q3 (P1)** — Should the function also be exported from the package root (`from testbed_utils import double`, added to `__all__`)? Recommendation: yes, because every existing helper is exported there (`src/testbed_utils/__init__.py`). If you want it importable only from `testbed_utils.doubler`, say no.
