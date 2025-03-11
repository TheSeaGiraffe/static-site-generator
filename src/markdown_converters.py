import re
from enum import Enum

from htmlnode import HTMLNode
from textnode import TextNode, TextType
from textnode_converters import (
    text_node_to_html,
    text_to_textnodes,
    textnodes_to_leafnodes,
)


class BlockType(Enum):
    """Used to indicate the type of a markdown text block

    Covers the most common types of text blocks seen in a markdown document.
    """

    HEADING = "heading"
    """
    A heading represented by the <h1>-<h6> tags
    """
    CODE = "code"
    """
    A code block, which is any text enclosed in 3 pairs of back ticks (`)
    """
    QUOTE = "quote"
    """
    A quote block, which is basically a block of text where each line begins with >.
    """
    UNORDERED_LIST = "unordered list"
    """
    An unordered list, which is a block of text where each line begins with a hyphen or
    an asteriskd and a space.
    """
    ORDERED_LIST = "ordered list"
    """
    An ordered list, which is a block of text where each line begins with a number,
    followed immediately by a period and then a space. The numbers must increment.
    """
    PARAGRAPH = "paragraph"
    """
    A block of regular text.
    """


BLOCK_TYPE_PATTERNS: dict[BlockType, str] = {
    BlockType.HEADING: r"^#{1,6}(?= \S)",
    BlockType.CODE: r"^(`{3}).*`{3}$",
    BlockType.QUOTE: r"^>",
    BlockType.UNORDERED_LIST: r"^(\*|-)(?= \S)",
    BlockType.ORDERED_LIST: r"^\d+\.(?= \S)",
    BlockType.PARAGRAPH: r".*",
}

BLOCK_TYPE_TAGS: dict[BlockType, list[str]] = {
    BlockType.HEADING: ["h"],
    BlockType.CODE: ["code", "pre"],
    BlockType.QUOTE: ["p", "blockquote"],
    BlockType.UNORDERED_LIST: ["li", "ul"],
    BlockType.ORDERED_LIST: ["li", "ol"],
    BlockType.PARAGRAPH: ["p"],
}


def markdown_to_blocks(markdown: str) -> list[str]:
    """Split markdown document into blocks

    Here blocks are defined as sections of text separated by a blank line.

    Parameters
    ----------
    markdown: str
        Text representing a markdown document.

    Returns
    -------
    list[str]
        A list of markdown blocks. Empty blocks resulting from excessive white space are
        omitted.
    """
    return [block.strip() for block in markdown.split("\n\n") if block]


def _check_listlike_block(
    list_block: list[str], pattern: str
) -> tuple[list[str], list[str]]:
    """Checks to see whether all elements of a list-like block match a pattern

    If any list element doesn't match then the entire block is considered invalid and an
    empty list is returned. If all elements match then the original list is returned.

    Parameters
    ----------
    list_block: list[str]
        A list of strings where each element corresponds to a list item

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple containing the following values
        - A list of matches. Empty if no matches
        - A list containing the text of the heading stripped of the markdown list
          notation including quotes. Text left as is if no matches
    """
    matches: list[str] = []
    stripped_lines: list[str] = []
    for list_el in list_block:
        m = re.search(pattern, list_el)
        if not m:
            matches = []
            stripped_lines = []
            break
        matches.append(m.group())
        list_el_replaced = list_el.replace(m.group() + " ", "", 1)
        stripped_lines.append(list_el_replaced)
    return matches, stripped_lines


def block_to_block_type(block: str) -> BlockType:
    """Returns the type of the block

    Checks whether "block" is one of the following types:

    - Heading
    - Code
    - Quote
    - Unordered list
    - Ordered list
    - Paragraph

    Assumes that "block" was obtained from "markdown_to_blocks" function.

    Parameters
    ----------
    block: str
        A string representing a block of text in a markdown document.

    Returns
    -------
    tuple[BlockType, list[Any]]
        The type of the block and a list of each line of the block without block level
        characters.
    """
    stripped_block = block.strip()  # Make sure that the block has no excess whitespace
    for block_type, pattern in BLOCK_TYPE_PATTERNS.items():
        m: list[str] = []
        match block_type:
            case BlockType.HEADING:
                m = re.findall(pattern, stripped_block)
            case BlockType.CODE:
                m = re.findall(pattern, stripped_block, re.S)
            case BlockType.QUOTE | BlockType.UNORDERED_LIST:
                m, _ = _check_listlike_block(stripped_block.split("\n"), pattern)
            case BlockType.ORDERED_LIST:
                m, _ = _check_listlike_block(stripped_block.split("\n"), pattern)
                if m:
                    list_nums = [int(num.split(".")[0]) for num in m]
                    if sorted(list_nums) != list_nums:
                        m = []
            case _:
                pass
        if m:
            return block_type
    return BlockType.PARAGRAPH


def _check_heading(block: str) -> tuple[list[str], list[str]]:
    """Checks to see whether block is a markdown heading

    Parameters
    ----------
    block: str
        Text representing a markdown block
    pattern: str
        The pattern used for identifying markdown headings

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple containing the following values
        - A list of matches. Empty if no matches
        - A list containing the text of the heading stripped of the markdown heading
          notation. Text left as is if no matches
    """
    pattern = BLOCK_TYPE_PATTERNS[BlockType.HEADING]
    m = re.findall(pattern, block)
    if m:
        return m, [block.lstrip(m[0])]
    return m, [block]


