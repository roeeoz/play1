# Implementation plan — PLAY-71

## Context

PLAY-71 adds a parameterized `greet(name)` function to the `testbed-utils` package in the `play1` repository (branch `halo/feat/play-71`), alongside the existing `hello_world()` in `src/testbed_utils/hello.py`. The function accepts a string and returns `"Hello, <name>!"`, raises on non-string input, and is exported from the package root. The planning inputs — `spec.md`, `hld.md`, and `work-items.md` — sit beside this file in `docs/plans/play-70/play-71/`.

## Research findings

**Change surface.**

| File | Current state | Change |
|---|---|---|
| `src/testbed_utils/hello.py` (24 lines) | Exports `hello_world()` (`:11-17`) and a CLI `main()` (`:20-23`). Uses `from __future__ import annotations`. Module docstring: `"Console script: print a hello-world greeting."` | Add `greet` between `hello_world` and `main`. |
| `src/testbed_utils/__init__.py` (28 lines) | Imports `hello_world` from `.hello` (`:9`). `__all__` is alphabetically sorted (`:14-26`). | Add `greet` to the import line and to `__all__` in alphabetical position. |
| `tests/test_hello.py` (30 lines) | `TestHelloWorld` (`:8-14`): return-value and package-root-export assertions. `TestDocstringExamples` (`:17-30`): doctest finder and `testmod` pass. Imports `doctest`, `testbed_utils`, and `testbed_utils.hello`. | Add test classes for `greet`: happy path, boundary, error, export, docstring. |

**Contracts touched.** The package's public API surface (`__all__` in `__init__.py`). No cross-repo consumers; no schema, wire format, or shared constant affected.

**Existing conventions.**

- Docstrings use `>>>` interactive examples (`hello.py:14-16`, `textutils.py:19-21`).
- Modules begin with `from __future__ import annotations`.
- `__all__` entries and import lines are alphabetically ordered.
- Test files group assertions in classes (`TestHelloWorld`, `TestDocstringExamples`).
- `TestDocstringExamples` uses `doctest.DocTestFinder` to check each function individually and `doctest.testmod` to run all doctests in the module.

**Test gate.** `.factory/testing.md` declares `test-gate: pytest`. CI (`.github/workflows/ci.yml`) runs `pip install -e ".[test]"` then `pytest` on Python 3.12. No linter, formatter, or type checker is configured.

**Name collision.** `greet` does not appear in the package's public API or in any module (confirmed by HLD, RK1 mitigated).

**Unknowns.** None remain after research.

## Locked decisions and assumptions

**Locked decisions.**

| Decision | Source |
|---|---|
| Function signature: `greet(name: str) -> str` | spec FR1, HLD §5 |
| Return format: `f"Hello, {name}!"` | spec FR1 |
| Non-string input raises an error with a message indicating the input must be a string | spec FR2 |
| Empty string is valid input, returns `"Hello, !"` | spec FR3 |
| Exported from the package root and listed in `__all__` | spec FR4 |
| Docstring with a `>>>` usage example | spec FR5, HLD §6 |
| Placed in `src/testbed_utils/hello.py` alongside `hello_world` | HLD §2, §6 |
| pytest cases: happy path, boundary (empty string), error (non-string) | spec FR6 |
| No new runtime dependency | spec FR8 |
| Change within one module plus tests, under 300 changed lines | spec FR9 |

**Assumptions.**

| Assumption | Evidence | Consequence if wrong |
|---|---|---|
| Exception type is `TypeError` | Pythonic convention for type validation; HLD §6 names `TypeError` as the first option; spec requires only "a clear error" | If `ValueError` is preferred, the `except` clause in the error-case test changes — a one-line fix |
| `greet` is placed after `hello_world` and before `main` in `hello.py` | Thematic grouping; `main` is the CLI entry point and conventionally last | No functional impact; only source ordering |
| Module docstring in `hello.py` is not updated | HLD §7 notes it as low risk; the ticket scope is the function, not module-level docs | A reviewer may request a follow-up to broaden the docstring |

## Solution proposal

Add `greet` as a pure function in the existing `hello.py` module, positioned between `hello_world` and `main`. The function validates `isinstance(name, str)`, raises `TypeError` with a descriptive message on failure, and returns `f"Hello, {name}!"` on success. The package root re-exports it alphabetically in both the import line and `__all__`. Tests extend `test_hello.py` with three new classes mirroring the existing pattern: one for functional assertions (happy path), one dedicated to the empty-string boundary case, one for the error case (`pytest.raises`), and additions to the existing `TestDocstringExamples` class for the new function's doctest. No new file, dependency, or CI change is needed.

This is the minimal change: one function body (~8 lines including docstring), two edits to `__init__.py`, and ~35 lines of new tests — well under the 300-line limit.

## Ordered implementation steps

1. **Add the `greet` function to `hello.py`.** Insert `greet(name: str) -> str` after `hello_world` (after line 17) and before `main` (line 20). The body: `isinstance` check raising `TypeError`, then `return f"Hello, {name}!"`. Include a docstring with a `>>>` example matching the existing convention. Files: `src/testbed_utils/hello.py`. Advances AC 1, 3, 4, 5. Test layer: `package-api` (pytest).

