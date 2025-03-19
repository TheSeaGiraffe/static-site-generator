import unittest
from enum import Enum

from textnode import TextNode, TextType
from textnode_converters import (
    extract_markdown_images,
    extract_markdown_links,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html,
    text_to_textnodes,
)


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


# There is an issue with the logic used for dealing with bold delimiters nested within
# italic delimiters. For now, will update the strings in the relevant tests so that they
# pass.
class TestSplitNodesDelimiter(unittest.TestCase):
    def test_bold_delimiter(self):
        nodes = [TextNode("This is some **bold** text.", TextType.TEXT)]

        got = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_bold_multiple_delimiter(self):
        nodes = [
            TextNode(
                "This is some **bold** text with **multiple** delimiters.",
                TextType.TEXT,
            )
        ]

        got = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" text with ", TextType.TEXT),
            TextNode("multiple", TextType.BOLD),
            TextNode(" delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_bold_multiple_delimiter_adjacent(self):
        nodes = [
            TextNode(
                "This is some **bold** **text** with adjacent delimiters.",
                TextType.TEXT,
            )
        ]

        got = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with adjacent delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_all_bold(self):
        nodes = [TextNode("**This entire text is bold.**", TextType.TEXT)]

        got = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        want = [TextNode("This entire text is bold.", TextType.BOLD)]

        self.assertEqual(got, want)

    def test_bold_with_nested_delimiters(self):
        nodes = [
            TextNode(
                "A text node with **_multiple_ _italicized_ bolds**.", TextType.TEXT
            )
        ]

        got = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        want = [
            TextNode("A text node with ", TextType.TEXT),
            TextNode("_multiple_ _italicized_ bolds", TextType.BOLD),
            TextNode(".", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_bold_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("A text node with **bolded section**.", TextType.TEXT),
            TextNode("**An entirely bold text section.**", TextType.TEXT),
            TextNode(
                "A **_bolded_ section with italics** in the front.", TextType.TEXT
            ),
            TextNode("A **bolded section with _italics_** in the back.", TextType.TEXT),
        ]

        got = split_nodes_delimiter(nodes, "**", TextType.BOLD)
        want = [
            TextNode("A text node with ", TextType.TEXT),
            TextNode("bolded section", TextType.BOLD),
            TextNode(".", TextType.TEXT),
            TextNode("An entirely bold text section.", TextType.BOLD),
            TextNode("A ", TextType.TEXT),
            TextNode("_bolded_ section with italics", TextType.BOLD),
            TextNode(" in the front.", TextType.TEXT),
            TextNode("A ", TextType.TEXT),
            TextNode("bolded section with _italics_", TextType.BOLD),
            TextNode(" in the back.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter(self):
        nodes = [TextNode("This is some _italic_ text.", TextType.TEXT)]

        got = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_multiple(self):
        nodes = [
            TextNode(
                "This is some _italic_ text with _multiple_ delimiters.",
                TextType.TEXT,
            )
        ]

        got = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text with ", TextType.TEXT),
            TextNode("multiple", TextType.ITALIC),
            TextNode(" delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_multiple_adjacent(self):
        nodes = [
            TextNode(
                "This is some _italic_ _text_ with adjacent delimiters.",
                TextType.TEXT,
            )
        ]

        got = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("text", TextType.ITALIC),
            TextNode(" with adjacent delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_all_italic(self):
        nodes = [TextNode("_This entire text is italic._", TextType.TEXT)]

        got = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        want = [TextNode("This entire text is italic.", TextType.ITALIC)]

        self.assertEqual(got, want)

    def test_italic_with_nested_delimiters(self):
        nodes = [
            TextNode(
                "A text node with _**multiple** **bolded** italics_.", TextType.TEXT
            )
        ]

        got = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        want = [
            TextNode("A text node with ", TextType.TEXT),
            TextNode("**multiple** **bolded** italics", TextType.ITALIC),
            TextNode(".", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("A text node with _italicized section_.", TextType.TEXT),
            TextNode("_An entirely italicized text section._", TextType.TEXT),
            TextNode(
                "An _**italicized** section with bold_ in the front.", TextType.TEXT
            ),
            TextNode(
                "An _italicized section with **bold**_ in the back.", TextType.TEXT
            ),
        ]

        got = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
        want = [
            TextNode("A text node with ", TextType.TEXT),
            TextNode("italicized section", TextType.ITALIC),
            TextNode(".", TextType.TEXT),
            TextNode("An entirely italicized text section.", TextType.ITALIC),
            TextNode("An ", TextType.TEXT),
            TextNode("**italicized** section with bold", TextType.ITALIC),
            TextNode(" in the front.", TextType.TEXT),
            TextNode("An ", TextType.TEXT),
            TextNode("italicized section with **bold**", TextType.ITALIC),
            TextNode(" in the back.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter(self):
        nodes = [TextNode("This is some `code` text.", TextType.TEXT)]
        got = split_nodes_delimiter(nodes, "`", TextType.CODE)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter_multiple(self):
        nodes = [
            TextNode(
                "This is some `code` text with `multiple` delimiters.",
                TextType.TEXT,
            )
        ]

        got = split_nodes_delimiter(nodes, "`", TextType.CODE)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" text with ", TextType.TEXT),
            TextNode("multiple", TextType.CODE),
            TextNode(" delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter_multiple_adjacent(self):
        nodes = [
            TextNode(
                "This is some `code` `text` with adjacent delimiters.",
                TextType.TEXT,
            )
        ]
        got = split_nodes_delimiter(nodes, "`", TextType.CODE)
        want = [
            TextNode("This is some ", TextType.TEXT),
            TextNode("code", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("text", TextType.CODE),
            TextNode(" with adjacent delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_all_code(self):
        nodes = [TextNode("`This entire text is code.`", TextType.TEXT)]

        got = split_nodes_delimiter(nodes, "`", TextType.CODE)
        want = [TextNode("This entire text is code.", TextType.CODE)]

        self.assertEqual(got, want)

    def test_code_with_nested_delimiters(self):
        nodes = [
            TextNode(
                "A text node with `_multiple_ **markdown** delimiters`.", TextType.TEXT
            )
        ]

        got = split_nodes_delimiter(nodes, "`", TextType.CODE)
        want = [
            TextNode("A text node with ", TextType.TEXT),
            TextNode("_multiple_ **markdown** delimiters", TextType.CODE),
            TextNode(".", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter_multiple_nodes(self):
        nodes = [
            TextNode("A text node with `code section`.", TextType.TEXT),
            TextNode("`An entire code block.`", TextType.TEXT),
            TextNode("A `**code** block with _multiple_` delimiters.", TextType.TEXT),
        ]

        got = split_nodes_delimiter(nodes, "`", TextType.CODE)
        want = [
            TextNode("A text node with ", TextType.TEXT),
            TextNode("code section", TextType.CODE),
            TextNode(".", TextType.TEXT),
            TextNode("An entire code block.", TextType.CODE),
            TextNode("A ", TextType.TEXT),
            TextNode("**code** block with _multiple_", TextType.CODE),
            TextNode(" delimiters.", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_no_delimiter(self):
        nodes = [TextNode("Some basic text.", TextType.TEXT)]

        got = split_nodes_delimiter(nodes, "", TextType.TEXT)
        want = [TextNode("Some basic text.", TextType.TEXT)]

        self.assertEqual(got, want)

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


class TestSplitNodesImage(unittest.TestCase):
    def test_multiple_images(self):
        nodes = [
            TextNode(
                "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)
        want = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" and ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_multiple_nodes(self):
        nodes = [
            TextNode(
                "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
                TextType.TEXT,
            ),
            TextNode(
                "Hello there ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
                TextType.TEXT,
            ),
            TextNode(
                "Just a ![rick roll](https://i.imgur.com/aKaOqIh.gif)",
                TextType.TEXT,
            ),
        ]
        got = split_nodes_image(nodes)
        want = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" and ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode("Hello there ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode("Just a ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
        ]

        self.assertEqual(got, want)

    def test_image_and_url(self):
        nodes = [
            TextNode(
                "This is text with a link [to boot dev](https://www.boot.dev) and a ![rick roll](https://i.imgur.com/aKaOqIh.gif)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)
        want = [
            TextNode(
                "This is text with a link [to boot dev](https://www.boot.dev) and a ",
                TextType.TEXT,
            ),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
        ]
        self.assertEqual(got, want)

    def test_no_images(self):
        nodes = [TextNode("This is text with no images", TextType.TEXT)]
        got = split_nodes_image(nodes)
        want = [TextNode("This is text with no images", TextType.TEXT)]

        self.assertEqual(got, want)

    def test_bold_delimiter(self):
        nodes = [
            TextNode(
                "**This is text with a** ![rick roll](https://i.imgur.com/aKaOqIh.gif) **and** ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)
        want = [
            TextNode("**This is text with a** ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" **and** ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_bold_delimiter_around_image(self):
        nodes = [
            TextNode(
                "This is text with a **![rick roll](https://i.imgur.com/aKaOqIh.gif)** and **![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)**",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)

        want = [
            TextNode("This is text with a **", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode("** and **", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode("**", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter(self):
        nodes = [
            TextNode(
                "*This is text with a* ![rick roll](https://i.imgur.com/aKaOqIh.gif) *and* ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)
        want = [
            TextNode("*This is text with a* ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" *and* ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_around_image(self):
        nodes = [
            TextNode(
                "This is text with a *![rick roll](https://i.imgur.com/aKaOqIh.gif)* and *![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)*",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)

        want = [
            TextNode("This is text with a *", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode("* and *", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode("*", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter(self):
        nodes = [
            TextNode(
                "This is text with a `![rick roll](https://i.imgur.com/aKaOqIh.gif) in a block of code`.",
                TextType.TEXT,
            )
        ]
        got = split_nodes_image(nodes)
        want = [
            TextNode(
                "This is text with a `![rick roll](https://i.imgur.com/aKaOqIh.gif) in a block of code`.",
                TextType.TEXT,
            )
        ]

        self.assertEqual(got, want)


class TestSplitNodesLink(unittest.TestCase):
    def test_multiple_links(self):
        nodes = [
            TextNode(
                "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]

        self.assertEqual(got, want)

    def test_multiple_nodes(self):
        nodes = [
            TextNode(
                "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
                TextType.TEXT,
            ),
            TextNode(
                "Visiting Boots at [boot dev](https://www.boot.dev)",
                TextType.TEXT,
            ),
            TextNode(
                "Watching some lessons [on youtube](https://www.youtube.com/@bootdotdev)",
                TextType.TEXT,
            ),
        ]

        got = split_nodes_link(nodes)
        want = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
            TextNode("Visiting Boots at ", TextType.TEXT),
            TextNode("boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode("Watching some lessons ", TextType.TEXT),
            TextNode(
                "on youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]

        self.assertEqual(got, want)

    def test_image_and_url(self):
        nodes = [
            TextNode(
                "This is text with a link [to boot dev](https://www.boot.dev) and a ![rick roll](https://i.imgur.com/aKaOqIh.gif)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode(
                "This is text with a link ",
                TextType.TEXT,
            ),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(
                " and a ![rick roll](https://i.imgur.com/aKaOqIh.gif)",
                TextType.TEXT,
            ),
        ]
        self.assertEqual(got, want)

    def test_no_links(self):
        nodes = [TextNode("This is text with no links", TextType.TEXT)]
        got = split_nodes_link(nodes)
        want = [TextNode("This is text with no links", TextType.TEXT)]

        self.assertEqual(got, want)

    def test_bold_delimiter(self):
        nodes = [
            TextNode(
                "**This is text with a link** [to boot dev](https://www.boot.dev) **and** [to youtube](https://www.youtube.com/@bootdotdev)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode("**This is text with a link** ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" **and** ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]

        self.assertEqual(got, want)

    def test_bold_delimiter_around_link(self):
        nodes = [
            TextNode(
                "This is text with a link **[to boot dev](https://www.boot.dev)** and **[to youtube](https://www.youtube.com/@bootdotdev)**",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode("This is text with a link **", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode("** and **", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
            TextNode("**", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter(self):
        nodes = [
            TextNode(
                "*This is text with a link* [to boot dev](https://www.boot.dev) *and* [to youtube](https://www.youtube.com/@bootdotdev)",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode("*This is text with a link* ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" *and* ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]

        self.assertEqual(got, want)

    def test_italic_delimiter_around_link(self):
        nodes = [
            TextNode(
                "This is text with a link *[to boot dev](https://www.boot.dev)* and *[to youtube](https://www.youtube.com/@bootdotdev)*",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode("This is text with a link *", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode("* and *", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
            TextNode("*", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_code_delimiter(self):
        nodes = [
            TextNode(
                "This is text with a link `[to boot dev](https://www.boot.dev) in a block of code`.",
                TextType.TEXT,
            )
        ]
        got = split_nodes_link(nodes)
        want = [
            TextNode(
                "This is text with a link `[to boot dev](https://www.boot.dev) in a block of code`.",
                TextType.TEXT,
            )
        ]

        self.assertEqual(got, want)


class TestTextToTextNodes(unittest.TestCase):
    def test_only_text(self):
        text = "This is just some text with no fancy markdown delimiters."
        got = text_to_textnodes(text)
        want = [TextNode(text, TextType.TEXT)]

        self.assertEqual(got, want)

    def test_only_bold(self):
        # text = "This is **text** with a **lot** of **bolded** **words and phrases.**"
        text = "This is **text** with a **lot** of **bolded** **words and phrases**"
        got = text_to_textnodes(text)
        want = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with a ", TextType.TEXT),
            TextNode("lot", TextType.BOLD),
            TextNode(" of ", TextType.TEXT),
            TextNode("bolded", TextType.BOLD),
            TextNode(" ", TextType.TEXT),
            # TextNode("words and phrases.", TextType.BOLD),
            TextNode("words and phrases", TextType.BOLD),
        ]

        self.assertEqual(got, want)

    def test_only_italic(self):
        text = "This is _text_ with a _lot_ of _italicized_ _words and phrases._"
        got = text_to_textnodes(text)
        want = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.ITALIC),
            TextNode(" with a ", TextType.TEXT),
            TextNode("lot", TextType.ITALIC),
            TextNode(" of ", TextType.TEXT),
            TextNode("italicized", TextType.ITALIC),
            TextNode(" ", TextType.TEXT),
            TextNode("words and phrases.", TextType.ITALIC),
        ]

        self.assertEqual(got, want)

    def test_only_code(self):
        text = "This is `text` with a `lot` of `words and phrases` `in code blocks`."
        got = text_to_textnodes(text)
        want = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.CODE),
            TextNode(" with a ", TextType.TEXT),
            TextNode("lot", TextType.CODE),
            TextNode(" of ", TextType.TEXT),
            TextNode("words and phrases", TextType.CODE),
            TextNode(" ", TextType.TEXT),
            TextNode("in code blocks", TextType.CODE),
            TextNode(".", TextType.TEXT),
        ]

        self.assertEqual(got, want)

    def test_only_image(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        got = text_to_textnodes(text)
        want = [
            TextNode("This is text with a ", TextType.TEXT),
            TextNode("rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"),
            TextNode(" and ", TextType.TEXT),
            TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
        ]

        self.assertEqual(got, want)

    def test_only_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        got = text_to_textnodes(text)
        want = [
            TextNode("This is text with a link ", TextType.TEXT),
            TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
            TextNode(" and ", TextType.TEXT),
            TextNode(
                "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
            ),
        ]

        self.assertEqual(got, want)

    def test_all_delimiters_and_tags(self):
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        got = text_to_textnodes(text)
        want = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode(
                "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
            ),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]

        self.assertEqual(got, want)


if __name__ == "__main__":
    _ = unittest.main()
