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
