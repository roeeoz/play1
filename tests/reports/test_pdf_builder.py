"""Tests for the PDF builder (WI-0EA8EA-5)."""
from __future__ import annotations

import re
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

FONT_DIR = Path(__file__).parent.parent.parent / "assets" / "fonts"


def _make_customer():
    from testbed_utils.reports.models import Customer
    return Customer(
        customer_id="CU1",
        full_name="ישראל ישראלי",
        policy_numbers=["POL-001"],
    )


def _make_claims():
    from testbed_utils.reports.models import Claim
    return [
        Claim(
            claim_id="C001",
            customer_id="CU1",
            submitted_at=date(2024, 3, 15),
            category="hospitalization",
            submitted_amount=Decimal("2000.00"),
            reimbursed_amount=Decimal("1500.00"),
            status="approved",
        ),
        Claim(
            claim_id="C002",
            customer_id="CU1",
            submitted_at=date(2024, 6, 1),
            category="dental",
            submitted_amount=Decimal("500.00"),
            reimbursed_amount=Decimal("400.00"),
            status="paid",
        ),
        Claim(
            claim_id="C003",
            customer_id="CU1",
            submitted_at=date(2024, 11, 20),
            category="optical",
            submitted_amount=Decimal("300.00"),
            reimbursed_amount=Decimal("250.00"),
            status="approved",
        ),
    ]


@pytest.fixture
def font_dir():
    if not FONT_DIR.exists() or not (FONT_DIR / "AlefHebrew-Regular.ttf").exists():
        pytest.skip("Alef font files not found")
    return str(FONT_DIR)


@pytest.fixture
def sample_pdf(font_dir):
    from testbed_utils.reports.pdf_builder import build_annual_claims_pdf
    customer = _make_customer()
    claims = _make_claims()
    return build_annual_claims_pdf(
        customer, claims, 2024,
        disclaimer="כל הזכויות שמורות",
        font_dir=font_dir,
    )


def test_returns_bytes(sample_pdf):
    assert isinstance(sample_pdf, bytes)
    assert len(sample_pdf) > 0


def test_valid_pdf_structure(sample_pdf):
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(sample_pdf))
    assert reader.pages is not None
    assert len(reader.pages) >= 1


def test_pdf_contains_year(sample_pdf):
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(sample_pdf))
    all_text = "".join(reader.pages[0].extract_text() or "" for page in reader.pages)
    assert "2024" in all_text


def test_pdf_contains_date_format(sample_pdf):
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(sample_pdf))
    all_text = "".join(page.extract_text() or "" for page in reader.pages)
    # Dates are LTR (numbers + slashes) and should appear as DD/MM/YYYY
    assert re.search(r"\d{2}/\d{2}/\d{4}", all_text), (
        f"No DD/MM/YYYY date found in extracted text: {all_text[:500]!r}"
    )


def test_pdf_contains_customer_name(sample_pdf):
    from pypdf import PdfReader
    from bidi.algorithm import get_display
    import arabic_reshaper
    import io
    reader = PdfReader(io.BytesIO(sample_pdf))
    all_text = "".join(page.extract_text() or "" for page in reader.pages)
    # The customer name is RTL; after bidi it appears visually reversed in PDF
    # Check individual characters are present
    customer_chars = set("ישראל ישראלי") - {" "}
    found_chars = set(all_text)
    overlap = customer_chars & found_chars
    assert len(overlap) >= 3, (
        f"Expected Hebrew characters from customer name in PDF. "
        f"Found chars: {found_chars!r}"
    )


def _extract_all_text(pdf_bytes: bytes) -> str:
    """Extract text from PDF using both default and layout modes."""
    from pypdf import PdfReader
    import io
    reader = PdfReader(io.BytesIO(pdf_bytes))
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
        try:
            parts.append(page.extract_text(extraction_mode="layout") or "")
        except Exception:
            pass
    return "\n".join(parts)


