import unittest

from page_helpers import extract_title


class TestExtractTitle(unittest.TestCase):
    def test_h1_present(self):
        md = """
# Some Markdown Document

This is just some markdown document

With multiple paragraphs

For testing the extract_title function

"""
        want = "Some Markdown Document"
        got = extract_title(md)
        self.assertEqual(got, want)

    def test_other_heading(self):
        md = """
## Not the right header

This is just some markdown document

With multiple paragraphs

For testing the extract_title function

"""
        want = "no title found"
        with self.assertRaises(Exception) as cm:
            _ = extract_title(md)

        got = cm.exception
        self.assertEqual(str(got), want)

    def test_no_h1_heading(self):
        md = """
This is just some markdown document

With multiple paragraphs

For testing the extract_title function

"""
        want = "no title found"
        with self.assertRaises(Exception) as cm:
            _ = extract_title(md)

        got = cm.exception
        self.assertEqual(str(got), want)
