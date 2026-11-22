# PLAY-189 — High-Level Design: add qa/s7_greeting.txt

## 1. System Overview

- **What:** one new static text file, `qa/s7_greeting.txt`, in `roeeoz/play1`, whose content is the single line `hello again from s7`.
- **Problem:** QA needs a minimal, verifiable change to exercise the factory's go-back flow (spec §1).
- **Responsibility:** the file exists, holds exactly that line, and nothing else in the product tree changes (spec FR1–FR3).
- **Content change:** the developer's change request on the plan replaces the spec's line `hello from s7` (spec FR2, AC2) with `hello again from s7`; everything else in the spec stands. This design and the work item follow the change request.

## 2. Architecture Overview

- No runtime component, service or code path is involved. The change is data-only.
- `qa/` exists at the repo root on `main` (verified with `git ls-tree origin/main qa/`): `qa/20261109-s1/`, `qa/20261110-s3/`, `qa/s3-a.sh`, `qa/s3-hello.sh`. `qa/s7_greeting.txt` does not exist on `main` or on the work branch — the code agrees with the spec.
- Ownership: the single work item owns `qa/s7_greeting.txt`. The plan folder `stories/PLAY-189/` is written by the factory, not by the work item.
- No external dependencies.

## 3. Data Flow Design

- None at runtime. The file is committed on the work branch `halo/feat/play-189-20261122-205349`, pushed by the platform, and reviewed/merged into `main` by a person.

## 4. Component Breakdown

| Component | Responsibility | Inputs / Outputs | Repository |
|---|---|---|---|
| `qa/s7_greeting.txt` | Static QA marker file | — / the line `hello again from s7` | `roeeoz/play1` |

## 5. Interface Contracts

- **File contract:** path `qa/s7_greeting.txt` (relative to repo root); UTF-8/ASCII bytes exactly `hello again from s7` followed by a single LF (`\n`) — 20 bytes, one line. No BOM, no CR, no leading/trailing spaces, no blank lines, no executable bit (mode `100644`).
- No APIs, events or cross-repo contracts. `roeeoz/play2` is not touched.

## 6. Key Technical Decisions

- **Trailing newline:** the file ends with exactly one `\n`. The spec leaves this to STRUCTURE (§8); a POSIX text line is newline-terminated, `wc -l` reports `1`, and git shows no "No newline at end of file" warning. Byte-exact check: `printf 'hello again from s7\n' | cmp - qa/s7_greeting.txt`.
- **No new test file.** The repo's pattern for QA *scripts* is a pytest module per script (`tests/test_qa_s3_greeting.py`, `tests/test_qa_20261109_s1_a.py`), but FR3 / AC3 forbid changing any product file other than `qa/s7_greeting.txt`. A test module would violate the approved scope, so verification is the byte-exact check above in the PR, and the existing `pytest` gate must stay green unchanged.
- **Alternatives considered:** adding `tests/test_qa_s7_greeting.py` (rejected: breaks AC3); no trailing newline (rejected: non-POSIX line, noisy diff, either accepted by spec but LF is the convention).

## 7. Risks & Constraints

- **Gates** (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`): rule 1 (Python under `src/`, tests under `tests/`) — not applicable; rule 2 (new shell scripts executable + shebang) — not a shell script, so the file must NOT be given a shebang or exec bit; rule 3 (≤ 200 KB) — 20 bytes. All pass.
- **Test gate** (`.factory/testing.md`, `.github/workflows/ci.yml`): `pip install -e ".[test]" && pytest` on Python 3.12; nothing imports or enumerates `qa/*.txt` (grep over `tests/`, `src/`), so the suite is unaffected. The `gate` job fails only if a root `CI_FAIL` file exists — the change must not create one.
- **`.gitignore`:** ignores `pip-log.txt` and `pip-delete-this-directory.txt` only; `qa/s7_greeting.txt` is not ignored.
- **Scope risk:** the only other paths on the PR are `stories/PLAY-189/` (factory plan folder, allowed by the developer per spec §8 Q2).
- Scale, performance and security: not applicable (static 20-byte file, no secrets).
