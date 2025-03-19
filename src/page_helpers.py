import re
from pathlib import Path
from shutil import copy2


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
    raise Exception("no H1 heading found")
