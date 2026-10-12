# Implementation plan — Round invoice amounts to cents

| Field | Value |
| --- | --- |
| Work item | dev-1 — Add round_to_cents with tests |
| Repo | `roeeoz/play1` — checkout at `/workspace` |
| Tier | T1 (single work item, no dependencies) |
| Inputs read | `docs/plans/play-5/spec.md`, `hld.md`, `work-items.md`; `src/testbed_utils/{__init__,numutils}.py`; `tests/test_numutils.py`; `pyproject.toml`; `.factory/testing.md`; `.github/workflows/ci.yml` |

## Research findings

### Change surface

| Path | Action | Why |
| --- | --- | --- |
| `src/testbed_utils/numutils.py` | **edit** | Add `round_to_cents` to the existing numeric helpers module. The function uses `Decimal` (stdlib), which is new to this module but consistent with its role as the package's numeric utility surface. |
| `src/testbed_utils/__init__.py` | **edit** | Import `round_to_cents` and add it to `__all__`. Every public helper in the package is re-exported here. |
| `tests/test_numutils.py` | **edit** | Add a `TestRoundToCents` class with the three required cases. The file already holds tests for `mean`, `median`, `percentile` in the same one-class-per-function pattern. |

Nothing else changes. Specifically **not** touched: `pyproject.toml` (no new dependency — `decimal` is stdlib), `.github/workflows/ci.yml`, `README.md`, other source modules, other test files, `__version__`. No `CI_FAIL` file exists at the root today and none must be created.

### Existing conventions

Observed in `numutils.py`:

- `from __future__ import annotations` as the first import.
- Module-level private constants prefixed `_` (e.g. `_EMPTY_MSG`).
- Function docstrings: one-line summary with `*param*` emphasis, optional detail, then a `>>>` example.
- Validation errors are plain `ValueError` with a short lowercase message.
- Type hints on every signature; return types are concrete.

Observed in `tests/test_numutils.py`:

- Import directly from the submodule (`from testbed_utils.numutils import mean, median, percentile`).
- One `Test<FunctionName>` class per function, plain `assert` statements.
- Error cases use `pytest.raises(ValueError, match=...)`.
- A `TestPackageExports` class verifies root import and `__all__`.
- A `TestDocstringExamples` class uses `doctest.testmod`.

### Toolchain

- `pyproject.toml`: `requires-python >= 3.10`, test extra `pytest>=8`, `testpaths = ["tests"]`, `addopts = "-q"`.
- `.factory/testing.md`: `test-gate: pytest`.
- CI (`ci.yml`): job **test** = `pip install -e ".[test]"` then `pytest` on Python 3.12; job **gate** fails iff `CI_FAIL` exists at root. Workflow-level `permissions: contents: read`.
- No linter, formatter, type checker, or coverage tool. Install plus pytest is the complete gate.

### Contracts

**Provided (new public API):**

| Name | Signature | Behaviour |
| --- | --- | --- |
| `round_to_cents` | `round_to_cents(amount: Decimal) -> Decimal` | Rounds half-up to two decimal places using `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`. Works for positive, negative, and zero amounts. |

Importable from both `testbed_utils.numutils` and `testbed_utils`.

**Consumed:** `decimal.Decimal` and `decimal.ROUND_HALF_UP` from the Python standard library.

### Glossary alignment

Per the claims-dev glossary: the function rounds invoice amounts (net or gross). The name `round_to_cents` is domain-neutral and does not conflict with glossary terms. Callers in invoice-processing code will apply it to `net_amount` or `gross_amount` fields — no glossary term is embedded in the function name, which is correct since the function is a general-purpose utility.

### Resolved unknowns

