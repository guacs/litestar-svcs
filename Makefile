.PHONY: clean check install fmt lint type-check test

clean:
	find . -name '__pycache__' -or -name '.ruff_cache' -or -name '.pytest_cache' -or -name '.mypy_cache' -exec rm -rf {} \;

check: lint type-check fmt

install:
	pre-commit install
	pdm install

fmt:
	pdm run black .

lint:
	pdm run ruff .

type-check:
	pdm run mypy .

test:
	pdm run pytest
