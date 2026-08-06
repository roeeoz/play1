from datetime import date
from decimal import Decimal

from testbed_utils.claims import Claim, generate_annual_report


def test_generate_annual_report_full_journey():
    claims = [
        Claim(
            service_date=date(2024, 3, 15),
            claimed_amount=Decimal("500.00"),
            reimbursed_amount=Decimal("400.00"),
            status="approved",
            denial_reason=None,
        ),
        Claim(
            service_date=date(2024, 7, 22),
            claimed_amount=Decimal("200.00"),
            reimbursed_amount=Decimal("0.00"),
            status="denied",
            denial_reason="Out of network",
        ),
        Claim(
            service_date=date(2023, 11, 5),
            claimed_amount=Decimal("350.00"),
            reimbursed_amount=Decimal("350.00"),
            status="approved",
            denial_reason=None,
        ),
    ]
    html = generate_annual_report("CUST-001", 2024, claims)

    assert isinstance(html, str)
    assert "CUST-001" in html
    assert "2024" in html
    assert "2024-03-15" in html
    assert "2024-07-22" in html
    assert "2023-11-05" not in html
    assert "400.00" in html
    assert "Out of network" in html
    assert "N/A" in html
    assert "Total claims: 2" in html
    assert "Total reimbursed: 400.00" in html
    assert "<table" in html
    assert "</table>" in html


def test_generate_annual_report_empty():
    html = generate_annual_report("CUST-002", 2024, [])

    assert "No claims for this period." in html
    assert "Total claims: 0" in html
