"""Integration tests to ensure pycify works as expected."""

from __future__ import annotations

import os.path
import shutil
import subprocess

import pycify

FileTree = dict[str, "FileTree"]


def pyc_tree(folder_path: str) -> FileTree:
    """Create a tree of the pyc files in given folder."""
    files: FileTree = {}
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)
        if os.path.isdir(filepath):
            pyc_subtree = pyc_tree(filepath)
            if pyc_subtree.values():
                files[filename] = pyc_subtree

        elif filename.endswith(".pyc"):
            files[filename] = {}

    return files


def test_pycify() -> None:
    """Integration test to ensure pycify works as expected."""
    clone_url = "https://github.com/tusharsadhwani/packaged"
    commit_oid = "e2f1d54"
    clone_path = os.path.join(os.path.dirname(__file__), "packaged")

    try:
        subprocess.check_call(["git", "clone", clone_url, clone_path])
        subprocess.check_call(["git", "checkout", commit_oid], cwd=clone_path)

        pycify.replace_py_with_pyc(clone_path)
        files = pyc_tree(clone_path)
        assert files == {
            "setup.pyc": {},
            "src": {
                "packaged": {
                    "config.pyc": {},
                    "cli.pyc": {},
                    "__main__.pyc": {},
                    "__init__.pyc": {},
                },
            },
            "example": {
                "minesweeper": {"setup.pyc": {}, "minesweeper.pyc": {}},
                "mandelbrot": {"mandelbrot.pyc": {}},
            },
            "tests": {
                "end_to_end": {
                    "test_packages": {
                        "configtest": {"setup.pyc": {}, "configtest.pyc": {}},
                        "numpy_pandas": {"somefile.pyc": {}},
                        "just_python": {"foo.pyc": {}},
                    },
                    "packaged_test.pyc": {},
                },
                "cli_test.pyc": {},
                "conftest.pyc": {},
            },
        }

    finally:
        shutil.rmtree(clone_path, ignore_errors=True)
