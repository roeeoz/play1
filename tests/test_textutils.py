from testbed_utils.textutils import (
    reading_time_minutes,
    sentence_count,
    slugify,
    truncate,
    word_count,
)


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


class TestSentenceCount:
    def test_counts_each_terminal_mark(self):
        assert sentence_count("Is this fast? Yes! It works.") == 3

    def test_no_terminal_punctuation_returns_zero(self):
        assert sentence_count("just some words here") == 0

    def test_run_of_punctuation_counts_each_character(self):
        assert sentence_count("Wait...") == 3


class TestReadingTimeMinutes:
    def test_exact_multiple(self):
        assert reading_time_minutes(200) == 1

    def test_rounds_up_fraction(self):
        assert reading_time_minutes(450) == 3

    def test_minimum_one_minute_for_short_text(self):
        assert reading_time_minutes(10) == 1

    def test_minimum_one_minute_for_zero_words(self):
        assert reading_time_minutes(0) == 1

    def test_importable_from_package_root(self):
        import testbed_utils

        assert testbed_utils.sentence_count is sentence_count
        assert testbed_utils.reading_time_minutes is reading_time_minutes
        assert "sentence_count" in testbed_utils.__all__
        assert "reading_time_minutes" in testbed_utils.__all__
