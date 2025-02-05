import unittest

from markdown_converters import markdown_to_blocks


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

* Item one of a new list
* Item two"""

        got = markdown_to_blocks(doc)
        want = [
            "# A document with a lot of spaces",
            "A *tiny* **paragraph**.",
            "* Item one\n* Item two\n* Item three",
            "* Item one of a new list\n* Item two",
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
