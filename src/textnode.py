from enum import Enum

from leafnode import LeafNode


class TextType(Enum):
    """Used to select the type of text at a given text node

    Covers the most common types of text seen in a Markdown document.
    """

    TEXT = "text"
    """
    Normal text, i.e., the kind of text that makes up the majority of any Markdown
    document
    """
    BOLD = "bold"
    """
    Bold text. Any text enclosed in two pairs of asterisks or underscores.
    """
    ITALIC = "italic"
    """
    Italic text. Any text enclosed in a single pair of asterisks or underscores.
    """
    CODE = "code"
    """
    Code block. Any text that is part of a code block. In Markdown code blocks are
    represented by three pairs of backticks (`)
    """
    LINK = "link"
    """
    A URL. Any text string representing a URL.
    """
    IMAGE = "image"
    """
    Image link. Any text string representing a link to an image. Can be a URL or file
    path.
    """


class TextNode:
    """Represents a text node within a larger HTML document tree.

    Essentially an object for representing the kinds of text that you're most likely to
    see in a Markdown document.

    Parameters
    ----------
    text: str
        The text content of the node
    text_type: int
        The type of text this node contains. Expected to be a member of the `TextType`
        enum
    url: str | None
        The URL of the link or image if the text is a link. Default: None
    """

    def __init__(self, text: str, text_type: TextType, url: str | None = None) -> None:
        self.text: str = text
        self.text_type: TextType = text_type
        self.url: str | None = url

    def __eq__(self, other: object, /) -> bool:
        if not isinstance(other, TextNode):
            return NotImplemented
        return (self.text, self.text_type, self.url) == (
            other.text,
            other.text_type,
            other.url,
        )

    def __repr__(self) -> str:
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html(text_node: TextNode) -> LeafNode:
    """Convert `TextNode` into `LeafNode`

    `TextNode` is converted into the `LeafNode` corresponding to it's `text_type`
    attribute.

    Parameters
    ----------
    `text_node`: TextNode
        A `TextNode` object

    Returns
    -------
    `LeafNode`
        A `LeafNode` object that matches `text_node`'s `text_type` attribute
    """
    if not isinstance(text_node.text_type, TextType):
        raise TypeError("`text_node.text_type` must be of type `TextType`")
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            if text_node.url is not None:
                return LeafNode("a", text_node.text, {"href": text_node.url})
            else:
                return LeafNode("a", text_node.text, {"href": ""})
        case TextType.IMAGE:
            if text_node.url is not None:
                return LeafNode(
                    "img", "", {"src": text_node.url, "alt": text_node.text}
                )
            raise ValueError("`src` parameter recieved no value")
        case _:
            # Not sure if I even need this. Will keep for now.
            raise ValueError("`text_node` does not match any `TextType` member")
