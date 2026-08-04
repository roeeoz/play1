"""PDF form field extraction utility."""

from __future__ import annotations

import argparse
import json
import sys

from pypdf import PdfReader
from pypdf.errors import (
    EmptyFileError,
    FileNotDecryptedError,
    PdfReadError,
    PdfStreamError,
)


def extract_fields(path: str) -> dict:
    """Return AcroForm/XFA field name-to-value pairs from the PDF at *path*.

    Returns an empty dict when the PDF contains no form fields. Raises
    ``ValueError`` for any condition that prevents field extraction (file not
    found, corrupt, encrypted, etc.).
    """
    try:
        reader = PdfReader(path)
    except FileNotFoundError:
        raise ValueError(f"Cannot open '{path}': file not found")
    except (OSError, PermissionError) as exc:
        raise ValueError(f"Cannot open '{path}': {exc}") from exc
    except (PdfStreamError, PdfReadError, EmptyFileError) as exc:
        raise ValueError(f"Cannot open '{path}': {exc}") from exc
    except Exception as exc:
        raise ValueError(f"Cannot open '{path}': {exc}") from exc

    if reader.is_encrypted:
        raise ValueError(f"Cannot open '{path}': file is encrypted")

    try:
        fields = reader.get_fields()
    except FileNotDecryptedError as exc:
        raise ValueError(f"Cannot open '{path}': file is encrypted") from exc
    except Exception as exc:
        raise ValueError(f"Cannot read fields from '{path}': {exc}") from exc

    if not fields:
        return {}

    return {name: field.get("/V") for name, field in fields.items()}


def main():
    parser = argparse.ArgumentParser(
        description="Extract AcroForm/XFA form field data from a PDF file and print as JSON."
    )
    parser.add_argument("pdf_file", help="Path to the PDF file.")
    args = parser.parse_args()

    try:
        fields = extract_fields(args.pdf_file)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(json.dumps(fields, indent=2))