| Question | Resolution | Basis |
| --- | --- | --- |
| Which module? | `src/testbed_utils/numutils.py` — the existing numeric helpers module. | HLD says "in a module under src/"; `numutils.py` already holds numeric utilities. Creating a separate module for one function would be over-engineering for a T1 task. |
| Rounding method? | `Decimal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` | HLD explicitly specifies `Decimal.quantize` with `ROUND_HALF_UP`. |
| Negative-amount behaviour? | `quantize` with `ROUND_HALF_UP` rounds toward positive infinity for midpoint values. For `-1.005` the result is `-1.00` (rounds the magnitude down since it rounds toward +∞). This is the standard half-up semantic. | Spec requires covering "a negative amount" in tests; the expected value follows from `ROUND_HALF_UP` semantics. |
| Re-export from package root? | Yes. | Every other public helper is re-exported; consistent with existing pattern. |
| Input validation? | None beyond what `Decimal.quantize` provides. The function accepts a `Decimal` and returns a `Decimal`. Passing a non-`Decimal` is a caller error (type hint documents the contract). | No existing `numutils` function validates types — they rely on type hints and duck typing. |

### Numeric verification

| Expression | Result |
| --- | --- |
| `Decimal("1.005").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` | `Decimal("1.01")` |
| `Decimal("2.004").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` | `Decimal("2.00")` |
| `Decimal("-1.005").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` | `Decimal("-1.00")` |
| `Decimal("-2.006").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` | `Decimal("-2.01")` |
| `Decimal("0").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` | `Decimal("0.00")` |

The three spec-required values (`1.005 → 1.01`, `2.004 → 2.00`, negative) are safe for exact `==` comparison since `Decimal` arithmetic is exact.

## Solution proposal

**Approach.** Add one function to the existing `numutils.py` module, using `Decimal.quantize` with `ROUND_HALF_UP` as the HLD prescribes. Update the package re-export, and extend the existing test file with a new test class. Three file edits, no new files.

**Key design decisions.**

1. **Add to `numutils.py` rather than creating a new module.** The module's purpose is numeric helpers; a rounding function fits. A single-function module would add file overhead without benefit. The `Decimal` import is new to this module but is stdlib and does not change the module's character.
2. **`Decimal.quantize` with `ROUND_HALF_UP`.** This is a locked decision from the HLD — not a choice to make. It gives exact decimal arithmetic (no float representation issues) and the "round half up" tie-breaking that finance expects.
3. **No input validation beyond the type hint.** The existing functions in `numutils.py` do not type-check their inputs. `round_to_cents` follows the same pattern: the `Decimal` type hint documents the contract; passing a `float` or `int` would be a caller bug, and `quantize` would raise `AttributeError` naturally.
4. **A `_CENTS` module-level constant** for `Decimal("0.01")` avoids reconstructing it on every call and follows the existing `_EMPTY_MSG` / `_RANGE_MSG` pattern of module-level private constants.
5. **Docstring with a `>>>` example.** Matches the existing convention in `numutils.py` where every public function has a runnable docstring example. The existing `TestDocstringExamples` class will automatically cover it via `doctest.testmod`.
6. **Update `TestPackageExports`** to verify the new name appears in `__all__` and is importable from the root.

## Ordered implementation tasks

All tasks belong to work item **dev-1**.

| # | Task | Files | Satisfies |
| --- | --- | --- | --- |
| 1 | Add `round_to_cents` to `numutils.py`: import `Decimal` and `ROUND_HALF_UP` from `decimal`; add a `_CENTS = Decimal("0.01")` constant; add the function with a docstring example `round_to_cents(Decimal("1.005"))` → `Decimal('1.01')`. | `src/testbed_utils/numutils.py` | AC1 |
| 2 | Edit `src/testbed_utils/__init__.py`: add `round_to_cents` to the `numutils` import line; insert `"round_to_cents"` into `__all__` in alphabetical position. | `src/testbed_utils/__init__.py` | AC1 (public surface) |
| 3 | Add `TestRoundToCents` class to `tests/test_numutils.py` with three test methods: `test_half_up_rounds_up` (`1.005 → 1.01`), `test_below_midpoint_rounds_down` (`2.004 → 2.00`), `test_negative_amount` (a negative value, e.g. `-1.005 → -1.00`). Update `TestPackageExports.test_root_import_and_all` to include `round_to_cents` in the import and the `__all__` check. Update `TestDocstringExamples.test_every_public_function_is_covered` to include `round_to_cents` in the expected set. | `tests/test_numutils.py` | AC2 |
| 4 | Run `pip install -e ".[test]" && pytest` from the repo root. Confirm all existing tests plus the new ones pass. | — | test gate |

