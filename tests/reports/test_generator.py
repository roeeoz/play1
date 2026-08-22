"""Tests for the report generator orchestrator (WI-0EA8EA-6)."""
from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from testbed_utils.reports.models import CustomerNotFound, ReportConfig, ReportRequest
from tests.fixtures.fake_claims import (
    FakeClaimsRepository,
    FakeCustomerRepository,
    make_claim,
    make_customer,
)


@pytest.fixture
def config(tmp_path):
    return ReportConfig(
        logo_path=str(tmp_path / "logo.png"),
        disclaimer="כל הזכויות שמורות",
        archive_base_path=str(tmp_path / "archive"),
        audit_log_path=str(tmp_path / "audit.jsonl"),
    )


@pytest.fixture
def customer():
    return make_customer()


@pytest.fixture
def customer_repo(customer):
    repo = FakeCustomerRepository()
    repo.add(customer)
    return repo


@pytest.fixture
def claims_repo():
    repo = FakeClaimsRepository()
    # 2 eligible claims
    repo.add(make_claim(claim_id="C001", submitted_at=date(2024, 3, 1), status="approved",
                        reimbursed_amount=Decimal("500.00")))
    repo.add(make_claim(claim_id="C002", submitted_at=date(2024, 8, 15), status="paid",
                        reimbursed_amount=Decimal("300.00")))
    # Ineligible: wrong status
    repo.add(make_claim(claim_id="C003", submitted_at=date(2024, 5, 10), status="pending",
                        reimbursed_amount=Decimal("0.00")))
    repo.add(make_claim(claim_id="C004", submitted_at=date(2024, 6, 20), status="rejected",
                        reimbursed_amount=Decimal("0.00")))
    # Ineligible: wrong year
    repo.add(make_claim(claim_id="C005", submitted_at=date(2023, 12, 31), status="approved",
                        reimbursed_amount=Decimal("200.00")))
    return repo


def test_returns_pdf_bytes(customer_repo, claims_repo, config):
    from testbed_utils.reports.generator import generate_annual_claims_report
    from pypdf import PdfReader
    import io
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test-user")
    pdf_bytes = generate_annual_claims_report(request, claims_repo, customer_repo, config)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1


def test_customer_not_found_raises(config):
    from testbed_utils.reports.generator import generate_annual_claims_report
    empty_customer_repo = FakeCustomerRepository()
    claims_repo = FakeClaimsRepository()
    request = ReportRequest(customer_id="NONEXISTENT", year=2024, actor_id="test")
    with pytest.raises(CustomerNotFound):
        generate_annual_claims_report(request, claims_repo, empty_customer_repo, config)


def test_only_eligible_statuses_passed_to_builder(customer_repo, claims_repo, config):
    """Pending and rejected claims must be excluded from the generated PDF."""
    from testbed_utils.reports.generator import generate_annual_claims_report
    from pypdf import PdfReader
    import io, re
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test")
    pdf_bytes = generate_annual_claims_report(request, claims_repo, customer_repo, config)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    # There should be exactly 2 qualifying dates in the PDF
    dates = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    assert len(dates) == 2, f"Expected 2 claim rows but got dates: {dates}"


def test_claims_sorted_ascending(customer_repo, config):
    """Claims must arrive at the PDF builder sorted by submitted_at ascending."""
    from testbed_utils.reports.generator import generate_annual_claims_report
    from pypdf import PdfReader
    import io, re
    from datetime import datetime as dt
    repo = FakeClaimsRepository()
    # Add claims in reverse order
    repo.add(make_claim(claim_id="C3", submitted_at=date(2024, 11, 1), status="approved"))
    repo.add(make_claim(claim_id="C1", submitted_at=date(2024, 2, 1), status="approved"))
    repo.add(make_claim(claim_id="C2", submitted_at=date(2024, 7, 1), status="paid"))
    customer = make_customer()
    c_repo = FakeCustomerRepository()
    c_repo.add(customer)
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test")
    pdf_bytes = generate_annual_claims_report(request, repo, c_repo, config)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    dates_found = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    assert len(dates_found) >= 3
    parsed = [dt.strptime(d, "%d/%m/%Y").date() for d in dates_found[:3]]
    assert parsed == sorted(parsed), f"Dates not ascending: {dates_found}"


def test_archive_saved_correctly(customer_repo, claims_repo, config, tmp_path):
    from testbed_utils.reports.generator import generate_annual_claims_report
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test")
    generate_annual_claims_report(request, claims_repo, customer_repo, config)
    expected_path = Path(config.archive_base_path) / "CU1" / "2024" / "annual_claims.pdf"
    assert expected_path.exists()
    assert expected_path.stat().st_size > 0


def test_audit_success_event_written(customer_repo, claims_repo, config):
    from testbed_utils.reports.generator import generate_annual_claims_report
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="unit-test")
    generate_annual_claims_report(request, claims_repo, customer_repo, config)
    lines = Path(config.audit_log_path).read_text().strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["outcome"] == "success"
    assert event["actor"] == "unit-test"
    assert event["customer_id"] == "CU1"
    assert event["year"] == 2024
    assert event["path"] is not None


def test_audit_error_event_on_exception(customer_repo, config):
    """When PDF builder raises, an error audit event is written and exception propagates."""
    from testbed_utils.reports.generator import generate_annual_claims_report

    class BrokenClaimsRepo:
        def list(self, *a, **kw):
            raise RuntimeError("DB connection failed")
        def list_customers_with_claims(self, year):
            return []

    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test")
    with pytest.raises(RuntimeError, match="DB connection failed"):
        generate_annual_claims_report(request, BrokenClaimsRepo(), customer_repo, config)

    lines = Path(config.audit_log_path).read_text().strip().splitlines()
    assert len(lines) == 1
    event = json.loads(lines[0])
    assert event["outcome"] == "error"
    assert "DB connection failed" in event["error"]


def test_zero_claims_does_not_raise(customer_repo, config):
    from testbed_utils.reports.generator import generate_annual_claims_report
    from pypdf import PdfReader
    import io
    empty_claims = FakeClaimsRepository()  # no claims
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test")
    pdf_bytes = generate_annual_claims_report(request, empty_claims, customer_repo, config)
    assert isinstance(pdf_bytes, bytes)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) >= 1


def test_out_of_year_claims_excluded(customer_repo, config):
    """Claims from adjacent years must not appear in the report."""
    from testbed_utils.reports.generator import generate_annual_claims_report
    from pypdf import PdfReader
    import io, re
    repo = FakeClaimsRepository()
    repo.add(make_claim(claim_id="PREV", submitted_at=date(2023, 12, 31), status="approved"))
    repo.add(make_claim(claim_id="NEXT", submitted_at=date(2025, 1, 1), status="approved"))
    repo.add(make_claim(claim_id="CURR", submitted_at=date(2024, 6, 15), status="approved"))
    request = ReportRequest(customer_id="CU1", year=2024, actor_id="test")
    pdf_bytes = generate_annual_claims_report(request, repo, customer_repo, config)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    dates = re.findall(r"\d{2}/\d{2}/\d{4}", text)
    assert len(dates) == 1
    assert dates[0] == "15/06/2024"
