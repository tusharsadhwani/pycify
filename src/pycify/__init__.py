from __future__ import annotations

import compileall
import os
import shutil
import sys


def yellow(string: str, /) -> str:
    """Wraps string in ANSI yellow code."""
    return f"\033[33m{string}\033[m"


def replace_py_with_pyc(folder: str, out_folder: str | None = None) -> list[str]:
    """
    Replaces all .py files with the cached .pyc files from __pycache__.
    If out_folder is provided, doesn't delete any existing Python files, simply
    creates the new `.pyc` files in the new location.
    """
    compileall.compile_dir(folder, quiet=1, force=True)

    if out_folder is None:
        out_folder = folder

    created_pyc_files: list[str] = []

    for name in os.listdir(folder):
        subfolder = os.path.join(folder, name)
        out_subfolder = os.path.join(out_folder, name)
        if os.path.isdir(subfolder):
            created_pyc_files.extend(replace_py_with_pyc(subfolder, out_subfolder))

    pycache_path = os.path.join(folder, "__pycache__")
    if not os.path.isdir(pycache_path):
        return []

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    # If pycache exists at this level, python files must also be at this level
    for file in os.listdir(folder):
        if not file.endswith(".py"):
            continue
        filepath = os.path.join(folder, file)
        if not os.path.isfile(filepath):
            continue

        filename = file.removesuffix(".py")
        pycache_filename = f"{filename}.cpython-3{sys.version_info.minor}.pyc"
        pyc_path = os.path.join(pycache_path, pycache_filename)
        if not os.path.exists(pyc_path):
            print(f"{yellow('NOTE:')} {pyc_path} not found, skipping.")
            continue

        print(f"Replacing {filepath} with {pyc_path}")
        # First move the .pyc file right next to .py file
        new_pyc_path = os.path.join(out_folder, filename + ".pyc")
        shutil.move(pyc_path, new_pyc_path)
        created_pyc_files.append(new_pyc_path)
        # Then delete the .py file if `out_folder` is the same as `folder`
        if folder == out_folder:
            os.remove(filepath)

    # Finally delete the pycache, it should be empty.
    os.rmdir(pycache_path)

    return created_pyc_files
