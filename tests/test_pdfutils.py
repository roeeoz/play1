import pathlib

import pytest

from testbed_utils import extract_fields

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


class TestExtractFieldsHappyPath:
    def test_fields_present(self):
        result = extract_fields(str(FIXTURES / "sample_form.pdf"))
        assert result["first_name"] == "Alice"
        assert result["last_name"] == "Smith"

    def test_no_fields_returns_empty_dict(self):
        result = extract_fields(str(FIXTURES / "no_fields.pdf"))
        assert result == {}


class TestExtractFieldsErrors:
    def test_file_not_found_raises_value_error(self):
        missing = str(FIXTURES / "does_not_exist.pdf")
        with pytest.raises(ValueError) as exc_info:
            extract_fields(missing)
        assert missing in str(exc_info.value)

    def test_corrupt_file_raises_value_error(self, tmp_path):
        corrupt = tmp_path / "corrupt.pdf"
        corrupt.write_bytes(b"This is not a valid PDF file")
        with pytest.raises(ValueError):
            extract_fields(str(corrupt))

    def test_encrypted_raises_value_error(self):
        encrypted_path = str(FIXTURES / "encrypted.pdf")
        with pytest.raises(ValueError) as exc_info:
            extract_fields(encrypted_path)
        msg = str(exc_info.value)
        assert encrypted_path in msg or "encrypt" in msg.lower() or "password" in msg.lower()
