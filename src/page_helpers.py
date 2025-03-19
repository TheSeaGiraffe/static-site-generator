import re
from pathlib import Path
from shutil import copy2

from jinja2 import Environment, FileSystemLoader

from markdown_converters import markdown_to_html_node


def _convert_to_pathlib_path(path_str: Path | str) -> Path:
    """Convert the specified file path to a pathlib.Path

    Parameters
    ----------
    path_str: pathlib.Path | str
        Path to be converted

    Returns
    -------
    pathlib.Path
        `path_str` as a pathlib.Path.
    """
    if isinstance(path_str, str):
        return Path(path_str)
    return path_str


def _delete_file_tree(path: Path) -> bool:
    """Recursively deletes the contents of the specified directory

    Parameters
    ----------
    path: pathlib.Path
        Path to directory that is to be deleted
    Returns
    -------
    bool
        True if the contents of the directory have been successfully deleted. False if
        any error occurs.
    """
    try:
        for f in path.iterdir():
            if f.is_dir():
                _ = _delete_file_tree(f)
                f.rmdir()
            else:
                f.unlink()
    except OSError:
        return False
    return True


# Works, but try to find a better way of doing this later.
def copy_tree(src: Path | str, dest: Path | str, dest_was_deleted: bool = False):
    """Copies the entire `src` directory into `dest`

    `copy_tree` first deletes the contents of `dest` before recursively copying all
    files from `src` to dest.

    Parameters
    ----------
    src: pathlib.Path | str
        Path to the source directory
    dest: pathlib.Path | str
        Path to the destination directory. Must already exist.
    dest_was_deleted: bool
        Whether the contents of `dest` have already been deleted. Only used to skip the
        deletion of the specified directory's contents during recursion. Should be left
        alone by the user.
    """
    src, dest = map(_convert_to_pathlib_path, (src, dest))

    # Delete all contents of destination tree including sub-directories
    dest_deleted: bool = False
    if not dest_was_deleted:
        dest_deleted = _delete_file_tree(dest)

    # Copy all files from src to dest
    for f_src in src.iterdir():
        if f_src.is_dir():
            dest_dir_mirror = dest / f_src.name
            if not dest_dir_mirror.exists():
                dest_dir_mirror.mkdir()
            copy_tree(f_src, dest_dir_mirror, dest_deleted)
        else:
            copy2(str(f_src), str(dest))


def extract_title(markdown: str) -> str:
    pattern = r"^#{1} (.*)$"
    m = re.search(pattern, markdown, re.M)
    if m:
        return m.group(1)
    raise Exception("no title found")


def generate_page(
    from_path: Path | str,
    template_path: Path | str,
    dest_path: Path | str,
    basepath: str,
):
    from_path, template_path, dest_path = map(
        _convert_to_pathlib_path, (from_path, template_path, dest_path)
    )

    print(
        f"Generating page from '{from_path}' to '{dest_path}' using '{template_path}'..."
    )

    # Load the markdown file
    with open(from_path) as md_file:
        md = md_file.read()

    # Get title
    try:
        title = extract_title(md)
    except Exception as e:
        raise Exception(f"could not generate page: {e}")

    # Get page HTML
    md_node = markdown_to_html_node(md)
    content = md_node.to_html()

    # Load the template
    template_env = Environment(loader=FileSystemLoader("."))
    template = template_env.get_template("template.html")

    # Generate page from template and write to dest_path
    if not dest_path.parent.exists():
        dest_path.parent.mkdir(parents=True)

    with open(dest_path, "w") as html_page:
        template_str = template.render(Title=title, Content=content)
        template_str = re.sub(r'(href|src)(=")/', rf"\1\2{basepath}", template_str)
        html_page.write(template_str)


def generate_pages_recursive(
    dir_path_content: Path | str,
    template_path: Path | str,
    dest_dir_path: Path | str,
    basepath: str,
):
    dir_path_content, template_path, dest_dir_path = map(
        _convert_to_pathlib_path, (dir_path_content, template_path, dest_dir_path)
    )

    for f_content in dir_path_content.iterdir():
        if f_content.is_dir():
            generate_pages_recursive(
                f_content, template_path, dest_dir_path / f_content.name, basepath
            )
        else:
            generate_page(
                f_content,
                template_path,
                dest_dir_path / f"{f_content.stem}.html",
                basepath,
            )
