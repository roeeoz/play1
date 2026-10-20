# High-Level Design: Add `greet(name)` to `testbed_utils`

## 1. System Overview

**What is being built:** A single public function `greet(name: str) -> str` added to the `testbed_utils` Python package, returning the string `"Hello, {name}!"`.

**Problem statement:** The testbed package currently has no canonical trivial callable to use as a fixture in end-to-end developer-tooling tests. `greet` fills this gap.

**Key responsibilities:**
- Accept a name string.
- Return a deterministic, stateless greeting string.
- Be importable as a top-level symbol of `testbed_utils`.

---

## 2. Architecture Overview

The repository uses a **src layout** (`src/testbed_utils/`). Public symbols are explicitly assembled in `src/testbed_utils/__init__.py` via named imports and an `__all__` list. The existing submodule `textutils.py` holds three analogous stateless string helpers (`slugify`, `truncate`, `word_count`) and its module docstring explicitly invites extension.

No new modules, files, or external dependencies are required.

```
src/
  testbed_utils/
    __init__.py          ← add greet to import line + __all__
    textutils.py         ← add greet(name) function
tests/
    test_textutils.py    ← add TestGreet class
```

---

## 3. Data Flow Design

```
caller → greet("Roee") → f"Hello, {name}!" → "Hello, Roee!"
```

Fully synchronous, stateless, no I/O, no side effects.

---

## 4. Component Breakdown

| Component | Responsibility | Inputs | Outputs | Repo |
|---|---|---|---|---|
| `textutils.greet` | Format and return greeting | `name: str` | `str` | play1 |
| `__init__.py` export | Re-export `greet` as public symbol | — | public API surface | play1 |
| `TestGreet` pytest class | Assert correctness | — | passing test | play1 |

---

## 5. Interface Contracts

```python
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

Top-level import: `from testbed_utils import greet` must succeed.

---

## 6. Key Technical Decisions

- **Place in `textutils.py`** (not a new module): the module is explicitly designed for small stateless string helpers; adding here avoids unnecessary fragmentation.
- **Single PR**: function, export wiring, and test are inseparable — splitting them would create a temporarily broken public API or an untested symbol.
- **No input validation**: out of scope per spec; no guard clauses added.
- **Type annotation included**: `str` parameter and return type annotations follow the existing style in `textutils.py`.

---

## 7. Risks & Constraints

- **CI_FAIL gate**: the `.github/workflows/ci.yml` `gate` job fails the build if a `CI_FAIL` file exists at the repo root. This change adds no such file — risk is nil.
- **`__all__` discipline**: both the `from … import` line and `__all__` in `__init__.py` must be updated; omitting either breaks strict importers and static analysis.
- **Alphabetical order in `__all__`**: `"greet"` sorts between `"days_between"` and `"humanize_delta"` — must be inserted at the correct position to maintain existing list ordering convention.
- **No breaking changes**: the additive nature of the change leaves all existing imports and tests untouched.
