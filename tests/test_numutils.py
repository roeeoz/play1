import doctest

import pytest

import testbed_utils
from testbed_utils import numutils
from testbed_utils.numutils import mean, median, percentile


class TestMean:
    def test_several_numbers(self):
        assert mean([1, 2, 3, 4]) == 2.5

    def test_single_element(self):
        assert mean([7]) == 7

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            mean([])


class TestMedian:
    def test_odd_length(self):
        assert median([3, 1, 2]) == 2

    def test_even_length_averages_middle(self):
        assert median([1, 2, 3, 4]) == 2.5

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            median([])


class TestPercentile:
    def test_linear_interpolation(self):
        assert percentile([1, 2, 3, 4, 5], 90) == 4.6

    def test_range_edges(self):
        assert percentile([1, 2, 3, 4, 5], 0) == 1
        assert percentile([1, 2, 3, 4, 5], 100) == 5

    def test_downstream_values(self):
        assert percentile([10, 20, 30], 90) == 28
        assert percentile([42], 90) == 42

    def test_empty_raises(self):
        with pytest.raises(ValueError, match="must not be empty"):
            percentile([], 50)

    def test_out_of_range_p_raises(self):
        with pytest.raises(ValueError, match="between 0 and 100"):
            percentile([1, 2, 3], 150)


class TestPackageExports:
    def test_root_import_and_all(self):
        from testbed_utils import mean as root_mean
        from testbed_utils import median as root_median
        from testbed_utils import percentile as root_percentile

        assert (root_mean, root_median, root_percentile) == (mean, median, percentile)
        for name in ("mean", "median", "percentile"):
            assert name in testbed_utils.__all__


class TestDocstringExamples:
    def test_doctests_pass(self):
        results = doctest.testmod(numutils)
        assert results.attempted > 0
        assert results.failed == 0
