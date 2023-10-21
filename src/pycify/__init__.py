from __future__ import annotations

import compileall
import os
import shutil
import sys


def yellow(string: str, /) -> str:
    """Wraps string in ANSI yellow code."""
    return f"\033[33m{string}\033[m"


def replace_py_with_pyc(folder: str) -> None:
    """Replaces all .py files with the cached .pyc files from __pycache__."""
    compileall.compile_dir(folder, quiet=1)

    for name in os.listdir(folder):
        subfolder = os.path.join(folder, name)
        if os.path.isdir(subfolder):
            replace_py_with_pyc(subfolder)

    pycache_path = os.path.join(folder, "__pycache__")
    if not os.path.isdir(pycache_path):
        return

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
        new_pyc_path = os.path.join(folder, filename + ".pyc")
        shutil.move(pyc_path, new_pyc_path)
        # Then delete the .py file
        os.remove(filepath)

    # Finally delete the pycache, it should be empty.
    os.rmdir(pycache_path)
