"""Tests for the batch runner (WI-0EA8EA-7)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from testbed_utils.reports.models import CustomerNotFound, ReportConfig
from tests.fixtures.fake_claims import (
    FakeClaimsRepository,
    FakeCustomerRepository,
    make_claim,
    make_customer,
)


@pytest.fixture
def config(tmp_path):
    return ReportConfig(
        logo_path="",
        disclaimer="בדיקה",
        archive_base_path=str(tmp_path / "archive"),
        audit_log_path=str(tmp_path / "audit.jsonl"),
    )


def _make_repos_with_three_customers(fail_customer_id: str):
    """3 customers with qualifying 2024 claims; one will always fail."""
    claims_repo = FakeClaimsRepository()
    customer_repo = FakeCustomerRepository()

    for cid in ("CU1", "CU2", fail_customer_id):
        customer_repo.add(make_customer(customer_id=cid, full_name=f"לקוח {cid}"))
        claims_repo.add(
            make_claim(
                claim_id=f"{cid}-C1",
                customer_id=cid,
                submitted_at=date(2024, 5, 1),
                status="approved",
            )
        )

    return claims_repo, customer_repo


class _FailingClaimsRepo(FakeClaimsRepository):
    """Raises for one specific customer when list() is called."""

    def __init__(self, base_repo: FakeClaimsRepository, fail_for: str) -> None:
        super().__init__(base_repo._claims)
        self._fail_for = fail_for

    def list(self, customer_id, date_from, date_to, statuses):
        if customer_id == self._fail_for:
            raise RuntimeError(f"Simulated failure for {customer_id}")
        return super().list(customer_id, date_from, date_to, statuses)


def test_returns_dict_with_all_customer_ids(config):
    from testbed_utils.reports.batch import run_annual_batch
    base_repo, customer_repo = _make_repos_with_three_customers("CU3")
    failing_repo = _FailingClaimsRepo(base_repo, fail_for="CU3")
    result = run_annual_batch(2024, failing_repo, customer_repo, config)
    assert set(result.keys()) == {"CU1", "CU2", "CU3"}


def test_successful_customers_marked_success(config):
    from testbed_utils.reports.batch import run_annual_batch
    base_repo, customer_repo = _make_repos_with_three_customers("CU3")
    failing_repo = _FailingClaimsRepo(base_repo, fail_for="CU3")
    result = run_annual_batch(2024, failing_repo, customer_repo, config)
    assert result["CU1"] == "success"
    assert result["CU2"] == "success"


def test_failed_customer_marked_error(config):
    from testbed_utils.reports.batch import run_annual_batch
    base_repo, customer_repo = _make_repos_with_three_customers("CU3")
    failing_repo = _FailingClaimsRepo(base_repo, fail_for="CU3")
    result = run_annual_batch(2024, failing_repo, customer_repo, config)
    assert result["CU3"].startswith("error:")


def test_loop_continues_after_failure(config):
    from testbed_utils.reports.batch import run_annual_batch
    base_repo, customer_repo = _make_repos_with_three_customers("CU3")
    failing_repo = _FailingClaimsRepo(base_repo, fail_for="CU3")
    # Even with CU3 failing, all 3 keys are present (loop didn't abort)
    result = run_annual_batch(2024, failing_repo, customer_repo, config)
    assert len(result) == 3


def test_archive_files_exist_for_successful_customers(config, tmp_path):
    from testbed_utils.reports.batch import run_annual_batch
    base_repo, customer_repo = _make_repos_with_three_customers("CU3")
    failing_repo = _FailingClaimsRepo(base_repo, fail_for="CU3")
    run_annual_batch(2024, failing_repo, customer_repo, config)
    for cid in ("CU1", "CU2"):
        expected = Path(config.archive_base_path) / cid / "2024" / "annual_claims.pdf"
        assert expected.exists(), f"Archive not found for {cid}"


def test_default_actor_id_is_batch_scheduler(config):
    from testbed_utils.reports.batch import run_annual_batch
    import json
    claims_repo = FakeClaimsRepository()
    customer_repo = FakeCustomerRepository()
    customer_repo.add(make_customer(customer_id="CU1"))
    claims_repo.add(make_claim(customer_id="CU1", submitted_at=date(2024, 1, 15)))
    run_annual_batch(2024, claims_repo, customer_repo, config)
    lines = Path(config.audit_log_path).read_text().strip().splitlines()
    event = json.loads(lines[0])
    assert event["actor"] == "batch-scheduler"


def test_custom_actor_id(config):
    from testbed_utils.reports.batch import run_annual_batch
    import json
    claims_repo = FakeClaimsRepository()
    customer_repo = FakeCustomerRepository()
    customer_repo.add(make_customer(customer_id="CU1"))
    claims_repo.add(make_claim(customer_id="CU1", submitted_at=date(2024, 1, 15)))
    run_annual_batch(2024, claims_repo, customer_repo, config, actor_id="cron-job")
    lines = Path(config.audit_log_path).read_text().strip().splitlines()
    event = json.loads(lines[0])
    assert event["actor"] == "cron-job"


def test_only_processes_customers_from_list_customers_with_claims(config):
    from testbed_utils.reports.batch import run_annual_batch
    claims_repo = FakeClaimsRepository()
    customer_repo = FakeCustomerRepository()
    # Only CU1 has a 2024 claim; CU2 has no claim at all
    customer_repo.add(make_customer(customer_id="CU1"))
    customer_repo.add(make_customer(customer_id="CU2"))
    claims_repo.add(make_claim(customer_id="CU1", submitted_at=date(2024, 6, 1)))
    result = run_annual_batch(2024, claims_repo, customer_repo, config)
    assert "CU1" in result
    assert "CU2" not in result
