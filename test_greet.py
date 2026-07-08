from greet import greet


def test_greet_with_name():
    assert greet("Alice") == "Hello, Alice!"


def test_greet_empty_string():
    assert greet("") == "Hello, stranger!"


def test_greet_whitespace_string():
    assert greet("   ") == "Hello, stranger!"
