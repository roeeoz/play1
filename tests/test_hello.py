import doctest

import testbed_utils
from testbed_utils import hello
from testbed_utils.hello import hello_world


class TestHelloWorld:
    def test_returns_greeting(self):
        assert hello_world() == "Hello, world!"

    def test_exported_from_package_root(self):
        assert testbed_utils.hello_world is hello.hello_world
        assert "hello_world" in testbed_utils.__all__


class TestDocstringExamples:
    def test_hello_world_has_a_runnable_example(self):
        found = {
            test.name.rsplit(".", 1)[-1]: test
            for test in doctest.DocTestFinder().find(hello)
        }
        test = found.get("hello_world")
        assert test is not None, "hello_world has no docstring"
        assert test.examples, "hello_world docstring has no >>> example"

    def test_doctests_pass(self):
        results = doctest.testmod(hello)
        assert results.attempted > 0
        assert results.failed == 0
