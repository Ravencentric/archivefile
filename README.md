<br/>
<p align="center">
  <a href="https://github.com/Ravencentric/archivefile">
    <img src="https://raw.githubusercontent.com/Ravencentric/archivefile/main/docs/assets/logo.png" alt="Logo" width="400">
  </a>
  <p align="center">
    Unified interface for tar, zip, sevenzip, and rar files
  </p>
</p>

<div align="center">

[![PyPI - Version](https://img.shields.io/pypi/v/archivefile?link=https%3A%2F%2Fpypi.org%2Fproject%2Farchivefile%2F)](https://pypi.org/project/archivefile/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/archivefile)
![License](https://img.shields.io/github/license/Ravencentric/archivefile)
![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/Ravencentric/archivefile/release.yml)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/ravencentric/archivefile/test.yml?label=tests)
[![codecov](https://codecov.io/gh/Ravencentric/archivefile/graph/badge.svg?token=B45ODO7TEY)](https://codecov.io/gh/Ravencentric/archivefile)

</div>

## Table Of Contents

* [About](#about)
* [Installation](#installation)
* [Docs](#docs)
* [License](#license)

## About

`archivefile` is a wrapper around [`tarfile`](https://docs.python.org/3/library/tarfile.html), [`zipfile`](https://docs.python.org/3/library/zipfile.html), [`py7zr`](https://github.com/miurahr/py7zr), and [`rarfile`](https://github.com/markokr/rarfile).

The above libraries are excellent when you are dealing with a single archive format but things quickly get annoying when you have a bunch of mixed archives such as `.zip`, `.7z`, `.cbr`, `.tar.gz`, etc because each library has a slightly different syntax and quirks which you need to deal with.

`archivefile` wraps the common methods from the above libraries to provide a unified interface that takes care of said differences under the hood. However, it's not as powerful as the libraries it wraps due to lack of support for features that are unique to a specific archive format and library.

## Installation

`archivefile` is available on [PyPI](https://pypi.org/project/archivefile/), so you can simply use [pip](https://github.com/pypa/pip) to install it.

1. Without optional dependencies:

    ```sh
    pip install archivefile
    ```

2. With optional dependencies:

    - Required for [`ArchiveFile.print_tree()`](https://archivefile.ravencentric.cc/api-reference/archivefile/#archivefile.ArchiveFile.print_tree)

        ```sh
        pip install archivefile[bigtree]
        ```

    - Required for [`ArchiveFile.print_table()`](https://archivefile.ravencentric.cc/api-reference/archivefile/#archivefile.ArchiveFile.print_table)

        ```sh
        pip install archivefile[rich]
        ```

3. With all dependencies:

    ```sh
    pip install archivefile[all]
    ```

## Usage

`archivefile` offers a single class called `ArchiveFile` to deal with various archive formats. Some examples are given below:

```py
from archivefile import ArchiveFile

with ArchiveFile("../source.zip") as archive:
    archive.extract("pyproject.toml", destination="./dest/") # Extract a single member by it's name
    archive.extractall(destination="./dest/") # Extract all members
    archive.get_member("pyproject.toml")  # Get the ArchiveMember object for the member by it's name
    archive.get_members()  # Retrieve all members from the archive as a tuple of ArchiveMember objects
    archive.get_names()  # Retrieve names of all members in the archive as a tuple of strings
    archive.read_bytes("pyproject.toml") # Read the contents of the member as bytes
    archive.read_text("pyproject.toml")  # Read the contents of the member as text
    archive.print_tree()  # Print the contents of the archive as a tree.
    archive.print_table()  # Print the contents of the archive as a table.

with ArchiveFile("../source.zip", "w") as archive:
    archive.write("foo.txt", arcname="bar.txt")  # Write foo.txt to the archive as bar.txt
    archive.writeall("./src/") # Recursively write the ./src/ directory to the archive
    archive.write_text("spam and eggs", arcname="recipe.txt") # Write a string to the archive as recipe.txt
    archive.write_bytes(b"0101001010100101", arcname="terminator.py")  # Write bytes to the archive as terminator.py
```

## Docs

Checkout the complete documentation [here](https://archivefile.ravencentric.cc/).

## License

Distributed under the [Unlicense](https://choosealicense.com/licenses/unlicense/) License. See [UNLICENSE](https://github.com/Ravencentric/archivefile/blob/main/UNLICENSE) for more information.
