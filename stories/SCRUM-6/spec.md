# Ticket draft: SCRUM-6, monthly expense report from a CSV ledger (intake, not ready)

**Status:** one P0 question is open: the CHANGELOG gate. The developer has said four times to "take the simplest reading and proceed". That covers every gap the story is silent on (assumptions A1–A5). It can't settle the gate conflict, because that conflict is between the story's explicit text and a repository rule that is checked mechanically.

## User story
As a developer keeping a CSV ledger, I want `python -m ledger report` to total one month by category in a base currency, so that I can see a month's income, expenses and largest categories deterministically, and have a bad row pointed at by its line number instead of a wrong total.

## Context (depends on the P0 answer)
The story's text as written:

> The story adds a new, stdlib-only Python package `ledger` under `src/` (src layout, discovered by the repository's manifest) with its tests under `tests/`, in three dependent work items: the model and CSV parser (t1), the monthly report (t2) and the command line (t3). A ledger is a UTF-8 CSV file with a header row naming the columns `id`, `date`, `amount`, `currency`, `category` and `memo`, in any order. Amounts are decimal numbers with at most two decimal places, positive for income and negative for expense. Currencies are ILS, USD or EUR, converted at fixed rates expressed in ILS per unit (ILS 1, USD 3.70, EUR 4.00), never fetched. Money is `decimal.Decimal` end to end; figures are rounded once, after summing, with `ROUND_HALF_EVEN`. Out of scope: other file formats, live exchange rates, persistent configuration, charts, any third-party dependency, changes to any existing file of the repository.

**The conflict.** Rule 4 of the repository gate (`.factory/plugins/claims-dev/skills/repo-gate/SKILL.md`, blocker `PLAY-G4`) requires every pull request to add a line under `## Unreleased` in `CHANGELOG.md`. The last clause of the paragraph above forbids that.
- **Option (a), recommended:** the last clause becomes "changes to any existing file of the repository other than one line per pull request under `## Unreleased` in `CHANGELOG.md`, which the repository's gate requires".
- **Option (b):** the sentence stays word for word, and this story waits until a separate change has altered rule 4.
- **Not an option:** an exemption for this story. The gate doesn't read the ticket.

## Traceability
- Traces to: R1 (CSV parsing), R2 (row validation), R3 (monthly report), R4 (currency conversion and rounding), R5 (command line) · steps 1–8 · RK1, RK2.
- Priority: Must. Size: M (≈5).
- Work items: t1 → t2 → t3, built in that order.

## Acceptance criteria
Scenarios 1–25 are kept word for word as the story states them.
- **t1, parsing and validation (scenarios 1–8):**
  - `parse_csv` and `parse_lines` return frozen `Transaction` values.
  - Header columns are matched by name in any order, and fields are stripped.
  - A BOM, blank lines and quoted memos are handled.
  - Errors are `LedgerError(line, reason)` with the exact reason texts, including a duplicate id, missing columns and a missing header.
- **t2, the monthly report (scenarios 9–18):**
  - `monthly_report` and the `RATES` constant.
  - Each figure is rounded once, after summing, half to even, and always shown with two decimal places.
  - Categories are ordered by absolute total, ties by name, with an optional top-N.
  - An empty month gives a zero report. `to_dict` returns the report as a dictionary. Caller errors raise `ValueError`.
- **t3, the command line (scenarios 19–25):**
  - Exact text and JSON output.
  - Exit codes 0, 2 and 3, with exact stderr for data errors.
  - `--help`.
  - Tests drive the command through `subprocess` with `sys.executable -m ledger`.

Under option (a) only, one criterion is added: **26.** Each pull request of the story adds exactly one line under `## Unreleased` in `CHANGELOG.md` and changes no other existing file.

## Assumptions (the simplest reading where the story is silent, as the developer directed)
- **A1. A row with several faults.** The field-count check comes first. The fields are then checked in canonical column order (`id`, `date`, `amount`, `currency`, `category`, `memo`), and the first fault found is reported. The duplicate-id check runs only once the row is otherwise valid.
- **A2. A quoted field that spans lines.** The error reports the physical line on which the row starts.
- **A3. A file of only blank or whitespace-only lines.** It is treated like the empty file: `LedgerError(1, "missing header")`.
- **A4. A duplicated column name in the header.** No new error text is added. The STRUCTURE stage chooses which occurrence is read and records that choice. Columns beyond the six named ones are still ignored.
- **A5. The contents of `sample.csv`.** Whatever the scenarios don't fix is the implementer's choice, such as each row's currency and the April row. Any fixture that satisfies scenarios 1, 9, 10, 16, 19 and 20 is acceptable.
- **A6. The CHANGELOG gate (unresolved, recorded with its risk).** The developer has not chosen between (a) and (b). If the stage is approved as it stands, each pull request either fails `PLAY-G4` or changes `CHANGELOG.md` against the story's text.

## Notes
- "Net" here means income + expense. That is not the glossary's "net amount" (before tax), which applies only to the claims and invoice code.
- The repository's only check is `pytest` on Python 3.12, run after an editable install. The code must also run on Python 3.10 and later. Only the standard library may be used.
- The Definition of Ready in the story template requires a working assumption for every blocker. The gate conflict can't be given a valid one, so it stays open as the P0 question.
