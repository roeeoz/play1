# High-Level Design — PLAY-83

## 1. System Overview

- **What is being built.** A behaviour change to the existing `truncate` helper in the `testbed_utils.textutils` module of the play1 repository.
- **Problem.** The current three-character ASCII ellipsis suffix consumes too much of the allowed length for display-truncation use cases, and raising `ValueError` on negative input forces unnecessary caller-side guards.
- **Key responsibilities.** The modified function accepts `(text, n)`, returns text unchanged when it fits, returns `""` for n ≤ 0, and truncates to exactly n characters using a single Unicode ellipsis (U+2026) otherwise.

## 2. Architecture Overview

- **Components.** One module (`textutils.py`) and its test file (`test_textutils.py`). No new modules, no new packages.
- **Boundaries.** The change is entirely within `truncate`; `slugify` and `word_count` in the same module are untouched.
- **Ownership.** Single repository: `roeeoz/play1`.
- **External dependencies.** None introduced. Pure Python, standard library only.

## 3. Data Flow Design

- Caller → `truncate(text, n)` → returns a string of length ≤ n.
- No I/O, no async, no events. Synchronous pure function.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|-----------|---------------|------------------|------------|
| `truncate` function | Truncate text to n chars with Unicode ellipsis | `(str, int)` → `str` | roeeoz/play1 |
| `TestTruncate` test class | Verify all truncate behaviours | pytest assertions | roeeoz/play1 |

## 5. Interface Contracts

- **Public API.** `truncate(text: str, n: int) -> str` — exported from `testbed_utils.textutils` and re-exported from `testbed_utils.__init__`.
- The `__init__.py` import is by name (`from testbed_utils.textutils import … truncate …`) and does not reference the old parameter, so it requires no change.

## 6. Key Technical Decisions

- **Fixed ellipsis, no parameter.** The `suffix` parameter is dropped entirely rather than defaulted to `"…"`, per the spec's explicit signature `truncate(text, n)`.
- **Modify in place, not add a second function.** The package is 0.x with no backwards-compatibility guarantee; a second function would create confusion.
- **n=1 yields `"…"`.** Step 4 of the to-be process: `text[:0] + "…"` = `"…"`, length 1. Correct by construction.

## 7. Risks & Constraints

- **RK1 (external callers).** Mitigated: package is 0.x, no compat guarantee.
- **RK2 (lost configurability).** Accepted: re-addable later if needed.
- No scaling, security, or operational concerns — this is a pure string helper in a test-fixture library.
