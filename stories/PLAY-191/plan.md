# Plan — PLAY-191: add qa/s7_stop.txt

## Context

PLAY-191 adds one static QA fixture file, `qa/s7_stop.txt`, holding the single line `stop and retry`, so QA can exercise the factory's stop / retry controls against a trivially checkable deliverable. Acceptance criteria: (1) the file exists in `qa/` at the repository root; (2) it contains exactly one line, `stop and retry`; (3) the pull request changes no other file except the plan folder `stories/PLAY-191/`. The change lands in `roeeoz/play1` on work branch `halo/feat/play-191-20261122-205349`, cut from and merging into `main`. `spec.md`, `hld.md` and `work-items.md` sit beside this file in `stories/PLAY-191/`.

## Research findings

- **Change surface:** one new file, `qa/s7_stop.txt`. `qa/` exists and holds only shell fixtures: `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/a.sh`, `qa/20261110-s3/hello.sh`, `qa/20261110-s3/test_hello.sh`. No `.txt` file exists there; none of these files changes.
- **Git ignore:** `git check-ignore -v qa/s7_stop.txt` returns no match (exit 1), so the file is tracked normally.
- **Contracts touched:** none. Nothing in `src/`, `tests/` or CI reads `qa/`. The only contract is the file's bytes, fixed by `hld.md` §5: `stop and retry\n` (15 bytes, LF, no CR, no BOM).
- **Test collection:** `pyproject.toml:27-29` sets `[tool.pytest.ini_options] testpaths = ["tests"]`, so `pytest` never collects anything under `qa/`.
- **Canonical gate:** `.factory/testing.md:3-4` declares `test-gate: pytest` and `local-test-gate: pip install -q -e ".[test]" && pytest`; one required layer, `package-api` (production-path, `runBy: canonical-gate`). Provider CI is `.github/workflows/ci.yml`: job `test` (`pip install -e ".[test]"`, then `pytest`, Python 3.12) and job `gate` (fails iff `CI_FAIL` exists at the repo root). `CI_FAIL` does not exist today.
- **MR gate:** `.factory/plugins/claims-dev/skills/repo-gate/SKILL.md` rules PLAY-G1 (Python under `src/`, tests under `tests/`), PLAY-G2 (new shell script executable with shebang), PLAY-G3 (no file over 200 KB). A 15-byte `.txt` triggers none.
- **Repo memory:** no `.factory/memory/` directory; no `AGENTS.md` or `CLAUDE.md`.
- **External data:** none.
- **Remaining unknowns:** whether QA compares bytes with or without the trailing LF (spec §8, non-blocking; resolved by assumption A1).

## Locked decisions and assumptions

**Locked decisions**

- Path is `qa/s7_stop.txt` relative to the repo root — spec FR1, AC 1.
- Content is the single line `stop and retry`: lowercase, single spaces, no quotes, no surrounding whitespace, no extra or blank lines — spec FR2, AC 2.
- No other repository file changes; only `stories/PLAY-191/` is exempt — spec FR4, AC 3.
- No new automated test — spec Non-Goals, `hld.md` §6, work item `t1`.
- A retry writes the whole file (overwrite, never append) — `hld.md` §3, work item `t1`.
- Target branch is `main` — platform.

**Assumptions**

- **A1 — trailing LF.** The file ends with exactly one LF (15 bytes). Evidence: spec FR3 and §8, `hld.md` §6, work item `t1` AC. If wrong: a byte-for-byte check against `stop and retry` without LF fails by one byte; the fix is dropping the LF.

## Solution proposal

Create `qa/s7_stop.txt` as a plain static file whose entire content is `stop and retry` followed by one LF, written whole (for example `printf 'stop and retry\n' > qa/s7_stop.txt`), so a stopped-and-retried run produces identical bytes. No code, configuration, test or CI change: nothing consumes the file and the existing gates already pass with it present.

