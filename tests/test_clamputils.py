import doctest
import inspect

import pytest

import testbed_utils
from testbed_utils import clamputils
from testbed_utils.clamputils import clamp


class TestClamp:
    def test_value_within_bounds(self):
        assert clamp(5, 1, 10) == 5

    def test_value_below_lower_bound(self):
        assert clamp(-3, 0, 10) == 0

    def test_value_above_upper_bound(self):
        assert clamp(15, 0, 10) == 10

    def test_value_equals_lower_bound(self):
        assert clamp(1, 1, 10) == 1

    def test_value_equals_upper_bound(self):
        assert clamp(10, 1, 10) == 10

    def test_inverted_bounds_raises(self):
        with pytest.raises(ValueError, match="low must not be greater than high"):
            clamp(7, 10, 5)


def public_functions():
    return [
        obj
        for name, obj in vars(clamputils).items()
        if not name.startswith("_")
        and inspect.isfunction(obj)
        and obj.__module__ == clamputils.__name__
    ]


class TestDocstringExamples:
    def test_every_public_function_is_covered(self):
        assert {f.__name__ for f in public_functions()} == {"clamp"}

    def test_every_public_function_has_a_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(clamputils)
        }
        for func in public_functions():
            test = found.get(func.__name__)
            assert test is not None, f"{func.__name__} has no docstring"
            assert test.examples, f"{func.__name__} docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(clamputils)
        assert results.attempted > 0
        assert results.failed == 0
