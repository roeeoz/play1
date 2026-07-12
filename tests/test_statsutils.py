import pytest

from testbed_utils.statsutils import mean, median, summarize


class TestMean:
    def test_basic(self):
        assert mean([1, 2, 3, 4, 5]) == 3.0

    def test_single_element(self):
        assert mean([7]) == 7.0

    def test_floats(self):
        assert mean([1.5, 2.5]) == 2.0

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            mean([])


class TestMedian:
    def test_odd_length(self):
        assert median([3, 1, 2]) == 2

    def test_even_length(self):
        assert median([1, 2, 3, 4]) == 2.5

    def test_single_element(self):
        assert median([42]) == 42

    def test_already_sorted(self):
        assert median([10, 20, 30]) == 20

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            median([])


class TestSummarize:
    def test_keys_present(self):
        s = summarize([1, 2, 3, 4, 5])
        assert set(s.keys()) == {"count", "min", "max", "mean", "median"}

    def test_count(self):
        assert summarize([10, 20, 30])["count"] == 3

    def test_min_max(self):
        s = summarize([5, 1, 9, 3])
        assert s["min"] == 1
        assert s["max"] == 9

    def test_mean(self):
        assert summarize([1, 2, 3, 4, 5])["mean"] == 3.0

    def test_median(self):
        assert summarize([1, 2, 3, 4, 5])["median"] == 3

    def test_single_element(self):
        s = summarize([7])
        assert s["count"] == 1
        assert s["min"] == 7
        assert s["max"] == 7
        assert s["mean"] == 7.0
        assert s["median"] == 7

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            summarize([])
