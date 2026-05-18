"""Tests for text filtering functionality."""

import unittest
from app.utils.text_filter import filter_hidden_text


class TestTextFilter(unittest.TestCase):
    """Test cases for the filter_hidden_text function."""

    def test_filter_hidden_text_with_markers(self):
        """Test that text between -- markers is removed and whitespace is cleaned."""
        text = "This is visible --this is hidden-- and this is visible"
        result = filter_hidden_text(text, should_filter=True)
        self.assertEqual(result, "This is visible and this is visible")

    def test_filter_hidden_text_without_filtering(self):
        """Test that text is not filtered when should_filter is False."""
        text = "This is visible --this is hidden-- and this is visible"
        result = filter_hidden_text(text, should_filter=False)
        self.assertEqual(result, text)

    def test_filter_hidden_text_multiple_sections(self):
        """Test filtering multiple hidden sections with whitespace cleanup."""
        text = "Visible --hidden1-- visible --hidden2-- visible"
        result = filter_hidden_text(text, should_filter=True)
        self.assertEqual(result, "Visible visible visible")

    def test_filter_hidden_text_multiline(self):
        """Test filtering multiline hidden text with whitespace cleanup."""
        text = "Visible\n--hidden\nmultiline--\nVisible"
        result = filter_hidden_text(text, should_filter=True)
        self.assertEqual(result, "Visible\nVisible")

    def test_filter_hidden_text_no_markers(self):
        """Test that text without markers is unchanged."""
        text = "This is visible and this is also visible"
        result = filter_hidden_text(text, should_filter=True)
        self.assertEqual(result, text)

    def test_filter_hidden_text_empty_string(self):
        """Test filtering an empty string."""
        text = ""
        result = filter_hidden_text(text, should_filter=True)
        self.assertEqual(result, "")

    def test_filter_hidden_text_only_markers(self):
        """Test text that is only markers."""
        text = "--hidden--"
        result = filter_hidden_text(text, should_filter=True)
        self.assertEqual(result, "")

    def test_filter_hidden_text_unclosed_marker(self):
        """Test text with unclosed marker (should not filter)."""
        text = "Visible --unclosed marker"
        result = filter_hidden_text(text, should_filter=True)
        # Unclosed markers should not be removed
        self.assertEqual(result, text)


if __name__ == '__main__':
    unittest.main()
