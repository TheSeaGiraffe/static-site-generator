import unittest

from markdown_converters import block_to_block_type, markdown_to_blocks


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
        want = "heading"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_heading_broken(self):
        block = "This is a # Broken H1 heading"
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_heading_h3(self):
        block = "### This is an H3 heading"
        want = "heading"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_heading_h6(self):
        block = "###### This is an H6 heading"
        want = "heading"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_code(self):
        block = """```python
print("This is some Python code")

a = 1
b = 4
print(f"a + b = {a+b}")```"""
        want = "code"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_code_single_backtick(self):
        block = """`print("This is a single line of code")`"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_code_unbalanced(self):
        block = """```python
print("This is some Python code in an unbalanced code block")

a = 1
b = 4
print(f"a + b = {a+b}")"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_quote(self):
        block = """> Some text in a
> quoted block.
>There are some sections
> where there are no spaces
>    after the quote character
> or there are several"""
        want = "quote"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_quote_broken(self):
        block = """> Here is a quoted block where
there is text > before the quote character.
> This invalidates the entire block."""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_hyphen(self):
        block = """- A proper unordered list
- using hyphens
- containing 3 items"""
        want = "unordered list"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_asterisk(self):
        block = """* A proper unordered list
* using asterisks
* containing 3 items"""
        want = "unordered list"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_broken_no_space(self):
        block = """- An invalid unordered list
-with no space
- between the hyphen and text"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_unordered_list_broken_character_in_middle(self):
        block = """- An invalid unordered list
with the - hyphen
- in the middle of the text"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list(self):
        block = """1. A proper ordered list
2. with spaces between the
3. numbers and text and
4. the numbers themselves in ascending order"""
        want = "ordered list"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list_broken_no_space(self):
        block = """1. An invalid ordered list
2.with no spaces between
3. numbers and text"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list_broken_in_middle(self):
        block = """1. An invalid ordered list
with the 2.number
3. coming in the middle of the text"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_ordered_list_unordered(self):
        block = """1. An invalid ordered list
4. where the numbers
2. are out of order
3. everything else is fine"""
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)

    def test_paragraph_single(self):
        block = "This is just some text with nothing extra going on. Should be seen as just a paragraph"
        want = "paragraph"
        got = block_to_block_type(block)

        self.assertEqual(got, want)
