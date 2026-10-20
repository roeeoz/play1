from datetime import date
from decimal import Decimal

from testbed_utils.claims import Claim, ReportData
from testbed_utils.claims.renderer import render_html


def _make_report(
    claims: list[Claim],
    customer_id: str = "cust-1",
    year: int = 2025,
) -> ReportData:
    total_claimed = sum((c.claimed_amount for c in claims), Decimal("0"))
    total_reimbursed = sum((c.reimbursed_amount for c in claims), Decimal("0"))
    return ReportData(
        customer_id=customer_id,
        year=year,
        claims_in_year=claims,
        total_claimed=total_claimed,
        total_reimbursed=total_reimbursed,
    )


def _approved_claim(
    claimed: str = "100.00",
    reimbursed: str = "80.00",
    service_date: date = date(2025, 3, 15),
) -> Claim:
    return Claim(
        service_date=service_date,
        claimed_amount=Decimal(claimed),
        reimbursed_amount=Decimal(reimbursed),
        status="approved",
    )


class TestRenderHtml:
    def test_single_approved_claim(self):
        claim = _approved_claim()
        report = _make_report([claim])
        output = render_html(report)
        assert "2025-03-15" in output
        assert "100.00" in output
        assert "80.00" in output
        assert "approved" in output
        assert "N/A" in output

    def test_single_denied_claim(self):
        claim = Claim(
            service_date=date(2025, 5, 1),
            claimed_amount=Decimal("200.00"),
            reimbursed_amount=Decimal("0.00"),
            status="denied",
            denial_reason="not covered",
        )
        report = _make_report([claim])
        output = render_html(report)
        assert "not covered" in output
        assert "denied" in output

    def test_xss_escaping_in_status(self):
        claim = Claim(
            service_date=date(2025, 1, 1),
            claimed_amount=Decimal("50.00"),
            reimbursed_amount=Decimal("0.00"),
            status="<b>bold</b>",
        )
        report = _make_report([claim])
        output = render_html(report)
        assert "&lt;b&gt;bold&lt;/b&gt;" in output
        assert "<b>" not in output

    def test_xss_escaping_in_denial_reason(self):
        claim = Claim(
            service_date=date(2025, 1, 1),
            claimed_amount=Decimal("50.00"),
            reimbursed_amount=Decimal("0.00"),
            status="denied",
            denial_reason="<script>alert(1)</script>",
        )
        report = _make_report([claim])
        output = render_html(report)
        assert "&lt;script&gt;alert(1)&lt;/script&gt;" in output
        assert "<script>" not in output

    def test_ampersand_in_customer_id(self):
        report = _make_report([], customer_id="A&B Corp")
        output = render_html(report)
        assert "&amp;" in output

    def test_empty_claims_list(self):
        report = _make_report([])
        output = render_html(report)
        assert 'colspan="5"' in output
        assert "No claims for this period." in output

    def test_decimal_formatting(self):
        claim = Claim(
            service_date=date(2025, 6, 1),
            claimed_amount=Decimal("99.9"),
            reimbursed_amount=Decimal("50.5"),
            status="approved",
        )
        report = _make_report([claim])
        output = render_html(report)
        assert "99.90" in output
        assert "50.50" in output

    def test_summary_line_one_claim(self):
        claim = _approved_claim(claimed="120.00", reimbursed="100.00")
        report = _make_report([claim])
        output = render_html(report)
        assert "Total claims: 1" in output
        assert "Total reimbursed: 100.00" in output

    def test_summary_line_empty(self):
        report = _make_report([])
        output = render_html(report)
        assert "Total claims: 0" in output
        assert "Total reimbursed: 0.00" in output

    def test_html_structure_contains_required_elements(self):
        report = _make_report([_approved_claim()])
        output = render_html(report)
        assert '<div class="claims-report">' in output
        assert "<table>" in output
        assert "<thead>" in output
        assert "<tbody>" in output
        assert "</table>" in output

    def test_thead_has_five_headers_in_order(self):
        report = _make_report([])
        output = render_html(report)
        headers = ["Service Date", "Claimed Amount", "Reimbursed Amount", "Status", "Denial Reason"]
        pos = 0
        for header in headers:
            idx = output.find(header, pos)
            assert idx != -1, f"Header '{header}' not found"
            pos = idx + len(header)

    def test_denial_reason_none_renders_na(self):
        claim = _approved_claim()
        assert claim.denial_reason is None
        output = render_html(_make_report([claim]))
        assert "N/A" in output

    def test_no_full_document_tags(self):
        output = render_html(_make_report([]))
        assert "<html" not in output
        assert "<head" not in output
        assert "<body" not in output
