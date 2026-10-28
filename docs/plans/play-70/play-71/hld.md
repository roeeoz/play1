# High-Level Design — PLAY-71: Parameterized Greeting Helper

## 1. System Overview

**What is being built.** A single pure function `greet(name: str) -> str` added to the existing `testbed-utils` Python package, returning `"Hello, <name>!"` for any string input and raising an error for non-string input.

**Problem statement.** The package offers only a static `hello_world()` helper. Consumers needing a parameterized greeting must roll their own formatting.

**Key responsibilities.** Accept a name string, validate its type, return the formatted greeting.

## 2. Architecture Overview

- **Component:** `greet` function in the existing `hello.py` module.
- **Boundary:** The function is a leaf in the package — no internal consumers, no downstream services.
- **Ownership:** Same module (`hello.py`) that owns `hello_world`.
- **External dependencies:** None. Pure-string operation using only builtins.

## 3. Data Flow

1. Caller imports `greet` from `testbed_utils` (package root) or `testbed_utils.hello`.
2. Caller passes a string argument.
3. Function validates input type → raises error if not `str`.
4. Function returns `f"Hello, {name}!"`.

No async, no events, no I/O.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `greet` function | Validate input type, return formatted greeting | `str` → `str`; non-str → error | play1 |
| Package root export | Re-export `greet` in `__init__.py` and `__all__` | — | play1 |
| Test suite additions | Verify happy path, boundary (empty string), error, docstring, export | — | play1 |

## 5. Interface Contracts

- **Public API:** `greet(name: str) -> str` importable from `testbed_utils`.
- **Error contract:** Non-string input raises an error with a message indicating the input must be a string.
- **No cross-repo contracts.** Single-repo change.

## 6. Key Technical Decisions

- **Place in existing `hello.py`** rather than a new module — thematically related to `hello_world`, keeps the change to one module plus tests (FR9).
- **Exception type deferred to implementer** — either `TypeError` (Pythonic for type validation) or `ValueError` (existing codebase convention) is acceptable; the spec requires only "a clear error."
- **Docstring with `>>>` example** following the convention in `textutils.py` and `hello.py`.

## 7. Risks & Constraints

- **RK1 — Name collision:** Mitigated. `greet` is unused in the codebase (verified by grep).
- **Module docstring:** `hello.py` docstring says "Console script" — adding `greet` makes it slightly incomplete. Low risk; implementer may update it.
- **No lint/format tooling:** Implementer must manually match existing style conventions.
