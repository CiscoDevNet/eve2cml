.PHONY: check clean cov covo format testreqs

clean:
	rm -rf dist .pdm-build
	rm -rf htmlcov .coverage
	rm -rf .pytest_cache .ruff_cache .mypy_cache
	find . -depth -type d -name __pycache__ -not -path "./.venv/*" -exec rm -rf {} \;

cov:
	coverage run -m pytest
	coverage report

covo: cov
	coverage html
	open htmlcov/index.html

check:
	mypy src
	ruff check

format: check
	ruff format

testreqs:
	pdm export -f requirements --without-hashes >tests/requirements.txt

