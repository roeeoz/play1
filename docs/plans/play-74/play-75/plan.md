# Implementation plan — PLAY-75: Range-clamping helper with full test coverage

## Context

PLAY-75 adds a `clamp(value, low, high)` function to the testbed-utils package in the `play1` repository (branch `halo/feat/play-75`). The function bounds a numeric value to [low, high] and raises `ValueError` on inverted bounds. It ships as a new module with full test coverage and package-root registration, following the established `*utils.py` convention. The specification (`spec.md`), design (`hld.md`) and breakdown (`work-items.md`) sit beside this file in `docs/plans/play-74/play-75/`.

## Research findings

**Package layout.** `src/testbed_utils/` contains six modules: `dateutils.py`, `hello.py`, `numsummary.py`, `numutils.py`, `pdfutils.py`, `textutils.py`. Four non-CLI utility modules use the `*utils.py` naming pattern. `__init__.py:8-12` imports specific functions from each module; `__init__.py:14-26` lists them alphabetically in `__all__`.

**Module convention (observed in `numutils.py:1-6`).** Each utility module starts with a module-level docstring, then `from __future__ import annotations`, then private constants for error messages (e.g. `_EMPTY_MSG` at `numutils.py:10`), then public functions with Google-style docstrings containing `>>>` examples.

**Test convention (observed in `test_numutils.py:1-99`).** Each test file imports `doctest`, `inspect`, `pytest`, the package root, and the submodule. Tests are grouped in classes: one per public function (happy path, boundary, error), plus `TestPackageExports` (verifying root import and `__all__` at `test_numutils.py:56-64`) and `TestDocstringExamples` (verifying every public function has a runnable `>>>` example via `doctest.DocTestFinder` and `doctest.testmod` at `test_numutils.py:77-98`). A `public_functions()` helper at `test_numutils.py:67-74` enumerates the module's public callables.

**Why a new module, not `numutils.py`.** `test_numutils.py:79-83` asserts the exact set of public functions in `numutils` is `{"mean", "median", "percentile"}`. Adding `clamp` there would break that assertion. The HLD locks this decision (HLD §6).

**Canonical gate.** `.factory/testing.md` declares `test-gate: pytest`. `.github/workflows/ci.yml` runs `pip install -e ".[test]"` then `pytest` on Python 3.12 with `permissions: contents: read`. No linter, formatter, type checker, or coverage tool is configured. `pytest` is the complete pre-merge check.

**No new dependencies.** `pyproject.toml:12` declares runtime deps `pypdf` and `flask>=3`; test extra is `pytest>=8`. The change introduces no new dependency (FR9).

**Change surface.** Three files, all in `play1`:

| File | Action | Lines affected |
|---|---|---|
| `tests/test_clamputils.py` | **Create** | ~55 new |
| `src/testbed_utils/clamputils.py` | **Create** | ~25 new |
| `src/testbed_utils/__init__.py` | **Edit** | +1 import line (~line 9), +1 `__all__` entry (~line 16) |

Estimated total: ~80 changed lines, well within the 300-line limit.

## Locked decisions and assumptions

**Locked decisions:**

- Module name is `clamputils.py` (HLD §2, §6).
- Implementation uses `max(low, min(value, high))` with a preceding `low > high` guard (HLD §6).
- Function signature is `clamp(value: float, low: float, high: float) -> float` (HLD §5).
- `ValueError` is raised when `low > high`; equal bounds are valid (spec §3 FR5, spec §3 edge cases).
- The function is registered in `__init__.py` and `__all__` (spec §3 FR8).
- No new runtime dependency (spec §3 FR9).
- Docstring contains a runnable `>>>` example (spec §3 FR6).
- Two work items: t1 (test suite and module) lands first, t2 (package-root registration) follows (work-items.md, HLD §6).

**Assumptions:**

- The error message constant follows the existing `_<NAME>_MSG` pattern (evidence: `numutils.py:10-11`). Consequence if wrong: cosmetic only; the `pytest.raises(match=...)` string in the test must match whatever wording is chosen.
- The `__all__` list stays alphabetically sorted (evidence: `__init__.py:14-26` is sorted). Consequence if wrong: none functional; style only.
- `clamp` is inserted into `__init__.py` imports after the `dateutils` line and before the `hello` line, maintaining alphabetical module order (evidence: `__init__.py:8-12` is alphabetical by module). Consequence if wrong: none functional.

