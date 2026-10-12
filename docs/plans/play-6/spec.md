## Story
As a finance user I want the total tax of an invoice so the VAT report can use it.

## Acceptance criteria
1. `src/` gains `invoice_tax_total(lines) -> Decimal` summing each line's `tax` (Decimal), 0 for no lines.
2. A unit test under `tests/` covers no lines, one line and several lines.
