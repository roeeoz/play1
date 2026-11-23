# HLD — SCRUM-112: add qa/gap-hello.txt

## 1. System Overview

- **What:** one new static text file, `qa/gap-hello.txt`, containing exactly `hello from gap\n` (15 bytes), on the work branch `halo/feat/scrum-112-20261123-053053`, cut from the frozen target branch `qa-20261122-s4-base`.
- **Why:** a factory QA story proving delivery onto a non-default base branch, and how the factory behaves when the base already carries a failing test (`tests/test_qa_20261122_s4_base.py`, `assert 1 == 2`, commit `ea6f718`).
- **Responsibility:** add the file; change nothing else in the repository.

## 2. Architecture Overview

- No runtime component, service, package or script. `qa/` today holds only shell scripts (`qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/hello.sh`, `qa/20261110-s3/test_hello.sh`); the new file sits beside them at the top level of `qa/` and touches none of them.
- Not a script, so the project's standing script rule (`--help`, stdout-only, exit 2 on unknown args) does not apply (spec §2 Non-Goals).
- No external dependencies. Nothing in `src/`, `tests/`, `pyproject.toml` or `.github/workflows/ci.yml` references or needs to reference the file.

## 3. Data Flow Design

- Static content only: a reviewer runs `cat qa/gap-hello.txt` and sees `hello from gap`. No sync/async processing, no events.
- Delivery flow: work branch → platform pushes → PR against `qa-20261122-s4-base` → CI `test` job (pytest) and `gate` job run → human reviews and merges.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `qa/gap-hello.txt` (new) | Hold the text `hello from gap` | In: none. Out: 15 bytes, `hello from gap` + one LF | `roeeoz/play1` |

## 5. Interface Contracts

- File contract: path `qa/gap-hello.txt`; bytes exactly `68 65 6c 6c 6f 20 66 72 6f 6d 20 67 61 70 0a` (`hello from gap\n`, 15 bytes) — lowercase, no quotes, no leading/trailing spaces, no BOM, LF (not CRLF), exactly one trailing newline, no extra blank line. Regular file, not executable (mode 100644).
- No APIs, events or cross-repo contracts.

## 6. Key Technical Decisions

- **One work item, one PR.** The change is a single file; splitting would be fragmentation.
- **No automated test.** The spec puts any test, script, package or CI change out of scope (§2 Non-Goals). Verification is by the byte check in the acceptance criteria (e.g. `wc -c` = 15, `cat` output), not a new test file.
- **Leave the failing base test alone.** Per Q1 (option c), `tests/test_qa_20261122_s4_base.py` is not fixed, skipped, or marked xfail; the PR's required `pytest` gate is expected to be red and that is the intended QA outcome. No gate exemption is sought.
- Alternatives rejected: fixing/xfail-ing the base test (explicitly out of scope); adding a pytest check for the file (out of scope, and would add a second changed file, breaking FR3).

## 7. Risks & Constraints

- **Required `pytest` gate is red by design.** `pytest` (`testpaths = ["tests"]` in `pyproject.toml`) collects `tests/test_qa_20261122_s4_base.py` and fails. Verified on the work branch: the only diff vs `origin/qa-20261122-s4-base` is the plan folder; the failing test comes from the base. The implementer must not "fix" this; the expected red is reported, not hidden.
- **CI `gate` job** stays green: the change adds no `CI_FAIL` file at the root.
- **Repo layout gate** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): PLAY-G1 (no Python added), PLAY-G2 (not a shell script), PLAY-G3 (15 B ≪ 200 KB) all pass.
- **Byte-exactness risk:** editors/tools that add CRLF, a BOM, or omit/double the final newline would break FR2. No `.gitattributes` exists in the repo, so git does no EOL conversion; the file must be written with a single LF.
- `.gitignore` does not ignore `qa/` or `*.txt` in general (only `pip-log.txt`, `pip-delete-this-directory.txt`), so the file is tracked normally.
- Scale/performance/security: not applicable — static 15-byte text, no secrets, no execution.

## 8. Assumptions

- **Plan folder in the diff.** This repo is also the artifacts repo, so the work branch carries the platform-committed plan folder `stories/SCRUM-112/` (spec, hld, work-items, plan). AC3 / FR3 ("no other file changes") is read as applying to the repository's code and content outside that platform-owned plan folder, matching the base branch, which already holds earlier stories' plan folders under `stories/`. Risk if wrong: a reviewer reading AC3 literally sees extra `stories/SCRUM-112/*` files in the PR; that is platform behaviour, not something this work item can or should change.