def _check_code_block(block: str) -> tuple[list[str], list[str]]:
    """Checks to see whether block is a markdown code block

    Parameters
    ----------
    block: str
        Text representing a markdown block
    pattern: str
        The pattern used for identifying markdown code blocks

    Returns
    -------
    list[str]
        A tuple containing the following values:
        - A list of matches. Empty if no matches
        - A list containing the text of the heading stripped of the markdown
          heading notation. Text left as is if no matches
    """
    pattern = BLOCK_TYPE_PATTERNS[BlockType.CODE]
    m = re.findall(pattern, block, re.S)
    if m:
        stripped_lines = block.strip(m[0]).split("\n")
        return m, stripped_lines[1:]
    return m, block.split("\n")


def process_block(block_type: BlockType, block: str) -> tuple[list[str], list[str]]:
    """Extracts both the special markdown character and just the text from a markdown
    block

    Parameters
    ----------
    block_type: BlockType
        A value from the BlockType enum denoting the type of the block
    block: str
        The text of the block itself

    Returns
    -------
    tuple[list[str], list[str]]
        A tuple containing the following values
        - A list containing any special markdown characters used at the block level.
          Empty if there are no such characters
        - The text of the markdown block with markdown block characters removed. Text
          will be left as is if the block is detected to be just plain text.
    """
    block_pattern = BLOCK_TYPE_PATTERNS[block_type]
    md_block_chars: list[str] = []
    processed_block: list[str] = []
    block_stripped = block.strip()
    match block_type:
        case BlockType.HEADING:
            md_block_chars, processed_block = _check_heading(block_stripped)
        case BlockType.CODE:
            md_block_chars, processed_block = _check_code_block(block_stripped)
        case BlockType.QUOTE | BlockType.UNORDERED_LIST | BlockType.ORDERED_LIST:
            md_block_chars, processed_block = _check_listlike_block(
                block_stripped.split("\n"), block_pattern
            )
        case BlockType.PARAGRAPH:
            processed_block = block.strip().split("\n")
    return md_block_chars, processed_block


def _create_block_html_node(
    block_type: BlockType, child_nodes: list[HTMLNode], md_block_chars: list[str]
) -> HTMLNode:
    """Create a block-level HTML node

    This node contains all of the child nodes related to the current block

    Parameter
    ---------
    block_type: BlockType
        A value from the BlockType enum denoting the type of the block
    child_nodes: list[HTMLNode]
        A list of HTMLNodes representing the children of this node
    md_block_chars: list[str]
        A list containing any block-level markdown characters

    Returns
    -------
    HTMLNode
        An HTMLNode representing a markdown block
    """
    match block_type:
        case BlockType.HEADING:
            tag = BLOCK_TYPE_TAGS[block_type][0]
            num_chars = md_block_chars[0].count("#")
            tag += f"{num_chars}"
            return HTMLNode(tag, None, child_nodes)
        case BlockType.CODE | BlockType.QUOTE:
            inner_tag, outer_tag = BLOCK_TYPE_TAGS[block_type]
            block_node = HTMLNode(inner_tag, None, child_nodes)
            return HTMLNode(outer_tag, None, [block_node])
        case BlockType.ORDERED_LIST | BlockType.UNORDERED_LIST:
            tag = BLOCK_TYPE_TAGS[block_type][1]
            return HTMLNode(tag, None, child_nodes)
        case _:
            tag = BLOCK_TYPE_TAGS[block_type][0]
            return HTMLNode(tag, None, child_nodes)


def markdown_to_html_node(markdown: str) -> HTMLNode:
    """Convert markdown text to an HTMLNode

    Takes markdown text and processes it block by block into an HTMLNode

    Parameters
    ----------
    markdown: str
        Text written in markdown format

    Returns
    -------
    HTMLNode
        An HTMLNode representing the entire markdown document.
    """
    blocks = markdown_to_blocks(markdown)

    block_htmlnodes: list[HTMLNode] = []
    for block in blocks:
        block_type = block_to_block_type(block)
        md_block_chars, block_lines = process_block(block_type, block)

        line_htmlnodes: list[HTMLNode] = []
        if block_type == BlockType.CODE:
            block_stripped = block.lstrip("`\n").rstrip("`")
            code_text_node = TextNode(block_stripped, TextType.TEXT)
            code_leaf_node = text_node_to_html(code_text_node)
            line_htmlnodes.append(code_leaf_node)
        else:
            num_lines = len(block_lines) - 1
            for i, block_line in enumerate(block_lines):
                if i < num_lines and not (
                    block_type == BlockType.UNORDERED_LIST
                    or block_type == BlockType.ORDERED_LIST
                ):
                    block_line += " "

                block_line_textnodes = text_to_textnodes(block_line)
                block_line_leafnodes = textnodes_to_leafnodes(block_line_textnodes)
                if (
                    block_type == BlockType.ORDERED_LIST
                    or block_type == BlockType.UNORDERED_LIST
                ):
                    tag = BLOCK_TYPE_TAGS[block_type][0]
                    block_line_leafnodes = [HTMLNode(tag, None, block_line_leafnodes)]

                line_htmlnodes.extend(block_line_leafnodes)
        block_htmlnode = _create_block_html_node(
            block_type, line_htmlnodes, md_block_chars
        )
        block_htmlnodes.append(block_htmlnode)

    return HTMLNode("div", None, block_htmlnodes)
