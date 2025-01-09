from htmlnode import HTMLNode


class ParentNode(HTMLNode):
    """Represents a parent node in an HTML document tree.

    Effectively an `HTMLNode` that contains only child nodes. The `tag` and `children`
    parameters are required with only the `props` parameter being optional.

    Parameters
    ----------
    tag: str | None
        A string representing the HTML tag name (e.g., "p", "a", "h1", etc.). Setting to
        `None` will cause the `HTMLNode` object to render as raw text. Default: None
    children: list[HTMLNode] | None
        A list of `HTMLNode` objects representing the children of this node. If set to
        `None`, `HTMLNode` object is assumed to have a value. Default: None
    props: dict[str, str] | None
        A dictionary of key-value pairs representing the attributes of the HTML tag. For
        example, a link (`<a>` tag) might have `{"href": "https://www.google.com"}`.
        Setting to `None` will simply cause the `HTMLNode` object to have no attributes.
        Default: None
    """

    def __init__(
        self,
        tag: str | None,
        children: list["HTMLNode"] | None,
        props: dict[str, str] | None = None,
    ) -> None:
        super().__init__(tag, None, children, props)

    def to_html(self) -> str:
        """Convert the `ParentNode` into valid HTML

        Returns a string containing the HTML string of all of the `ParentNode`s children
        enclosed in the `ParentNode`s `tag`. Raises an exception if either `tag` or
        `children` are missing values.

        Returns
        -------
        str
            Valid HTML string constructed from the `tag`s of the `ParentNode` and the
            HTML string of all the child nodes.
        """
        if self.tag is None:
            raise ValueError("'tag' attribute has no value")
        if self.children is None:
            raise ValueError("'children' attribute has no value")
        html_str = f"<{self.tag}>"
        for child in self.children:
            html_str += child.to_html()
        html_str += f"</{self.tag}>"
        return html_str
