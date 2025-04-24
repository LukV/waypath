# Makefile

.PHONY: install lint typecheck test commit format clean

install:
	uv sync --active 
	uv run --active pre-commit install

lint:
	uvx ruff check --output-format=github

format:
	uvx ruff format .

typecheck:
	uvx mypy .

commit:
	uvx --from commitizen cz commit

bump:
	uvx --from commitizen cz bump

clean:
	rm -rf .venv .pytest_cache __pycache__ dist build .ruff_cache