"""Tests for auth helpers (WI-0EA8EA-8)."""
from __future__ import annotations

import pytest
from flask import Flask

from testbed_utils.api.auth import AuthInfo, authorize_customer, decode_token, get_bearer_token


TOKEN_STORE: dict[str, AuthInfo] = {
    "valid-token-1": AuthInfo(actor_id="alice", allowed_customers=frozenset(["CU1", "CU2"])),
    "valid-token-2": AuthInfo(actor_id="bob", allowed_customers=frozenset(["CU3"])),
}


@pytest.fixture
def app():
    from testbed_utils.api.app import create_app
    from testbed_utils.reports.models import ReportConfig
    from tests.fixtures.fake_claims import FakeClaimsRepository, FakeCustomerRepository
    return create_app(
        claims_repo=FakeClaimsRepository(),
        customer_repo=FakeCustomerRepository(),
        report_config=ReportConfig(logo_path="", disclaimer="", archive_base_path="/tmp", audit_log_path="/tmp/audit.jsonl"),
        token_store=TOKEN_STORE,
        testing=True,
    )


def test_decode_token_valid():
    info = decode_token("valid-token-1", TOKEN_STORE)
    assert info is not None
    assert info.actor_id == "alice"
    assert "CU1" in info.allowed_customers


def test_decode_token_invalid():
    info = decode_token("bad-token", TOKEN_STORE)
    assert info is None


def test_authorize_customer_allowed():
    info = AuthInfo(actor_id="alice", allowed_customers=frozenset(["CU1", "CU2"]))
    assert authorize_customer(info, "CU1") is True


def test_authorize_customer_denied():
    info = AuthInfo(actor_id="alice", allowed_customers=frozenset(["CU1"]))
    assert authorize_customer(info, "CU99") is False


def test_get_bearer_token_present(app):
    with app.test_request_context(headers={"Authorization": "Bearer my-token"}):
        token = get_bearer_token()
    assert token == "my-token"


def test_get_bearer_token_missing(app):
    with app.test_request_context():
        token = get_bearer_token()
    assert token is None


def test_get_bearer_token_malformed(app):
    with app.test_request_context(headers={"Authorization": "Basic dXNlcjpwYXNz"}):
        token = get_bearer_token()
    assert token is None
