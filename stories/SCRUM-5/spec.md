# Ticket draft: Monthly expense report from a CSV ledger (intake still open)

## Status
NOT READY. One P0 question is open: the story's scope (no changes to any existing file) conflicts with repository gate rule `PLAY-G4`, which requires every pull request to add a line under `## Unreleased` in `CHANGELOG.md`. The spec will be produced once the developer picks one of the two options below.

## Persona and intent
The user is a developer who keeps a personal or small-team ledger as a CSV file. They want a deterministic monthly summary from the terminal, with no spreadsheet: totals by category in one base currency, plus income, expense, net and the largest categories. When a row is bad, they want it pointed at by line number instead of getting a wrong total.

## Context, as the story states it (pending P0)
The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

If the developer picks option (a), the last sentence becomes: "...any third-party dependency, changes to any existing file of the repository other than adding one line under `## Unreleased` in `CHANGELOG.md` per pull request."

## Scope
- **In scope:**
  - New files only: `src/ledger/`, `tests/test_ledger_*.py` and `tests/fixtures/ledger/`.
  - The entry point is `python -m ledger report FILE --month YYYY-MM [--base ILS|USD|EUR] [--top N] [--json]`.
- **Out of scope:**
  - Other file formats, live exchange rates, persistent configuration and charts.
  - Any third-party dependency.
  - Any edit to an existing file, including `pyproject.toml`, so there is no console script. The one possible exception is the changelog line, if the developer picks option (a).

## Acceptance criteria
The story's 25 scenarios, unchanged:
- t1, parser: Scenarios 1–8.
- t2, report: Scenarios 9–18.
- t3, command line: Scenarios 19–25.

They will be copied word for word into section 5 of the spec. Intake checks so far:
- I recomputed every figure they quote and they are consistent: March in ILS is income 12925.00, expense -3025.50, net 9899.50. In USD it is 3493.24 / -817.70 / 2675.54, with salary 3243.24. Scenario 11 gives 0.01 and 0.04.
- Each scenario has an observable outcome with exact values and exit codes.
- The happy path is covered, and so are boundaries, edge cases and errors.

## Open questions
- **P0. CHANGELOG.md vs `PLAY-G4`:**
  - (a) Amend scope to allow one added changelog line per pull request.
  - (b) Change the rule in the repository first.
  - I recommend (a).
- **P1. Line number for a quoted memo that spans several lines:** I recommend the row's first line.
- **P1. A FILE that isn't valid UTF-8 or has broken CSV quoting:** I recommend exit 3 with a `line N:` message.
- **P2. The contents of `sample.csv`:** the story fixes only its row count, dates, ids and totals. Assumption: any nine rows that reproduce Scenarios 9, 10, 13, 16, 19 and 20 are acceptable.
- **P2. How amounts like `1.500` or `+5`, and headers with extra columns, are judged:** these are left to STRUCTURE, within the story's exact error strings.
