import unittest

from markdown_converters import (
    BlockType,
    block_to_block_type,
    markdown_to_blocks,
    markdown_to_html_node,
)


class TestMarkdownToBlocks(unittest.TestCase):
    def test_split_doc_simple(self):
        doc = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""

        got = markdown_to_blocks(doc)
        want = [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
            "* This is the first list item in a list block\n* This is a list item\n* This is another list item",
        ]

        self.assertEqual(got, want)

    def test_split_doc_many_spaces(self):
        doc = """# A document with a lot of spaces




A *tiny* **paragraph**.



* Item one
* Item two
* Item three

1. Item one of a new list
2. Item two"""

        got = markdown_to_blocks(doc)
        want = [
            "# A document with a lot of spaces",
            "A *tiny* **paragraph**.",
            "* Item one\n* Item two\n* Item three",
            "1. Item one of a new list\n2. Item two",
        ]

        self.assertEqual(got, want)

    def test_split_doc_code_block(self):
        doc = """# A document with a block of code

Another tiny paragraph.

```python
print("This is a code block")
```"""

        got = markdown_to_blocks(doc)
        want = [
            "# A document with a block of code",
            "Another tiny paragraph.",
            '```python\nprint("This is a code block")\n```',
        ]

        self.assertEqual(got, want)


class TestBlockToBlockType(unittest.TestCase):
    def test_heading_h1(self):
        block = "# This is an H1 heading"
        want = BlockType.HEADING
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_heading_broken(self):
        block = "This is a # Broken H1 heading"
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_heading_h3(self):
        block = "### This is an H3 heading"
        want = BlockType.HEADING
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_heading_h6(self):
        block = "###### This is an H6 heading"
        want = BlockType.HEADING
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_code(self):
        block = """```python
print("This is some Python code")

a = 1
b = 4
print(f"a + b = {a+b}")```"""
        want = BlockType.CODE
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_code_single_backtick(self):
        block = """`print("This is a single line of code")`"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_code_unbalanced(self):
        block = """```python
print("This is some Python code in an unbalanced code block")

a = 1
b = 4
print(f"a + b = {a+b}")"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_quote(self):
        block = """> Some text in a
> quoted block.
>There are some sections
> where there are no spaces
>    after the quote character
> or there are several"""
        want = BlockType.QUOTE
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_quote_broken(self):
        block = """> Here is a quoted block where
there is text > before the quote character.
> This invalidates the entire block."""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_hyphen(self):
        block = """- A proper unordered list
- using hyphens
- containing 3 items"""
        want = BlockType.UNORDERED_LIST
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_asterisk(self):
        block = """* A proper unordered list
* using asterisks
* containing 3 items"""
        want = BlockType.UNORDERED_LIST
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_broken_no_space(self):
        block = """- An invalid unordered list
-with no space
- between the hyphen and text"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_broken_character_in_middle(self):
        block = """- An invalid unordered list
with the - hyphen
- in the middle of the text"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list(self):
        block = """1. A proper ordered list
2. with spaces between the
3. numbers and text and
4. the numbers themselves in ascending order"""
        want = BlockType.ORDERED_LIST
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list_broken_no_space(self):
        block = """1. An invalid ordered list
2.with no spaces between
3. numbers and text"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list_broken_in_middle(self):
        block = """1. An invalid ordered list
with the 2.number
3. coming in the middle of the text"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list_unordered(self):
        block = """1. An invalid ordered list
4. where the numbers
2. are out of order
3. everything else is fine"""
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_paragraph_single(self):
        block = "This is just some text with nothing extra going on. Should be seen as just a paragraph"
        want = BlockType.PARAGRAPH
        got = block_to_block_type(block)

        self.assertEqual(got, want)


class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph text in a p
tag here

This is another paragraph with *italic* text and `code` here

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that *should* remain
the **same** even with inline stuff
```
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that *should* remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_quoteblock(self):
        md = """
> This is a quote block
> with **bold** text
> and *italic* text
> that `should` be wrapped
> with the correct tags
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote><p>This is a quote block with <b>bold</b> text and <i>italic</i> text that <code>should</code> be wrapped with the correct tags</p></blockquote></div>",
        )

    def test_unordered_list(self):
        md = """
- this is an **unordered** `list`
- containing *inline* markdown
- spread across 3 lines
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>this is an <b>unordered</b> <code>list</code></li><li>containing <i>inline</i> markdown</li><li>spread across 3 lines</li></ul></div>",
        )

    def test_ordered_list_valid(self):
        md = """
1. this is a *valid* ordered `list`
2. with **inline** markdown
3. this time spread across
4. 4 lines
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ol><li>this is a <i>valid</i> ordered <code>list</code></li><li>with <b>inline</b> markdown</li><li>this time spread across</li><li>4 lines</li></ol></div>",
        )

    def test_ordered_list_invalid(self):
        md = """
2. this is an invalid
1. *ordered list*
4. where **everything**
3. is out of order
5. should show as a paragraph
"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>2. this is an invalid 1. <i>ordered list</i> 4. where <b>everything</b> 3. is out of order 5. should show as a paragraph</p></div>",
        )

    def test_heading_valid(self):
        md = """
# This is an H1 heading

Some additional text to pad out this example

### This is an H3 heading

Some more text

###### This is an H6 heading

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1> This is an H1 heading</h1><p>Some additional text to pad out this example</p><h3> This is an H3 heading</h3><p>Some more text</p><h6> This is an H6 heading</h6></div>",
        )

    def test_heading_invalid(self):
        md = """
####### This is an invalid heading

It should be rendered as raw text in p tags

"""
        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>####### This is an invalid heading</p><p>It should be rendered as raw text in p tags</p></div>",
        )
