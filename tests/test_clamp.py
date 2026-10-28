import doctest
import inspect
import sys

import pytest

import testbed_utils
import testbed_utils.clamp
from testbed_utils.clamp import clamp

clamp_module = sys.modules["testbed_utils.clamp"]


class TestClamp:
    def test_value_within_range(self):
        assert clamp(5, 0, 10) == 5

    def test_value_below_range_clamped_to_low(self):
        assert clamp(-3, 0, 10) == 0

    def test_value_above_range_clamped_to_high(self):
        assert clamp(15, 0, 10) == 10

    def test_low_equals_high(self):
        assert clamp(42, 7, 7) == 7

    def test_low_greater_than_high_raises(self):
        with pytest.raises(ValueError, match="low must not be greater than high"):
            clamp(5, 10, 5)


class TestPackageExports:
    def test_root_import_and_all(self):
        from testbed_utils import clamp as root_clamp

        assert root_clamp is clamp
        assert "clamp" in testbed_utils.__all__


def public_functions():
    return [
        obj
        for name, obj in vars(clamp_module).items()
        if not name.startswith("_")
        and inspect.isfunction(obj)
        and obj.__module__ == clamp_module.__name__
    ]


class TestDocstringExamples:
    def test_every_public_function_has_a_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(clamp_module)
        }
        for func in public_functions():
            test = found.get(func.__name__)
            assert test is not None, f"{func.__name__} has no docstring"
            assert test.examples, f"{func.__name__} docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(clamp_module)
        assert results.attempted > 0
        assert results.failed == 0
