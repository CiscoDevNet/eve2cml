.PHONY: build check clean cov covo format mrproper sync test

build:
	$(shell ./version.sh)
	uv build

clean:
	rm -rf dist
	rm -rf htmlcov .coverage
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	rm -rf src/eve2cml.egg-info
	find . -depth -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} \;

mrproper: clean
	rm -rf .venv

cov:
	uv run coverage run -m pytest
	uv run coverage report

covo: cov
	uv run coverage html
	open htmlcov/index.html

check:
	uv run mypy --check-untyped-def src
	uv run ruff check

format: check
	uv run ruff format

sync:
	uv sync --dev --frozen

test:
	uv run pytest

