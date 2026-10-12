# Plan — Add invoice net-amount helper

## Research findings

### Change surface

The repository is a Python package (`testbed-utils`) using a setuptools `src/` layout. Source modules live in `src/testbed_utils/` (dateutils, numutils, textutils, pdfutils, hello, numsummary) and `src/guestbook/`. There is no existing invoice-related module; the function needs a new module.

The public API is re-exported from `src/testbed_utils/__init__.py` and listed in `__all__`. Every existing module follows the same pattern: `from __future__ import annotations`, type-hinted signatures, docstrings with `>>>` examples.

Tests live in `tests/test_<module>.py` using pytest classes. The test suite for `numutils` additionally validates `__all__` exports and doctest examples — the new test file should follow the same conventions.

### Contracts

- **Test gate:** `pytest` (declared in `.factory/testing.md`; invoked by `.github/workflows/ci.yml` test job on Python 3.12 after `pip install -e ".[test]"`).
- **No linter, formatter, or type checker** is configured anywhere in this repository.
- **Claims glossary (plugin):** "invoice" is the correct noun (never "bill"/"receipt"); "net amount" means before tax. The function name `invoice_net_amount` satisfies both terms.

### Resolved unknowns

- **Line representation:** the AC specifies "each line's `amount` (Decimal)," so each line is an object with an `.amount` attribute of type `Decimal`. Duck typing suffices; no class hierarchy is needed for the helper alone.
- **Return type for empty input:** the AC says "0 for no lines." Since the function operates on `Decimal`, the zero is `Decimal(0)` to keep the return type consistent.
- **Module placement:** the hld says "a small module under `src/`." Following the existing pattern (`numutils.py`, `dateutils.py`), the new module is `src/testbed_utils/invoices.py`.

## Solution proposal

Add a single new module `src/testbed_utils/invoices.py` containing the function `invoice_net_amount(lines)`. The function accepts an iterable of objects whose `.amount` attribute is a `Decimal`, and returns the sum as a `Decimal` — or `Decimal(0)` for an empty iterable. Export it from `src/testbed_utils/__init__.py` and add it to `__all__`, matching how `mean`, `median`, and `percentile` are surfaced from `numutils`.

Add `tests/test_invoices.py` with pytest covering the three cases the AC requires (no lines, one line, several lines), plus a root-import/`__all__` check consistent with the existing `TestPackageExports` pattern in `test_numutils.py`.

No new dependencies, no CI changes, no configuration changes. The existing `pytest` gate covers the new test file automatically.

## Ordered implementation tasks

### Task 1 — Create `src/testbed_utils/invoices.py` with `invoice_net_amount`

**Work item:** dev-1
**Advances:** AC 1 (function exists under `src/`), AC 3 (glossary-compliant naming)

Create the module with:

- `from __future__ import annotations` and `from decimal import Decimal`.
- `invoice_net_amount(lines: Iterable[Any]) -> Decimal` that iterates over `lines`, sums each element's `.amount`, and returns the total. Returns `Decimal(0)` when `lines` is empty.
- A docstring with a `>>>` example, following the existing module style.

**Files:** `src/testbed_utils/invoices.py` (new)

### Task 2 — Export from `__init__.py`

**Work item:** dev-1
**Advances:** AC 1 (function available from the package's public surface)

Add `invoice_net_amount` to the import block and to `__all__` in `src/testbed_utils/__init__.py`, matching the existing alphabetical order.

**Files:** `src/testbed_utils/__init__.py` (modify)

### Task 3 — Add unit tests

**Work item:** dev-1
**Advances:** AC 2 (test coverage for no lines, one line, several lines)

Create `tests/test_invoices.py` with:

- A lightweight test-only object (e.g. a `SimpleNamespace` or a small dataclass) providing an `.amount` attribute, used to build test inputs.
- `test_no_lines` — empty list returns `Decimal(0)`.
- `test_one_line` — single-element list returns that element's amount.
- `test_several_lines` — multi-element list returns the correct sum.
- A root-import and `__all__` membership check, consistent with the pattern in `test_numutils.py`.

**Files:** `tests/test_invoices.py` (new)

**Existing test layer:** `package-api` (the `pytest` canonical gate).

## Verification

The repository gate is `pytest`, run from the repo root after `pip install -e ".[test]"`. A green run at the committed SHA from a clean worktree proves:

1. `invoice_net_amount` is importable from both `testbed_utils.invoices` and the package root (`testbed_utils`).
2. The three required test cases (no lines, one line, several lines) pass.
3. No existing tests regress.

No other gate (linter, type checker, formatter) is configured.

## Risks and scope guards

- **No new dependencies.** `Decimal` is in the standard library; no change to `pyproject.toml` is needed.
- **No changes to CI.** The existing workflow and test gate cover the new test file without modification.
- **Scope guard — no invoice model.** This task adds only the `invoice_net_amount` helper. It does not introduce an `InvoiceLine` class, a data model, or any persistence layer. The function duck-types on `.amount`.
- **Scope guard — no CSV export.** The story mentions exports as motivation; the AC scopes the deliverable to the helper function and its tests only.

## Clarification outcomes

No clarifications needed. The AC, hld, and glossary are consistent and sufficient.
