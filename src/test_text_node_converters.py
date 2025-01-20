import unittest
from enum import Enum

from text_node_converters import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    text_node_to_html,
)
from textnode import TextNode, TextType


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


class TestSplitNodesDelimiter(unittest.TestCase):
    def check_nodes(
        self, nodes: list[TextNode], node_texts: list[str], node_types: list[TextType]
    ):
        for node, node_text, node_type in zip(nodes, node_texts, node_types):
            self.assertEqual(node.text, node_text)
            self.assertEqual(node.text_type, node_type)

    def test_bold_delimiter(self):
        nodes = [TextNode("This is some **bold** text.", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 3)

        new_node_texts = ["This is some ", "bold", " text."]
        new_node_types = [TextType.TEXT, TextType.BOLD, TextType.TEXT]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_bold_multiple_delimiter(self):
        nodes = [
            TextNode(
                "This is some **bold** text with **multiple** delimiters.",
                TextType.TEXT,
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 5)

        new_node_texts = [
            "This is some ",
            "bold",
            " text with ",
            "multiple",
            " delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_bold_multiple_delimiter_adjacent(self):
        nodes = [
            TextNode(
                "This is some **bold** **text** with adjacent delimiters.",
                TextType.TEXT,
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 4)

        new_node_texts = [
            "This is some ",
            "bold",
            "text",
            " with adjacent delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.BOLD,
            TextType.BOLD,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_all_bold(self):
        nodes = [TextNode("**This entire text is bold.**", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 1)

        new_node_texts = [
            "This entire text is bold.",
        ]
        new_node_types = [
            TextType.BOLD,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_bold_with_nested_delimiters(self):
        nodes = [
            TextNode(
                "A text node with ***multiple* *italicized* bolds**.", TextType.TEXT
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 3)

        new_node_texts = [
            "A text node with ",
            "*multiple* *italicized* bolds",
            ".",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_bold_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("A text node with **bolded section**.", TextType.TEXT),
            TextNode("**An entirely bold text section.**", TextType.TEXT),
            TextNode(
                "A ***bolded* section with italics** in the front.", TextType.TEXT
            ),
            TextNode("A **bolded section with *italics*** in the back.", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)

        self.assertEqual(len(new_nodes), 10)

        new_node_texts = [
            "A text node with ",
            "bolded section",
            ".",
            "An entirely bold text section.",
            "A ",
            "*bolded* section with italics",
            " in the front.",
            "A ",
            "bolded section with *italics*",
            " in the back.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
            TextType.TEXT,
            TextType.BOLD,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_italic_delimiter(self):
        nodes = [TextNode("This is some *italic* text.", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        self.assertEqual(len(new_nodes), 3)

        new_node_texts = ["This is some ", "italic", " text."]
        new_node_types = [TextType.TEXT, TextType.ITALIC, TextType.TEXT]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_italic_delimiter_multiple(self):
        nodes = [
            TextNode(
                "This is some *italic* text with *multiple* delimiters.",
                TextType.TEXT,
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        self.assertEqual(len(new_nodes), 5)

        new_node_texts = [
            "This is some ",
            "italic",
            " text with ",
            "multiple",
            " delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_italic_delimiter_multiple_adjacent(self):
        nodes = [
            TextNode(
                "This is some *italic* *text* with adjacent delimiters.",
                TextType.TEXT,
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        self.assertEqual(len(new_nodes), 4)

        new_node_texts = [
            "This is some ",
            "italic",
            "text",
            " with adjacent delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.ITALIC,
            TextType.ITALIC,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_all_italic(self):
        nodes = [TextNode("*This entire text is italic.*", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        self.assertEqual(len(new_nodes), 1)

        new_node_texts = [
            "This entire text is italic.",
        ]
        new_node_types = [
            TextType.ITALIC,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_italic_with_nested_delimiters(self):
        nodes = [
            TextNode(
                "A text node with ***multiple** **bolded** italics*.", TextType.TEXT
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        self.assertEqual(len(new_nodes), 3)

        new_node_texts = [
            "A text node with ",
            "**multiple** **bolded** italics",
            ".",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_italic_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("A text node with *italicized section*.", TextType.TEXT),
            TextNode("*An entirely italicized text section.*", TextType.TEXT),
            TextNode(
                "An ***italicized** section with bold* in the front.", TextType.TEXT
            ),
            TextNode(
                "An *italicized section with **bold*** in the back.", TextType.TEXT
            ),
        ]
        new_nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)

        self.assertEqual(len(new_nodes), 10)

        new_node_texts = [
            "A text node with ",
            "italicized section",
            ".",
            "An entirely italicized text section.",
            "An ",
            "**italicized** section with bold",
            " in the front.",
            "An ",
            "italicized section with **bold**",
            " in the back.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
            TextType.TEXT,
            TextType.ITALIC,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_code_delimiter(self):
        nodes = [TextNode("This is some `code` text.", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(len(new_nodes), 3)

        new_node_texts = ["This is some ", "code", " text."]
        new_node_types = [TextType.TEXT, TextType.CODE, TextType.TEXT]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_code_delimiter_multiple(self):
        nodes = [
            TextNode(
                "This is some `code` text with `multiple` delimiters.",
                TextType.TEXT,
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(len(new_nodes), 5)

        new_node_texts = [
            "This is some ",
            "code",
            " text with ",
            "multiple",
            " delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.CODE,
            TextType.TEXT,
            TextType.CODE,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_code_delimiter_multiple_adjacent(self):
        nodes = [
            TextNode(
                "This is some `code` `text` with adjacent delimiters.",
                TextType.TEXT,
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(len(new_nodes), 4)

        new_node_texts = [
            "This is some ",
            "code",
            "text",
            " with adjacent delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.CODE,
            TextType.CODE,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_all_code(self):
        nodes = [TextNode("`This entire text is code.`", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(len(new_nodes), 1)

        new_node_texts = [
            "This entire text is code.",
        ]
        new_node_types = [
            TextType.CODE,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_code_with_nested_delimiters(self):
        nodes = [
            TextNode(
                "A text node with `*multiple* **markdown** delimiters`.", TextType.TEXT
            )
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(len(new_nodes), 3)

        new_node_texts = [
            "A text node with ",
            "*multiple* **markdown** delimiters",
            ".",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.CODE,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_code_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("A text node with `code section`.", TextType.TEXT),
            TextNode("`An entire code block.`", TextType.TEXT),
            TextNode("A `**code** block with *multiple*` delimiters.", TextType.TEXT),
        ]
        new_nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)

        self.assertEqual(len(new_nodes), 7)

        new_node_texts = [
            "A text node with ",
            "code section",
            ".",
            "An entire code block.",
            "A ",
            "**code** block with *multiple*",
            " delimiters.",
        ]
        new_node_types = [
            TextType.TEXT,
            TextType.CODE,
            TextType.TEXT,
            TextType.CODE,
            TextType.TEXT,
            TextType.CODE,
            TextType.TEXT,
        ]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_no_delimiter(self):
        nodes = [TextNode("Some basic text.", TextType.TEXT)]
        new_nodes = split_nodes_delimiter(nodes, "", TextType.TEXT)

        self.assertEqual(len(new_nodes), 1)

        new_node_texts = ["Some basic text."]
        new_node_types = [TextType.TEXT]
        self.check_nodes(new_nodes, new_node_texts, new_node_types)

    def test_invalid_delimiter(self):
        with self.assertRaises(ValueError):
            nodes = [TextNode("Some basic text.", TextType.TEXT)]
            _ = split_nodes_delimiter(nodes, "@", TextType.TEXT)

    def test_mismatched_delim_and_text_type(self):
        with self.assertRaises(ValueError):
            nodes = [TextNode("A text node with a **bold section.**", TextType.TEXT)]
            _ = split_nodes_delimiter(nodes, "**", TextType.ITALIC)

    def test_unbalanced_delimiters(self):
        with self.assertRaises(ValueError):
            nodes = [
                TextNode(
                    "A text node with *unbalanced* italic* delimiters.", TextType.TEXT
                )
            ]
            _ = split_nodes_delimiter(nodes, "*", TextType.ITALIC)


class TestExtractMarkdownImages(unittest.TestCase):
    def test_multiple_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        got = extract_markdown_images(text)
        want = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_image_and_url(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and a ![rick roll](https://i.imgur.com/aKaOqIh.gif)"
        got = extract_markdown_images(text)
        want = [("rick roll", "https://i.imgur.com/aKaOqIh.gif")]

        self.assertEqual(got, want)

    def test_no_images(self):
        text = "This is a text with no images"
        got = extract_markdown_images(text)
        want = []

        self.assertEqual(got, want)

    def test_bold_delimiter(self):
        text = "**This is text with a** ![rick roll](https://i.imgur.com/aKaOqIh.gif) **and** ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        got = extract_markdown_images(text)
        want = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_bold_delimiter_around_image(self):
        text = "This is text with a **![rick roll](https://i.imgur.com/aKaOqIh.gif)** and **![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)**"
        got = extract_markdown_images(text)
        want = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter(self):
        text = "*This is text with a* ![rick roll](https://i.imgur.com/aKaOqIh.gif) *and* ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        got = extract_markdown_images(text)
        want = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_around_image(self):
        text = "This is text with a *![rick roll](https://i.imgur.com/aKaOqIh.gif)* and *![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)*"
        got = extract_markdown_images(text)
        want = [
            ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
            ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter(self):
        text = "This is text with a `![rick roll](https://i.imgur.com/aKaOqIh.gif) in a block of code`."
        got = extract_markdown_images(text)
        want = []

        self.assertEqual(got, want)


class TestExtractMarkdownLinks(unittest.TestCase):
    def test_multiple_urls(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        got = extract_markdown_links(text)
        want = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ]

        self.assertEqual(got, want)

    def test_image_and_url(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and a ![rick roll](https://i.imgur.com/aKa OqIh.gif)"
        got = extract_markdown_links(text)
        want = [("to boot dev", "https://www.boot.dev")]

        self.assertEqual(got, want)

    def test_no_urls(self):
        text = "This is a text with no URLs."
        got = extract_markdown_links(text)
        want = []

        self.assertEqual(got, want)

    def test_bold_delimiter(self):
        text = "**This is text with a link** [to boot dev](https://www.boot.dev) **and** [to youtube](https://www.youtube.com/@bootdotdev)"
        got = extract_markdown_links(text)
        want = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ]

        self.assertEqual(got, want)

    def test_bold_delimiter_around_image(self):
        text = "This is text with a link **[to boot dev](https://www.boot.dev)** and **[to youtube](https://www.youtube.com/@bootdotdev)**"
        got = extract_markdown_links(text)
        want = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter(self):
        text = "*This is text with a link* [to boot dev](https://www.boot.dev) *and* [to youtube](https://www.youtube.com/@bootdotdev)"
        got = extract_markdown_links(text)
        want = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_around_image(self):
        text = "This is text with a link *[to boot dev](https://www.boot.dev)* and *[to youtube](https://www.youtube.com/@bootdotdev)*"
        got = extract_markdown_links(text)
        want = [
            ("to boot dev", "https://www.boot.dev"),
            ("to youtube", "https://www.youtube.com/@bootdotdev"),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter(self):
        text = "This is text with a `link [to boot dev](https://www.boot.dev) in a block of code`."
        got = extract_markdown_links(text)
        want = []

        self.assertEqual(got, want)


if __name__ == "__main__":
    _ = unittest.main()
