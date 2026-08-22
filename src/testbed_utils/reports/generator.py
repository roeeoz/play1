"""Orchestrate customer lookup, claim filtering, PDF build, archive & audit."""
from __future__ import annotations

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from testbed_utils.reports.archive import save_report
from testbed_utils.reports.audit import record_audit_event
from testbed_utils.reports.models import (
    Claim,
    CustomerNotFound,
    ReportConfig,
    ReportRequest,
)
from testbed_utils.reports.pdf_builder import build_annual_claims_pdf
from testbed_utils.reports.repository import ClaimsRepository, CustomerRepository

_TZ_IL = ZoneInfo("Asia/Jerusalem")
_ELIGIBLE_STATUSES = frozenset({"approved", "paid"})


def generate_annual_claims_report(
    request: ReportRequest,
    claims_repo: ClaimsRepository,
    customer_repo: CustomerRepository,
    config: ReportConfig,
) -> bytes:
    """Generate a PDF annual claims report and persist it.

    Returns the PDF bytes on success.
    Raises CustomerNotFound if the customer does not exist.
    Always writes an audit event (success or error).
    """
    ts = datetime.now(tz=timezone.utc).isoformat()
    archive_path: str | None = None

    try:
        customer = customer_repo.get(request.customer_id)
        if customer is None:
            raise CustomerNotFound(
                f"Customer {request.customer_id!r} not found"
            )

        date_from = date(request.year, 1, 1)
        date_to = date(request.year, 12, 31)

        all_claims = claims_repo.list(
            request.customer_id, date_from, date_to, list(_ELIGIBLE_STATUSES)
        )

        eligible = _filter_eligible(all_claims, request.year)
        sorted_claims = sorted(eligible, key=lambda c: c.submitted_at)

        pdf_bytes = build_annual_claims_pdf(
            customer,
            sorted_claims,
            request.year,
            logo_path=config.logo_path,
            disclaimer=config.disclaimer,
        )

        archive_path = save_report(
            pdf_bytes,
            config.archive_base_path,
            request.customer_id,
            request.year,
        )

        record_audit_event(
            log_path=config.audit_log_path,
            ts=ts,
            actor=request.actor_id,
            customer_id=request.customer_id,
            year=request.year,
            outcome="success",
            path=archive_path,
        )

        return pdf_bytes

    except Exception as exc:
        record_audit_event(
            log_path=config.audit_log_path,
            ts=ts,
            actor=request.actor_id,
            customer_id=request.customer_id,
            year=request.year,
            outcome="error",
            path=archive_path,
            error=str(exc),
        )
        raise


def _filter_eligible(claims: list[Claim], year: int) -> list[Claim]:
    """Keep only approved/paid claims whose submission date is in the year (Asia/Jerusalem)."""
    jan1 = date(year, 1, 1)
    dec31 = date(year, 12, 31)
    result = []
    for claim in claims:
        if claim.status not in _ELIGIBLE_STATUSES:
            continue
        submitted = _to_jerusalem_date(claim.submitted_at)
        if jan1 <= submitted <= dec31:
            result.append(claim)
    return result


def _to_jerusalem_date(d: date) -> date:
    """Interpret a date in Asia/Jerusalem timezone (it's already a date, not datetime)."""
    return d
