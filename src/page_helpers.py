from pathlib import Path
from shutil import copy2


def _convert_to_pathlib_path(path_str: Path | str) -> Path:
    if isinstance(path_str, str):
        return Path(path_str)
    return path_str


# Delete this later
def _traverse_file_tree(path: Path):
    for f in path.iterdir():
        print(f)
        if f.is_dir():
            _traverse_file_tree(f)


def _delete_file_tree_old(path: Path):
    for f in path.iterdir():
        if f.is_dir():
            _ = _delete_file_tree(f)
            f.rmdir()
        else:
            f.unlink()


def _delete_file_tree(path: Path) -> bool:
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
