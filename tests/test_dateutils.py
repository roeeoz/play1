from datetime import date, timedelta

from testbed_utils import business_days_between as package_level_export
from testbed_utils.dateutils import (
    business_days_between,
    days_between,
    humanize_delta,
    is_weekend,
)


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


class TestBusinessDaysBetween:
    def test_full_business_week(self):
        assert business_days_between(date(2024, 1, 1), date(2024, 1, 8)) == 5

    def test_weekend_only_span(self):
        assert business_days_between(date(2024, 1, 6), date(2024, 1, 7)) == 0

    def test_single_business_day(self):
        assert business_days_between(date(2024, 1, 1), date(2024, 1, 2)) == 1

    def test_identical_dates(self):
        assert business_days_between(date(2024, 1, 3), date(2024, 1, 3)) == 0

    def test_exported_from_package_root(self):
        assert package_level_export is business_days_between
        assert package_level_export(date(2024, 1, 1), date(2024, 1, 8)) == 5

    def test_reversed_order_matches_forward(self):
        assert business_days_between(date(2024, 1, 8), date(2024, 1, 1)) == 5
        assert business_days_between(
            date(2024, 1, 8), date(2024, 1, 1)
        ) == business_days_between(date(2024, 1, 1), date(2024, 1, 8))


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
