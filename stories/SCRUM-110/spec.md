# Feature Specification — SCRUM-110: farewell greeting in greetlib (play2) and a matching qa script in play1

> Status: in-progress intake draft (NOT_READY). One blocking question is open; see §8.

## 1. Feature Overview

- **What is being built:** a `farewell` greeting in two repositories. In `roeeoz/play2`, the `greetlib` library gets `farewell(name: str = "world") -> str`, which returns `"goodbye, <name>"` the same way `greet` returns `"hello, <name>"` (`src/greetlib/greet.py:5-8`), plus a pytest test. In `roeeoz/play1`, a standalone Python file defines `FAREWELL_FORMAT = "goodbye, {name}"` and a `farewell(name)` that produces the same text without importing greetlib, plus a pytest test.
- **Problem:** this is a factory QA story (`QA-20261122-S3`) that checks that one story can deliver a small, coordinated change in two target repositories, with each repository staying testable on its own.
- **Target users:** the factory QA team, who run the story and review the two pull requests, and Python callers of `greetlib`.

## 2. Goals & Non-Goals

### Goals

- play2: `greetlib` offers `farewell`, which behaves like `greet` (the name is stripped, and an empty or blank name becomes `"world"`), and a pytest test covers it.
- play1: a standalone `farewell(name)` produces the same text as greetlib's `farewell`, built from `FAREWELL_FORMAT`. It is covered by a pytest test, and play1 does not depend on greetlib.
- Each change stays tiny, and no other files change in either repository.

### Non-Goals

- No `farewell` console command or CLI flag in either repository. The story asks for none, so the existing `greet` entry point and the play1 scripts stay as they are.
- No change to `greet`, to its CLI, or to any existing test.
- No dependency from play1 on greetlib, and no shared package between the two repositories.
- No changes to CI, packaging (`pyproject.toml`) or the repository gate rules, unless the person answers Q1 by choosing to change a rule first. That would be a separate change, not part of this story.

## 3. Functional Requirements

- **FR1 (play2):** `farewell(name: str = "world") -> str` in `src/greetlib/greet.py` returns `"goodbye, " + name.strip()`. When the stripped name is empty, it returns `"goodbye, world"`.
  - `farewell()` → `"goodbye, world"`
  - `farewell("Ada")` → `"goodbye, Ada"`
  - `farewell("  ")` → `"goodbye, world"`
  - `farewell("  Ada  ")` → `"goodbye, Ada"`. This value is derived from "strip the name" in the story.
- **FR2 (play2):** a pytest test under `tests/` covers at least `farewell("Ada")` and `farewell("  ")`. CI's `pytest` collects it (`testpaths = ["tests"]`).
- **FR3 (play1):** a standalone module defines `FAREWELL_FORMAT = "goodbye, {name}"` and `farewell(name)`, which returns the same text as greetlib's `farewell` for the same input. `farewell("Ada")` → `"goodbye, Ada"`. The module does not import greetlib. **Its location is blocked on Q1**, because the story's path `qa/s3_greeting.py` breaks play1's gate rule PLAY-G1.
- **FR4 (play1):** a pytest test covers `farewell("Ada") == "goodbye, Ada"`. **Its location is blocked on Q1**, because the story's path `qa/test_s3_greeting.py` breaks PLAY-G1, and play1's `pytest` (`testpaths = ["tests"]`) would never run it in CI.
- **FR5 (play1, working assumption, Q2):** "the same text as greetlib's farewell" includes the blank-name rule, so play1's `farewell("  ")` returns `"goodbye, world"`.

## 4. User Experience & Behavior

- Developer flow (play2): `from greetlib.greet import farewell` and then `farewell("Ada")` returns `"goodbye, Ada"`. Whether `from greetlib import farewell` also works is open (Q3), because `greet` is re-exported in `src/greetlib/__init__.py:2-4`.
- Developer flow (play1): with only play1 installed (`pip install -e ".[test]" && pytest`), the farewell test runs and passes, and greetlib is not installed.
- Output format: lowercase `goodbye`, then a comma, one space and the name, with no trailing newline or punctuation. This matches `greet`'s `"hello, <name>"`.
- There is no UI, visual style, sound or CLI output in scope.

## 5. Acceptance Criteria

1. In play2, `farewell("Ada")` returns `"goodbye, Ada"` and `farewell("  ")` returns `"goodbye, world"`; covered by a pytest test.
2. In play1, `qa/s3_greeting.py` exists, its `farewell("Ada")` returns `"goodbye, Ada"`, covered by `qa/test_s3_greeting.py`.
3. No other files change in either repository.

## 6. Dependencies & Constraints (product-level)

- **play1 gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`), rule 1:** "Python source lives under `src/`; tests live under `tests/`." The gate runs on every pull request and reads neither this ticket nor its answers. A new `qa/s3_greeting.py` and `qa/test_s3_greeting.py` would each be a PLAY-G1 blocker. **This is the open conflict in Q1.**
- **play1 test gate (`.factory/testing.md`, `.github/workflows/ci.yml`):** CI runs `pytest`, and `pyproject.toml` sets `testpaths = ["tests"]`. A test file under `qa/` is not collected, so CI would not prove criterion 2.
- **play2 test gate:** the same setup (`pytest`, `testpaths = ["tests"]`). A new test under `tests/` is collected. play2 has no layout gate plugin.
- The two pull requests are independent: play1 must not import greetlib, so neither repository depends on the other. A person merges each one after review.

## 7. Technical Design (deferred to STRUCTURE)

How the play1 test imports the standalone module (package placement and import path), and whether play1's `farewell` formats through `FAREWELL_FORMAT.format(...)`, are left to STRUCTURE once Q1 fixes the file locations.

## 8. Open Questions

- **Q1 (P0, blocking):** the play1 paths `qa/s3_greeting.py` and `qa/test_s3_greeting.py` break play1's layout gate rule PLAY-G1, which requires Python source under `src/` and tests under `tests/`. CI's `pytest` also only collects `tests/`. Options:
  - (a) Move the play1 files to `src/testbed_utils/s3_greeting.py` and `tests/test_s3_greeting.py`, and reword criterion 2 to match.
  - (b) First change play1's gate rule and its pytest `testpaths` in a separate change to allow `qa/`, then keep the story's paths.

  Recommendation: (a). It is the only option that passes the gate as the gate stands, and CI then runs the test. If the `qa/` location itself is what the QA scenario checks, (b) is the answer instead.
- **Q2 (P1):** should play1's `farewell` also strip the name and turn a blank name into `"world"`, and should its test cover `farewell("  ")`? Working assumption: yes, because "the same text as greetlib's farewell" implies it.
- **Q3 (P1):** should `farewell` be importable as `from greetlib import farewell`, the way `greet` is? That needs an edit to `src/greetlib/__init__.py`, which criterion 3 ("no other files change") seems to forbid. Working assumption: no. Only `greet.py` and one test file change, and callers import it from `greetlib.greet`.
- The epic PRD, backlog and Confluence research mentioned in the request were not present in this turn's context. Only the story text and the two repositories were read.