Alternatives rejected:
- **Adding a pytest check of the file's content** — explicitly a spec Non-Goal, and it would widen the diff beyond AC 3.
- **No trailing LF** — contradicts the spec's working assumption FR3 and leaves a "No newline at end of file" marker in the diff.
- **Appending with `echo >>`** — not idempotent under retry; would duplicate the line.

## Ordered implementation steps

1. **Create `qa/s7_stop.txt`** with exactly the bytes `stop and retry\n`, using an overwrite (`>`), never an append. Advances AC 1, AC 2. Test layer: none — no automated test by spec; verified by a byte check (step 2).
2. **Verify the file's bytes** before commit: `wc -c qa/s7_stop.txt` gives `15`, `wc -l` gives `1`, `cat` prints `stop and retry`, and `od -c` shows no `\r` and no BOM. Advances AC 2. Test layer: manual byte check (no existing layer covers non-code fixtures).
3. **Confirm scope:** `git status --porcelain` and `git diff --name-only main...HEAD` list only `qa/s7_stop.txt` (plus `stories/PLAY-191/`); no `CI_FAIL` at the repo root; `git ls-files qa/s7_stop.txt` shows it tracked after the commit. Advances AC 3. Test layer: existing `gate` job (CI_FAIL) and the `repo-gate` MR gate; the `package-api` layer (`pytest`) proves no regression.

Invariants: authorization/tenancy, concurrency and validation paths do not apply — no runtime code. Idempotency is covered by the overwrite in step 1. Dependencies: none new; the gate acquires its own via `pip install -e ".[test]"`. No generated deliverables; nothing for `.factory/delivery-assets`.

## Work-item mapping

| Step | Work item | Title |
|---|---|---|
| 1 | `t1` | Add qa/s7_stop.txt with the single line 'stop and retry' |
| 2 | `t1` | Add qa/s7_stop.txt with the single line 'stop and retry' |
| 3 | `t1` | Add qa/s7_stop.txt with the single line 'stop and retry' |

## Verification and CI gate

- **Canonical gate, in order:** `pip install -e ".[test]"` then `pytest` (job `test`, Python 3.12), plus job `gate` (no `CI_FAIL` at root), both in `.github/workflows/ci.yml`, run by provider CI on the pull request at the exact head.
- **Local run:** the one local run is the gate's own, `run-tests-gate.sh --run` on the committed SHA, which runs `local-test-gate:` from `.factory/testing.md` (`pip install -q -e ".[test]" && pytest`). Do not also run the command by hand.
- **Required layers:** `package-api` (`pytest`), runnable in a pod; it is unaffected by the change and must stay green.
- **Provider CI configuration:** no change needed.
- **`.factory/testing.md` / `.factory/delivery-assets`:** no obligation — no new layer, no binary asset.
- **Done means:** `test` and `gate` jobs green at the head; `repo-gate` passes with no findings; the diff contains only `qa/s7_stop.txt` (plus `stories/PLAY-191/`); the file is exactly 15 bytes, `stop and retry` + LF.

## Risks and scope guards

**Risks**

- Byte mismatch if QA expects no trailing LF — mitigated by assumption A1 stated in spec and HLD; a one-byte fix if needed.
- Duplicate line after retry — mitigated by writing the file whole (overwrite).
- Editor or platform adding CRLF or a BOM — mitigated by the `od -c` check in step 2.

**Scope guards — the implement phase must NOT:**

- Touch any existing file: `qa/s3-a.sh`, `qa/s3-hello.sh`, `qa/20261109-s1/`, `qa/20261110-s3/`, `src/`, `tests/`, `.github/workflows/ci.yml`, `.factory/`, `pyproject.toml`, `README.md`, `.gitignore`.
- Add a test, a CHANGELOG entry, documentation or any reference to the new file.
- Create `CI_FAIL` or any other file.
- Edit `spec.md`, `hld.md` or `work-items.md`.
- Make any check green by deleting, skipping, disabling or weakening it; a failing check is reported as blocked.

## Clarification outcomes

None.
