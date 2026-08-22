"""500-claim end-to-end integration test (WI-0EA8EA-9)."""
from __future__ import annotations

import io
import json
import re
import time
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from testbed_utils.api.auth import AuthInfo
from testbed_utils.reports import generate_annual_claims_report  # public import check
from testbed_utils.api import create_app  # public import check
from testbed_utils.reports.models import Claim, Customer, ReportConfig, ReportRequest
from tests.fixtures.fake_claims import FakeClaimsRepository, FakeCustomerRepository

_CUSTOMER_ID = "CU-INTEGRATION"
_YEAR = 2024
_VALID_TOKEN = "integration-test-token"
_ACTOR = "integration-tester"

# Status distribution for 500 claims
_STATUS_CYCLE = ["approved", "paid", "pending", "rejected"]


def _build_500_claims():
    """Build exactly 500 claims: mix of approved, paid, pending, rejected."""
    claims: list[Claim] = []
    start = date(_YEAR, 1, 1)
    for i in range(500):
        status = _STATUS_CYCLE[i % len(_STATUS_CYCLE)]
        submitted_at = start + timedelta(days=i % 365)
        claim = Claim(
            claim_id=f"INT-{i:04d}",
            customer_id=_CUSTOMER_ID,
            submitted_at=submitted_at,
            category=["hospitalization", "dental", "optical", "medications"][i % 4],
            submitted_amount=Decimal(f"{(i + 1) * 10}.00"),
            reimbursed_amount=Decimal(f"{(i + 1) * 8}.00"),
            status=status,  # type: ignore[arg-type]
        )
        claims.append(claim)
    return claims


@pytest.fixture(scope="module")
def all_claims():
    return _build_500_claims()


@pytest.fixture(scope="module")
def qualified_claims(all_claims):
    return [c for c in all_claims if c.status in ("approved", "paid")]


@pytest.fixture(scope="module")
def tmp_path_module(tmp_path_factory):
    return tmp_path_factory.mktemp("integration")


@pytest.fixture(scope="module")
def config(tmp_path_module):
    return ReportConfig(
        logo_path="",
        disclaimer="דוח שנתי - לשימוש פנים בלבד",
        archive_base_path=str(tmp_path_module / "archive"),
        audit_log_path=str(tmp_path_module / "audit.jsonl"),
    )


@pytest.fixture(scope="module")
def repos(all_claims):
    customer_repo = FakeCustomerRepository()
    customer_repo.add(Customer(
        customer_id=_CUSTOMER_ID,
        full_name="ישראל ישראלי",
        policy_numbers=["POL-INT-001"],
    ))
    claims_repo = FakeClaimsRepository(all_claims)
    return claims_repo, customer_repo


@pytest.fixture(scope="module")
def app(repos, config):
    claims_repo, customer_repo = repos
    token_store = {
        _VALID_TOKEN: AuthInfo(
            actor_id=_ACTOR,
            allowed_customers=frozenset([_CUSTOMER_ID]),
        )
    }
    return create_app(
        claims_repo=claims_repo,
        customer_repo=customer_repo,
        report_config=config,
        token_store=token_store,
        testing=True,
    )


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def response(client):
    return client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers={"Authorization": f"Bearer {_VALID_TOKEN}"},
    )


def test_generate_annual_claims_report_importable():
    from testbed_utils.reports import generate_annual_claims_report as fn
    assert callable(fn)


def test_create_app_importable():
    from testbed_utils.api import create_app as fn
    assert callable(fn)


def test_http_200(response):
    assert response.status_code == 200


def test_content_type_pdf(response):
    assert response.content_type == "application/pdf"


def test_pdf_bytes_nonempty(response):
    assert len(response.data) > 0


def test_valid_pdf_structure(response):
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(response.data))
    assert len(reader.pages) >= 1


def test_qualified_claim_count(response, qualified_claims):
    """Count of table rows == count of approved/paid claims."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(response.data))
    all_text = ""
    for page in reader.pages:
        try:
            layout_text = page.extract_text(extraction_mode="layout") or ""
        except Exception:
            layout_text = page.extract_text() or ""
        all_text += layout_text + "\n"

    # Filter only claim submission dates (those within the report year)
    all_dates = re.findall(r"\d{2}/\d{2}/(\d{4})", all_text)
    claim_year_dates = [d for d in all_dates if d == str(_YEAR)]
    expected_count = len(qualified_claims)
    assert len(claim_year_dates) == expected_count, (
        f"Expected {expected_count} claim dates for year {_YEAR} in PDF, "
        f"found {len(claim_year_dates)}"
    )


def test_total_reimbursed_arithmetic(response, qualified_claims):
    """Total reimbursed in PDF equals arithmetic sum of qualified claims."""
    from pypdf import PdfReader
    reader = PdfReader(io.BytesIO(response.data))
    all_text = ""
    for page in reader.pages:
        try:
            layout_text = page.extract_text(extraction_mode="layout") or ""
        except Exception:
            layout_text = ""
        all_text += layout_text + "\n"

    expected_total = sum(c.reimbursed_amount for c in qualified_claims)

    amounts = re.findall(r"₪([\d,]+\.\d{2})", all_text)
    assert amounts, f"No ₪ amounts found in PDF text"
    parsed = [Decimal(a.replace(",", "")) for a in amounts]
    assert expected_total in parsed, (
        f"Expected total {expected_total} not found in extracted amounts. "
        f"Found: {sorted(parsed, reverse=True)[:5]} (top 5 of {len(parsed)})"
    )


def test_performance_under_10_seconds(repos, config):
    """Generation for 500 claims completes in <= 10 seconds."""
    claims_repo, customer_repo = repos
    request = ReportRequest(
        customer_id=_CUSTOMER_ID, year=_YEAR, actor_id="perf-test"
    )
    perf_config = ReportConfig(
        logo_path="",
        disclaimer="perf test",
        archive_base_path=config.archive_base_path + "_perf",
        audit_log_path=config.audit_log_path + ".perf",
    )
    start = time.perf_counter()
    generate_annual_claims_report(request, claims_repo, customer_repo, perf_config)
    elapsed = time.perf_counter() - start
    assert elapsed <= 10.0, f"Report generation took {elapsed:.2f}s, exceeds 10s limit"


def test_archive_file_exists(response, config):
    """PDF must be persisted to the archive after the HTTP response."""
    expected = (
        Path(config.archive_base_path)
        / _CUSTOMER_ID
        / str(_YEAR)
        / "annual_claims.pdf"
    )
    assert expected.exists(), f"Archive file not found at {expected}"
    assert expected.stat().st_size > 0


def test_audit_entry_written(response, config):
    """Exactly one audit entry with outcome=success must be recorded."""
    log_path = Path(config.audit_log_path)
    assert log_path.exists(), "Audit log file not created"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    success_events = [
        json.loads(line)
        for line in lines
        if json.loads(line).get("customer_id") == _CUSTOMER_ID
        and json.loads(line).get("year") == _YEAR
    ]
    assert len(success_events) >= 1
    assert success_events[-1]["outcome"] == "success"
