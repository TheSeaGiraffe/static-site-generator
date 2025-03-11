from collections.abc import Sequence


class HTMLNode:
    """Represents a node in an HTML document tree

    `HTMLNode` is specifically designed to be the parent class for all other classes
    that are meant to be specialized HTML nodes. The nodes represented by HTMLNode are
    effectively all of the HTML tags used in any HTML document plus its contents. Some
    examples include a `<p>` tag and its contents or an `<a>` tag and its contents. An
    `HTMLNode` can contain other `HTMLNode`s.

    Parameters
    ----------
    tag: str | None
        A string representing the HTML tag name (e.g., "p", "a", "h1", etc.). Setting to
        `None` will cause the `HTMLNode` object to render as raw text. Default: `None`
    value: str | None
        A string representing the value of the HTML tag (e.g., the text inside a
        paragraph). If set to `None`, `HTMLNode` object is assumed to have children.
        Default: `None`
    children: Sequence[HTMLNode] | None
        A list of `HTMLNode` objects representing the children of this node. If set to
        `None`, `HTMLNode` object is assumed to have a value. Default: `None`
    props: dict[str, str] | None
        A dictionary of key-value pairs representing the attributes of the HTML tag. For
        example, a link (`<a>` tag) might have `{"href": "https://www.google.com"}`.
        Setting to `None` will simply cause the `HTMLNode` object to have no attributes.
        Default: `None`
    """

    def __init__(
        self,
        tag: str | None = None,
        value: str | None = None,
        children: Sequence["HTMLNode"] | None = None,
        props: dict[str, str] | None = None,
    ) -> None:
        self.tag: str | None = tag
        self.value: str | None = value
        self.children: Sequence["HTMLNode"] | None = children
        self.props: dict[str, str] | None = props

    def __repr__(self) -> str:
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

    def to_html(self) -> str:
        """Convert the `HTMLNode` into valid HTML

        Returns
        -------
        str
            A string containing valid HTML tags for the current node and its children
        """
        if self.children is None:
            if self.value is None:
                raise ValueError("'value' attribute has no value")
            else:
                if self.tag is None:
                    return self.value
                else:
                    return (
                        f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
                    )
        else:
            html_string = ""
            for child in self.children:
                html_string += child.to_html()
            return f"<{self.tag}{self.props_to_html()}>{html_string}</{self.tag}>"

    def props_to_html(self) -> str:
        """Convert the attributes contained in `props` into an HTML tag attribute string

        Creates a string containing all of the attributes in `props`. If `props` is
        `None`, will return an empty string.

        Returns
        -------
        str
            The tag attributes as a string of "attribute=value" pairs separated by
            spaces.
        """
        prop_str = ""
        if self.props is not None:
            for html_attr, value in self.props.items():
                prop_str += f' {html_attr}="{value}"'
        return prop_str
