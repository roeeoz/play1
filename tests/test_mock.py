from summarize.mock import mock_summarize


def test_mock_summarize_single_line():
    assert mock_summarize("Hello world") == "mock summary: Hello world"


def test_mock_summarize_first_line_only():
    assert mock_summarize("Hello world\nLine 2\nLine 3") == "mock summary: Hello world"


def test_mock_summarize_prefix():
    result = mock_summarize("Some text")
    assert result.startswith("mock summary:")


def test_mock_summarize_empty_lines():
    result = mock_summarize("First\n\nThird")
    assert result == "mock summary: First"
