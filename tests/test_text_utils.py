import pytest

from guestbook.text_utils import word_count


class TestWordCount:
    def test_normal_sentence(self):
        assert word_count("The quick brown fox") == 4

    def test_mixed_whitespace(self):
        assert word_count("  hello\tworld\nfoo  ") == 3

    def test_empty_string(self):
        assert word_count("") == 0

    def test_whitespace_only(self):
        assert word_count("   \t\n") == 0

    def test_non_string_raises(self):
        with pytest.raises(TypeError):
            word_count(None)
        with pytest.raises(TypeError):
            word_count(42)
