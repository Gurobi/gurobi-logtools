.PHONY : mypy format lint test testnb tox build docs

init:
	uv sync --locked
	uv run pre-commit install

mypy:
	uv run mypy --install-types --check-untyped-defs --non-interactive src/gurobi_logtools

format:
	uvx ruff format

lint:
	uvx ruff check

test:
	uv run --no-dev pytest ./tests

testnb:
	uv run --no-dev pytest ./tests
	uv run pytest --nbmake --nbmake-kernel=python3 gurobi-logtools.ipynb

tox:
	uv run tox

build:
	uv build

docs:
	# placeholder for docs make command
