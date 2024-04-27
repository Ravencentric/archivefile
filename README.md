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

`archivefile` is a wrapper around [`tarfile`](https://docs.python.org/3/library/tarfile.html), [`zipfile`](https://docs.python.org/3/library/zipfile.html), [`py7zr`](https://github.com/miurahr/py7zr), and [`rarfile`](https://github.com/markokr/rarfile). It simplifies archive management tasks by providing a unified interface.

## Installation

`archivefile` is available on [PyPI](https://pypi.org/project/archivefile/), so you can simply use [pip](https://github.com/pypa/pip) to install it.

```sh
pip install archivefile
```

## Usage

```py
from archivefile import ArchiveFile

with ArchiveFile("archive.tar", "w") as archive:
    archive.extract("member.txt") # Extract a single member of the archive

with ArchiveFile("archive.tar", "w") as archive:
    archive.extractall(destination="~/output") # Extract all members

with ArchiveFile("archive.tar") as archive:
    archive.read_text("member.txt") # Read a member of the archive
```
