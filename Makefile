.PHONY : mypy format ruff lint pytest build

mypy:
	uv run mypy --python-executable=.venv/bin/python --install-types --check-untyped-defs --non-interactive src/gurobi_logtools

format:
	uvx ruff format

ruff:
	uvx ruff check

lint:
	format ruff

test:
	uv run pytest ./tests

build:
	uv build

docs:
	# placeholder for docs make command
