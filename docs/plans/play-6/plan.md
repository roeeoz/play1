# Implementation plan — Sum invoice tax amounts

| Field | Value |
| --- | --- |
| Work item | dev-1 — Add invoice_tax_total with tests |
| Repo | `roeeoz/play1` — single repo, single PR |
| Tier | T1 (one work item, no dependencies) |
| Traces | spec AC1–AC2 · work-item dev-1 |
| Inputs read | `docs/plans/play-6/{spec,hld,work-items}.md`; `src/testbed_utils/{__init__,numutils,dateutils,textutils,pdfutils}.py`; `tests/test_numutils.py`; `pyproject.toml`; `.factory/testing.md`; `.github/workflows/ci.yml` |

## Research findings

### Change surface

| Path | Action | Why |
| --- | --- | --- |
| `src/testbed_utils/invoiceutils.py` | **create** | New module housing `invoice_tax_total`. Follows the `*utils.py` naming pattern (`numutils`, `textutils`, `dateutils`, `pdfutils`). |
| `src/testbed_utils/__init__.py` | **edit** (2 lines) | Import and re-export `invoice_tax_total` in `__all__`, consistent with every other public function in the package. |
| `tests/test_invoiceutils.py` | **create** | Unit tests covering the three required scenarios: no lines, one line, several lines. |

**Not touched:** `pyproject.toml` (no new dependency — `decimal` is stdlib; no new console script), `numutils.py`, `textutils.py`, `dateutils.py`, `pdfutils.py`, `hello.py`, `numsummary.py`, `.github/workflows/ci.yml`, `.factory/`, `README.md`, any existing test file.

### Toolchain

- `pyproject.toml`: `requires-python >= 3.10`; runtime dep `pypdf`, `flask>=3`; test extra `pytest>=8`; setuptools `src/` layout (`[tool.setuptools.packages.find] where = ["src"]`), so tests import only the installed distribution.
- Gate (`.factory/testing.md`, `ci.yml`): `pip install -e ".[test]"` then `pytest` on Python 3.12. No linter, formatter, type-checker, or coverage tool. Install + pytest is the complete check. Layer id `package-api`, class production-path, run by canonical gate.
- `Decimal` is from Python's `decimal` stdlib module — no new dependency.

### Existing conventions to follow

From existing `*utils.py` modules:

- `from __future__ import annotations` at the top.
- Short module-level docstring on one line.
- Stdlib imports, then package imports.
- Functions use type annotations.
- Each public function is re-exported from `__init__.py` and added to `__all__`.

From existing test files (`test_numutils.py`):

- Import the function under test from its module directly.
- Class-based grouping by function/scenario (`TestMean`, `TestMedian`).
- Plain `assert` statements, `pytest.raises` for errors.
- Verify the function appears in `testbed_utils.__all__` and is importable from the package root.

### Contracts

**Consumed:** `decimal.Decimal` (stdlib) — standard arithmetic and construction.

**Provided (new):**

| Surface | Contract |
| --- | --- |
| `invoice_tax_total(lines)` | Accepts an iterable of objects with a `.tax` attribute (each a `Decimal`). Returns a `Decimal`: the sum of all `.tax` values. Returns `Decimal("0")` when the iterable is empty. |
| Package re-export | `from testbed_utils import invoice_tax_total` works; `"invoice_tax_total"` is in `__all__`. |

### Resolved unknowns

| Question | Resolution | Basis |
| --- | --- | --- |
| Module name | `invoiceutils.py` | Follows the `*utils.py` naming pattern used throughout the package. |
| What is a "line"? | Any object with a `.tax` attribute of type `Decimal`. Duck-typed access via attribute, not a defined class. | AC says "each line's `tax` (Decimal)". Keeping it duck-typed avoids introducing a data class the spec does not require. |
| Return type for empty input | `Decimal("0")` (not `Decimal(0)` — both are equivalent, but the string form is conventional). | AC: "0 for no lines". Return type is `Decimal` per the signature. |
| New dependencies | None. `decimal` is stdlib. | `pyproject.toml` unchanged. |
| `__init__.py` re-export | Yes — every other public function is re-exported. | Convention from existing `__init__.py`. |

## Solution proposal

**Approach.** One new stdlib-only module `src/testbed_utils/invoiceutils.py` defines a single function `invoice_tax_total(lines) -> Decimal` that iterates over `lines`, sums each element's `.tax` attribute using Python's built-in `sum()` with a `Decimal("0")` start value, and returns the result. The function is re-exported from the package `__init__.py`. A single test file `tests/test_invoiceutils.py` covers the three AC scenarios (no lines, one line, several lines) plus a package-export check.

**Key design decisions.**