## Solution proposal

Add a single new module `src/testbed_utils/clamputils.py` containing the `clamp` function. The function validates `low <= high` (raising `ValueError` with a private-constant message when violated), then returns `max(low, min(value, high))` — a zero-branch idiom that naturally handles value-within-bounds, below-lower, and above-upper in one expression. The module follows the established pattern: module docstring, `from __future__ import annotations`, private error constant, public function with a Google-style docstring and `>>>` example.

Register `clamp` in `__init__.py` with an import line and an `__all__` entry, both in alphabetical position.

Create `tests/test_clamputils.py` mirroring the `test_numutils.py` pattern: a `TestClamp` class covering AC1–AC6, a `TestPackageExports` class covering AC7 (root import and `__all__`), a `public_functions()` helper, and a `TestDocstringExamples` class verifying the `>>>` example is present and passes `doctest.testmod`.

**Two-commit split (developer feedback).** The implementation is delivered in two commits, tests first:

| Commit | Name | Work item | Content |
|---|---|---|---|
| 1 | `Add clamp test suite and module` | t1 | `tests/test_clamputils.py` (creates), `src/testbed_utils/clamputils.py` (creates) |
| 2 | `Register clamp in package root` | t2 | `src/testbed_utils/__init__.py` (edits: import + `__all__`), `tests/test_clamputils.py` (edits: appends export and discoverability tests) |

Commit 1 delivers the test suite and the module it tests — the tests define the contract, the module satisfies it. Commit 2 wires `clamp` into the package's public API and adds the tests that verify the wiring.

**Alternatives rejected:**

- Extending `numutils.py`: breaks `test_numutils.py:79-83` exact-set assertion. Locked out by HLD §6.
- Adding type enforcement (rejecting non-numeric arguments): spec §2 non-goal; Python's comparison operators handle int/float naturally.

## Ordered implementation steps

### Commit 1 — `Add clamp test suite and module` (t1)

1. **Create `tests/test_clamputils.py` (core tests only).**
   - Import `doctest`, `inspect`, `pytest`, `testbed_utils`, `testbed_utils.clamputils`, and `clamp` from `testbed_utils.clamputils`.
   - `TestClamp` class: `test_value_within_bounds` (AC1: `clamp(5, 1, 10) == 5`), `test_value_below_lower` (AC2: `clamp(-3, 0, 10) == 0`), `test_value_above_upper` (AC3: `clamp(15, 0, 10) == 10`), `test_value_equals_lower` (AC4: `clamp(1, 1, 10) == 1`), `test_value_equals_upper` (AC5: `clamp(10, 1, 10) == 10`), `test_inverted_bounds_raises` (AC6: `pytest.raises(ValueError)` on `clamp(7, 10, 5)`).
   - `public_functions()` helper following the `test_numutils.py:67-74` pattern.
   - `TestDocstringExamples` class: verify every public function has a `>>>` example via `doctest.DocTestFinder`, and all doctests pass via `doctest.testmod` (AC7 docstring clause).
   - Advances: AC1–AC6, AC7 (docstring clause only).
   - Mapped requirements: FR7.
   - Test layer: `package-api` (pytest).

2. **Create `src/testbed_utils/clamputils.py`.**
   - Module docstring, `from __future__ import annotations`, private `_RANGE_MSG` constant, `clamp` function with type hints and a Google-style docstring containing a `>>>` example. The guard raises `ValueError(_RANGE_MSG)` when `low > high`; the body returns `max(low, min(value, high))`.
   - Advances: AC1 (value within bounds), AC2 (below lower), AC3 (above upper), AC4 (equals lower), AC5 (equals upper), AC6 (inverted bounds error).
   - Mapped requirements: FR1, FR2, FR3, FR4, FR5, FR6.
   - Test layer: `package-api` (pytest), covered by step 1.

3. **Commit as `Add clamp test suite and module`.**

### Commit 2 — `Register clamp in package root` (t2)

