set shell := ["sh", "-c"]

default: lint test

lint:
    uv run ruff check . --fix
    uv run ruff format .
    uv run mypy

test *args:
    rm -f .coverage
    uv sync --locked
    uv run coverage run -m pytest {{args}}
    uv sync --all-extras --locked
    uv run coverage run --append -m pytest {{args}}
    uv run coverage report -m
