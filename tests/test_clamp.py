import doctest
import importlib
import inspect

import pytest

import testbed_utils
from testbed_utils.clamp import clamp

clamp_mod = importlib.import_module("testbed_utils.clamp")


class TestClamp:
    def test_value_within_range(self):
        assert clamp(5, 1, 10) == 5

    def test_value_equals_low(self):
        assert clamp(1, 1, 10) == 1

    def test_value_equals_high(self):
        assert clamp(10, 1, 10) == 10

    def test_value_below_low(self):
        assert clamp(-3, 1, 10) == 1

    def test_value_above_high(self):
        assert clamp(15, 1, 10) == 10

    def test_inverted_range_raises(self):
        with pytest.raises(ValueError, match="low must not exceed high"):
            clamp(5, 10, 1)


class TestPackageExports:
    def test_root_import_and_all(self):
        from testbed_utils import clamp as root_clamp

        assert root_clamp is clamp
        assert "clamp" in testbed_utils.__all__


def public_functions():
    return [
        obj
        for name, obj in vars(clamp_mod).items()
        if not name.startswith("_")
        and inspect.isfunction(obj)
        and obj.__module__ == clamp_mod.__name__
    ]


class TestDocstringExamples:
    def test_every_public_function_is_covered(self):
        assert {f.__name__ for f in public_functions()} == {"clamp"}

    def test_every_public_function_has_a_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(clamp_mod)
        }
        for func in public_functions():
            test = found.get(func.__name__)
            assert test is not None, f"{func.__name__} has no docstring"
            assert test.examples, f"{func.__name__} docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(clamp_mod)
        assert results.attempted > 0
        assert results.failed == 0
