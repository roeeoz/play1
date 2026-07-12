from testbed_utils.textutils import romanize, slugify, truncate, word_count


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


class TestRomanize:
    def test_single_digits(self):
        assert romanize(1) == "I"
        assert romanize(4) == "IV"
        assert romanize(5) == "V"
        assert romanize(9) == "IX"

    def test_tens(self):
        assert romanize(10) == "X"
        assert romanize(40) == "XL"
        assert romanize(50) == "L"
        assert romanize(90) == "XC"

    def test_hundreds(self):
        assert romanize(100) == "C"
        assert romanize(400) == "CD"
        assert romanize(500) == "D"
        assert romanize(900) == "CM"

    def test_thousands(self):
        assert romanize(1000) == "M"
        assert romanize(3000) == "MMM"

    def test_compound(self):
        assert romanize(2024) == "MMXXIV"
        assert romanize(1999) == "MCMXCIX"
        assert romanize(3999) == "MMMCMXCIX"

    def test_out_of_range_raises(self):
        import pytest

        with pytest.raises(ValueError):
            romanize(0)
        with pytest.raises(ValueError):
            romanize(4000)

    def test_non_integer_raises(self):
        import pytest

        with pytest.raises(TypeError):
            romanize(3.5)
