from pathlib import Path

from page_helpers import copy_tree


def main():
    static_dir = Path("static")
    public_dir = Path("public")
    if not public_dir.exists():
        public_dir.mkdir()
    copy_tree(static_dir, public_dir)


if __name__ == "__main__":
    main()
