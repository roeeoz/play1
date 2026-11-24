# SCRUM-121 — High-Level Design: `marker()` helper that reads `QA_S4_MARKER`

## 1. System Overview
- **What:** a new module `src/testbed_utils/s4_marker.py` with a public function `marker()` that returns the process environment's `QA_S4_MARKER` value verbatim, or `""` when it is unset. It is re-exported from the `testbed_utils` package root. A new pytest file `tests/test_s4_marker.py` covers it.
- **Problem:** whoever runs the factory QA check needs proof that the project's environment variables reach the factory run, without inspecting it by eye. The new test asserts it, but only when the run is a factory run.
- **Responsibilities:**
  - `marker()` reads the value; it never sets, prints or logs it.
  - The test checks `marker()` against values it sets itself (environment-independent), and, in a factory run only, checks that the real `QA_S4_MARKER` is non-empty.

## 2. Architecture Overview
- **Components:**
  - `src/testbed_utils/s4_marker.py` (new) — the helper, following the one-small-module-per-concern pattern of `src/testbed_utils/hello.py`.
  - `src/testbed_utils/__init__.py` (edit) — one import line and `"marker"` added to `__all__`, kept alphabetical like the existing list (`__init__.py:8-26`).
  - `tests/test_s4_marker.py` (new) — the pytest file, following `tests/test_hello.py` (class-grouped tests, import through the installed package, a root-export check).
- **Boundary:** nothing else changes — not the other `testbed_utils` modules, `src/guestbook/`, the existing tests (including the pre-existing failing `tests/test_qa_20261122_s4_base.py`), `qa/`, `pyproject.toml` or `.github/workflows/ci.yml`.
- **Ownership:** one ticket (t1) owns all three files.
- **External dependencies:** Python standard library (`os`) for the helper; `pytest>=8` (already the `test` extra in `pyproject.toml`) for the test, using its built-in `monkeypatch` fixture and `pytest.skip` / `pytest.fail`. No new dependency.

## 3. Data Flow Design
1. A caller invokes `marker()`; it reads `QA_S4_MARKER` from the process environment **at call time** (no module-level caching, so a value changed by `monkeypatch` is seen) and returns it unchanged, or `""` if absent.
2. Unit tests set or delete `QA_S4_MARKER` with `monkeypatch`, call `marker()` and compare. `monkeypatch` restores the real environment after each test, so the factory check below still sees the run's real value.
3. The factory check reads `HALO_PROJECT_ENV_NAMES`, splits it on `,`, strips whitespace from each item and looks for an exact, case-sensitive `QA_S4_MARKER` item.
   - Not found (variable unset, empty, or name absent) → `pytest.skip` with a reason saying the run is not a factory run.
   - Found → the real `marker()` value must be non-empty; otherwise the test fails with a fixed message saying `QA_S4_MARKER` is not set in the run's environment.

Everything is synchronous and in-process. No state is persisted; no events.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repo |
|---|---|---|---|
| `src/testbed_utils/s4_marker.py` | Read `QA_S4_MARKER` | In: process environment. Out: `str` — the value verbatim, `""` when unset or set to empty. Never raises for a missing variable. | roeeoz/play1 |
| `src/testbed_utils/__init__.py` | Public package surface | Adds `marker` to the root imports and `__all__` | roeeoz/play1 |
| `tests/test_s4_marker.py` | Prove FR1–FR9 | In: values the tests set via `monkeypatch`; in the factory check, the real `HALO_PROJECT_ENV_NAMES` and `QA_S4_MARKER`. Out: pass / fail / skip with reason. Never outputs the marker value. | roeeoz/play1 |

## 5. Interface Contracts
- **Python API:** `from testbed_utils import marker` and `from testbed_utils.s4_marker import marker` both resolve to the same function; `"marker" in testbed_utils.__all__`. `marker()` takes no arguments and returns `str`.
- **Value semantics (settled):**
  - unset → `""`; set to `""` → `""`;
  - any other value is returned byte-for-byte as Python's `os.environ` exposes it — leading/trailing spaces, a whitespace-only value, `=` and non-ASCII characters are all preserved (no trimming, no normalisation).
