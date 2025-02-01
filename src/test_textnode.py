import unittest

from textnode import TextNode, TextType


# Tests specifically for the `TextNode` class
# Will need to think about cleaning up some of these tests. I feel like a good chunk of
# them aren't necessary.
class TestTextNode(unittest.TestCase):
    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        want = 'TextNode("This is a text node", BOLD, "https://www.google.com")'
        self.assertEqual(repr(node), want)

    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_eq_with_url(self):
        node = TextNode(
            "This is a text node", TextType.BOLD, "https://www.homestarrunner.com"
        )
        node2 = TextNode(
            "This is a text node", TextType.BOLD, "https://www.homestarrunner.com"
        )
        self.assertEqual(node, node2)

    def test_eq_when_url_set_to_none(self):
        node = TextNode("This is a text node", TextType.BOLD, None)
        node2 = TextNode("This is a text node", TextType.BOLD, None)
        self.assertEqual(node, node2)

    def test_eq_for_diff_type(self):
        node = TextNode("This is a text node", TextType.TEXT)
        node2 = TextNode("This is a text node", TextType.TEXT)
        self.assertEqual(node, node2)

    def test_eq_for_diff_text(self):
        node = TextNode("A new text string", TextType.BOLD)
        node2 = TextNode("A new text string", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_not_eq_for_different_text(self):
        node = TextNode("String A", TextType.BOLD)
        node2 = TextNode("String B", TextType.BOLD)
        self.assertNotEqual(node, node2)

    def test_not_eq_for_different_type(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_not_eq_for_different_url(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.github.com")
        node2 = TextNode("This is a text node", TextType.BOLD, "https://www.gitlab.com")
        self.assertNotEqual(node, node2)


if __name__ == "__main__":
    _ = unittest.main()
