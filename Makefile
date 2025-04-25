# Makefile

.PHONY: install format lint typecheck test serve clean commit bump

install:
	pip install -r requirements.txt

format:
	python -m ruff format src

lint:
	python -m ruff check src

typecheck:
	python -m mypy src

test:
	pytest tests

serve:
	uvicorn src.api.app:app --reload --reload-dir src

clean:
	rm -rf .venv .pytest_cache __pycache__ dist build .ruff_cache

commit:
	uvx --from commitizen cz commit

bump:
	uvx --from commitizen cz bump