## Test plan

Layer: pytest unit tests (`tests/test_numutils.py`). No files, network, clock, or external state.

| Class | Test | Assertion | AC |
| --- | --- | --- | --- |
| `TestRoundToCents` | `test_half_up_rounds_up` | `round_to_cents(Decimal("1.005")) == Decimal("1.01")` | AC2 — 1.005 → 1.01 |
| `TestRoundToCents` | `test_below_midpoint_rounds_down` | `round_to_cents(Decimal("2.004")) == Decimal("2.00")` | AC2 — 2.004 → 2.00 |
| `TestRoundToCents` | `test_negative_amount` | `round_to_cents(Decimal("-1.005")) == Decimal("-1.00")` | AC2 — negative amount |
| `TestDocstringExamples` | `test_every_public_function_is_covered` | `round_to_cents` appears in the expected set | existing invariant |
| `TestDocstringExamples` | `test_doctests_pass` | `doctest.testmod(numutils).failed == 0` (covers the new docstring example) | existing invariant |
| `TestPackageExports` | `test_root_import_and_all` | `round_to_cents` importable from `testbed_utils` and in `__all__` | existing invariant |

## Verification gate

Run from the repo root:

```bash
pip install -e ".[test]"
pytest
```

Expected:

- `pytest` — whole suite passes; all existing tests (`test_textutils`, `test_dateutils`, `test_pdfutils`, `test_pdf_extract_cli`, `test_hello`, `test_hello_cli`, `test_num_summary_cli`, `test_guestbook_api`, existing `test_numutils`) still green.
- The three new `TestRoundToCents` tests pass.
- The updated `TestPackageExports` and `TestDocstringExamples` tests pass (covering the new function's re-export and docstring).
- `git diff --stat main` shows exactly three changed files (`src/testbed_utils/numutils.py`, `src/testbed_utils/__init__.py`, `tests/test_numutils.py`).
- `pyproject.toml` has no diff (no new dependency — `decimal` is stdlib).
- No `CI_FAIL` file exists at the root.

The repo has no linter or formatter, so install + pytest is the complete pre-merge check. CI's **test** job runs the same gate on Python 3.12.

## Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **`ROUND_HALF_UP` on negatives.** `Decimal("-1.005").quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` yields `-1.00`, not `-1.01`. This is correct per Python docs — `ROUND_HALF_UP` rounds toward positive infinity at the midpoint. The test pins this behaviour. | Pinned by `test_negative_amount`. If the spec intended a different rounding for negatives, the test makes the actual behaviour explicit for review. |
| **Doctest repr.** `Decimal("1.01")` reprs as `Decimal('1.01')` — the docstring example must use that exact form. | Use `>>> round_to_cents(Decimal("1.005"))` with expected output `Decimal('1.01')`. The existing doctest infrastructure validates this. |
| **Existing test assertions must be updated.** `TestPackageExports` and `TestDocstringExamples` hard-code the set of public functions. Adding `round_to_cents` without updating these sets will fail those tests. | Task 3 explicitly includes updating these assertions. |
| **No `float` variant.** The function accepts only `Decimal`. Callers passing `float` get `AttributeError` from `quantize`. | By design — the spec requires `Decimal` in the signature. Float-based rounding is a different concern (and lossy for finance). |
| **Scope lock.** Only the three files in the change surface are modified. No `pyproject.toml`, CI, README, CLI, new modules, or `__version__` bump. No `CI_FAIL`. No merge without human approval. | |

## Clarification outcomes

No clarification needed. The spec and HLD are unambiguous: `Decimal.quantize` with `ROUND_HALF_UP`, three test cases with specified inputs and outputs, added to `src/`. All unknowns resolved in the research phase. No `plan-questions.json` written.
