from datetime import date, timedelta

from testbed_utils.dateutils import days_between, humanize_delta, is_weekend


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
