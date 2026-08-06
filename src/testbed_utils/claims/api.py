from testbed_utils.claims.engine import generate_report
from testbed_utils.claims.model import Claim
from testbed_utils.claims.renderer import render_html


def generate_annual_report(customer_id: str, year: int, claims: list[Claim]) -> str:
    report = generate_report(customer_id, year, claims)
    return render_html(report)
