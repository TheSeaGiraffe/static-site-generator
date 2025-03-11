import unittest

from htmlnode import HTMLNode


class TestHTMLNode(unittest.TestCase):
    # Don't know if I even need this test
    def test_to_html_paragraph(self):
        node = HTMLNode("p", "This is just some text")
        self.assertEqual(node.to_html(), "<p>This is just some text</p>")

    def test_to_html_props(self):
        node = HTMLNode("a", "A link to some site", None, {"href": "www.google.com"})
        self.assertEqual(
            node.to_html(), '<a href="www.google.com">A link to some site</a>'
        )

    def test_repr_str_default(self):
        node = HTMLNode()
        want = "HTMLNode(None, None, None, None)"
        self.assertEqual(repr(node), want)

    def test_repr_str_tag_value(self):
        node = HTMLNode("p", "Some text")
        want = "HTMLNode(p, Some text, None, None)"
        self.assertEqual(repr(node), want)

    def test_repr_str_children(self):
        node_a = HTMLNode()
        node_b = HTMLNode()
        node_main = HTMLNode(children=[node_a, node_b])
        want = (
            "HTMLNode(None, None, [HTMLNode(None, None, None, None), "
            "HTMLNode(None, None, None, None)], None)"
        )
        self.assertEqual(repr(node_main), want)

    def test_repr_str_props(self):
        props = {
            "href": "https://www.google.com",
            "referrerpolicy": "origin",
            "target": "_blank",
        }
        node = HTMLNode(props=props)
        want = (
            "HTMLNode(None, None, None, {'href': 'https://www.google.com', "
            "'referrerpolicy': 'origin', 'target': '_blank'})"
        )
        self.assertEqual(repr(node), want)

    def test_props_to_html(self):
        props = {
            "href": "https://www.google.com",
            "referrerpolicy": "origin",
            "target": "_blank",
        }
        node = HTMLNode(props=props)
        want = ' href="https://www.google.com" referrerpolicy="origin" target="_blank"'
        self.assertEqual(node.props_to_html(), want)
