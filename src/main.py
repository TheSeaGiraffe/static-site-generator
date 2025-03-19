from pathlib import Path
from sys import argv

from page_helpers import copy_tree, generate_pages_recursive


def main():
    # Get first CLI argument as the basepath
    basepath = "/"
    if len(argv) > 1:
        basepath = argv[1]

    # Copy contents of static to public
    static_dir = Path("static")
    page_dir = Path("docs")
    if not page_dir.exists():
        page_dir.mkdir()
    copy_tree(static_dir, page_dir)

    # Generate pages in "content" using template
    content_path = Path("content")
    template_path = Path("template.html")
    generate_pages_recursive(content_path, template_path, page_dir, basepath)


if __name__ == "__main__":
    main()
