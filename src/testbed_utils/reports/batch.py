"""Year-end batch runner: generate reports for all customers with qualifying claims."""
from __future__ import annotations

from testbed_utils.reports.generator import generate_annual_claims_report
from testbed_utils.reports.models import ReportConfig, ReportRequest
from testbed_utils.reports.repository import ClaimsRepository, CustomerRepository


def run_annual_batch(
    year: int,
    claims_repo: ClaimsRepository,
    customer_repo: CustomerRepository,
    config: ReportConfig,
    *,
    actor_id: str = "batch-scheduler",
) -> dict[str, str]:
    """Generate annual claims reports for every customer with qualifying claims.

    Returns a dict mapping customer_id -> 'success' | 'error: <detail>'.
    Errors for individual customers are caught and recorded; the loop continues.
    """
    customer_ids = claims_repo.list_customers_with_claims(year)
    results: dict[str, str] = {}

    for customer_id in customer_ids:
        request = ReportRequest(
            customer_id=customer_id,
            year=year,
            actor_id=actor_id,
        )
        try:
            generate_annual_claims_report(request, claims_repo, customer_repo, config)
            results[customer_id] = "success"
        except Exception as exc:
            results[customer_id] = f"error: {exc}"

    return results
