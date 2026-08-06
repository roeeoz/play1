import html

from testbed_utils.claims.model import ReportData

_THEAD = (
    "<thead>"
    "<tr>"
    "<th>Service Date</th>"
    "<th>Claimed Amount</th>"
    "<th>Reimbursed Amount</th>"
    "<th>Status</th>"
    "<th>Denial Reason</th>"
    "</tr>"
    "</thead>"
)


def render_html(report: ReportData) -> str:
    h2 = (
        f'<h2>Annual Claims Report — {html.escape(report.customer_id)}'
        f" ({report.year})</h2>"
    )

    if report.claims_in_year:
        rows = []
        for claim in report.claims_in_year:
            denial = "N/A" if claim.denial_reason is None else html.escape(claim.denial_reason)
            row = (
                "<tr>"
                f"<td>{claim.service_date.isoformat()}</td>"
                f"<td>{claim.claimed_amount:.2f}</td>"
                f"<td>{claim.reimbursed_amount:.2f}</td>"
                f"<td>{html.escape(claim.status)}</td>"
                f"<td>{denial}</td>"
                "</tr>"
            )
            rows.append(row)
        tbody = f"<tbody>{''.join(rows)}</tbody>"
    else:
        tbody = '<tbody><tr><td colspan="5">No claims for this period.</td></tr></tbody>'

    table = f"<table>{_THEAD}{tbody}</table>"
    n = len(report.claims_in_year)
    summary = (
        f'<p class="summary">Total claims: {n} | '
        f"Total reimbursed: {report.total_reimbursed:.2f}</p>"
    )

    return f'<div class="claims-report">{h2}{table}{summary}</div>'
