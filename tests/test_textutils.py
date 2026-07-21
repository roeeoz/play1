from testbed_utils.textutils import greet, slugify, truncate, word_count


class TestSlugify:
    def test_basic(self):
        assert slugify("Hello, World!") == "hello-world"

    def test_collapses_whitespace_and_hyphens(self):
        assert slugify("a  b --  c") == "a-b-c"

    def test_strips_accents(self):
        assert slugify("Café au Lait") == "cafe-au-lait"

    def test_empty(self):
        assert slugify("") == ""


class TestTruncate:
    def test_short_text_unchanged(self):
        assert truncate("hi", 10) == "hi"

    def test_truncates_with_suffix(self):
        assert truncate("hello world", 8) == "hello..."

    def test_exact_fit(self):
        assert truncate("hello", 5) == "hello"

    def test_tiny_limit_clips_suffix(self):
        assert truncate("hello world", 2) == ".."

    def test_negative_limit_raises(self):
        import pytest

        with pytest.raises(ValueError):
            truncate("x", -1)


class TestWordCount:
    def test_basic(self):
        assert word_count("the quick brown fox") == 4

    def test_extra_whitespace(self):
        assert word_count("  a   b  ") == 2

    def test_empty(self):
        assert word_count("") == 0


class TestGreet:
    def test_returns_greeting(self):
        assert greet("Roee") == "Hello, Roee!"
