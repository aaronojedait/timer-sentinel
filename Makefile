.PHONY: setup install lint test precommit

setup:
	pipx install poetry
	poetry install
	pre-commit install

install:
	poetry install

type-check:
	poetry run mypy ./src ./tests --strict

lint:
	poetry run ruff check src/ tests/ --fix

test:
	pytest

precommit:
	pre-commit run --all-files
