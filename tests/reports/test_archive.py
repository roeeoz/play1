from pathlib import Path

from testbed_utils.reports.archive import save_report


def test_file_stored_at_expected_path(tmp_path):
    pdf = b"%PDF-1.4 test content"
    returned_path = save_report(pdf, str(tmp_path), "CU1", 2024)
    expected = tmp_path / "CU1" / "2024" / "annual_claims.pdf"
    assert expected.exists()
    assert returned_path == str(expected.resolve())


def test_file_content_matches_bytes(tmp_path):
    pdf = b"%PDF-1.4 hello world"
    save_report(pdf, str(tmp_path), "CU2", 2023)
    stored = (tmp_path / "CU2" / "2023" / "annual_claims.pdf").read_bytes()
    assert stored == pdf


def test_returns_absolute_path(tmp_path):
    returned = save_report(b"data", str(tmp_path), "CU3", 2022)
    assert Path(returned).is_absolute()


def test_creates_intermediate_directories(tmp_path):
    deep_base = tmp_path / "a" / "b" / "c"
    save_report(b"data", str(deep_base), "CU4", 2021)
    assert (deep_base / "CU4" / "2021" / "annual_claims.pdf").exists()


def test_overwrite_replaces_content(tmp_path):
    first = b"first PDF content"
    second = b"second PDF content -- different"
    save_report(first, str(tmp_path), "CU5", 2024)
    save_report(second, str(tmp_path), "CU5", 2024)
    final = (tmp_path / "CU5" / "2024" / "annual_claims.pdf").read_bytes()
    assert final == second
    assert final != first


def test_overwrite_does_not_append(tmp_path):
    save_report(b"aaa", str(tmp_path), "CU6", 2024)
    save_report(b"bb", str(tmp_path), "CU6", 2024)
    assert (tmp_path / "CU6" / "2024" / "annual_claims.pdf").read_bytes() == b"bb"
