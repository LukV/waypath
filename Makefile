.PHONY: install format lint typecheck test serve clean commit bump pre-commit

install:
	poetry update
	poetry install

format:
	poetry run ruff format src

lint:
	poetry run ruff check src

typecheck:
	poetry run mypy src

pre-commit:
	poetry run pre-commit run --all-files

serve:
	poetry run uvicorn src.api.app:app --reload --reload-dir src

clean:
	rm -rf .venv .pytest_cache __pycache__ dist build .ruff_cache

commit:
	poetry run cz commit

bump:
	poetry run cz bump
