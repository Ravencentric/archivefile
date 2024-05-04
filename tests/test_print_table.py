from archivefile import ArchiveFile
from pytest import CaptureFixture

table = """
| Name                                              | Date modified             | Type   | Size     | Compressed Size |
|---------------------------------------------------|---------------------------|--------|----------|-----------------|
| pyanilist-main                                    | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/.github                            | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/.github/cliff-template.toml        | 2024-04-10T20:10:57+00:00 | File   | 4.1KiB   | 4.1KiB          |
| pyanilist-main/.github/workflows                  | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/.github/workflows/docs.yml         | 2024-04-10T20:10:57+00:00 | File   | 1.2KiB   | 1.2KiB          |
| pyanilist-main/.github/workflows/release.yml      | 2024-04-10T20:10:57+00:00 | File   | 1.2KiB   | 1.2KiB          |
| pyanilist-main/.github/workflows/test.yml         | 2024-04-10T20:10:57+00:00 | File   | 1.9KiB   | 1.9KiB          |
| pyanilist-main/.gitignore                         | 2024-04-10T20:10:57+00:00 | File   | 3.0KiB   | 3.0KiB          |
| pyanilist-main/.pre-commit-config.yaml            | 2024-04-10T20:10:57+00:00 | File   | 366B     | 366B            |
| pyanilist-main/README.md                          | 2024-04-10T20:10:57+00:00 | File   | 3.7KiB   | 3.7KiB          |
| pyanilist-main/UNLICENSE                          | 2024-04-10T20:10:57+00:00 | File   | 1.2KiB   | 1.2KiB          |
| pyanilist-main/docs                               | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/docs/CNAME                         | 2024-04-10T20:10:57+00:00 | File   | 14B      | 14B             |
| pyanilist-main/docs/api-reference                 | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/docs/api-reference/clients.md      | 2024-04-10T20:10:57+00:00 | File   | 236B     | 236B            |
| pyanilist-main/docs/api-reference/enums.md        | 2024-04-10T20:10:57+00:00 | File   | 338B     | 338B            |
| pyanilist-main/docs/api-reference/exceptions.md   | 2024-04-10T20:10:57+00:00 | File   | 3.0KiB   | 3.0KiB          |
| pyanilist-main/docs/api-reference/models.md       | 2024-04-10T20:10:57+00:00 | File   | 646B     | 646B            |
| pyanilist-main/docs/api-reference/types.md        | 2024-04-10T20:10:57+00:00 | File   | 711B     | 711B            |
| pyanilist-main/docs/assets                        | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/docs/assets/logo.png               | 2024-04-10T20:10:57+00:00 | File   | 70.2KiB  | 70.2KiB         |
| pyanilist-main/docs/assets/logo.svg               | 2024-04-10T20:10:57+00:00 | File   | 1.7KiB   | 1.7KiB          |
| pyanilist-main/docs/examples.md                   | 2024-04-10T20:10:57+00:00 | File   | 3.2KiB   | 3.2KiB          |
| pyanilist-main/docs/index.md                      | 2024-04-10T20:10:57+00:00 | File   | 3.5KiB   | 3.5KiB          |
| pyanilist-main/mkdocs.yml                         | 2024-04-10T20:10:57+00:00 | File   | 2.1KiB   | 2.1KiB          |
| pyanilist-main/poetry.lock                        | 2024-04-10T20:10:57+00:00 | File   | 115.6KiB | 115.6KiB        |
| pyanilist-main/pyproject.toml                     | 2024-04-10T20:10:57+00:00 | File   | 1.9KiB   | 1.9KiB          |
| pyanilist-main/src                                | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/src/pyanilist                      | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/src/pyanilist/__init__.py          | 2024-04-10T20:10:57+00:00 | File   | 2.7KiB   | 2.7KiB          |
| pyanilist-main/src/pyanilist/_clients             | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/src/pyanilist/_clients/__init__.py | 2024-04-10T20:10:57+00:00 | File   | 99B      | 99B             |
| pyanilist-main/src/pyanilist/_clients/_async.py   | 2024-04-10T20:10:57+00:00 | File   | 10.2KiB  | 10.2KiB         |
| pyanilist-main/src/pyanilist/_clients/_sync.py    | 2024-04-10T20:10:57+00:00 | File   | 10.0KiB  | 10.0KiB         |
| pyanilist-main/src/pyanilist/_compat.py           | 2024-04-10T20:10:57+00:00 | File   | 329B     | 329B            |
| pyanilist-main/src/pyanilist/_enums.py            | 2024-04-10T20:10:57+00:00 | File   | 5.7KiB   | 5.7KiB          |
| pyanilist-main/src/pyanilist/_exceptions.py       | 2024-04-10T20:10:57+00:00 | File   | 1.4KiB   | 1.4KiB          |
| pyanilist-main/src/pyanilist/_models.py           | 2024-04-10T20:10:57+00:00 | File   | 20.3KiB  | 20.3KiB         |
| pyanilist-main/src/pyanilist/_query.py            | 2024-04-10T20:10:57+00:00 | File   | 4.8KiB   | 4.8KiB          |
| pyanilist-main/src/pyanilist/_types.py            | 2024-04-10T20:10:57+00:00 | File   | 1.5KiB   | 1.5KiB          |
| pyanilist-main/src/pyanilist/_utils.py            | 2024-04-10T20:10:57+00:00 | File   | 3.2KiB   | 3.2KiB          |
| pyanilist-main/src/pyanilist/_version.py          | 2024-04-10T20:10:57+00:00 | File   | 477B     | 477B            |
| pyanilist-main/src/pyanilist/py.typed             | 2024-04-10T20:10:57+00:00 | File   | 0B       | 0B              |
| pyanilist-main/tests                              | 2024-04-10T20:10:57+00:00 | Folder | 0B       | 0B              |
| pyanilist-main/tests/__init__.py                  | 2024-04-10T20:10:57+00:00 | File   | 0B       | 0B              |
| pyanilist-main/tests/mock_descriptions.py         | 2024-04-10T20:10:57+00:00 | File   | 21.3KiB  | 21.3KiB         |
| pyanilist-main/tests/test_anilist.py              | 2024-04-10T20:10:57+00:00 | File   | 9.2KiB   | 9.2KiB          |
| pyanilist-main/tests/test_async_anilist.py        | 2024-04-10T20:10:57+00:00 | File   | 9.3KiB   | 9.3KiB          |
| pyanilist-main/tests/test_async_exceptions.py     | 2024-04-10T20:10:57+00:00 | File   | 600B     | 600B            |
| pyanilist-main/tests/test_enums.py                | 2024-04-10T20:10:57+00:00 | File   | 867B     | 867B            |
| pyanilist-main/tests/test_exceptions.py           | 2024-04-10T20:10:57+00:00 | File   | 554B     | 554B            |
| pyanilist-main/tests/test_models.py               | 2024-04-10T20:10:57+00:00 | File   | 306B     | 306B            |
| pyanilist-main/tests/test_utils.py                | 2024-04-10T20:10:57+00:00 | File   | 4.1KiB   | 4.1KiB          |
"""


def test_print_table(capsys: CaptureFixture[str]) -> None:
    with ArchiveFile("tests/test_data/source_GNU.tar") as archive:
        archive.print_table(title="")
        assert capsys.readouterr().out.strip() == table.strip()