1. **New module `invoiceutils.py`**, not added to an existing module — the function is domain-distinct from numeric utilities, text utilities, or date utilities. Follows the established `*utils.py` pattern.
2. **Duck-typed `lines` parameter** — accepts any `Iterable` of objects with a `.tax` attribute. No dataclass or protocol is defined; the spec does not require one, and introducing one would exceed scope.
3. **`sum()` with `start=Decimal("0")`** — handles the empty-iterable case naturally (returns the start value), satisfying AC1's "0 for no lines" without a special branch. Also correct for one or many lines.
4. **Type annotation `Iterable[Any]`** for `lines` — avoids importing or creating a structural type for the line object. The `-> Decimal` return annotation is explicit per the AC.

**Target function:**

```python
def invoice_tax_total(lines: Iterable[Any]) -> Decimal:
    return sum((line.tax for line in lines), start=Decimal("0"))
```

## Ordered implementation tasks

All tasks belong to work item **dev-1**. Order: module → `__init__.py` → tests → verify.

| # | Task | Files | Satisfies |
| --- | --- | --- | --- |
| 1 | Create `src/testbed_utils/invoiceutils.py` with `invoice_tax_total` per the solution proposal. Module docstring, `from __future__ import annotations`, imports of `Decimal` and `Iterable`/`Any` from typing. | `src/testbed_utils/invoiceutils.py` | AC1 |
| 2 | Edit `src/testbed_utils/__init__.py`: add import of `invoice_tax_total` from `invoiceutils`, add to `__all__`. Alphabetical insertion in both the import block and the `__all__` list. | `src/testbed_utils/__init__.py` | AC1 (package export convention) |
| 3 | Create `tests/test_invoiceutils.py` with three test scenarios: `test_no_lines` (empty list → `Decimal("0")`), `test_one_line` (single-element list → that element's tax), `test_several_lines` (multiple elements → correct sum). Use a minimal helper (e.g. `types.SimpleNamespace(tax=...)`) to create line objects. Add a `TestPackageExports` class verifying root import and `__all__` membership, matching the pattern in `test_numutils.py`. | `tests/test_invoiceutils.py` | AC2 |
| 4 | Run `pip install -e ".[test]" && pytest` from the repo root. Full suite must be green, including all existing tests. Confirm no `CI_FAIL` at root. | — | test gate |

## Test plan (layer: `package-api` — pytest under `tests/`, production-path)

| Class | Test | Setup | Assertion | AC |
| --- | --- | --- | --- | --- |
| `TestInvoiceTaxTotal` | `test_no_lines` | `lines = []` | `invoice_tax_total(lines) == Decimal("0")` | AC1, AC2 |
| `TestInvoiceTaxTotal` | `test_one_line` | `lines = [SimpleNamespace(tax=Decimal("10.50"))]` | `invoice_tax_total(lines) == Decimal("10.50")` | AC2 |
| `TestInvoiceTaxTotal` | `test_several_lines` | `lines = [SimpleNamespace(tax=Decimal("10.00")), SimpleNamespace(tax=Decimal("5.25")), SimpleNamespace(tax=Decimal("3.75"))]` | `invoice_tax_total(lines) == Decimal("19.00")` | AC2 |
| `TestPackageExports` | `test_root_import_and_all` | — | `from testbed_utils import invoice_tax_total` succeeds; `"invoice_tax_total" in testbed_utils.__all__` | AC1 |

## Verification — what the gate must show

Run from the repo root:

```bash
pip install -e ".[test]"
pytest
pytest tests/test_invoiceutils.py -v
test ! -e CI_FAIL && echo "no CI_FAIL"
```

Expected:

- `pytest` — whole suite green, including all existing tests (`test_numutils.py`, `test_textutils.py`, `test_dateutils.py`, `test_pdfutils.py`, `test_hello.py`, `test_hello_cli.py`, `test_pdf_extract_cli.py`, `test_num_summary_cli.py`, `test_guestbook_api.py`).
- `pytest tests/test_invoiceutils.py -v` — 4 tests pass (3 scenario tests + 1 package export test).
- No `CI_FAIL` file.
- CI's **test** job repeats install + pytest on Python 3.12; the **gate** job stays green while `CI_FAIL` is absent.

## Risks and scope guards

| Risk / guard | Handling |
| --- | --- |
| **Existing tests break** if `__init__.py` edit introduces a syntax error or import cycle. | The edit is two lines (one import, one `__all__` entry), alphabetically inserted. Verify with full `pytest`. |
| **`test_numutils.py::TestDocstringExamples` breaks** if a public function is accidentally added to `numutils.py`. | The new function lives in `invoiceutils.py`; `numutils.py` is untouched. |
| **Scope lock.** | Only three files change: `invoiceutils.py` (create), `__init__.py` (edit), `test_invoiceutils.py` (create). No new dependencies, no `pyproject.toml` edit, no CLI, no CI change, no `CI_FAIL`, no merge without the human approval gate. |
| **No dataclass/protocol for line objects.** | Intentional — the AC specifies duck-typed `.tax` access. A structural type can be added later if needed without breaking the function signature. |

## Clarification outcomes

None required. The AC is unambiguous: one function, one return type, three test cases. No `plan-questions.json` is written.
