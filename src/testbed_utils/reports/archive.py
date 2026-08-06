from pathlib import Path


def save_report(
    pdf_bytes: bytes,
    base_path: str,
    customer_id: str,
    year: int,
) -> str:
    """Persist pdf_bytes to {base_path}/{customer_id}/{year}/annual_claims.pdf.

    Creates parent directories as needed. Overwrites any prior file for the same
    customer/year pair. Returns the resolved absolute path as a string.
    """
    dest = Path(base_path) / customer_id / str(year) / "annual_claims.pdf"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(pdf_bytes)
    return str(dest.resolve())