4. **Edit `src/testbed_utils/__init__.py`.**
   - Add `from testbed_utils.clamputils import clamp` after the `dateutils` import line (`__init__.py:8`), before the `hello` import (`__init__.py:9`). Add `"clamp"` to `__all__` in alphabetical position (after the opening bracket, before `"days_between"`).
   - Advances: AC7 (importable from package root, appears in `__all__`).
   - Mapped requirement: FR8.
   - Test layer: `package-api` (pytest), covered by step 5.

5. **Append package-export tests to `tests/test_clamputils.py`.**
   - `TestPackageExports` class: verify `from testbed_utils import clamp` succeeds and `"clamp"` is in `testbed_utils.__all__` (AC7).
   - Advances: AC7 (import and `__all__` clauses).
   - Mapped requirement: FR8.
   - Test layer: `package-api` (pytest).

6. **Commit as `Register clamp in package root`.**

**Implicit invariants:** No authorization, tenancy, concurrency, or idempotency concerns — the function is a pure, synchronous, stateless computation with no I/O or side effects. Validation is limited to the `low > high` guard (FR5).

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add clamp test suite and module |
| 2 | t1 | Add clamp test suite and module |
| 3 | t1 | Add clamp test suite and module |
| 4 | t2 | Register clamp in package root |
| 5 | t2 | Register clamp in package root |
| 6 | t2 | Register clamp in package root |

Every work item maps to at least one step. No work item is unmapped.

## Verification and CI gate

**Canonical gate:** `pytest`, run from the repository root after `pip install -e ".[test]"`.

**Required test layer:** `package-api` (production-path, required, `runBy: canonical-gate`). This is the only declared layer in `.factory/testing.md`.

**What the gate must show:**

- All existing tests pass (no regressions).
- `test_clamputils.py` discovers and passes all new test cases (AC1–AC7).
- Doctests in `clamputils.py` pass.
- No new runtime dependency in `pyproject.toml`.

**Per-commit gate expectation:**

- After commit 1 (`Add clamp test suite and module`): `pytest` passes. The `TestClamp` and `TestDocstringExamples` classes in `test_clamputils.py` are green. No `TestPackageExports` yet — that lands in commit 2.
- After commit 2 (`Register clamp in package root`): `pytest` passes. All tests green including the new `TestPackageExports` class.

**Provider CI:** `.github/workflows/ci.yml` already runs `pip install -e ".[test]"` then `pytest` on `pull_request`. No change to CI configuration is needed. The `gate` job checks for a `CI_FAIL` marker file; this change does not create one.

**Validation from clean worktree:** The implement phase validates at the committed SHA from a clean temporary worktree: `pip install -e ".[test]" && pytest`.

**No `.factory/testing.md` update needed:** The canonical `test-gate: pytest` is unchanged.

**No `.factory/delivery-assets` obligation:** No binary deliverable is introduced.

## Risks and scope guards

**Risks:**

| Risk | Likelihood | Mitigation |
|---|---|---|
| Package-level coverage drops below 90% | Low | The new function is fully branch-covered by the test suite; all existing tests remain unchanged. The 90% target is informational (no `pytest-cov` gate). |
| `__all__` ordering or import position causes a merge conflict with concurrent changes | Low | The change is two lines in `__init__.py`; resolve on merge if needed. |
| Commit 1 tests import `testbed_utils` but `clamp` is not yet in `__all__` | None | Commit 1 tests import from `testbed_utils.clamputils` directly; `TestPackageExports` (which needs the `__init__.py` wiring) is deferred to commit 2. |

**Scope guards — the implement phase must NOT:**

- Modify `numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, `hello.py`, `numsummary.py`, or any existing test file.
- Add a console script or CLI entry point for `clamp`.
- Add any runtime dependency to `pyproject.toml`.
- Add type enforcement or coercion logic (no `isinstance` checks).
- Modify `.github/workflows/ci.yml`.
- Delete, skip, disable, or weaken any existing test or CI check.
- Create or modify `.factory/testing.md` (the gate is unchanged).

## Clarification outcomes

The developer reviewed the previous plan and requested: "Split the implementation into two commits: tests first, then the helper; name them in the plan." Applied: the ordered implementation steps are now grouped under two named commits — commit 1 `Add clamp test suite and module` (t1) and commit 2 `Register clamp in package root` (t2) — with per-commit gate expectations documented in the verification section.
