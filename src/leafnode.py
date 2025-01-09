from htmlnode import HTMLNode


class LeafNode(HTMLNode):
    """Represents a leaf node in a HTML document tree

    Effectively an `HTMLNode` without any children. Accordingly, `LeafNode` does not
    take a `children` argument.


    Parameters
    ----------
    tag: str | None
        A string representing the HTML tag name (e.g., "p", "a", "h1", etc.). Setting to
        `None` will cause the `HTMLNode` object to render as raw text.
    value: str | None
        A string representing the value of the HTML tag (e.g., the text inside a
        paragraph). If set to `None`, `HTMLNode` object is assumed to have children.
    props: dict[str, str] | None
        A dictionary of key-value pairs representing the attributes of the HTML tag. For
        example, a link (`<a>` tag) might have `{"href": "https://www.google.com"}`.
        Setting to `None` will simply cause the `HTMLNode` object to have no attributes.
        Default: None
    """

    def __init__(
        self, tag: str | None, value: str | None, props: dict[str, str] | None = None
    ):
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self) -> str:
        if self.value is None:
            raise ValueError("'value' attribute has no value")
        if self.tag is None:
            return self.value
        else:
            return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
