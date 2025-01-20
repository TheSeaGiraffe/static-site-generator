import re

from leafnode import LeafNode
from textnode import TextNode, TextType

ALLOWED_DELIMS: dict[str, TextType] = {
    "": TextType.TEXT,
    "`": TextType.CODE,
    "*": TextType.ITALIC,
    "**": TextType.BOLD,
}

TRIPLE_ASTERISK_PATTERN: dict[str, dict[str, str]] = {
    "*": {
        r"\b\*{3}": "_*",
        r"\*{3}\b": "*_",
    },
    "**": {r"\b\*{3}": "_**", r"\*{3}\b": "**_"},
}

# ASTERISK_PATTERN_ITALICS: dict[str, str] = {
#     r"\b\*{2}|\*{2}\b": "@",
# }


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


def split_nodes_delimiter(
    old_nodes: list[TextNode], delimiter: str, text_type: TextType
) -> list[TextNode]:
    """Converts text with Markdown delimiters to a list of `TextNodes`

    Each `TextNode` has the corresponding `TextType`. For now, `split_nodes_delimiter`
    does not handle nested delimiters. Will raise exceptions if `delimiter` is not
    valid, does not match `text_type`, or there are unbalanced `delimiter`s in the
    `text` of a `TextNode`.

    Parameters
    ----------
    old_nodes: list[TextNode]
        A list of `TextNode`s
    delimiter: str
        A string containing a valid Markdown delimiter. If an empty string is passed
        then it assumed that none of the nodes in `old_nodes` contain delimiters and
        should be treated as regular text.
    text_type: TextType
        A `TextType` member that matches `delimiter`

    Returns
    -------
    list[TextNode]
        A list of `TextNodes` constructed from `old_nodes`
    """
    if delimiter not in ALLOWED_DELIMS.keys():
        raise ValueError(f"'delimiter' {delimiter} is invalid")
    if ALLOWED_DELIMS[delimiter] != text_type:
        raise ValueError(
            f"`demlimiter` {delimiter} does not match `text_type` {text_type}"
        )
    num_delims: int = 0
    text_nodes: list[TextNode] = []
    for node in old_nodes:
        num_delims = node.text.count(delimiter)
        if delimiter != "" and (num_delims % 2) > 0:
            raise ValueError("Unbalanced delimiters")
        if num_delims == 0:
            text_node = TextNode(node.text, text_type)
            text_nodes.append(text_node)
        else:
            node_text_sub = node.text
            if text_type == TextType.ITALIC:
                node_text_sub = re.sub(r"\b\*{2}|\*{2}\b", "@", node_text_sub)
            node_text_sub_split: list[str]
            if delimiter != "":
                if delimiter != "`":
                    for pattern, sub_str in TRIPLE_ASTERISK_PATTERN[delimiter].items():
                        node_text_sub = re.sub(pattern, sub_str, node_text_sub)
                node_text_sub_split = node_text_sub.split(delimiter)
            else:
                node_text_sub_split = [node_text_sub]
            for i, sub_str in enumerate(node_text_sub_split):
                if sub_str.strip() == "":
                    continue
                if text_type == TextType.ITALIC:
                    sub_str = re.sub("@|_", "**", sub_str)
                elif text_type == TextType.BOLD:
                    sub_str = re.sub("_", "*", sub_str)
                if (i % 2) == 0:
                    text_node = TextNode(sub_str, TextType.TEXT)
                else:
                    text_node = TextNode(sub_str, text_type)
                text_nodes.append(text_node)
    return text_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    """Extract the alt text and URL of any image tags in the provided text.

    Parameters
    ----------
    text: str
        A string representing raw Markdown

    Returns
    -------
    list[tuple[str, str]]
        A list containing tuples representing the alt text and URL of the Markdown image
        tag. If there are no matches, returns an empty list.
    """
    img_tag_pattern = r"(?<=!)\[(.*?)\]\((.*?)\)"
    code_block_pattern = r"(`|`{3}).*?" + img_tag_pattern + r".*?(`|`{3})"
    if re.search(code_block_pattern, text) is not None:
        return []
    return re.findall(img_tag_pattern, text)


def extract_markdown_links(text: str) -> list[tuple[str, str]]:
    """Extract the alt text and URL of any URL tags in the provided text.

    Parameters
    ----------
    text: str
        A string representing raw Markdown

    Returns
    -------
    list[tuple[str, str]]
        A list containing tuples representing the alt text and URL of the Markdown URL
        tag. If there are no matches, returns an empty list.
    """
    link_tag_pattern = r"(?<!!)\[(.*?)\]\((.*?)\)"
    code_block_pattern = r"(`|`{3}).*?" + link_tag_pattern + r".*?(`|`{3})"
    if re.search(code_block_pattern, text) is not None:
        return []
    return re.findall(link_tag_pattern, text)
