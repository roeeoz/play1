## Story
As a finance user I want invoice amounts rounded to whole cents so totals match the bank statement.

## Acceptance criteria
1. `src/` gains `round_to_cents(amount: Decimal) -> Decimal` that rounds half up to two decimal places.
2. A unit test under `tests/` covers 1.005 -> 1.01, 2.004 -> 2.00 and a negative amount.
