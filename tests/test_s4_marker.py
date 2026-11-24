import os

import pytest

import testbed_utils
from testbed_utils import s4_marker
from testbed_utils.s4_marker import marker

_NAME = "QA_S4_MARKER"
_FACTORY_NAMES = "HALO_PROJECT_ENV_NAMES"


def _is_factory_run() -> bool:
    """A factory run lists QA_S4_MARKER in HALO_PROJECT_ENV_NAMES."""
    names = os.environ.get(_FACTORY_NAMES, "")
    return any(item.strip() == _NAME for item in names.split(","))


class TestMarker:
    @pytest.mark.parametrize("value", ["abc123", "  a=b ü  ", " "])
    def test_returns_value_unchanged(self, monkeypatch, value):
        monkeypatch.setenv(_NAME, value)
        result = marker()
        assert isinstance(result, str)
        assert result == value

    def test_returns_empty_string_when_unset(self, monkeypatch):
        monkeypatch.delenv(_NAME, raising=False)
        assert marker() == ""

    def test_returns_empty_string_when_set_to_empty(self, monkeypatch):
        monkeypatch.setenv(_NAME, "")
        assert marker() == ""

    def test_reads_environment_at_call_time(self, monkeypatch):
        monkeypatch.setenv(_NAME, "first")
        assert marker() == "first"
        monkeypatch.setenv(_NAME, "second")
        assert marker() == "second"
        monkeypatch.delenv(_NAME)
        assert marker() == ""


class TestExport:
    def test_exported_from_package_root(self):
        assert testbed_utils.marker is s4_marker.marker
        assert "marker" in testbed_utils.__all__

    def test_existing_exports_remain(self):
        for name in [
            "days_between",
            "extract_fields",
            "hello_world",
            "humanize_delta",
            "is_weekend",
            "mean",
            "median",
            "percentile",
            "slugify",
            "truncate",
            "word_count",
        ]:
            assert name in testbed_utils.__all__
            assert hasattr(testbed_utils, name)


class TestFactoryDetection:
    def test_unset_is_not_a_factory_run(self, monkeypatch):
        monkeypatch.delenv(_FACTORY_NAMES, raising=False)
        assert _is_factory_run() is False

    @pytest.mark.parametrize(
        "names, expected",
        [
            ("", False),
            (",", False),
            ("qa_s4_marker", False),
            ("QA_S4_MARKER_X", False),
            ("QA_S4_MARKER", True),
            ("A, QA_S4_MARKER", True),
        ],
    )
    def test_detection(self, monkeypatch, names, expected):
        monkeypatch.setenv(_FACTORY_NAMES, names)
        assert _is_factory_run() is expected


def test_factory_run_has_marker_set():
    if not _is_factory_run():
        pytest.skip("not a factory run: HALO_PROJECT_ENV_NAMES does not list QA_S4_MARKER")
    # Never compare the real value in an assert: pytest would echo it on failure.
    if marker() == "":
        pytest.fail("QA_S4_MARKER is not set in the run's environment", pytrace=False)
