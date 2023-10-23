"""CLI interface for pycify."""
from __future__ import annotations

import argparse

from pycify import replace_py_with_pyc


class PycifyArgs:
    directory: str
    out_dir: str


def cli(argv: list[str] | None = None) -> None:
    """CLI to run pycify."""
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Folder to convert .py files in")
    parser.add_argument(
        "--out-dir",
        help=(
            "Folder to output .pyc files to. "
            "Defaults to replacing the existing `.py` files."
        ),
    )
    args = parser.parse_args(argv, namespace=PycifyArgs)
    replace_py_with_pyc(args.directory, out_folder=args.out_dir)
