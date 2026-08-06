from decimal import Decimal

from testbed_utils.claims.model import Claim, ReportData


def generate_report(customer_id: str, year: int, claims: list[Claim]) -> ReportData:
    filtered = [c for c in claims if c.service_date.year == year]
    total_claimed = sum((c.claimed_amount for c in filtered), Decimal("0"))
    total_reimbursed = sum((c.reimbursed_amount for c in filtered), Decimal("0"))
    return ReportData(
        customer_id=customer_id,
        year=year,
        claims_in_year=filtered,
        total_claimed=total_claimed,
        total_reimbursed=total_reimbursed,
    )