2. **Export `greet` from the package root.** In `src/testbed_utils/__init__.py`: add `greet` to the import on line 9 (`from testbed_utils.hello import greet, hello_world`) and insert `"greet"` into `__all__` in alphabetical position (between `"extract_fields"` and `"hello_world"`). Files: `src/testbed_utils/__init__.py`. Advances AC 2. Test layer: `package-api` (pytest).

3. **Add happy-path and export tests for `greet` in `test_hello.py`.** Add a `TestGreet` class with: `test_returns_greeting` asserting `greet("World") == "Hello, World!"`; `test_exported_from_package_root` asserting `testbed_utils.greet is hello.greet` and `"greet" in testbed_utils.__all__`. Add `from testbed_utils.hello import greet` to the imports. Files: `tests/test_hello.py`. Advances AC 1, 2. Test layer: `package-api` (pytest).

4. **Add an explicit boundary test for the empty-string input.** In the `TestGreet` class in `tests/test_hello.py`, add `test_empty_name` asserting `greet("") == "Hello, !"`. This is a dedicated test case for the empty-name boundary: it verifies that passing an empty string produces `"Hello, !"` with no error raised. Files: `tests/test_hello.py`. Advances AC 4 (Scenario 4 — Boundary: empty string input). Test layer: `package-api` (pytest).

5. **Add error-case tests for non-string input.** Add a `TestGreetErrors` class in `tests/test_hello.py` with: `test_rejects_integer` and `test_rejects_none`, each using `pytest.raises(TypeError, match=...)`. Add `import pytest` to the imports. Files: `tests/test_hello.py`. Advances AC 5. Test layer: `package-api` (pytest).

6. **Extend docstring tests for `greet`.** In `TestDocstringExamples` in `tests/test_hello.py`, add `test_greet_has_a_runnable_example` mirroring the existing `test_hello_world_has_a_runnable_example` pattern with `DocTestFinder`. The existing `test_doctests_pass` already runs `doctest.testmod(hello)` and will pick up the new `>>>` example automatically. Files: `tests/test_hello.py`. Advances AC 3. Test layer: `package-api` (pytest).

**Implicit invariants.** Authorization/tenancy: not applicable (pure library function). Concurrency/idempotency: not applicable (stateless, no I/O). Validation/error paths: covered by the `TypeError` raise and the error-case tests.

**Dependencies.** No new dependency to acquire. The existing `pytest>=8` test extra suffices (`pytest.raises` is available).

**Generated deliverables.** None. No binary artifacts, no generated files.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | t1 | Add greet(name) function with tests and package export |
| 2 | t1 | Add greet(name) function with tests and package export |
| 3 | t1 | Add greet(name) function with tests and package export |
| 4 | t1 | Add greet(name) function with tests and package export |
| 5 | t1 | Add greet(name) function with tests and package export |
| 6 | t1 | Add greet(name) function with tests and package export |

All steps belong to the single work item. No planning gap.

## Verification and CI gate

The repository's canonical gate is `pytest`, run from the repo root after `pip install -e ".[test]"`.

**Gate command (canonical order):**
1. `pip install -e ".[test]"`
2. `pytest`

**What the gate must show:**
- All existing tests pass (no regressions).
- The new `TestGreet` tests pass, including the dedicated `test_empty_name` asserting `greet("") == "Hello, !"`.
- The new `TestGreetErrors` tests pass.
- The extended `TestDocstringExamples` tests pass.
- `doctest.testmod(hello)` reports zero failures with an increased `attempted` count.

**Provider CI.** No change to `.github/workflows/ci.yml` — the existing `test` job already runs `pytest` on Python 3.12 against the installed package, which will pick up the new tests automatically.

**`.factory/testing.md`.** No update needed — `test-gate: pytest` remains correct.

**`.factory/delivery-assets`.** Not applicable — no binary deliverable.

**Validation.** The implement phase validates from a clean temporary worktree at the committed SHA by running the gate commands above. All test layers run in a pod; none require an external environment.

## Risks and scope guards

**Risks.**

| Risk | Mitigation |
|---|---|
| RK1 — Name collision with `greet` | Already mitigated: confirmed unused in the codebase (HLD §7) |
| Module docstring in `hello.py` says "Console script" and does not mention `greet` | Low impact; out of ticket scope. A reviewer may request a follow-up |

**Scope guards — the implement phase must NOT:**
- Add a CLI entry point or console script for `greet`.
- Add localized or parameterized greeting templates.
- Add any new runtime dependency to `pyproject.toml`.
- Modify or refactor `hello_world`, `main`, or any other existing function.
- Change `.github/workflows/ci.yml` or `.factory/testing.md`.
- Touch any file outside `src/testbed_utils/hello.py`, `src/testbed_utils/__init__.py`, and `tests/test_hello.py`.
- Delete, skip, disable, or weaken any existing test or CI check.

## Clarification outcomes

The developer reviewed the initial plan and requested one change: add an explicit test task for `greet('')` (empty name) asserting it returns `'Hello, !'`, mapped to the acceptance criteria. Applied: step 4 is now a dedicated boundary-test task for the empty-string input, mapped to AC 4 (Scenario 4 — Boundary: empty string input). No other clarification was needed.
