import unittest

from leafnode import LeafNode
from parentnode import ParentNode


class TestParentNode(unittest.TestCase):
    def test_value_error_tag(self):
        node = ParentNode(None, [LeafNode(None, "Just some text in a leaf node")])
        self.assertRaises(ValueError, node.to_html)

    def test_value_error_children(self):
        node = ParentNode("p", None)
        self.assertRaises(ValueError, node.to_html)

    def test_leaf_node_children_single(self):
        node = ParentNode("p", [LeafNode("b", "Bold text")])
        want = "<p><b>Bold text</b></p>"
        self.assertEqual(node.to_html(), want)

    def test_leaf_node_children_single_with_props(self):
        node = ParentNode(
            "p",
            [
                LeafNode(
                    "a",
                    "Check this out!",
                    {"href": "https://www.homestarrunner.com", "target": "_blank"},
                ),
            ],
        )
        want = (
            '<p><a href="https://www.homestarrunner.com" target="_blank">'
            "Check this out!</a></p>"
        )
        self.assertEqual(node.to_html(), want)

    def test_leaf_node_children_single_value_error(self):
        node = ParentNode("p", [LeafNode(None, None)])
        self.assertRaises(ValueError, node.to_html)

    def test_leaf_node_children_multiple(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        want = "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>"
        self.assertEqual(node.to_html(), want)

    def test_leaf_node_children_multiple_value_error(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
                LeafNode(None, None),
            ],
        )
        self.assertRaises(ValueError, node.to_html)

    def test_parent_node_children(self):
        pnode01 = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode("i", "Italic text"),
            ],
        )
        pnode02 = ParentNode(
            "div",
            [
                LeafNode(None, "Regular old text"),
                LeafNode("a", "A link", {"href": "https://www.google.com"}),
            ],
        )
        pnode = ParentNode("div", [pnode01, pnode02])
        want = (
            "<div><div><b>Bold text</b><i>Italic text</i></div>"
            '<div>Regular old text<a href="https://www.google.com">A link</a>'
            "</div></div>"
        )
        self.assertEqual(pnode.to_html(), want)

    def test_parent_node_children_value_error(self):
        pnode01 = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode("i", "Italic text"),
            ],
        )
        pnode02 = ParentNode(
            "div",
            [
                LeafNode(None, "Regular old text"),
                LeafNode(None, None),
            ],
        )
        pnode = ParentNode("div", [pnode01, pnode02])
        self.assertRaises(ValueError, pnode.to_html)

    def test_parent_node_children_nested(self):
        pnode_inner = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode("i", "Italic text"),
            ],
        )
        pnode_outer = ParentNode(
            "div",
            [
                LeafNode(None, "Regular old text"),
                LeafNode("a", "A link", {"href": "https://www.google.com"}),
                pnode_inner,
            ],
        )
        pnode = ParentNode("div", [pnode_outer])
        want = (
            '<div><div>Regular old text<a href="https://www.google.com">A link</a>'
            "<div><b>Bold text</b><i>Italic text</i></div></div></div>"
        )
        self.assertEqual(pnode.to_html(), want)

    def test_parent_node_children_nested_value_error_inner(self):
        pnode_inner = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode("i", "Italic text"),
                LeafNode(None, None),
            ],
        )
        pnode_outer = ParentNode(
            "div",
            [
                LeafNode(None, "Regular old text"),
                LeafNode("a", "A link", {"href": "https://www.google.com"}),
                pnode_inner,
            ],
        )
        pnode = ParentNode("div", [pnode_outer])
        self.assertRaises(ValueError, pnode.to_html)

    def test_parent_node_children_nested_value_error_outer(self):
        pnode_inner = ParentNode(
            "div",
            [
                LeafNode("b", "Bold text"),
                LeafNode("i", "Italic text"),
            ],
        )
        pnode_outer = ParentNode(
            "div",
            [
                LeafNode(None, "Regular old text"),
                LeafNode("a", "A link", {"href": "https://www.google.com"}),
                LeafNode(None, None),
                pnode_inner,
            ],
        )
        pnode = ParentNode("div", [pnode_outer])
        self.assertRaises(ValueError, pnode.to_html)
