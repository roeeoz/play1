import doctest
from datetime import date, timedelta

import pytest

import testbed_utils
from testbed_utils import dateutils
from testbed_utils.dateutils import date_range_days, days_between, humanize_delta, is_weekend


class TestDaysBetween:
    def test_forward(self):
        assert days_between(date(2026, 1, 1), date(2026, 1, 8)) == 7

    def test_backward_is_negative(self):
        assert days_between(date(2026, 1, 8), date(2026, 1, 1)) == -7

    def test_same_day(self):
        assert days_between(date(2026, 1, 1), date(2026, 1, 1)) == 0


class TestIsWeekend:
    def test_saturday(self):
        assert is_weekend(date(2026, 7, 4)) is True

    def test_sunday(self):
        assert is_weekend(date(2026, 7, 5)) is True

    def test_wednesday(self):
        assert is_weekend(date(2026, 7, 8)) is False


class TestHumanizeDelta:
    def test_days_plural(self):
        assert humanize_delta(timedelta(days=3)) == "3 days"

    def test_single_hour(self):
        assert humanize_delta(timedelta(hours=1)) == "1 hour"

    def test_minutes(self):
        assert humanize_delta(timedelta(minutes=5)) == "5 minutes"

    def test_moments(self):
        assert humanize_delta(timedelta(seconds=30)) == "moments"

    def test_negative_gets_ago(self):
        assert humanize_delta(timedelta(hours=-1)) == "1 hour ago"

    def test_largest_unit_wins(self):
        assert humanize_delta(timedelta(days=1, hours=5)) == "1 day"


class TestDateRangeDays:
    def test_happy_path(self):
        assert date_range_days("2024-01-01", "2024-01-10") == 9

    def test_reversed_order(self):
        assert date_range_days("2024-01-10", "2024-01-01") == 9

    def test_identical_dates(self):
        assert date_range_days("2024-06-15", "2024-06-15") == 0

    def test_trailing_z_start(self):
        assert date_range_days("2024-01-10Z", "2024-01-01") == 9

    def test_trailing_z_end(self):
        assert date_range_days("2024-01-01", "2024-01-10Z") == 9

    def test_trailing_z_both(self):
        assert date_range_days("2024-01-01Z", "2024-01-10Z") == 9

    def test_invalid_start(self):
        with pytest.raises(ValueError, match="Invalid date"):
            date_range_days("not-a-date", "2024-01-01")

    def test_invalid_end(self):
        with pytest.raises(ValueError, match="Invalid date"):
            date_range_days("2024-01-01", "not-a-date")


class TestDateRangeDaysDocstring:
    def test_has_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(dateutils)
        }
        test = found.get("date_range_days")
        assert test is not None, "date_range_days has no docstring"
        assert test.examples, "date_range_days docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(dateutils)
        assert results.attempted > 0
        assert results.failed == 0


class TestDateRangeDaysExport:
    def test_exported_from_package_root(self):
        assert testbed_utils.date_range_days is dateutils.date_range_days

    def test_in_all(self):
        assert "date_range_days" in testbed_utils.__all__
