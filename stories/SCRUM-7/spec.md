# Ticket draft: SCRUM-7, monthly expense report from a CSV ledger (intake in progress)

**Status:** NOT_READY. One blocking question is open: the CHANGELOG gate against the out-of-scope clause.

## User story (unchanged)
As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

## Context: proposed change, pending the answer to Q1
The text below is the original Context. The bracketed part is option (a), which is added only if you choose it:

> The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository **[(a) only: except one line per pull request under `## Unreleased` in `CHANGELOG.md`, as the repository's gate requires]**.

## Open questions
- **Q1 (P0):** Option (a), the CHANGELOG exception above, or option (b), keep the clause and change rule 4 in the repository first? I recommend (a).

## Working assumptions (from the story's wording)
- The `expected N fields, got M` reason uses the header's actual field count as N. With the six named columns that gives `expected 6 fields, got 5`, as scenario 5 states.
- For the usage errors in scenario 22, argparse's standard usage message on stderr meets "a message on stderr".

## Acceptance criteria
Scenarios 1–25 from the story, work items t1, t2 and t3, carry over word for word. None changes under either option.

## Repository facts checked
- `pyproject.toml` discovers packages under `src/` and sets `testpaths = ["tests"]`.
- CI runs `pip install -e ".[test]"` then `pytest` on Python 3.12.
- The repository has no `src/ledger/`, no `tests/test_ledger_*.py` and no `tests/fixtures/ledger/`.
- `CHANGELOG.md` exists with `## Unreleased`.
- Repo-gate rule 4 raises the blocker `PLAY-G4` on any pull request whose diff doesn't touch `CHANGELOG.md`.
