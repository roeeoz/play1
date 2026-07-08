# pdlc-testbed

Fixture repo for **deterministic coding-phase testing of the Demerzel agent**
(per `pdlc-infra/docs/plans/coding-phase-testing-plan.md`, option O6). It gives
the agent real branch/PR/push targets, real GitHub Actions CI classification,
and a deterministic fix loop — realism without flakiness.

Dedicated on purpose: deterministic CI must not fight other users of a shared
demo repo.

## What's in here

- `src/testbed_utils/` — a tiny, real Python package (text + date helpers),
  deliberately simple and genuinely extendable. Canned tasks target it.
- `tests/` — a small passing pytest suite.
- `.github/workflows/ci.yml` — two jobs, total runtime well under a minute:
  - **test** — installs the package and runs pytest.
  - **gate** — **fails if and only if a file named `CI_FAIL` exists at the
    repo root** ("CI_FAIL marker present — remove it to make CI green");
    green when it is absent.

That gate is what makes the fix loop deterministic: seed a ticket that
instructs creating `CI_FAIL` → CI genuinely red → the real poller classifies
`ci_failed` with real check output → fix-pr (reason says remove it) → CI
green → merge. Real branch/PR/push, real classification, the full
retro-attributed score shape.

## Local development

```bash
pip install -e ".[test]"   # or: uv pip install -e ".[test]"
pytest
```

## Canned tasks

Seed via `stepctl` (plan §O3) against a dev stack with `DEMERZEL_DEV_ENDPOINTS`
enabled. API base defaults to `http://localhost:30080/api`.

### Task A — deterministic fix loop (the CI_FAIL gimmick)

A T2 task whose implementation makes CI genuinely red, so the real fix loop
runs against a real, coherent failure (plan §7, Recipe 1).

```bash
stepctl seed --state structured --repo pdlc-testbed --items 1 --tier T2 \
  --title "Add a CI_FAIL marker file at the repository root. Create an empty file named exactly CI_FAIL (no extension) at the repo root and commit it. Do not modify any other files."
stepctl implement <wid>          # real coding pod → real branch + PR; gate job goes red
# real poll classifies ci_failed ("CI_FAIL marker present — remove it to make CI green")
# → fix-pr removes CI_FAIL → gate green → merge
stepctl inspect <fid> --langfuse
```

Alternatively, drive the fix step directly against an already-red PR
(a branch containing `CI_FAIL`), per Recipe 1:

```bash
stepctl seed --state in_review --repo pdlc-testbed --pr <testbed PR url> --suppress-poll
stepctl implement <wid>          # parks in awaitMerge (no pod — idempotent resume)
stepctl fix <wid> --event ci_failed --summary "gate failed: CI_FAIL present" --detail-file ci.txt
stepctl inspect <fid> --langfuse # fix-pr.turns / ci_passed / fix_addressed on the trace
stepctl merge <wid>              # → implement.final.* + postmortem on the session
```

### Task B — small real feature (function + tests)

A well-specified T2 feature against the package (plan §7, Recipe 3): a real
implement step producing a real branch and PR that should pass CI first try.

```bash
stepctl seed --state structured --repo pdlc-testbed --items 1 --tier T2 \
  --title "Add ordinal(n: int) -> str to src/testbed_utils/textutils.py returning the ordinal string for a non-negative integer: 1 -> '1st', 2 -> '2nd', 3 -> '3rd', 4 -> '4th', 11 -> '11th', 12 -> '12th', 13 -> '13th', 21 -> '21st', 101 -> '101st'. Raise ValueError for negative input. Export it from testbed_utils/__init__.py and add pytest tests in tests/test_textutils.py covering the 1/2/3 suffixes, the 11-13 exceptions, a large number, and the negative-input error."
stepctl implement <wid>          # real coding pod → real branch + PR on the testbed
stepctl inspect <fid> --langfuse
```

## Caveat — what CI_FAIL runs do and do not prove

Per plan §O6: the `CI_FAIL` gimmick tests **CI classification and loop
mechanics, not fix quality**. A one-file-delete fix is trivially "addressed" —
do **not** read `fix_addressed` (or other judge) values from testbed CI_FAIL
runs as evidence about the judge or about real-world fix quality.
