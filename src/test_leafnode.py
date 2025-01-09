import unittest

from leafnode import LeafNode


class TestLeafNode(unittest.TestCase):
    def test_value_missing_error(self):
        leaf = LeafNode(None, None)
        self.assertRaises(ValueError, leaf.to_html)

    def test_to_html(self):
        leaf = LeafNode("p", "This is a paragraph of text.")
        want = "<p>This is a paragraph of text.</p>"
        self.assertEqual(leaf.to_html(), want)

    def test_to_html_with_attributes(self):
        leaf = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        want = '<a href="https://www.google.com">Click me!</a>'
        self.assertEqual(leaf.to_html(), want)

    def test_to_html_no_tag(self):
        leaf = LeafNode(None, "This is just some text.")
        want = "This is just some text."
        self.assertEqual(leaf.to_html(), want)
