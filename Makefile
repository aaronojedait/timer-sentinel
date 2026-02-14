.PHONY: setup install lint test precommit

setup:
	pipx install poetry
	poetry install
	pre-commit install

install:
	poetry install

lint:
	ruff check src/ tests/ --fix

test:
	pytest

precommit:
	pre-commit run --all-files
