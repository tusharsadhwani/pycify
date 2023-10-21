"""CLI interface for pycify."""
import argparse

from pycify import replace_py_with_pyc


class PycifyArgs:
    directory: str


def cli(argv: list[str] | None = None) -> None:
    """CLI to run pycify."""
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", help="Folder to convert .py files in")
    args = parser.parse_args(argv, namespace=PycifyArgs)
    replace_py_with_pyc(args.directory)
