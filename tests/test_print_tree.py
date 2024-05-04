from archivefile import ArchiveFile

tree = """
source_GNU.tar
└── pyanilist-main
    ├── .github
    │   ├── cliff-template.toml
    │   └── workflows
    │       ├── docs.yml
    │       ├── release.yml
    │       └── test.yml
    ├── .gitignore
    ├── .pre-commit-config.yaml
    ├── docs
    │   ├── api-reference
    │   │   ├── clients.md
    │   │   ├── enums.md
    │   │   ├── exceptions.md
    │   │   ├── models.md
    │   │   └── types.md
    │   ├── assets
    │   │   ├── logo.png
    │   │   └── logo.svg
    │   ├── CNAME
    │   ├── examples.md
    │   └── index.md
    ├── mkdocs.yml
    ├── poetry.lock
    ├── pyproject.toml
    ├── README.md
    ├── src
    │   └── pyanilist
    │       ├── py.typed
    │       ├── _clients
    │       │   ├── _async.py
    │       │   ├── _sync.py
    │       │   └── __init__.py
    │       ├── _compat.py
    │       ├── _enums.py
    │       ├── _exceptions.py
    │       ├── _models.py
    │       ├── _query.py
    │       ├── _types.py
    │       ├── _utils.py
    │       ├── _version.py
    │       └── __init__.py
    ├── tests
    │   ├── mock_descriptions.py
    │   ├── test_anilist.py
    │   ├── test_async_anilist.py
    │   ├── test_async_exceptions.py
    │   ├── test_enums.py
    │   ├── test_exceptions.py
    │   ├── test_models.py
    │   ├── test_utils.py
    │   └── __init__.py
    └── UNLICENSE
""".strip()


def test_print_tree(capsys) -> None:  # type: ignore
    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        archive.print_tree()
        assert capsys.readouterr().out.strip() == tree.strip()
