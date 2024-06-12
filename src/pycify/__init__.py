from __future__ import annotations

import compileall
import os
import re
import shutil
import sys
import yen.github
import subprocess


class PythonNotAvailable(Exception):
    """Raised when the Python version asked for is not available for download."""

    def __init__(self, python_version: str) -> None:
        super().__init__(python_version)
        self.python_version = python_version


def yellow(string: str, /) -> str:
    """Wraps string in ANSI yellow code."""
    return f"\033[33m{string}\033[m"


def replace_py_with_pyc(
    folder: str,
    out_folder: str | None = None,
    python_version: str | None = None,
    ignore_file_patterns: list[str] | None = None,
    _original_folder: str | None = None,
) -> list[str]:
    """
    Replaces all .py files with the cached .pyc files from __pycache__.
    If out_folder is provided, doesn't delete any existing Python files, simply
    creates the new `.pyc` files in the new location.
    """
    if ignore_file_patterns is None:
        ignore_file_patterns = []
    if _original_folder is None:
        _original_folder = folder
    if python_version is None:
        compileall.compile_dir(folder, quiet=1, force=True)
    else:
        # Use `yen` to ensure a portable Python is present on the system
        python_version, yen_python_bin_path = ensure_python(python_version)
        compile_command = f"{yen_python_bin_path} -m compileall -q -f {folder}"
        try:
            subprocess.run(
                [compile_command],
                shell=True,
                env={
                    "PATH": os.pathsep.join(
                        [yen_python_bin_path, os.environ.get("PATH", "")]
                    )
                },
                cwd=folder,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as exc:
            print("*** Build Failed:", file=sys.stderr)
            print("Stdout:\n" + exc.stdout.decode(errors="ignore"), file=sys.stderr)
            print("Stderr:\n" + exc.stdout.decode(errors="ignore"), file=sys.stderr)
            raise

    if out_folder is None:
        out_folder = folder

    created_pyc_files: list[str] = []

    for name in os.listdir(folder):
        subfolder = os.path.join(folder, name)
        out_subfolder = os.path.join(out_folder, name)
        if os.path.isdir(subfolder):
            created_pyc_files.extend(
                replace_py_with_pyc(
                    subfolder,
                    out_subfolder,
                    python_version,
                    ignore_file_patterns,
                    _original_folder=_original_folder,
                )
            )

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

        relative_path_file = os.path.relpath(filepath, _original_folder)
        if any(
            re.match(pattern, relative_path_file) for pattern in ignore_file_patterns
        ):
            print(f"{yellow('NOTE:')} Ignoring {filepath} as per ignore_file_patterns.")
            continue

        filename = file.removesuffix(".py")
        version_info_minor = python_version.split(".")[1]
        pycache_filename = f"{filename}.cpython-3{version_info_minor}.pyc"
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


def ensure_python(version: str) -> tuple[str, str]:
    """
    Checks that the version of Python we want to use is available on the
    system, and if not, downloads it.
    """
    try:
        return yen.ensure_python(version)
    except yen.github.NotAvailable:
        raise PythonNotAvailable(version)
