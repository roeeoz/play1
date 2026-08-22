"""Flask application factory."""
from __future__ import annotations

from flask import Flask

from testbed_utils.api.auth import AuthInfo
from testbed_utils.api.routes import _make_blueprint
from testbed_utils.reports.models import ReportConfig
from testbed_utils.reports.repository import ClaimsRepository, CustomerRepository


def create_app(
    *,
    claims_repo: ClaimsRepository,
    customer_repo: CustomerRepository,
    report_config: ReportConfig,
    token_store: dict[str, AuthInfo] | None = None,
    testing: bool = False,
) -> Flask:
    """Create and return a configured Flask application.

    token_store maps bearer token strings to AuthInfo objects.
    If None, no token grants access (all requests get 401).
    """
    app = Flask(__name__)
    app.testing = testing

    app.config["CLAIMS_REPO"] = claims_repo
    app.config["CUSTOMER_REPO"] = customer_repo
    app.config["REPORT_CONFIG"] = report_config

    resolved_token_store: dict[str, AuthInfo] = token_store or {}
    bp = _make_blueprint(resolved_token_store)
    app.register_blueprint(bp)

    return app
