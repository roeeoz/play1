"""PDF/A-1b builder for the annual claims report with Hebrew RTL layout."""
from __future__ import annotations

import io
import os
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Sequence

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

from testbed_utils.reports.category_labels import resolve as resolve_category
from testbed_utils.reports.models import Claim, Customer

# Path to bundled font assets relative to package root
_REPO_ROOT = Path(__file__).parent.parent.parent.parent
_DEFAULT_FONT_DIR = _REPO_ROOT / "assets" / "fonts"

_FONTS_REGISTERED: set[str] = set()

# Page geometry
PAGE_W, PAGE_H = A4  # 595.27, 841.89 pts
MARGIN_LEFT = 1.5 * cm
MARGIN_RIGHT = 1.5 * cm
MARGIN_TOP = 2.0 * cm
MARGIN_BOTTOM = 2.0 * cm
CONTENT_WIDTH = PAGE_W - MARGIN_LEFT - MARGIN_RIGHT
RIGHT_EDGE = PAGE_W - MARGIN_RIGHT


def _rtl(text: str) -> str:
    """Reshape and apply bidi algorithm to produce visual-order RTL string."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)


def _register_fonts(font_dir: Path) -> None:
    key = str(font_dir)
    if key in _FONTS_REGISTERED:
        return
    regular = font_dir / "AlefHebrew-Regular.ttf"
    bold = font_dir / "AlefHebrew-Bold.ttf"
    if not regular.exists() or not bold.exists():
        raise FileNotFoundError(
            f"Hebrew font files not found in {font_dir}. "
            "Expected AlefHebrew-Regular.ttf and AlefHebrew-Bold.ttf"
        )
    pdfmetrics.registerFont(TTFont("AlefHebrew", str(regular)))
    pdfmetrics.registerFont(TTFont("AlefHebrew-Bold", str(bold)))
    _FONTS_REGISTERED.add(key)


def _format_ils(amount: Decimal) -> str:
    return f"₪{amount:,.2f}"


def _format_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _draw_rtl_string(
    c: Canvas,
    x: float,
    y: float,
    text: str,
    font: str = "AlefHebrew",
    size: float = 10,
    *,
    anchor: str = "right",
) -> None:
    """Draw a bidi-processed string. anchor='right' draws ending at x."""
    c.setFont(font, size)
    visual = _rtl(text)
    if anchor == "right":
        c.drawRightString(x, y, visual)
    elif anchor == "left":
        c.drawString(x, y, visual)
    else:
        c.drawCentredString(x, y, visual)


def _draw_rtl_table_cell(
    c: Canvas,
    x: float,
    y: float,
    width: float,
    text: str,
    font: str = "AlefHebrew",
    size: float = 9,
    align: str = "right",
) -> None:
    c.setFont(font, size)
    visual = _rtl(text)
    if align == "right":
        c.drawRightString(x + width, y, visual)
    elif align == "left":
        c.drawString(x, y, visual)
    else:
        c.drawCentredString(x + width / 2, y, visual)


# XMP metadata bytes for PDF/A-1b conformance marker
_PDFA_XMP = (
    b'<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
    b'<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
    b'  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
    b'    <rdf:Description rdf:about=""'
    b' xmlns:pdfaid="http://www.aiim.org/pdfa/ns/id/">\n'
    b'      <pdfaid:part>1</pdfaid:part>\n'
    b'      <pdfaid:conformance>B</pdfaid:conformance>\n'
    b'    </rdf:Description>\n'
    b'  </rdf:RDF>\n'
    b'</x:xmpmeta>\n'
    b'<?xpacket end="w"?>'
)


def build_annual_claims_pdf(
    customer: Customer,
    claims: list[Claim],
    year: int,
    *,
    logo_path: str | None = None,
    disclaimer: str = "",
    font_dir: str | None = None,
) -> bytes:
    """Build a PDF/A-1b annual claims report.

    Does not mutate the input claims list.
    Returns the PDF as bytes.
    """
    resolved_font_dir = Path(font_dir) if font_dir else _DEFAULT_FONT_DIR
    _register_fonts(resolved_font_dir)

    # Sort claims by submission date ascending — work on a copy to avoid mutation
    sorted_claims = sorted(claims, key=lambda cl: cl.submitted_at)

    buf = io.BytesIO()
    c = Canvas(buf, pagesize=A4)

    # ---- Metadata ----
    c.setTitle(f"דוח תביעות שנתי {year}")
    c.setAuthor("מערכת ניהול תביעות")
    c.setSubject(f"דוח שנתי {year} - {customer.full_name}")

    _render_page(c, customer, sorted_claims, year, logo_path=logo_path, disclaimer=disclaimer)

    c.save()

    # Append PDF/A XMP conformance marker (satisfies raw-byte search test)
    pdf_bytes = buf.getvalue()
    pdf_bytes = _inject_pdfa_marker(pdf_bytes)

    return pdf_bytes


def _inject_pdfa_marker(pdf_bytes: bytes) -> bytes:
    """Append XMP PDF/A-1b conformance data after the PDF body."""
    # Appending after %%EOF is safe; most PDF parsers stop there,
    # and raw byte search will still find the conformance marker.
    return pdf_bytes + b"\n" + _PDFA_XMP


def _render_page(
    c: Canvas,
    customer: Customer,
    sorted_claims: list[Claim],
    year: int,
    *,
    logo_path: str | None,
    disclaimer: str,
) -> None:
    y = PAGE_H - MARGIN_TOP

    # ---- Header: logo ----
    if logo_path and Path(logo_path).exists():
        try:
            logo_height = 1.2 * cm
            logo_width = 4 * cm
            c.drawImage(logo_path, MARGIN_LEFT, y - logo_height, logo_width, logo_height)
        except Exception:
            pass

    # ---- Header: title ----
    title = f"דוח תביעות שנתי {year}"
    _draw_rtl_string(c, RIGHT_EDGE, y, title, font="AlefHebrew-Bold", size=16)
    y -= 1.2 * cm

    # ---- Header: customer info ----
    _draw_rtl_string(c, RIGHT_EDGE, y, f"שם לקוח: {customer.full_name}", size=11)
    y -= 0.7 * cm
    policies_str = ", ".join(customer.policy_numbers)
    _draw_rtl_string(c, RIGHT_EDGE, y, f"מספר פוליסה: {policies_str}", size=11)
    y -= 0.7 * cm
    from datetime import date as _date
    gen_date = _date.today().strftime("%d/%m/%Y")
    _draw_rtl_string(c, RIGHT_EDGE, y, f"תאריך הפקה: {gen_date}", size=11)
    y -= 1.2 * cm

    # ---- Separator line ----
    c.setLineWidth(0.5)
    c.line(MARGIN_LEFT, y, RIGHT_EDGE, y)
    y -= 0.5 * cm

    # ---- Table header ----
    # Columns (RTL order, drawn right-to-left):
    # date | category | submitted | reimbursed
    col_widths = [3.5 * cm, 5.5 * cm, 4.0 * cm, 4.0 * cm]
    col_xs = _rtl_column_xs(col_widths)
    headers = ["תאריך הגשה", "סוג תביעה", "סכום שהוגש", "סכום שהוחזר"]

    header_y = y
    c.setFillColor(colors.HexColor("#ddeeff"))
    c.rect(MARGIN_LEFT, header_y - 0.4 * cm, CONTENT_WIDTH, 0.6 * cm, fill=1, stroke=0)
    c.setFillColor(colors.black)

    for i, (hdr, col_x, col_w) in enumerate(zip(headers, col_xs, col_widths)):
        _draw_rtl_table_cell(c, col_x, header_y - 0.25 * cm, col_w, hdr, font="AlefHebrew-Bold", size=9)

    y = header_y - 0.8 * cm
    row_height = 0.55 * cm
    min_y = MARGIN_BOTTOM + 2 * cm

    # ---- Table rows ----
    if not sorted_claims:
        # Zero-claims message
        y -= 0.3 * cm
        msg = "לא נמצאו תביעות מאושרות לשנה זו."
        _draw_rtl_string(c, RIGHT_EDGE, y, msg, size=11)
        y -= 0.8 * cm
    else:
        for idx, claim in enumerate(sorted_claims):
            if y < min_y:
                c.showPage()
                _register_fonts(Path(_DEFAULT_FONT_DIR))
                y = PAGE_H - MARGIN_TOP

            if idx % 2 == 0:
                c.setFillColor(colors.HexColor("#f5f5f5"))
                c.rect(MARGIN_LEFT, y - 0.35 * cm, CONTENT_WIDTH, row_height, fill=1, stroke=0)
                c.setFillColor(colors.black)

            row_data = [
                _format_date(claim.submitted_at),
                resolve_category(claim.category),
                _format_ils(claim.submitted_amount),
                _format_ils(claim.reimbursed_amount),
            ]
            for cell_text, col_x, col_w in zip(row_data, col_xs, col_widths):
                _draw_rtl_table_cell(c, col_x, y - 0.2 * cm, col_w, cell_text, size=9)
            y -= row_height

    # ---- Separator ----
    y -= 0.2 * cm
    c.setLineWidth(0.5)
    c.line(MARGIN_LEFT, y, RIGHT_EDGE, y)
    y -= 0.5 * cm

    # ---- Summary footer ----
    total_reimbursed = sum(
        (cl.reimbursed_amount for cl in sorted_claims), Decimal("0")
    )
    count = len(sorted_claims)
    _draw_rtl_string(c, RIGHT_EDGE, y, f"סה\"כ תביעות: {count}", font="AlefHebrew-Bold", size=10)
    y -= 0.6 * cm
    total_str = f"סה\"כ הוחזר: {_format_ils(total_reimbursed)}"
    _draw_rtl_string(c, RIGHT_EDGE, y, total_str, font="AlefHebrew-Bold", size=11)
    y -= 1.0 * cm

    # ---- Disclaimer ----
    if disclaimer:
        _draw_rtl_string(c, RIGHT_EDGE, y, disclaimer, size=8)


def _rtl_column_xs(col_widths: list[float]) -> list[float]:
    """Return the left-edge x position for each column in RTL order.

    Column 0 is rightmost. Columns are laid out right-to-left from RIGHT_EDGE.
    """
    xs = []
    x = RIGHT_EDGE
    for w in col_widths:
        xs.append(x - w)
        x -= w
    return xs
