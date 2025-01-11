import unittest
from enum import Enum

from textnode import TextNode, TextType, text_node_to_html


# Tests specifically for the `TextNode` class
# Will need to think about cleaning up some of these tests. I feel like a good chunk of
# them aren't necessary.
class TestTextNode(unittest.TestCase):
    def test_repr(self):
        node = TextNode("This is a text node", TextType.BOLD, "https://www.google.com")
        want = "TextNode(This is a text node, bold, https://www.google.com)"
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


# Tests specifically for the `text_node_to_html` function
# Need to figure out how to test for `TextNode` defined using incorrect `TextType`
# member
class TestTextNodeToHTML(unittest.TestCase):
    def test_create_node_wrong_enum(self):
        class DummyEnum(Enum):
            POODONKIS = "poodonkis"

        text_node = TextNode(
            "A text node with incorrect TextType enum", DummyEnum.POODONKIS
        )
        with self.assertRaises(TypeError):
            _ = text_node_to_html(text_node)

    def test_create_node_type_text(self):
        text_node = TextNode("A test node", TextType.TEXT)
        leaf = text_node_to_html(text_node)
        self.assertEqual(text_node.text, leaf.value)
        self.assertIsNone(leaf.tag)
        self.assertIsNone(leaf.props)

    def test_create_node_type_bold(self):
        text_node = TextNode("Bold text", TextType.BOLD)
        leaf = text_node_to_html(text_node)
        self.assertEqual(text_node.text, leaf.value)
        self.assertEqual(leaf.tag, "b")
        self.assertIsNone(leaf.props)

    def test_create_node_type_italic(self):
        text_node = TextNode("Italic text", TextType.ITALIC)
        leaf = text_node_to_html(text_node)
        self.assertEqual(text_node.text, leaf.value)
        self.assertEqual(leaf.tag, "i")
        self.assertIsNone(leaf.props)

    def test_create_node_type_code(self):
        text_node = TextNode("Some code", TextType.CODE)
        leaf = text_node_to_html(text_node)
        self.assertEqual(text_node.text, leaf.value)
        self.assertEqual(leaf.tag, "code")
        self.assertIsNone(leaf.props)

    def test_create_node_type_link(self):
        text_node = TextNode("A link", TextType.LINK, "https://www.google.com")
        leaf = text_node_to_html(text_node)
        self.assertEqual(text_node.text, leaf.value)
        self.assertEqual(leaf.tag, "a")
        self.assertEqual(leaf.props, {"href": "https://www.google.com"})

    def test_create_node_type_link_no_url(self):
        text_node = TextNode("A link with no URL", TextType.LINK)
        leaf = text_node_to_html(text_node)
        self.assertEqual(text_node.text, leaf.value)
        self.assertEqual(leaf.tag, "a")
        self.assertEqual(leaf.props, {"href": ""})

    def test_create_node_type_image(self):
        text_node = TextNode("An image", TextType.IMAGE, "https://www.img.com/api/test")
        leaf = text_node_to_html(text_node)
        self.assertEqual(leaf.value, "")
        self.assertEqual(leaf.tag, "img")
        self.assertEqual(leaf.props, {"src": text_node.url, "alt": text_node.text})

    def test_create_node_type_image_no_src(self):
        text_node = TextNode("An image", TextType.IMAGE)
        with self.assertRaises(ValueError):
            _ = text_node_to_html(text_node)


if __name__ == "__main__":
    _ = unittest.main()
