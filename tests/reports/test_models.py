from datetime import date
from decimal import Decimal

import pytest

from testbed_utils.reports import (
    Claim,
    Customer,
    CustomerNotFound,
    ReportConfig,
    ReportRequest,
)


def test_claim_construction():
    c = Claim(
        claim_id="C001",
        customer_id="CU1",
        submitted_at=date(2024, 3, 15),
        category="hospitalization",
        submitted_amount=Decimal("1500.00"),
        reimbursed_amount=Decimal("1200.00"),
        status="approved",
    )
    assert c.claim_id == "C001"
    assert c.customer_id == "CU1"
    assert c.submitted_at == date(2024, 3, 15)
    assert c.category == "hospitalization"
    assert c.submitted_amount == Decimal("1500.00")
    assert c.reimbursed_amount == Decimal("1200.00")
    assert c.status == "approved"


def test_claim_paid_status():
    c = Claim(
        claim_id="C002",
        customer_id="CU1",
        submitted_at=date(2024, 6, 1),
        category="dental",
        submitted_amount=Decimal("300.00"),
        reimbursed_amount=Decimal("250.00"),
        status="paid",
    )
    assert c.status == "paid"


def test_claim_pending_status():
    c = Claim(
        claim_id="C003",
        customer_id="CU1",
        submitted_at=date(2024, 7, 1),
        category="optical",
        submitted_amount=Decimal("500.00"),
        reimbursed_amount=Decimal("0.00"),
        status="pending",
    )
    assert c.status == "pending"


def test_claim_rejected_status():
    c = Claim(
        claim_id="C004",
        customer_id="CU1",
        submitted_at=date(2024, 8, 1),
        category="medications",
        submitted_amount=Decimal("100.00"),
        reimbursed_amount=Decimal("0.00"),
        status="rejected",
    )
    assert c.status == "rejected"


def test_customer_construction():
    cu = Customer(
        customer_id="CU1",
        full_name="ישראל ישראלי",
        policy_numbers=["POL-001", "POL-002"],
    )
    assert cu.customer_id == "CU1"
    assert cu.full_name == "ישראל ישראלי"
    assert cu.policy_numbers == ["POL-001", "POL-002"]


def test_customer_single_policy():
    cu = Customer(
        customer_id="CU2",
        full_name="שרה כהן",
        policy_numbers=["POL-100"],
    )
    assert len(cu.policy_numbers) == 1
    assert cu.policy_numbers[0] == "POL-100"


def test_report_request_construction():
    rr = ReportRequest(customer_id="CU1", year=2024, actor_id="user@example.com")
    assert rr.customer_id == "CU1"
    assert rr.year == 2024
    assert rr.actor_id == "user@example.com"


def test_report_config_construction():
    rc = ReportConfig(
        logo_path="/assets/logo.png",
        disclaimer="כל הזכויות שמורות",
        archive_base_path="/reports",
        audit_log_path="/logs/audit.jsonl",
    )
    assert rc.logo_path == "/assets/logo.png"
    assert rc.disclaimer == "כל הזכויות שמורות"
    assert rc.archive_base_path == "/reports"
    assert rc.audit_log_path == "/logs/audit.jsonl"


def test_customer_not_found_is_exception():
    with pytest.raises(CustomerNotFound):
        raise CustomerNotFound("CU999 not found")


def test_customer_not_found_is_exception_subclass():
    exc = CustomerNotFound("test")
    assert isinstance(exc, Exception)


def test_customer_not_found_reraise():
    exc = CustomerNotFound("test")
    with pytest.raises(CustomerNotFound):
        raise exc


def test_claims_repository_protocol_satisfied():
    """An in-memory class with the right methods satisfies ClaimsRepository."""
    from datetime import date
    from testbed_utils.reports.repository import ClaimsRepository

    class FakeClaimsRepo:
        def list(self, customer_id, date_from, date_to, statuses):
            return []

        def list_customers_with_claims(self, year):
            return []

    repo = FakeClaimsRepo()
    assert isinstance(repo, ClaimsRepository)


def test_customer_repository_protocol_satisfied():
    """An in-memory class with a get method satisfies CustomerRepository."""
    from testbed_utils.reports.repository import CustomerRepository

    class FakeCustomerRepo:
        def get(self, customer_id):
            return None

    repo = FakeCustomerRepo()
    assert isinstance(repo, CustomerRepository)
