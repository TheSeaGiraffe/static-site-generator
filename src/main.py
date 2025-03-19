from pathlib import Path

from page_helpers import copy_tree, generate_page


def main():
    # Copy contents of static to public
    static_dir = Path("static")
    public_dir = Path("public")
    if not public_dir.exists():
        public_dir.mkdir()
    copy_tree(static_dir, public_dir)

    # Generate page using template
    content_path = Path("content/index.md")
    template_path = Path("template.html")
    page_path = Path("public/index.html")
    generate_page(content_path, template_path, page_path)


if __name__ == "__main__":
    main()
