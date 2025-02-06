import re

BLOCK_TYPE_PATTERNS = {
    "heading": r"^#{1,6} .*",
    "code": r"^`{3}.*`{3}$",
    "quote": r"^>",
    "unordered list": r"^(\*|-) ",
    "ordered list": r"^\d+\. ",
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


def _check_listlike_block(list_block: list[str], pattern: str) -> list[str]:
    """Checks to see whether all elements of a list-like block match a pattern

    If any list element doesn't match then the entire block is considered invalid and an
    empty list is returned. If all elements match then the original list is returned.

    Parameters
    ----------
    list_block: list[str]
        A list of strings where each element corresponds to a list item

    Returns
    -------
    list[str]
        Either the original "list_block" or and empty list if there was an element that
        did not match the pattern.
    """
    for list_el in list_block:
        if not re.search(pattern, list_el):
            list_block = []
            break
    return list_block


def block_to_block_type(block: str) -> str:
    """Returns the type of the block

    Checks whether "block" is one of the following types:

    - Heading
    - Code
    - Quote
    - Unordered list
    - Ordered list
    - Paragraph

    Assumes that "block" was obtained from "markdown_to_blocks" function

    Parameters
    ----------
    block: str
        A string representing a block of text in a markdown document.

    Returns
    -------
    str
        The type of the block.
    """
    for block_type, pattern in BLOCK_TYPE_PATTERNS.items():
        m: list[str] = []
        match block_type:
            case "heading":
                m = re.findall(pattern, block)
            case "code":
                m = re.findall(pattern, block, re.S)
            case "quote" | "unordered list":
                m = _check_listlike_block(block.split("\n"), pattern)
            case "ordered list":
                m = _check_listlike_block(block.split("\n"), pattern)
                if m:
                    list_nums = [int(num.split(".")[0]) for num in m]
                    if sorted(list_nums) != list_nums:
                        m = []
            case _:
                pass
        if m:
            return block_type
    return "paragraph"
