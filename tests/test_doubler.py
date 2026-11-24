import doctest
import inspect

import testbed_utils
from testbed_utils import doubler
from testbed_utils.doubler import double


class TestDouble:
    def test_positive(self):
        assert double(3) == 6

    def test_zero(self):
        assert double(0) == 0

    def test_negative(self):
        assert double(-4) == -8

    def test_large_integer_is_exact(self):
        assert double(2**100) == 2**101

    def test_single_parameter_named_n(self):
        assert list(inspect.signature(double).parameters) == ["n"]


class TestPackageExports:
    def test_root_import_is_same_function(self):
        from testbed_utils import double as root_double

        assert root_double is doubler.double

    def test_double_in_all(self):
        assert "double" in testbed_utils.__all__

    def test_existing_names_still_exported(self):
        for name in (
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
        ):
            assert name in testbed_utils.__all__


class TestDocstringExamples:
    def test_doctests_pass(self):
        results = doctest.testmod(doubler)
        assert results.attempted > 0
        assert results.failed == 0