def test_total_reimbursed_arithmetic(sample_pdf):
    """Total reimbursed in PDF equals sum of reimbursed_amount values."""
    all_text = _extract_all_text(sample_pdf)

    # Expected total
    expected_total = Decimal("1500.00") + Decimal("400.00") + Decimal("250.00")

    # Find ₪ amounts in the extracted text (format: ₪#,##0.00)
    amounts = re.findall(r"₪([\d,]+\.\d{2})", all_text)
    assert amounts, f"No ₪ amounts found in text: {all_text[:500]!r}"

    parsed = [Decimal(a.replace(",", "")) for a in amounts]
    assert expected_total in parsed, (
        f"Expected total {expected_total} not found in amounts {parsed}"
    )


def test_currency_format_ils_symbol(sample_pdf):
    """All currency amounts use ₪ symbol and exactly 2 decimal places."""
    all_text = _extract_all_text(sample_pdf)
    amounts = re.findall(r"₪[\d,]+\.\d{2}", all_text)
    assert len(amounts) >= 1, f"No ₪ amounts found. Text: {all_text[:300]!r}"
    for a in amounts:
        assert re.fullmatch(r"₪[\d,]+\.\d{2}", a), f"Malformed amount: {a}"


def test_zero_claims_message(font_dir):
    from testbed_utils.reports.pdf_builder import build_annual_claims_pdf
    from testbed_utils.reports.models import Customer
    from pypdf import PdfReader
    import io
    customer = Customer(customer_id="CU_EMPTY", full_name="ריק ריקי", policy_numbers=["P1"])
    pdf_bytes = build_annual_claims_pdf(customer, [], 2024, font_dir=font_dir)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    all_text = "".join(page.extract_text() or "" for page in reader.pages)
    # The zero-claims message should appear (Hebrew chars will be in visual order)
    zero_msg_chars = set("לא נמצאו תביעות מאושרות לשנה זו") - {" ", "."}
    found = set(all_text)
    overlap = zero_msg_chars & found
    assert len(overlap) >= 5, (
        f"Zero-claims message not found in PDF. Extracted: {all_text[:500]!r}"
    )


def test_pdfa_conformance_marker(sample_pdf):
    """PDF bytes contain PDF/A-1b conformance marker (raw byte search)."""
    assert b"pdfaid:conformance" in sample_pdf
    assert b"pdfaid:part" in sample_pdf


def test_import_does_not_raise():
    """Importing the builder module should not raise when fonts exist."""
    import importlib
    import testbed_utils.reports.pdf_builder  # noqa: F401


def test_does_not_mutate_claims_list(font_dir):
    from testbed_utils.reports.pdf_builder import build_annual_claims_pdf
    customer = _make_customer()
    claims = _make_claims()
    original_order = [c.claim_id for c in claims]
    original_length = len(claims)
    build_annual_claims_pdf(customer, claims, 2024, font_dir=font_dir)
    assert len(claims) == original_length
    assert [c.claim_id for c in claims] == original_order


def test_rows_in_ascending_date_order(font_dir):
    """Table rows appear in ascending order by submitted_at."""
    from testbed_utils.reports.pdf_builder import build_annual_claims_pdf
    from testbed_utils.reports.models import Claim, Customer
    from pypdf import PdfReader
    import io
    customer = Customer(customer_id="CU1", full_name="בדיקה", policy_numbers=["P1"])
    claims = [
        Claim("C3", "CU1", date(2024, 11, 1), "dental", Decimal("100"), Decimal("80"), "approved"),
        Claim("C1", "CU1", date(2024, 1, 5), "medications", Decimal("50"), Decimal("40"), "paid"),
        Claim("C2", "CU1", date(2024, 6, 15), "optical", Decimal("200"), Decimal("150"), "approved"),
    ]
    pdf_bytes = build_annual_claims_pdf(customer, claims, 2024, font_dir=font_dir)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    all_text = "".join(page.extract_text() or "" for page in reader.pages)

    # Find all DD/MM/YYYY dates in extracted text
    dates_found = re.findall(r"\d{2}/\d{2}/\d{4}", all_text)
    assert len(dates_found) >= 3, f"Expected at least 3 dates, got: {dates_found}"
    # Verify they appear in chronological order
    from datetime import datetime
    parsed_dates = [datetime.strptime(d, "%d/%m/%Y").date() for d in dates_found[:3]]
    assert parsed_dates == sorted(parsed_dates), (
        f"Dates not in ascending order: {dates_found}"
    )
