from enum import Enum


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
        repr_str = f'TextNode("{self.text}", {self.text_type.name}, '
        repr_str += f'"{self.url}")' if self.url is not None else f"{self.url})"
        return repr_str
