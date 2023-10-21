# pycify

Convert your entire Python project from `.py` files to `.pyc` files.

## Installation

```bash
pip install pycify
```

## Usage

```console
$ python cli.py
Hello CLI!

$ pycify .
Replacing ./utils/foo.py with ./utils/__pycache__/foo.cpython-311.pyc
Replacing ./cli.py with ./__pycache__/cli.cpython-311.pyc

$ tree .
.
├── cli.pyc
└── utils
    └── foo.pyc

2 directories, 2 files

$ python cli.pyc
Hello CLI!
```

## Local Development / Testing

- Create and activate a virtual environment
- Run `pip install -r requirements-dev.txt` to do an editable install
- Run `pytest` to run tests

## Type Checking

Run `mypy .`

## Create and upload a package to PyPI

Make sure to bump the version in `setup.cfg`.

Then run the following commands:

```bash
rm -rf build dist
python setup.py sdist bdist_wheel
```

Then upload it to PyPI using [twine](https://twine.readthedocs.io/en/latest/#installation):

```bash
twine upload dist/*
```
