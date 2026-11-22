# HLD — PLAY-191: add qa/s7_stop.txt

## 1. System Overview

- **What:** one new static text file, `qa/s7_stop.txt`, holding the single line `stop and retry`.
- **Why:** a small, predictable deliverable on which QA exercises the factory's stop / retry controls; after a stopped-and-retried run the reviewer can see at a glance that exactly this one file was delivered.
- **Responsibility:** none at runtime. Nothing reads, imports or tests the file.

## 2. Architecture Overview

- **Location:** `qa/` already exists at the repo root and holds only QA fixture shell scripts (`qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/hello.sh`, `qa/20261110-s3/test_hello.sh`). There is no `.txt` there yet; the new file sits beside them and changes none of them.
- **No code boundary is touched:** the Python package (`src/`, setuptools `src/` layout per `pyproject.toml`), the tests (`tests/`), CI (`.github/workflows/ci.yml`) and `.factory/` stay as they are.
- **Git:** `git check-ignore qa/s7_stop.txt` matches no `.gitignore` rule, so the file is committed normally.
- **External dependencies:** none.

## 3. Data Flow Design

- No runtime flow. The only flow is delivery: the implementing agent creates the file on the work branch `halo/feat/play-191-20261122-205349` (cut from `main`), the platform pushes it and opens the PR against `main`, a person reviews and merges.
- Stop / retry: if the run is stopped and retried, the retry writes the same full file content again (an overwrite, never an append), so the delivered file is identical whichever attempt finishes.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `qa/s7_stop.txt` | QA fixture for the stop / retry check | In: none. Out: the 15-byte file `stop and retry` + LF | `roeeoz/play1` |

## 5. Interface Contracts

- **File contract:** path `qa/s7_stop.txt` relative to the repo root; content is exactly the bytes `stop and retry\n` (15 bytes: lowercase, single spaces, no quotes, no leading/trailing whitespace, no BOM, one LF line ending, no CR, nothing after the LF). `wc -l` gives 1; `cat` prints `stop and retry`.
- **No API, event or cross-repo contract.**

## 6. Key Technical Decisions

- **One work item, one file.** The change is atomic; splitting it is impossible and adding tests is a spec Non-Goal.
- **Trailing LF:** follow the spec's working assumption (FR3) — a single LF terminator, the POSIX text-file convention, so `git diff` shows no "No newline at end of file" marker.
- **No automated test:** the spec excludes new tests; `pytest` collects only `tests/` (`[tool.pytest.ini_options] testpaths = ["tests"]` in `pyproject.toml`), so the `.txt` never reaches the suite. Verification is a byte check of the file plus the existing gates.

## 7. Risks & Constraints

- **Gates (all pass by construction):** `repo-gate` (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`) — no Python, no shell script, file far below 200 KB; `test` job in `.github/workflows/ci.yml` (`pip install -e ".[test]"` + `pytest`) — untouched; `gate` job — no `CI_FAIL` at the root, and this story must not create one.
- **Scope risk:** any other file in the diff (besides the factory's `stories/PLAY-191/` folder) breaks acceptance criterion 3.
- **Retry risk:** a retry that appends instead of overwrites would duplicate the line; the work item requires the exact final bytes.
- **Byte-for-byte risk:** if QA compares against `stop and retry` without LF, the check fails by one byte (see Assumptions).
- **Scale / performance / security:** not applicable — a 15-byte static file with no secret content.

## 8. Assumptions

- **A1 — trailing LF (from spec §8, non-blocking):** the file ends with exactly one LF. Risk if wrong: a byte-for-byte comparison without the LF fails; the fix is removing one byte.
