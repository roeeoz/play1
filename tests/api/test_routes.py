"""Tests for POST /reports/annual-claims route (WI-0EA8EA-8)."""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from testbed_utils.api.auth import AuthInfo
from testbed_utils.reports.models import ReportConfig
from tests.fixtures.fake_claims import (
    FakeClaimsRepository,
    FakeCustomerRepository,
    make_claim,
    make_customer,
)

_VALID_TOKEN = "test-bearer-token"
_ACTOR = "test-user"
_CUSTOMER_ID = "CU1"
_YEAR = 2024


@pytest.fixture
def tmp_config(tmp_path):
    return ReportConfig(
        logo_path="",
        disclaimer="בדיקה",
        archive_base_path=str(tmp_path / "archive"),
        audit_log_path=str(tmp_path / "audit.jsonl"),
    )


@pytest.fixture
def customer_repo():
    repo = FakeCustomerRepository()
    repo.add(make_customer(customer_id=_CUSTOMER_ID, full_name="ישראל ישראלי"))
    return repo


@pytest.fixture
def claims_repo():
    repo = FakeClaimsRepository()
    repo.add(make_claim(
        claim_id="C1",
        customer_id=_CUSTOMER_ID,
        submitted_at=date(_YEAR, 6, 1),
        status="approved",
        submitted_amount=Decimal("1000.00"),
        reimbursed_amount=Decimal("800.00"),
    ))
    return repo


@pytest.fixture
def token_store():
    return {
        _VALID_TOKEN: AuthInfo(
            actor_id=_ACTOR,
            allowed_customers=frozenset([_CUSTOMER_ID]),
        )
    }


@pytest.fixture
def app(customer_repo, claims_repo, tmp_config, token_store):
    from testbed_utils.api.app import create_app
    return create_app(
        claims_repo=claims_repo,
        customer_repo=customer_repo,
        report_config=tmp_config,
        token_store=token_store,
        testing=True,
    )


@pytest.fixture
def client(app):
    return app.test_client()


def _auth_headers(token=_VALID_TOKEN):
    return {"Authorization": f"Bearer {token}"}


# ---- Success path ----

def test_200_with_valid_request(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers=_auth_headers(),
    )
    assert resp.status_code == 200


def test_response_content_type_is_pdf(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers=_auth_headers(),
    )
    assert resp.content_type == "application/pdf"


def test_response_content_disposition(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers=_auth_headers(),
    )
    cd = resp.headers.get("Content-Disposition", "")
    assert "attachment" in cd
    assert f"annual_claims_{_CUSTOMER_ID}_{_YEAR}.pdf" in cd


def test_response_body_is_valid_pdf(client):
    from pypdf import PdfReader
    import io
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers=_auth_headers(),
    )
    reader = PdfReader(io.BytesIO(resp.data))
    assert len(reader.pages) >= 1


# ---- Auth failures ----

def test_401_no_authorization_header(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
    )
    assert resp.status_code == 401


def test_401_malformed_token(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers={"Authorization": "Bearer bad-token-xyz"},
    )
    assert resp.status_code == 401


def test_401_wrong_scheme(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": _YEAR},
        headers={"Authorization": "Basic dXNlcjpwYXNz"},
    )
    assert resp.status_code == 401


# ---- Authorisation failure ----

def test_403_unauthorized_customer(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": "CU_OTHER", "year": _YEAR},
        headers=_auth_headers(),
    )
    assert resp.status_code == 403


# ---- Validation errors ----

def test_400_missing_year(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID},
        headers=_auth_headers(),
    )
    assert resp.status_code == 400


def test_400_missing_customer_id(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"year": _YEAR},
        headers=_auth_headers(),
    )
    assert resp.status_code == 400


def test_400_non_integer_year(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": "2024"},
        headers=_auth_headers(),
    )
    assert resp.status_code == 400


def test_400_float_year(client):
    resp = client.post(
        "/reports/annual-claims",
        json={"customer_id": _CUSTOMER_ID, "year": 2024.5},
        headers=_auth_headers(),
    )
    assert resp.status_code == 400


# ---- Not found ----

def test_404_unknown_customer(client, token_store, claims_repo, tmp_config):
    from testbed_utils.api.app import create_app
    # Add an auth entry that allows the unknown customer
    ts = {_VALID_TOKEN: AuthInfo(actor_id=_ACTOR, allowed_customers=frozenset(["UNKNOWN"]))}
    app2 = create_app(
        claims_repo=claims_repo,
        customer_repo=FakeCustomerRepository(),  # empty
        report_config=tmp_config,
        token_store=ts,
        testing=True,
    )
    client2 = app2.test_client()
    resp = client2.post(
        "/reports/annual-claims",
        json={"customer_id": "UNKNOWN", "year": _YEAR},
        headers=_auth_headers(),
    )
    assert resp.status_code == 404
