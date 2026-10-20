from datetime import date
from decimal import Decimal

from testbed_utils.claims import Claim, ReportData
from testbed_utils.claims.engine import generate_report


def _claim(
    year: int,
    claimed: str,
    reimbursed: str,
    status: str = "approved",
    denial_reason: str | None = None,
) -> Claim:
    return Claim(
        service_date=date(year, 6, 1),
        claimed_amount=Decimal(claimed),
        reimbursed_amount=Decimal(reimbursed),
        status=status,
        denial_reason=denial_reason,
    )


class TestGenerateReport:
    def test_happy_path_mixed_years(self):
        claims = [
            _claim(2024, "100.00", "80.00"),
            _claim(2025, "200.00", "150.00"),
            _claim(2025, "300.00", "250.00"),
            _claim(2025, "400.00", "350.00"),
            _claim(2026, "500.00", "400.00"),
        ]
        report = generate_report("cust-1", 2025, claims)
        assert len(report.claims_in_year) == 3
        assert report.total_claimed == Decimal("900.00")
        assert report.total_reimbursed == Decimal("750.00")

    def test_empty_input_list(self):
        report = generate_report("cust-1", 2025, [])
        assert len(report.claims_in_year) == 0
        assert report.total_claimed == Decimal("0")
        assert report.total_reimbursed == Decimal("0")

    def test_year_mismatch_all_wrong(self):
        claims = [_claim(2023, "100.00", "80.00"), _claim(2024, "200.00", "150.00")]
        report = generate_report("cust-1", 2025, claims)
        assert len(report.claims_in_year) == 0
        assert report.total_claimed == Decimal("0")
        assert report.total_reimbursed == Decimal("0")

    def test_single_claim(self):
        claims = [_claim(2025, "123.45", "99.99")]
        report = generate_report("cust-1", 2025, claims)
        assert len(report.claims_in_year) == 1
        assert report.total_claimed == Decimal("123.45")
        assert report.total_reimbursed == Decimal("99.99")

    def test_decimal_precision_no_float_coercion(self):
        claims = [
            _claim(2025, "123.45", "67.89"),
            _claim(2025, "10.01", "5.55"),
        ]
        report = generate_report("cust-1", 2025, claims)
        assert isinstance(report.total_claimed, Decimal)
        assert isinstance(report.total_reimbursed, Decimal)
        assert report.total_claimed == Decimal("133.46")
        assert report.total_reimbursed == Decimal("73.44")

    def test_totals_are_decimal_instances(self):
        report = generate_report("cust-1", 2025, [])
        assert isinstance(report.total_claimed, Decimal)
        assert isinstance(report.total_reimbursed, Decimal)

    def test_customer_id_passthrough(self):
        report = generate_report("my-customer-42", 2025, [])
        assert report.customer_id == "my-customer-42"

    def test_year_passthrough(self):
        report = generate_report("cust-1", 2025, [])
        assert report.year == 2025

    def test_input_order_preserved(self):
        c1 = _claim(2025, "10.00", "5.00")
        c2 = _claim(2025, "20.00", "15.00")
        c3 = _claim(2025, "30.00", "25.00")
        report = generate_report("cust-1", 2025, [c1, c2, c3])
        assert list(report.claims_in_year) == [c1, c2, c3]

    def test_denied_claims_pass_through(self):
        claims = [
            _claim(2025, "100.00", "0.00", status="denied", denial_reason="not covered"),
            _claim(2025, "200.00", "0.00", status="denied", denial_reason="excluded"),
        ]
        report = generate_report("cust-1", 2025, claims)
        assert len(report.claims_in_year) == 2
        assert report.total_claimed == Decimal("300.00")
        assert report.total_reimbursed == Decimal("0.00")

    def test_returns_report_data_instance(self):
        report = generate_report("cust-1", 2025, [])
        assert isinstance(report, ReportData)
