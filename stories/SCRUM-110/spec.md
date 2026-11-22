# Feature Specification — SCRUM-110: farewell greeting in greetlib (play2) and a matching qa script in play1

> Status: READY_FOR_SPEC. The developer answered all intake questions on 2026-11-22: the play1 files move to `src/` and `tests/` (criterion 2 reworded), play1's `farewell` handles blank names like greetlib's, and greetlib's `__init__.py` stays unchanged.

## 1. Feature Overview

- **What is being built:** a `farewell` greeting in two repositories. In `roeeoz/play2`, the `greetlib` library gets `farewell(name: str = "world") -> str`, which returns `"goodbye, <name>"` the same way `greet` returns `"hello, <name>"` (`src/greetlib/greet.py:5-8`), plus a pytest test. In `roeeoz/play1`, a standalone module `src/testbed_utils/s3_greeting.py` defines `FAREWELL_FORMAT = "goodbye, {name}"` and a `farewell(name)` that produces the same text without importing greetlib, plus a pytest test `tests/test_s3_greeting.py`.
- **Problem:** this is a factory QA story (`QA-20261122-S3`) that checks that one story can deliver a small, coordinated change in two target repositories, with each repository staying testable on its own.
- **Target users:** the factory QA team, who run the story and review the two pull requests, and Python callers of `greetlib`.

## 2. Goals & Non-Goals

### Goals

- play2: `greetlib` offers `farewell`, which behaves like `greet` (the name is stripped, and an empty or blank name becomes `"world"`), and a pytest test covers it.
- play1: a standalone `farewell(name)` in `src/testbed_utils/s3_greeting.py` produces the same text as greetlib's `farewell` (including the strip and blank-name rule), built from `FAREWELL_FORMAT`. It is covered by `tests/test_s3_greeting.py`, and play1 does not depend on greetlib.
- Each change stays tiny. play2 changes exactly `src/greetlib/greet.py` plus one new test file under `tests/`. play1 only adds the two new files and edits no existing file.

### Non-Goals

- No `farewell` console command or CLI flag in either repository. The story asks for none, so the existing `greet` entry point and the play1 scripts stay as they are.
- No change to `greet`, to its CLI, or to any existing test.
- No dependency from play1 on greetlib, and no shared package between the two repositories.
- No re-export of `farewell` from `src/greetlib/__init__.py`: callers import it from `greetlib.greet`.
- No `qa/` directory files for this story, and no changes to CI, packaging (`pyproject.toml`), the repository gate rules or any existing play1 file (including `src/testbed_utils/__init__.py`).

## 3. Functional Requirements

- **FR1 (play2):** `farewell(name: str = "world") -> str` in `src/greetlib/greet.py` returns `"goodbye, " + name.strip()`. When the stripped name is empty, it returns `"goodbye, world"`.
  - `farewell()` → `"goodbye, world"`
  - `farewell("Ada")` → `"goodbye, Ada"`
  - `farewell("  ")` → `"goodbye, world"`
  - `farewell("  Ada  ")` → `"goodbye, Ada"`. This value is derived from "strip the name" in the story.
- **FR2 (play2):** a pytest test under `tests/` covers at least `farewell("Ada")` and `farewell("  ")`. CI's `pytest` collects it (`testpaths = ["tests"]`).
- **FR3 (play1):** a new standalone module `src/testbed_utils/s3_greeting.py` defines `FAREWELL_FORMAT = "goodbye, {name}"` and `farewell(name)`, which returns the same text as greetlib's `farewell` for the same input. The module does not import greetlib.
  - `farewell("Ada")` → `"goodbye, Ada"`
  - `farewell("  ")` → `"goodbye, world"` (the name is stripped, and a blank name becomes `"world"`, as the developer confirmed)
- **FR4 (play1):** a new pytest test `tests/test_s3_greeting.py` covers at least `farewell("Ada") == "goodbye, Ada"` and `farewell("  ") == "goodbye, world"`. CI's `pytest` collects it (`testpaths = ["tests"]`). Its name is distinct from the existing `tests/test_qa_s3_greeting.py` (which tests `qa/s3-hello.sh`), and that file stays untouched.
- **FR5 (play1):** the change only adds files. `src/testbed_utils/__init__.py` already exists, so no `__init__.py` is added or edited.

## 4. User Experience & Behavior

- Developer flow (play2): `from greetlib.greet import farewell` and then `farewell("Ada")` returns `"goodbye, Ada"`. `from greetlib import farewell` is not offered, because `src/greetlib/__init__.py` stays unchanged.
- Developer flow (play1): `from testbed_utils.s3_greeting import farewell, FAREWELL_FORMAT`. With only play1 installed (`pip install -e ".[test]" && pytest`), the farewell test runs and passes, and greetlib is not installed.
- Output format: lowercase `goodbye`, then a comma, one space and the name, with no trailing newline or punctuation. This matches `greet`'s `"hello, <name>"`.
- There is no UI, visual style, sound or CLI output in scope.

## 5. Acceptance Criteria

1. In play2, `farewell("Ada")` returns `"goodbye, Ada"` and `farewell("  ")` returns `"goodbye, world"`; covered by a pytest test.
2. In play1, `src/testbed_utils/s3_greeting.py` exists and defines `FAREWELL_FORMAT = "goodbye, {name}"`; its `farewell("Ada")` returns `"goodbye, Ada"` and `farewell("  ")` returns `"goodbye, world"`, without importing greetlib; covered by `tests/test_s3_greeting.py`.
3. No other files change in either repository: play2 changes only `src/greetlib/greet.py` plus one new test file under `tests/`, and play1 only adds the two new files above without editing any existing file.

## 6. Dependencies & Constraints (product-level)

- **play1 gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`), rule 1:** "Python source lives under `src/`; tests live under `tests/`." The gate runs on every pull request and reads neither this ticket nor its answers. The agreed paths `src/testbed_utils/s3_greeting.py` and `tests/test_s3_greeting.py` satisfy it.
- **play1 test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** CI runs `pytest`, and `pyproject.toml` sets `testpaths = ["tests"]`, so `tests/test_s3_greeting.py` is collected.
- **play2 test gate:** the same setup (`pytest`, `testpaths = ["tests"]`). A new test under `tests/` is collected. play2 has no layout gate plugin.
- The two pull requests are independent: play1 must not import greetlib, so neither repository depends on the other. A person merges each one after review.

## 7. Technical Design (deferred to STRUCTURE)

How the play1 test imports the standalone module (package placement and import path), and whether play1's `farewell` formats through `FAREWELL_FORMAT.format(...)`, are left to STRUCTURE. The product constraint is fixed: the module lives inside the existing `testbed_utils` package, and the test imports it without greetlib.

## 8. Open Questions

Resolved by the developer on 2026-11-22:

- **Q1 (play1 location):** option (a). The module is `src/testbed_utils/s3_greeting.py` and the test is `tests/test_s3_greeting.py`; criterion 2 is reworded to match. Only new files in play1.
- **Q2 (play1 blank names):** yes. play1's `farewell` strips the name and a blank name becomes `"world"`, with a test for `farewell("  ")`.
- **Q3 (greetlib re-export):** no. `src/greetlib/__init__.py` stays unchanged; callers import from `greetlib.greet`.

Still open (no product decision needed):

- The epic PRD, backlog and Confluence research mentioned in the request were not present in this intake's context. Only the story text and the two repositories were read.
