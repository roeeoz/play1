# Ticket draft: SCRUM-7, monthly expense report from a CSV ledger (intake in progress)

**Status:** NOT_READY. One blocking question is open: Q1, the CHANGELOG gate against the out-of-scope clause.

The developer has told me five times to take the simplest reading where the story is silent. That settled A1–A5. It cannot settle Q1, because there the story's text and the repository's gate require opposite things, so there is no gap to fill.

## User story (unchanged)
As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

## Context: proposed change, pending the answer to Q1
The text below is the original Context. The bracketed part is added only if option (a) is chosen.

> The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository **[(a) only: except one line per pull request under `## Unreleased` in `CHANGELOG.md`, as the repository's gate requires]**.

## Open questions
- **Q1 (P0):** Which option?
  - **(a)** Add the CHANGELOG exception shown above.
  - **(b)** Keep the clause, change rule 4 in the repository first, and have this story wait for that change.

  I recommend (a): the story can ship now, and its only change to an existing file is the one line the gate requires anyway. Choose (b) only if leaving every existing file untouched is a goal in itself.

## Assumptions (simplest reading, per the developer's instruction)
- **A1, field-count reason:** in `expected N fields, got M`, N is the header's actual field count. With the six named columns this gives `expected 6 fields, got 5`, as scenario 5 states.
- **A2, usage errors:** for the usage errors in scenario 22, argparse's standard usage message on stderr counts as "a message on stderr". Only the exit code 2 and the empty stdout are checked.
- **A3, value-quoting reasons:** reasons about values follow the story's examples and quote the offending value (`date '…'`, `amount '…'`, `unknown currency '…'`). `empty id` and `empty category` are exactly as given.
- **A4, epic traces:** the traces R1–R5, steps 1–8 and RK1/RK2 are kept as the story states them. The epic documents were not available to check them against.
- **A5, the sample fixture:** the story's scenarios define the content of the sample fixture: nine rows, ids `t001`…`t009`, with the dates and totals given in scenarios 1, 9, 10, 16 and 20. The fixture is built to reproduce exactly those figures.

## Acceptance criteria
Scenarios 1–25 from the story, in work items t1, t2 and t3, carry over word for word. None of them changes under either option for Q1.

## Repository facts checked
- `pyproject.toml` discovers packages under `src/`, sets `testpaths = ["tests"]` and requires Python >=3.10.
- CI runs `pip install -e ".[test]"` and then `pytest`, on Python 3.12.
- There is no `src/ledger/`, no `tests/test_ledger_*.py` and no `tests/fixtures/ledger/`.
- `CHANGELOG.md` exists and has a `## Unreleased` heading.
- Repo-gate rule 4 raises the blocker `PLAY-G4` on any pull request whose diff does not add a line under `## Unreleased` in `CHANGELOG.md`.
- I recomputed the figures in scenarios 9, 10, 11 and 20; they are internally consistent.
