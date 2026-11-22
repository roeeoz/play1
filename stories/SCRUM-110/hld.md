# HLD — SCRUM-110: farewell greeting in greetlib (play2) and a matching module in play1

## 1. System Overview

- **What:** a pure `farewell` function in two repositories that returns `"goodbye, <name>"`. The name is stripped first, and an empty or blank name becomes `world`.
  - play2: added beside `greet` in `src/greetlib/greet.py` (`greet` is at lines 5-8).
  - play1: a new standalone module `src/testbed_utils/s3_greeting.py` that defines `FAREWELL_FORMAT`.
- **Why:** factory QA story `QA-20261122-S3`. It shows that one story can deliver a coordinated change in two repositories, where each repository stays testable on its own.
- **Responsibilities:** play2 owns the library function. play1 owns an independent copy of the same behavior. The two repositories share no code.

## 2. Architecture Overview

- **play2 (`roeeoz/play2`):** `src/greetlib/greet.py` gets `farewell`, next to `greet`. Three things stay unchanged: `src/greetlib/__init__.py` (which exports only `greet`), `main`, and the `greet` console script in `pyproject.toml`. A new test file `tests/test_farewell.py` is added. The existing `tests/test_greet.py` is not touched.
- **play1 (`roeeoz/play1`):** a new leaf module `src/testbed_utils/s3_greeting.py` and a new test `tests/test_s3_greeting.py`.
  - `src/testbed_utils/__init__.py` is not edited, so the module is not re-exported from the package root. The test imports it as `testbed_utils.s3_greeting`.
  - The name is distinct from the existing `tests/test_qa_s3_greeting.py`, which tests `qa/s3-hello.sh` and stays untouched.
- **External dependencies:** none. Both modules use only the standard library, and play1 never imports `greetlib`.

## 3. Data Flow Design

- The call is synchronous and in-process: `name: str` → strip → fall back to `"world"` if empty → return the formatted string. There is no I/O, no state and no events.
- There is no runtime flow between the repositories. Their behavior is kept the same by matching tests in each repository, not by a shared import.

## 4. Component Breakdown

| Component | Responsibility | Input → Output | Repo |
|---|---|---|---|
| `greetlib.greet.farewell` | Library farewell, in the same style as `greet` | `str` (default `"world"`) → `str` | roeeoz/play2 |
| `tests/test_farewell.py` (play2) | Pytest coverage for FR1/FR2 | — | roeeoz/play2 |
| `testbed_utils.s3_greeting` (`FAREWELL_FORMAT`, `farewell`) | Standalone farewell, built from `FAREWELL_FORMAT` | `str` → `str` | roeeoz/play1 |
| `tests/test_s3_greeting.py` (play1) | Pytest coverage for FR3/FR4 | — | roeeoz/play1 |

## 5. Interface Contracts

The two implementations must behave the same on these inputs. I checked the values with Python 3, using `str.strip()` and `str.format`.

| Input | Output |
|---|---|
| no argument (play2; play1 too, see §6) | `"goodbye, world"` |
| `"Ada"` | `"goodbye, Ada"` |
| `"  "` or `""` | `"goodbye, world"` |
| `"  Ada  "` or `"\tAda\n"` | `"goodbye, Ada"` (`str.strip()` removes all leading and trailing whitespace) |
| `"{x}"` | `"goodbye, {x}"` (braces inside the name are not reinterpreted when it is substituted into `FAREWELL_FORMAT`) |
| a non-`str` value, e.g. `None` | No validation is added. The call fails the same way `greet` does today (`AttributeError` from `.strip()`); this is the same as `greet` and is not tested as a contract |

- The output is lowercase `goodbye`, then a comma, one space and the name, with no trailing newline or punctuation.
- play2 import path: `from greetlib.greet import farewell`. `from greetlib import farewell` is not offered.
- play1 import path: `from testbed_utils.s3_greeting import farewell, FAREWELL_FORMAT`, where `FAREWELL_FORMAT == "goodbye, {name}"`.
- There is no contract between the repositories.

## 6. Key Technical Decisions

- **play1 formats through `FAREWELL_FORMAT`.** The spec left this to STRUCTURE. Building the result from the constant makes the constant the real source of the text, not a value nobody uses. Substituting with `str.format` is safe for names that contain braces (§5).
- **play1 `farewell` defaults `name` to `"world"`.** The spec writes `farewell(name)`. A default keeps play1 the same as greetlib, including for a call with no argument, and costs nothing.
- **A new test file in play2 (`tests/test_farewell.py`)** rather than extending `tests/test_greet.py`. Spec AC3 allows "one new test file under `tests/`" and forbids changes to existing tests.
- **No re-export and no `__init__.py` edits** in either repository (spec Q3 and FR5). The cost is that callers use the submodule path.
- **Alternative rejected:** a shared package, or play1 importing greetlib. The spec forbids both, and either would couple the two independent PRs.

## 7. Risks & Constraints

- **play1 layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): source goes under `src/` and tests under `tests/`. Both new paths comply. No shell script is added, so rule 2 does not apply.
- **Test gates** (`.factory/testing.md` and `.github/workflows/ci.yml` in both repositories): CI runs `pip install -e ".[test]"` and then `pytest` on Python 3.12, with `testpaths = ["tests"]`.
  - There is no `conftest.py` and no `sys.path` setup, so tests import the installed `src/` package. Both new test files are collected without any configuration change.
  - The `gate` job only checks for a `CI_FAIL` file, which must not be added.
  - No linter or formatter is configured.
- **play1 package import side effect:** importing `testbed_utils.s3_greeting` runs `src/testbed_utils/__init__.py`, which imports `pdfutils` and so `pypdf`. `pypdf` is already a declared runtime dependency installed by the gate, so this is not a new risk.
- **Python version:** `requires-python >= 3.10`. Nothing used here varies by version.
- **Scale, performance and security:** not applicable. The functions are pure and constant-time, with no I/O and no secrets.

## 8. Assumptions

- The epic PRD, backlog and Confluence research mentioned in the story were not in the intake context, and this turn did not retrieve them. The design rests only on `spec.md` and the two repositories. Risk: low, because the spec is fully settled.
- play1's `farewell` has a default argument of `"world"` (§6). If reviewers want exactly `farewell(name)` with no default, only the signature changes, and no tested behavior in the spec is affected.
