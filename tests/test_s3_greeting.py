import ast
import inspect

from testbed_utils import s3_greeting
from testbed_utils.s3_greeting import FAREWELL_FORMAT, farewell


class TestFarewell:
    def test_format_constant(self):
        assert FAREWELL_FORMAT == "goodbye, {name}"

    def test_named_farewell(self):
        assert farewell("Ada") == "goodbye, Ada"

    def test_default_farewell(self):
        assert farewell() == "goodbye, world"

    def test_blank_name_falls_back(self):
        assert farewell("  ") == "goodbye, world"
        assert farewell("") == "goodbye, world"

    def test_name_is_stripped(self):
        assert farewell("  Ada  ") == "goodbye, Ada"

    def test_braces_in_name_are_literal(self):
        assert farewell("{x}") == "goodbye, {x}"

    def test_built_from_format_constant(self):
        assert farewell("Ada") == FAREWELL_FORMAT.format(name="Ada")


class TestStandalone:
    def test_does_not_import_greetlib(self):
        tree = ast.parse(inspect.getsource(s3_greeting))
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
        assert "greetlib" not in imported