- **Factory-run detection contract (`HALO_PROJECT_ENV_NAMES`):** comma-separated list; each item is stripped of surrounding whitespace; match is exact and case-sensitive. Verified with Python 3.12: `""` → not factory; `","` → not factory; `"A, QA_S4_MARKER"` → factory; `"qa_s4_marker"` → not factory; `"QA_S4_MARKER_X"` → not factory; `"QA_S4_MARKER"` → factory.
- **Factory check verdict:** a factory run passes when `QA_S4_MARKER` is non-empty — a whitespace-only value counts as non-empty (consistent with FR1's no-trimming rule; only `""` counts as "not set", per FR6/Q2).
- **Secret-safety contract:** neither the skip reason, the failure message, nor any `print`/log in the test contains the value of `QA_S4_MARKER` (or of `HALO_PROJECT_ENV_NAMES`). The failure is raised with a fixed message, not a bare `assert` comparing the real value, so pytest's assertion introspection cannot echo it.
- No cross-repo contracts.

## 6. Key Technical Decisions
- **Read at call time, not import time** — required so `monkeypatch` tests work and the factory check sees the real value. Alternative (module constant) rejected.
- **Factory gate inside the test body (`pytest.skip`) rather than a module-level `skipif`** — either meets FR7; the coding agent may choose, provided detection is evaluated against the environment at test run time and the skip reason names the not-a-factory-run condition without values.
- **Unit tests use `monkeypatch.setenv` / `monkeypatch.delenv(raising=False)`** — makes FR1/FR2/FR3 independent of the host environment (FR4), and restores the real factory value for the factory check regardless of test order.
- **No `conftest.py`, no `sys.path` edits** — `.factory/testing.md` relies on tests importing only through the installed `src/` package.
- **No CI change** — in GitHub Actions `HALO_PROJECT_ENV_NAMES` is unset, so the factory check skips.

## 7. Risks & Constraints
- **Pre-existing red suite:** `tests/test_qa_20261122_s4_base.py` fails on the base branch `qa-20261122-s4-base` (`assert 1 == 2`), so `pytest` overall — and the CI `test` job — stays red for reasons outside this story. Done means: the new tests pass (or the factory check skips outside the factory) and the only failing test is that pre-existing one. Fixing it is out of scope per the spec.
- **Secret exposure:** the marker value could leak through pytest introspection, `-l/--showlocals`, or a skip reason; mitigated by the fixed-message contract in §5. The repo's `addopts` is just `-q`.
- **Factory env drift:** if the factory stops listing `QA_S4_MARKER` in `HALO_PROJECT_ENV_NAMES`, the factory check silently skips. Accepted: that is the spec's detection rule.
- **Repo gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`):** Python under `src/`, tests under `tests/`, files < 200 KB, no new shell script — all met.
- **Scale/performance:** none (one env lookup).
- **Versions:** `requires-python >=3.10`; only `os.environ` and pytest ≥ 8 APIs that exist across that range are used. CI runs 3.12.

## 8. Assumptions
- **Q4 (spec, non-blocking):** whitespace around names in `HALO_PROJECT_ENV_NAMES` is ignored and matching is case-sensitive, as the spec's working assumption states. Risk if wrong: a factory run with an unusual separator format would skip instead of checking; low, since this turn's environment has `HALO_PROJECT_ENV_NAMES=QA_S4_MARKER` and a non-empty `QA_S4_MARKER` (value not inspected).
- **Whitespace-only marker value counts as set** (derived from FR1 + FR6, which only treat `""` as unset). Risk if wrong: a whitespace-only value would pass the factory check; it can be tightened later without changing `marker()`.
- The Epic PRD and backlog were not in this turn's context (as the spec notes); the design rests on the spec and the repository only.
