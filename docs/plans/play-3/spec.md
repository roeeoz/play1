## Story
As a finance user I want the net amount of an invoice (the sum of its line amounts before tax) available as a helper, so exports can show it.

## Acceptance criteria
1. `src/` gains a function `invoice_net_amount(lines)` returning the sum of each line's `amount` (Decimal), 0 for no lines.
2. A unit test under `tests/` covers no lines, one line and several lines.
3. Names follow the claims glossary (net amount, invoice).
