import dataclasses
from datetime import date
from decimal import Decimal

import pytest

from testbed_utils.claims import Claim, ReportData


class TestClaim:
    def test_valid_claim_roundtrip(self):
        c = Claim(
            service_date=date(2025, 3, 15),
            claimed_amount=Decimal("200.00"),
            reimbursed_amount=Decimal("150.00"),
            status="approved",
        )
        assert c.service_date == date(2025, 3, 15)
        assert c.claimed_amount == Decimal("200.00")
        assert c.reimbursed_amount == Decimal("150.00")
        assert c.status == "approved"
        assert c.denial_reason is None

    def test_denial_reason_defaults_to_none(self):
        c = Claim(
            service_date=date(2025, 1, 1),
            claimed_amount=Decimal("100"),
            reimbursed_amount=Decimal("0"),
            status="denied",
        )
        assert c.denial_reason is None

    def test_denial_reason_can_be_set(self):
        c = Claim(
            service_date=date(2025, 1, 1),
            claimed_amount=Decimal("100"),
            reimbursed_amount=Decimal("0"),
            status="denied",
            denial_reason="not covered",
        )
        assert c.denial_reason == "not covered"

    def test_claim_is_frozen(self):
        c = Claim(
            service_date=date(2025, 6, 1),
            claimed_amount=Decimal("50"),
            reimbursed_amount=Decimal("50"),
            status="approved",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            c.status = "denied"  # type: ignore[misc]

    def test_decimal_monetary_values_preserved(self):
        amount = Decimal("123.456")
        c = Claim(
            service_date=date(2025, 1, 1),
            claimed_amount=amount,
            reimbursed_amount=Decimal("0"),
            status="pending",
        )
        assert c.claimed_amount is amount


class TestReportData:
    def _make_claims(self) -> list[Claim]:
        return [
            Claim(
                service_date=date(2025, 1, 10),
                claimed_amount=Decimal("300.00"),
                reimbursed_amount=Decimal("200.00"),
                status="approved",
            ),
            Claim(
                service_date=date(2025, 7, 20),
                claimed_amount=Decimal("100.00"),
                reimbursed_amount=Decimal("0.00"),
                status="denied",
                denial_reason="excluded procedure",
            ),
        ]

    def test_valid_report_data_fields(self):
        claims = self._make_claims()
        rd = ReportData(
            customer_id="cust-001",
            year=2025,
            claims_in_year=claims,
            total_claimed=Decimal("400.00"),
            total_reimbursed=Decimal("200.00"),
        )
        assert rd.customer_id == "cust-001"
        assert rd.year == 2025
        assert rd.total_claimed == Decimal("400.00")
        assert rd.total_reimbursed == Decimal("200.00")

    def test_claims_in_year_stored_as_tuple(self):
        claims = self._make_claims()
        rd = ReportData(
            customer_id="cust-001",
            year=2025,
            claims_in_year=claims,
            total_claimed=Decimal("400.00"),
            total_reimbursed=Decimal("200.00"),
        )
        assert isinstance(rd.claims_in_year, tuple)
        assert len(rd.claims_in_year) == 2

    def test_report_data_is_frozen(self):
        rd = ReportData(
            customer_id="cust-001",
            year=2025,
            claims_in_year=[],
            total_claimed=Decimal("0"),
            total_reimbursed=Decimal("0"),
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            rd.year = 2026  # type: ignore[misc]

    def test_report_data_accepts_list_and_tuple(self):
        claims = self._make_claims()
        rd_from_list = ReportData(
            customer_id="x",
            year=2025,
            claims_in_year=claims,
            total_claimed=Decimal("0"),
            total_reimbursed=Decimal("0"),
        )
        rd_from_tuple = ReportData(
            customer_id="x",
            year=2025,
            claims_in_year=tuple(claims),
            total_claimed=Decimal("0"),
            total_reimbursed=Decimal("0"),
        )
        assert rd_from_list.claims_in_year == rd_from_tuple.claims_in_year
