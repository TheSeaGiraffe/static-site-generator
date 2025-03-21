import re

from leafnode import LeafNode
from textnode import TextNode, TextType

ALLOWED_DELIMS: dict[str, TextType] = {
    "": TextType.TEXT,
    "`": TextType.CODE,
    # "*": TextType.ITALIC,
    "_": TextType.ITALIC,
    "**": TextType.BOLD,
}

TRIPLE_ASTERISK_PATTERN: dict[str, dict[str, str]] = {
    "*": {
        r"\b\*{3}": "_*",
        r"\*{3}\b": "*_",
    },
    "**": {r"\b\*{3}": "_**", r"\*{3}\b": "**_"},
}


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


def textnodes_to_leafnodes(textnodes: list[TextNode]) -> list[LeafNode]:
    leafnodes: list[LeafNode] = []
    for textnode in textnodes:
        leafnode = text_node_to_html(textnode)
        leafnodes.append(leafnode)
    return leafnodes


def split_nodes_delimiter_old(
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
            text_node = TextNode(node.text, node.text_type)
            text_nodes.append(text_node)
        else:
            node_text_sub = node.text
            if text_type == TextType.ITALIC:
                # The issue is here. What is the proper pattern to use?
                # Will leave this for now.
                # node_text_sub = re.sub(r"(\b|\B)\*{2}|\*{2}\b", "~", node_text_sub)
                node_text_sub = re.sub(r"(\b)\*{2}|\*{2}\b", "~", node_text_sub)
            node_text_sub_split: list[str]
            if delimiter != "":
                if delimiter != "`":
                    for pattern, sub_str in TRIPLE_ASTERISK_PATTERN[delimiter].items():
                        node_text_sub = re.sub(pattern, sub_str, node_text_sub)
                node_text_sub_split = node_text_sub.split(delimiter)
            else:
                node_text_sub_split = [node_text_sub]
            for i, sub_str in enumerate(node_text_sub_split):
                if sub_str == "":
                    continue
                if text_type == TextType.ITALIC:
                    sub_str = re.sub("~|_", "**", sub_str)
                elif text_type == TextType.BOLD:
                    sub_str = re.sub("_", "*", sub_str)
                if (i % 2) == 0:
                    text_node = TextNode(sub_str, TextType.TEXT)
                else:
                    text_node = TextNode(sub_str, text_type)
                text_nodes.append(text_node)
    return text_nodes


# Need to fix this so that splitting on italics with periods works properly.
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
            text_node = TextNode(node.text, node.text_type)
            text_nodes.append(text_node)
        else:
            node_text_sub = node.text
            node_text_sub_split: list[str]
            if delimiter != "":
                # if delimiter != "`":
                #     for pattern, sub_str in TRIPLE_ASTERISK_PATTERN[delimiter].items():
                #         node_text_sub = re.sub(pattern, sub_str, node_text_sub)
                node_text_sub_split = node_text_sub.split(delimiter)
            else:
                node_text_sub_split = [node_text_sub]
            for i, sub_str in enumerate(node_text_sub_split):
                if sub_str == "":
                    continue
                # if text_type == TextType.ITALIC:
                #     sub_str = re.sub("~|_", "**", sub_str)
                # elif text_type == TextType.BOLD:
                #     sub_str = re.sub("_", "*", sub_str)
                if (i % 2) == 0:
                    text_node = TextNode(sub_str, TextType.TEXT)
                else:
                    text_node = TextNode(sub_str, text_type)
                text_nodes.append(text_node)
    return text_nodes


def extract_markdown_images(text: str) -> list[tuple[str, str]]:
    """Extract the alt text and URL of any image tags in the provided text.

    Ignores any image tags that are enclosed in code blocks.

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

    Ignores any URL tags athat are enclosed in code blocks.

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


def split_nodes_image(old_nodes: list[TextNode]) -> list[TextNode]:
    """Splits text nodes containing images into nodes with the appropriate text type

    Raises and exception if old_nodes is empty. Currently ignores images that are
    enclosed in code blocks.

    Parameters
    ----------
    old_nodes: list[TextNode]
        A list of text nodes containing image links

    Returns
    -------
    list[TextNode]
        A list of TextNodes built from the old_nodes. Only works with image links.
    """
    if len(old_nodes) == 0:
        raise ValueError("'old_nodes' is empty")

    img_tag_pattern = r"\!\[.*?\]\(.*?\)"
    code_block_pattern = r"(`|`{3}).*?" + img_tag_pattern + r".*?(`|`{3})"
    text_nodes: list[TextNode] = []
    for node in old_nodes:
        imgs: list[tuple[str, str]] = []
        text_splits = [node.text]
        if re.search(code_block_pattern, node.text) is None:
            imgs = extract_markdown_images(node.text)[::-1]
            text_splits = re.split(img_tag_pattern, node.text)[::-1]

        while (len(imgs) > 0) or (len(text_splits) > 0):
            text: str = text_splits.pop() if text_splits else ""
            img: tuple[str, str] | None = imgs.pop() if imgs else None
            if text:
                text_node = TextNode(text, node.text_type, node.url)
                text_nodes.append(text_node)
            if img is not None:
                alt_text, url = img
                text_node = TextNode(alt_text, TextType.IMAGE, url)
                text_nodes.append(text_node)
    return text_nodes


def split_nodes_link(old_nodes: list[TextNode]) -> list[TextNode]:
    """Splits text nodes containing URLs into nodes with the appropriate text type

    Raises and exception if old_nodes is empty. Currently ignores links that are
    enclosed in code blocks.

    Parameters
    ----------
    old_nodes: list[TextNode]
        A list of text nodes containing image links

    Returns
    -------
    list[TextNode]
        A list of TextNodes built from the old_nodes. Only works with image links.
    """
    if len(old_nodes) == 0:
        raise ValueError("'old_nodes' is empty")

    link_tag_pattern = r"(?<!!)\[.*?\]\(.*?\)"
    code_block_pattern = r"(`|`{3}).*?" + link_tag_pattern + r".*?(`|`{3})"
    text_nodes: list[TextNode] = []
    for node in old_nodes:
        links: list[tuple[str, str]] = []
        text_splits = [node.text]
        if re.search(code_block_pattern, node.text) is None:
            links = extract_markdown_links(node.text)[::-1]
            text_splits = re.split(link_tag_pattern, node.text)[::-1]

        while (len(links) > 0) or (len(text_splits) > 0):
            text: str = text_splits.pop() if text_splits else ""
            link: tuple[str, str] | None = links.pop() if links else None
            if text:
                text_node = TextNode(text, node.text_type, node.url)
                text_nodes.append(text_node)
            if link is not None:
                alt_text, url = link
                text_node = TextNode(alt_text, TextType.LINK, url)
                text_nodes.append(text_node)
    return text_nodes


def text_to_textnodes(text: str) -> list[TextNode]:
    """Converts text to a list of 'TextNodes' of the appropriate type

    Parameters
    ----------
    text: str
        A string containing valid markdown delimiters and tags.

    Returns
    -------
    list[TextNode]
        A list of `TextNode`s whose type matches the corresponding delimiter.
    """
    nodes = [TextNode(text, TextType.TEXT)]
    for delimiter, text_type in ALLOWED_DELIMS.items():
        nodes = split_nodes_delimiter(nodes, delimiter, text_type)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    return nodes
