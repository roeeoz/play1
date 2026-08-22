"""Flask route: POST /reports/annual-claims."""
from __future__ import annotations

from flask import Blueprint, jsonify, request, current_app

from testbed_utils.reports.models import CustomerNotFound, ReportRequest
from testbed_utils.reports.generator import generate_annual_claims_report
from testbed_utils.api.auth import AuthInfo, require_auth, authorize_customer

reports_bp = Blueprint("reports", __name__)


def _make_blueprint(token_store: dict) -> Blueprint:
    bp = Blueprint("reports", __name__)

    @bp.route("/reports/annual-claims", methods=["POST"])
    @require_auth(token_store)
    def annual_claims(*, auth_info: AuthInfo):
        body = request.get_json(silent=True)
        if body is None:
            return jsonify({"error": "Invalid or missing JSON body"}), 400

        customer_id = body.get("customer_id")
        year = body.get("year")

        if customer_id is None:
            return jsonify({"error": "Missing field: customer_id"}), 400
        if year is None:
            return jsonify({"error": "Missing field: year"}), 400
        if not isinstance(year, int):
            return jsonify({"error": "year must be an integer"}), 400

        if not authorize_customer(auth_info, customer_id):
            return jsonify({"error": "Forbidden"}), 403

        claims_repo = current_app.config["CLAIMS_REPO"]
        customer_repo = current_app.config["CUSTOMER_REPO"]
        report_config = current_app.config["REPORT_CONFIG"]

        rr = ReportRequest(
            customer_id=customer_id,
            year=year,
            actor_id=auth_info.actor_id,
        )

        try:
            pdf_bytes = generate_annual_claims_report(
                rr, claims_repo, customer_repo, report_config
            )
        except CustomerNotFound:
            return jsonify({"error": f"Customer {customer_id!r} not found"}), 404

        filename = f"annual_claims_{customer_id}_{year}.pdf"
        return (
            pdf_bytes,
            200,
            {
                "Content-Type": "application/pdf",
                "Content-Disposition": f'attachment; filename="{filename}"',
            },
        )

    return bp
